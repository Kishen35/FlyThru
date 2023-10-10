import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://flythru.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'piAwh72HXnGs1bxY8bkwGTXroHUc9LjCsbcte0slGpD0IPu3djb4Y0qLVR6hfsAStr4fX6IAWQMVACDbCoT5mA=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'flythru'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'client'),
}

openAI = {
    'endpoint': os.environ.get('OPENAI_LINK', 'https://flythru-gpt.openai.azure.com/'),
    'api_key': os.environ.get('OPENAI_API', '1478e1c88d94457a99a0af5a00ad6a31'),
    'api_type': os.environ.get('GPT_PROVIDER', 'azure')
}