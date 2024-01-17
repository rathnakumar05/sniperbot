import os
import re
import aiohttp
import json

def message_formater(message_details):
    message = (
        "Status: {status} \n"
        "User Details: \n"
        "id: {id}\n"
        "username: {username}\n\n"
        "Content: "
        "{content}"
    )
    message_param = {}
    message_param["status"] = message_details.get("status")
    message_param["content"] = message_details.get("message") 
    if(message_details.get("from_user")):
        message_param["id"] = message_details.get("from_user").id
        message_param["username"] = message_details.get("from_user").username
    else:
        message_param["id"] = None
        message_param["username"] = None

    return message.format(**message_param)

async def support_notifier(message_details):
    if os.getenv("MODE")=="DEV":
        return
    
    url = f"https://api.telegram.org/bot{os.getenv('SUPPORT_BOT_TOKEN')}/sendMessage"
    payload = json.dumps({
        "chat_id": os.getenv('SUPPORT_GROUP_ID'),
        "text": message_formater(message_details)
    })
    headers = {
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            res = await response.text()