import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = 'order'

client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
db = client.get_database_client(DATABASE_ID)
container = db.get_container_client(CONTAINER_ID)

import json, requests, uuid

def create_order(clientEmail):
    print('\nCreating Order\n')

    order_id = str(uuid.uuid4())

    order_info = {
        'id': order_id,
        'clientEmail': clientEmail,
        'items' : [],
        "totalAmount": 0,
        "context": [],
        "plateNumber": None,
        "stop_order": 0
    }

    try:
        container.create_item(body=order_info)

    except exceptions.CosmosResourceExistsError as e:
        return "Error in order creation"
    
    return order_id

def update_display(clientEmail, order_id):
    return container.read_item(item=order_id, partition_key=clientEmail)

def get_order(clientEmail, order_id):
    order = container.read_item(item=order_id, partition_key=clientEmail)
    order["context"] = ""
    return str(order)

def update_context(clientEmail, order_id, context):
    read_item = container.read_item(item=order_id, partition_key=clientEmail)
    read_item["context"] = context

    response = container.replace_item(item=read_item, body=read_item)

def update_order(clientEmail, order_id, items, amount):
    print('\nUpdating Order\n')

    read_item = container.read_item(item=order_id, partition_key=clientEmail)
    read_item["items"] = json.loads(items)
    read_item["totalAmount"] = amount

    print(items)
    response = container.replace_item(item=read_item, body=read_item)

    print(response)

    return 'Replaced Item\'s Id is {0}'.format(response['id'])

def update_plateNumber(clientEmail, order_id, plateNumber):
    read_item = container.read_item(item=order_id, partition_key=clientEmail)
    read_item["plateNumber"] = plateNumber

    response = container.replace_item(item=read_item, body=read_item)

def stop_order(clientEmail, order_id):
    read_item = container.read_item(item=order_id, partition_key=clientEmail)
    read_item["stop_order"] = 1

    response = container.replace_item(item=read_item, body=read_item)