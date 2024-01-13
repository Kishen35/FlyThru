import os
import azure.cognitiveservices.speech as speechsdk
import openai

import item, order # item.py
import json

# This example requires environment variables named "OPEN_AI_KEY" and "OPEN_AI_ENDPOINT"
# Your endpoint should look like the following https://YOUR_OPEN_AI_RESOURCE_NAME.openai.azure.com/
import config
openai.api_key = config.openAI['api_key']
openai.api_base =  config.openAI['endpoint']
openai.api_type = config.openAI['api_type']
openai.api_version = '2023-12-01-preview'

# This will correspond to the custom name you chose for your deployment when you deployed a model.
deployment_id='flythru-ai' 

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription='62013dae4b9148fd86bf1629683eb86d', region='southeastasia')
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Should be the locale for the speaker's language.
speech_config.speech_recognition_language="en-SG"
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# The language of the voice that responds on behalf of Azure OpenAI.
speech_config.speech_synthesis_voice_name='en-US-JennyMultilingualNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

# TODO: printf for restaurant name & clientEmail
clientEmail = ""
menu_items = ""
orderID = ""

context = []

# for item in item.format_items("ron@mcdonalds.com"):
#     context.append({"role":"system", "content": item})

def updateContext(role, message, name=None): # for AI
    if name == None:
        context.append({"role": role, "content": message})
    else:
        context.append({"role": role, "name": name, "content": message})

conversation = []
def updateConversation(role, message): # for user
    conversation.append({"role": role, "content": message})
    order.update_context(clientEmail, orderID, conversation)
    return conversation

# Explanation of functions to OpenAI
functionDefinitions = [
    {
        "name": "get_item_details",
        "description": "Retrieves details for the ordered item such as the price and customization options. Called only when user has chosen exactly which item they would like to order. These details do not need to be specifically elaborated to the user unless asked.",
        "parameters": {
            "type": "object",
            "properties": {
                "ID": {
                    "type": "string",
                    "description": "The ID of the ordered item as provided by the system."
                }
            },
            "required": ["ID"],
        }
    },
    {
        "name": "get_order",
        "description": "Gets the customer's ordered items in JSON format.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The id of the order"
                }
            },
            "required": ["order_id"],
        }
    },
    {
        "name": "update_order",
        "description": "Update the order with all items ordered by the customer. Always called whenever customer makes changes to their order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The id of the order"
                },
                "items": {
                    "type": "string",
                    "description": "JSON of ordered items"
                },
                "amount": {
                    "type": "string",
                    "description": "Total amount of the ordered items"
                }
            },
            "required": ["order_id", "items", "amount"],
        }
    }
]

# Prompts Azure OpenAI with a request and synthesizes the response.
def ask_openai():
    # Ask Azure OpenAI
    response = openai.ChatCompletion.create(engine=deployment_id, 
                                            messages = context,
                                            functions = functionDefinitions,
                                            function_call = "auto")
    print(response)
    response_message = response['choices'][0]['message']
    
    # function calling
    if response_message.get("function_call"):
        available_functions = {
            "get_item_details" : item.get_item_details,
            "get_order": order.get_order,
            "update_order" : order.update_order
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])

        if function_name == "get_item_details":
            function_response = function_to_call(menu_items, **function_args) # need to pass in menu_items
        else:
            function_response = function_to_call(clientEmail, **function_args)
        
        updateContext("function", function_response, function_name)
        ask_openai()
    
    else:
        text = response['choices'][0]['message']['content']
        #text = response.choices[0].message.replace('\n', ' ').replace(' .', '.').strip()
        #print(response)
        print('Azure OpenAI response: ' + text)
        updateContext("assistant", text)
        updateConversation("assistant", text)

        # Azure text to speech output
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        # Check result
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            #print("Speech synthesized to speaker for text [{}]".format(text))
            pass
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

def intialize(email, order_id):
    global clientEmail
    clientEmail = email

    global menu_items
    menu_items = item.get_items(email)

    global orderID
    orderID = order_id

    global context
    context = []
    updateContext("system",
            """You are an AI assistant that takes orders at a drive-thru. Always limit responses to about 30 tokens only.
            
            For menu items:
            - You only take orders for items available in the menu.
            - The customer might use a short form when describing a menu item.
            - If the said item is not in the menu or the customer did not specify the exact item, follow-up with options of similar items in the menu.
            
            With regards to item customization:
            - You only allow customizations available for the item (obtained from the get_item_details function).
            - Do not elaborate on all the available customization options.
            - Ask follow-up questions if the user does not specify which item or customization options they would like to order.
            - Follow-up with customers if they have yet to choose a customization option that has a minimum higher than 0. For example if they have chosen a drink but not a side.
            - If the customization options have a minimum of 0, do not mention it unless asked.

            For item ordering:
            - Use the get_order() function to retrieve the order details in JSON format.
            - Call the update_order() function when the customer:
                - orders an item.
                - wants to remove an item.
                - wants to make changes to an ordered item.
            - Make sure that the update_order() function has already been called everytime you say you are updating the order.
            - For the 'items' parameter in the update_order() function:
                - pass in all the customer's ordered items (including the previously ordered items) details in JSON format as a string.
                - This is because the 'items' parameter will overwrite the entire list of ordered items.
                - Sample Data: [{
                                "itemName": "Burger Meal"
                                "itemPrice": "RM 10.50"
                                "quantity": "1"
                                "imgHref": "https://cloudfront.net/d66e676d_TPO9983.webp"
                                "customizations": [
                                {
                                    "itemName": "Fries",
                                    "itemType": "Sides",
                                    "price": "RM 0.00"
                                },
                                {
                                    "itemName": "Large Coke"
                                    "itemType": "Drink",
                                    "price": "RM 2.14"
                                }
                                ],
                                "itemAmount": "RM 12.64"
                                },
                                {
                                "itemName": "Iced Latte"
                                "itemPrice": "RM 12.50"
                                "quantity": "2"
                                "imgHref": "https://cloudfront.net/sa6sa88s9_TPO3288.webp"
                                "customizations": [],
                                "itemAmount": "RM 25.00"
                                }]
            - For the 'amount' parameter in the update_order() function, always pass in the sum of the 'itemAmount' for each ordered item.
            - The total is indicated by 'totalAmount', not 'itemAmount'.
            - After updating an order, follow up with the customer if they'd like anything else. If not, tell them the total amount to be paid in front and end the conversation.

            Other guidelines:
            - Only give a maximum of 3 suggestions, options, or choices for menu items and customization options.
            - Keep responses as short as possible at only about 30 tokens.
            """)

    global conversation
    conversation = []
    updateConversation("assistant", "Welcome to our drive-thru! How can I assist you today?")

loop = True
# Continuously listens for speech input to recognize and send as text to Azure OpenAI
def chat_with_open_ai():
    updateContext("system", f"List of items available for order which have been seperated by semicolon: \n {item.get_menu_items(menu_items)}")
    updateContext("system", f"order_id: {orderID}")
    updateContext("system", "Welcome to our drive-thru! How can I assist you today?")
    speech_synthesizer.speak_text_async("Welcome to our drive-thru! How can I assist you today?").get()

    global loop
    loop = True
    while loop:
        print("Azure OpenAI is listening. Say 'Stop' or press Ctrl-Z to end the conversation.")
        updateConversation("system", "Listening: Please speak into the microphone.")
        try:
            # Get audio from the microphone and then send it to the TTS service.
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            # If speech is recognized, send it to Azure OpenAI and listen for the response.
            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # if speech_recognition_result.text == "Stop.": 
                #     print("Conversation ended.")
                #     break
                
                if loop == False:
                    break

                print("Recognized speech: {}".format(speech_recognition_result.text))
                updateContext("user", speech_recognition_result.text)
                updateConversation("user", speech_recognition_result.text)
                ask_openai()
            # elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            #     print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
            #     updateConversation("system", "No speech could be recognized. Restart")
            #     break
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                updateConversation("system", "Speech Recognition canceled")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
        except EOFError:
            break
        except Exception as e:
            updateConversation("system", "An unexpected error occured, please restart.")
            print(e)
            break

# Main
# try:
#     order_id = order.create_order("ron@mcdonalds.com")
#     intialize("ron@mcdonalds.com", order_id)
#     chat_with_open_ai()
# except Exception as err:
#     print("Encountered exception. {}".format(err))

# REFERENCES
#
# Azure OpenAI speech to speech chat
# https://learn.microsoft.com/en-gb/azure/ai-services/speech-service/openai-speech?tabs=windows&pivots=programming-language-python
# 
# Introduction to prompt engineering
# https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering
#
# OpenAI Chat Completion's API Function Calling - JavaScript Example
# https://groff.dev/blog/openai-chat-completion-function-calls
# 
# How to use function calling with Azure OpenAI Service (Preview)
# https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling
#
# GPT models
# https://platform.openai.com/docs/guides/gpt

# Create chat completion
# https://platform.openai.com/docs/api-reference/chat/create?lang=python