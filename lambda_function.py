
import boto3
import json
import time
from decimal import Decimal


TABLE = 'vehicles'
dynamo = boto3.resource('dynamodb').Table(TABLE)


class Error(Exception):
    def __init__(self, message=''):
        self.message = message


class InvalidData(Error):
    """Raise when data is missing"""


class InvalidVIN(Error):
    """Raise when VIN is not found in db"""


class Validate(object):
    @classmethod
    def create(cls, data):
        cls.VIN(data)
        assert 'Make' in data
        assert 'Model' in data
        assert 'Year' in data

    @classmethod
    def patch(cls, data):
        cls.VIN(data)

    @staticmethod
    def VIN(data):
        assert 'VIN' in data and isinstance(data.get('VIN', None), str)


def get(payload):
    VIN = payload.get('VIN', None)
    if not VIN:
        return dynamo.scan().get('Items', [])

    try:
        return dynamo.get_item(Key={'VIN': VIN})['Item']

    except KeyError:
        raise InvalidVIN


def post_or_put(payload):
    Validate.create(payload)
    if payload.get('Sold', None):
        payload.update({'SoldAt': int(time.time())})

    dynamo.put_item(Item=payload)
    return {'message': 'Success'}


def prepare_update_expression(data):
    # support for dynamic attributes and prepare expression string and values for dynamo update_item
    UpdateExpression = 'set '
    expression_items = []
    ExpressionAttributeValues = {}
    for key, value in data.items():
        key, key_map = key, ':{}'.format(key)
        if key == 'Year':
            # handling random error stating year is reserved keyword ..
            key = '#year_attr'
            key_map = ':year_attr'

        expression_items.append('{}={}'.format(key, key_map))
        ExpressionAttributeValues.update({key_map: value})

    UpdateExpression = UpdateExpression + ', '.join(expression_items)
    return UpdateExpression, ExpressionAttributeValues


def patch(payload):
    Validate.VIN(payload)
    if payload.get('Sold', None):
        payload.update({'SoldAt': int(time.time())})

    VIN = payload.pop('VIN')
    UpdateExpression, ExpressionAttributeValues = prepare_update_expression(payload)
    dynamo.update_item(
        Key={'VIN': VIN},
        UpdateExpression=UpdateExpression,
        ExpressionAttributeValues=ExpressionAttributeValues,
        ExpressionAttributeNames={
            "#year_attr": "Year"  # handling random error stating year is reserved keyword ..
        }
    )
    return {'message': 'Success'}


def delete(payload):
    Validate.VIN(payload)
    dynamo.delete_item(Key={'VIN': payload['VIN']})
    return {'message': 'Success'}


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            # prepare dynamo number for json
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)

        return super().default(o)


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps({'message': err.message}) if err else json.dumps(res, cls=JsonEncoder),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    methods = {
        'DELETE': lambda payload: delete(payload),
        'GET': lambda payload: get(payload),
        'POST': lambda payload: post_or_put(payload),
        'PUT': lambda payload: post_or_put(payload),
        'PATCH': lambda payload: patch(payload),
    }

    method = event['httpMethod']
    if method not in methods:
        return respond(ValueError('Unsupported method "{}"'.format(method)))

    if method == 'GET':
        payload = event['queryStringParameters'] or {}

    else:
        payload = json.loads(event['body'], parse_int=Decimal, parse_float=Decimal)

    try:
        return respond(None, methods[method](payload))

    except InvalidVIN:
        return respond(InvalidVIN('No such vehicle'))

    except AssertionError:
        return respond(InvalidData('Invalid data provided'))
