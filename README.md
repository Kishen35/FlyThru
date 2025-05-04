# FlyThru: Automated Drive-Thru Ordering System

## Vision Enhancement Preview



https://github.com/user-attachments/assets/2282d614-effc-4e49-8d36-7b10041d23f8








Learn More: Check out the [Slides on Canva](https://www.canva.com/design/DAFwGzPJbH8/RnbRAqfv8rEJAwqB4wbGJw/view) or watch the Pitch Video below (note that the interface is slightly outdated)



https://github.com/user-attachments/assets/c4b4ce71-3f7a-4790-9e48-4570499d6fa9



![FlyThru Poster](https://github.com/Kishen35/FlyThru/blob/FYP/assets/FlyThru.png)

## Getting Started
### 1. Installing necessary packages
```python
pip install -r requirements.txt
```
### 2. Resource Creation
FlyThru relies on three main resources which are Azure Speech Service, Azure OpenAI, and Azure CosmosDB.

Azure OpenAI needs to have a gpt model (existing version runs on gpt-35-turbo-16k for more tokens) deployed under the name `flythru-ai`.

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

speech = {
    'subscription': os.environ.get('SPEECH_SUBSCRIPTION', '<YOUR_SPEECH_SUBSCRIPTION_KEY>'),
    'region': os.environ.get('SPEECH_REGION', '<YOUR_SPEECH_REGION>'),
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
