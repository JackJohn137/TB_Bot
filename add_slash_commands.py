import requests
import time
import os


def add_command(command_json, headers, url):
	r = requests.post(url, headers=headers, json=command_json)
	print(command_json['name'], r)
	print(r.content)
	print()
	return r

def get_commands(headers, ID):
	url = f"https://discord.com/api/v8/applications/{ID}/commands"
	r = requests.get(url, headers=headers)
	#r = requests.get(url)
	print(r)
	print(r.content)
	return r

ID = os.getenv("ID")
TOKEN = os.getenv("TOKEN")
url = f"https://discord.com/api/v8/applications/{ID}/commands"

command_list = []

# AAAAAAAAA command
json = {
    "name": "aaaaaaaaa",
    "description": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
}
command_list.append(json)

command_list.append({
    "name": "idiot",
    "description": "u",
})

command_list.append({
    "name": "headnod",
    "description": "headnod",
})

command_list.append({
    "name": "help",
    "description": "Get information about TB Bot",
})

command_list.append({
    "name": "bonk",
    "description": "Send someone to horny jail",
})

command_list.append({
    "name": "stats",
    "description": "Get the stats for some ship",
    "options": [
        {
            "name": "name",
            "description": "The name of the ship",
            "required": True,
            "type":3
        }
    ]
})

command_list.append({
    "name": "skills",
    "description": "Get the skills for some ship",
    "options": [
        {
            "name": "name",
            "description": "The name of the ship",
            "required": True,
            "type":3
        }
    ]
})

command_list.append({
    "name": "gear",
    "description": "Search for some gear",
    "options": [
        {
            "name": "type",
            "description": "The type of gear",
            "required": True,
            "type":3,
            "choices": [
                {
                    "name": "Auxiliary",
                    "value": "aux"
                },
                {
                    "name": "Gun",
                    "value": "gun"
                },
                {
                    "name": "Plane",
                    "value": "plane"
                },
                {
                    "name": "Torpedo",
                    "value": "torp"
                },
                {
                    "name": "Anti-aircraft Gun",
                    "value": "aa"
                },
            ]
        },
        {
        	"name":"name",
        	"description":"The name of the gear you are looking for",
        	"required":True,
        	"type":3
        },
        {
        	"name":"flags",
        	"description":"Additional modifiers for your search",
        	"type":3,
        	"choices": [
        		{
        			"name":"Any",
        			"value":"-a"
        		}
        	]
        }
    ]
})

# Use bot token for authorization
headers = {
    "Authorization": f"Bot {TOKEN}"
}

add_command(command_list[-1], headers, url)
for command in command_list:
	add_command(command, headers, url)
	# Need to sleep to avoid getting a 429
	time.sleep(10)


get_commands(headers=headers, ID=ID)