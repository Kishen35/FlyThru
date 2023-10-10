import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = 'item'

client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
db = client.get_database_client(DATABASE_ID)
container = db.get_container_client(CONTAINER_ID)

import json, requests

def get_menu(clientEmail, merchant_id): # uses Grab's API
    CONTAINER_ID = 'item'
    container = db.get_container_client(CONTAINER_ID)

    response = requests.get(f"https://portal.grab.com/foodweb/v2/merchants/{merchant_id}")
    
    try:    
        items = response.json()["merchant"]["menu"]["categories"]

        print('\nQuerying for an  Item by Partition Key\n')

        # first clear existing menu
        oldItems = list(container.query_items(
            query="SELECT * FROM r WHERE r.clientEmail=@account_number",
            parameters=[
                { "name":"@account_number", "value": clientEmail }
            ]
        ))

        for oldItem in oldItems:
            print('\nDeleting Item by Id\n')
            response = container.delete_item(item=oldItem.get("id"), partition_key=clientEmail)
            print('Deleted item\'s Id is {0}'.format(oldItem.get("id")))
            
        # create an item for each category
        for newItem in items:
            if newItem['ID'] != "TRUNCATED": # some categories are truncated
                newItem['id'] = newItem['ID']
                newItem['clientEmail'] = clientEmail
                container.create_item(body=newItem)

        return merchant_id

    except KeyError as e: # error triggered when no "merchant" in Grab's API
        return 1
    
def get_items(clientEmail):
    return list(container.query_items(
                    query="SELECT * FROM r WHERE r.clientEmail=@account_number",
                    parameters=[
                        { "name":"@account_number", "value": clientEmail }
                    ]
            ))

def format_price(price): # because JSON data is not in decimal
    price = int(price) / 100
    return price

def get_menu_items(menu_items):
    items = ""
    for category in menu_items:
        for item in category["items"]:
            items = f'{items} ID: {item["ID"]} | itemName: {item["name"]}; \n'
    return items

# print(get_menu_items(get_items("ron@mcdonalds.com")))

def get_item_details(menu_items, ID):
    details = "Item not found or incomplete item name"

    for category in menu_items:
        for item in category["items"]:
            if ID == item["ID"]:
                details = f'The {item["name"]} costs RM {format_price(item["priceInMinorUnit"])}\n'
                
                try:
                    # Modifier Groups
                    for modifierGroup in item["modifierGroups"]:
                        
                        selectionRangeMin = "0"
                        selectionRangeMax = "0"
                        try:
                            selectionRangeMin = modifierGroup['selectionRangeMin']
                            selectionRangeMax = modifierGroup['selectionRangeMax']
                        except KeyError:
                            pass

                        details = f'{details}This item also comes with customization options for {modifierGroup["name"]}. Customers can choose a minimum of {selectionRangeMin} to a maximum of {selectionRangeMax} options. These options are:\n'
                        
                        for customization in modifierGroup["modifiers"]:
                            details = f'{details}- {customization["name"]} for RM {customization["priceV2"]["amountDisplay"]}\n'
                except KeyError:
                    details = "Item not found"

    return details

# print(get_item_details(get_items("ron@mcdonalds.com"), "MYITE20230721231147011597"))

# def format_items(clientEmail):
#     categories = get_items(clientEmail)
#     formatted_items = []

#     i = 0
#     for category in categories:
#         for item in category["items"]:
#             formatted_items.append(f"{item['name']} costs RM {format_price(item['priceInMinorUnit'])}")
            
#             try:
#                 formatted_items[i] = f"{formatted_items[i]}. It comes with the following customization options:"

#                 # Modifier Groups
#                 for modifierGroup in item["modifierGroups"]:
#                     formatted_items[i] = f"{formatted_items[i]} {modifierGroup['selectionRangeMax']} {modifierGroup['name']} that can be chosen from:"
#                     for customization in modifierGroup["modifiers"]:
#                         formatted_items[i] = f"{formatted_items[i]} {customization['name']} (RM {format_price(customization['priceV2']['amountDisplay'])});"
            
#             except KeyError:
#                 pass

#             i=i+1
    
#     return formatted_items

# def format_items(clientEmail):
#     categories = get_items(clientEmail)

#     for category in categories:
#         print(category["items"][0]["name"])
#         for item in category["items"]:
#             return (item["name"] + 
#                   "costs RM " + format_price(item['priceInMinorUnit']),
#                   f'{"comes with the following sides" if item["modifierGroups"][0]["name"] == "Side" else ""}', 
#                   *[side["name"] for side in item["modifierGroups"]])