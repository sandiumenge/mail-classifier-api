## API Definition

**Endpoint:** `/classify-email` 

**Method:** `POST` 

**Parameters** (sent in the body as JSON text): 

``` json
{ 
  "client_id": integer, 
  "fecha_envio": string, 
  "email_body": string 
} 
```

### Response

### If the client has no outstanding debts

**Response code:** 200 

**Response body** (in JSON format): 

``` json
{ 
  "success": boolean,
  "prediction": string 
} 
```

### If the client has outstanding debts

**Response code:** 200

**Response body** (in JSON format): 

``` json
{ 
  "success": false,
  "reason": "The client has outstanding debts"
} 
```

**Description**: The `/classify-email` endpoint accepts requests with the `POST` method. 
It expects three parameters in the request body: 
`client_id`, which must be an integer; `fecha_envio`, which represents the date and time of sending in datetime format 
(format `YYYY-MM-dd hh:mm:ss`); and `email_body`, which is a string containing the body of the email 
to classify. If the request is successfully processed, the endpoint will return a status code 200 and a JSON object 
with a field named `prediction`, which will contain a string with the prediction, along with a field
`success`, a boolean with the value `true`.

If the client is listed as having outstanding debts, the endpoint will return a status code 200 and a JSON object
with a `success` field set to `false` and a `reason` field with the message "The client has outstanding debts".
