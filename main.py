import discord
import os
import requests
import re
from caffeinate import caffeinate

client = discord.Client()

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  print("\nReceived a message!")
  if msg.startswith("!info"):
    print("Asked for info!")
    await message.channel.send("What info do you want?\nUse !stats ship_name or !skills ship_name")
  elif msg.startswith("!stats "):
    print("Asked for stats!")
    if (msg == "!stats "):
      print("No ship listed...")
      await message.channel.send("What stats do you want?\n")
      return
    ship = msg.split("!stats ")[1]
    stats = get_stats(ship)
    if stats is None:
      await message.channel.send("Error 404: Shipfu not found!")
    else:
      results = ["Here are the stats for {0} at level 120 and 100 affinity (with retrofit if applicable):\n\n".format(ship)]
      for stat in stats:
        results.append(stat[0] + ": " + stat[1] + "\n")
      await message.channel.send("".join(results))
  elif msg.startswith("!skills "):
    print("Asked for skills")
    await message.channel.send("Skills search will be implemented at a later date.")
  elif msg.startswith("!"):
    print("Message was not a valid command")
    await message.channel.send("Invalid command!\n")
  else:
    print("Message was not a command")
    return

def get_stats(ship):
  response = requests.get("https://azurlane.koumakan.jp/" + ship)

  if response.status_code == 200:
    print("Successful get request!")
  else:
    print("Unsucessful get request!")
    return None

  stat_names = ["Health", "Armor", "Reload", "Luck", "Firepower", "Torpedo", "Evasion", "Speed", "Anti-Air", "Aviation", "Oil Cost",  "Accuracy", "ASW"]
  stat_values = re.findall("</th>\n<td.*>([A-Za-z0-9]*)\n</td>", response.text.split("wikitable")[4])

  print("Here are the stats for {0} at level 120 and 100 affinity (with retrofit if applicable):\n\n".format(ship))
  for stat in zip(stat_names, stat_values):
    print(stat[0], stat[1], sep=": ")

  return zip(stat_names, stat_values)

def get_skills(ship):
  return

caffeinate()
client.run(os.getenv("TOKEN"))