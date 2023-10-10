# FlyThru: Automated Drive-Thru Ordering System
Learn More: 

[Slides on Canva](https://www.canva.com/design/DAFwGzPJbH8/RnbRAqfv8rEJAwqB4wbGJw/view)
//
[Pitch Video](https://cloudmails-my.sharepoint.com/:v:/g/personal/tp055296_mail_apu_edu_my/EROObqn2ImROp5gpdPhCWN0B-Csk8qexEClBWhuxtOdDqQ?e=1tgtoy&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19) 

![FlyThru Poster](https://github.com/Kishen35/FlyThru/blob/FYP/assets/FlyThru.png)

## Getting Started
### 1. Installing necessary packages
```python
pip install -r requirements.txt
```
### 2. Resource Creation
FlyThru relies on three main resources which are Azure Speech Service, Azure OpenAI, and Azure CosmosDB.

Azure Cosmos DB needs to have three containers [`client`, `item`, `order`] with `clientEmail` as the partition key and `id` as the primary key for each.

Once these resources have been created, the secrets are to be stored in a `config.py` file.
```python
# config.py
import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', '<YOUR_COSMOSDB_ENDPOINT>'),
    'master_key': os.environ.get('ACCOUNT_KEY', '<YOUR_COSMOSDB_KEY>'),
    'database_id': os.environ.get('COSMOS_DATABASE', 'flythru'), # suggested to name database as flythru
}

openAI = {
    'endpoint': os.environ.get('OPENAI_LINK', '<YOUR_OPENAI_ENDPOINT>'),
    'api_key': os.environ.get('OPENAI_API', '<YOUR_OPENAI_KEY>'),
    'api_type': os.environ.get('GPT_PROVIDER', 'azure') # can be openai if using OpenAI's API directly
}
```

### 3. Running system
1. Run `main.py`
2. Visit [localhost](http://127.0.0.1:5000/)
3. Login and Register for an account
4. Import menu items by adding the Grab Merchant ID of the restaurant
5. Click on "Start Order" to begin taking an order
6. Speak into the microphone when the action bar turns blue
7. Once order completed, click on "Stop Order"

## Preview
![Screenshot](https://github.com/Kishen35/FlyThru/blob/FYP/assets/FlyThru%20interface.png)
