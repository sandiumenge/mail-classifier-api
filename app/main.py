"""
El modelo que voy a usar es el nuevo modelo de Google, Gemma 3N.
El motivo por el cual he elegido este modelo es porque acaba de salir hace un par de semanas y promete
ser un muy buen modelo "lightweight". Además, este modelo permite hacer classificaciones zero-shot,
que debido a que la cantidad de datos que nos proporcionan es muy pequeña, es lo que buscamos.
Por otro lado, tenia ganas de probarlo desde que salió así que voy a usar esto como excusa para probarlo.

Autor: Jacob Sandiumenge
Fecha: Julio 2025
"""

from fastapi import FastAPI
import mysql.connector
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
import json
from pydantic import BaseModel

class EmailRequest(BaseModel):
    client_id: int
    email_body: str

model_name = "facebook/bart-large-mnli"
model_local_path = "data/" + model_name.replace("/", "_")

# Guarda el modelo en local (si no existe) y lo carga
def load_model():
    if not os.path.exists(model_local_path):
        print(f"Downloading model '{model_name}' to '{model_local_path}'")
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Save the model and tokenizer locally
        os.makedirs(model_local_path, exist_ok=True)
        model.save_pretrained(model_local_path)
        tokenizer.save_pretrained(model_local_path)
    else:
        print(f"Loading model from local directory '{model_local_path}'")
        model = AutoModelForSequenceClassification.from_pretrained(model_local_path)
        tokenizer = AutoTokenizer.from_pretrained(model_local_path)

    return model, tokenizer

app = FastAPI()

# Hay dos formas de hacer esto, teniendo el modelo cargado constantemente mientras el docker
# está corriendo o cargando el modelo cada vez que se hace una petición. Para este caso,
# como se supone que es una herramienta de atencion al cliente, es mejor tener el modelo cargado
# constantemente para que las respuestas sean más rápidas.
model, tokenizer = load_model()
classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

@app.post("/classify-email")
def classify_text(data: EmailRequest):    
    client_id = data.client_id
    email_body = data.email_body
    with mysql.connector.connect(
        host="db",
        port=3306,
        user="root",
        password="root",
        database="atc"
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM impagos WHERE client_id = %s", (client_id,))
            impago = cursor.fetchone()
    # <-- Now, after both 'with' blocks have closed
    if impago:
        return {
            "exito": False,
            "razon": "El cliente tiene impagos"
        }
    
    # Puse las categorias y descripciones en un archivo JSON para faciles futuras modificaciones
    with open("categories.json", "r") as f:
        categories = json.load(f)["categories"]

    # Para dar más contexto a las categorias, las descripciones se incluyen en el label
    label_map = {f"{cat}: {desc}": cat for cat, desc in categories.items()}
    labels = list(label_map.keys())

    result = classifier(email_body, candidate_labels=labels)

    best_label = result["labels"][0]
    best_category = label_map[best_label]
     
    return { 
        "exito": True,
        "prediccion": best_category
    }


# # result = classifier(email_body, candidate_labels=labels)
#     pipe = pipeline("zero-shot-classification", model="google/gemma-3n-E2B-it")
#     result = pipe(email_body, candidate_labels=labels)

#     best_label = result["labels"][0]
#     best_category = label_map[best_label]