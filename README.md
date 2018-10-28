Vehicle API

This is JSON based rest api. In request you must provide these headers:
```
Content-Type: application/json
x-api-key: API_KEY
```

API URL: https://j3u87ofncc.execute-api.eu-west-1.amazonaws.com/default/inventory_api

**GET** returns all vehicles (if you provide VIN in url query parameters eg.`link?VIN=test` you will get specific vehicle)

**POST/PUT** creates or replaces vehicle with provided one. Required JSON schema:
```
{
  VIN: 'vin',
  Model: 'model',
  Make: 'make',
  Year: 123
}
```

**PATCH** partial update vehicle. Required JSON schema:
```
{
 VIN: 'vin'
}
```

**DELETE** delete vehicle
```
{
 VIN: 'vin'
}
```
If you provide `Sold: true` in any PUT/POST/PATCH it will create timestampp when it was sold.
You can also provide any extra variables for example buyers data.
