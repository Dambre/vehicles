Vehicle API

This is JSON based rest api. In request you must provide these headers:
```
Content-Type: application/json
x-api-key: API_KEY
```

API URL: https://j3u87ofncc.execute-api.eu-west-1.amazonaws.com/default/inventory_api

* GET returns all vehicles (if you provide VIN in url query parameters you will get specific vehicle)
* POST/PUT creates or replaces vehicle with provided one
* PATCH partial update vehicle
* DELETE delete vehicle
