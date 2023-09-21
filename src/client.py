import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = 'client'

client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
db = client.get_database_client(DATABASE_ID)
container = db.get_container_client(CONTAINER_ID)

def create_account(clientEmail, password, clientName):
    print('\nCreating Account\n')

    account_info = {'id': clientEmail,
        'clientEmail': clientEmail,
        'password' : password,
        'clientName': clientName
    }

    try:
        container.create_item(body=account_info)

    except exceptions.CosmosResourceExistsError as e:
        return 1
    
    return 0

def update_account(clientEmail, password, clientName):
    print('\nUpdating Account\n')

    read_item = container.read_item(item=clientEmail, partition_key=clientEmail)
    read_item['password'] = password
    read_item['clientName'] = clientName

    response = container.replace_item(item=read_item, body=read_item)

    print('Replaced Item\'s Id is {0}'.format(response['id']))

def login(clientEmail, password):
    print('\nLogging In\n')

    try:
        # Including the partition key value of clientEmail in the WHERE filter results in a more efficient query
        items = list(container.query_items(
            query="SELECT * FROM r WHERE r.clientEmail=@clientEmail AND r.password=@password",
            parameters=[
                { "name":"@clientEmail", "value": clientEmail },
                { "name":"@password", "value": password }
            ]
        ))
        
        print('Item queried by Partition Key {0}'.format(items[0].get("id")))

    except IndexError as e:
        return 1
    
    return items[0]

def update_merchantid(merchant_id, clientEmail):
    print('\nUpserting an item\n')

    read_item = container.read_item(item=clientEmail, partition_key=clientEmail)
    read_item['merchant_id'] = merchant_id
    response = container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}'.format(response['id']))