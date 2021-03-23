import discord
import os
import requests
import re
import bs4 as bs
import difflib
from caffeinate import caffeinate

def init_aux():
  url = "https://azurlane.koumakan.jp/List_of_Auxiliary_Equipment#Max_Enhanced"
  response = requests.get(url)

  if response.status_code == 200:
    pass
  else:
    print("Failed aux gear list initialization!")
    return None

  soup = bs.BeautifulSoup(response.text,'html.parser')
  aux = soup.find_all("tbody")  
  aux_page = aux[-1]
  aux_data = aux_page.find_all('tr')
  aux_gear_list = []

  for row in aux_data[1:]:
    data = row.find('td').get_text().strip()
    aux_gear_list.append(data)
  print("Successfully initialized aux gear list.")
  print(aux_gear_list)
  return aux_gear_list

'''
Initialize reference data
'''
aux_gear_list = init_aux()

# Keys must be tuples
common_nicknames = {
  # Aux gear
  ("oxytorp", "rainbow dildo"):"Pure Oxygen Torpedo", 
  ("wheel", "gold wheel", "gold steering gear", "High Performance Hydraulic Steering Gear"):"improved hydraulic rudder",
  ("sg"):"SG Radar",
  ("gold air radar"):"High Performance Anti-Air Radar",
  ("gold fire control radar"):"High Performance Fire Control Radar",
  ("white shell"):"Type 1 Armor Piercing Shell",
  ("black shell"):"Super Heavy Shell",

}


client = discord.Client()

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  split_msg = msg.split(' ')
  command = split_msg[0]
  contents = split_msg[1:]
  # Convert underscore separated text to title case except for numbers
  parsed_contents = ['_'.join([y.title() if not y[0].isdigit() else y for y in x.replace('_', ' ').split()]) for x in contents]
  parsed_contents = ' '.join(parsed_contents)
  print("\nReceived a message!")
  print(f'"{command}, {parsed_contents}"')
  try:
    parsed_contents = next(value for keys, value in common_nicknames.items() if parsed_contents.lower() in keys)
    print(f"Replaced alias {common_nicknames} with {parsed_contents}.")
  except:
    pass
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
    ship = msg.split("!skills ")[1]
    skills = get_skills(ship)
    if skills is None:
      await message.channel.send("Error 404: Shipfu not found!")
    else:
      results = ["Here are the skills for {0}:\n\n".format(ship)]
      for skill in skills:
        results.append(skill[0] + ": " + skill[1] + "\n\n")
      await message.channel.send("".join(results))
  elif command == "!aux":
    await execute_aux(message, parsed_contents)
  elif msg.startswith("!"):
    print("Message was not a valid command")
    await message.channel.send("Invalid command!\n")
  else:
    print("Message was not a command")
    return

async def execute_aux(message, parsed_contents):
  if parsed_contents.strip() == "":
    await message.channel.send("Please enter an equipment name to serach for.\n> !aux <name>")
    return

  print("Asked for aux gear")
  #gear = msg.split("!aux")[1]
  #gear = parsed_contents.replace(' ', '_')
  try:
    gear = difflib.get_close_matches(parsed_contents, aux_gear_list, 1, cutoff=0.2)[0]
  except:
    await message.channel.send("Error 404: Gear not found!")
    return
  print(f"Found closest match to '{parsed_contents}' '{gear}'")
  info = get_aux(gear)
  if info is None:
    await message.channel.send("Error 404: Gear not found!")
  else:
    image_url = info['img_url']
    gear = info['name']
    results = info['stats']
    misc = info['misc']
    description = ""
    for item in misc:
      if item[0] == "Notes":
        description += item[1]
      else:
        description += item[0] + ' ' + item[1] + '\n'
    embed = make_embed(gear, description, results, image_url)

    await message.channel.send(embed=embed)  

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
  response = requests.get("https://azurlane.koumakan.jp/" + ship)

  if response.status_code == 200:
    print("Successful get request!")
  else:
    print("Unsucessful get request!")
    return None
  
  tables = response.text.split("mw-collapsible wikitable")[1]
  unfiltered_text = "".join(tables)
  skill_effects = []
  for _ in re.findall("<td.*>([A-Z].*[\.|)])[ \n]*<", unfiltered_text):
    if _ not in skill_effects:
      skill_effects.append(_)
  
  skill_names = re.findall("<b>(.*)</b><br />", unfiltered_text)
  for _ in range(len(skill_names)):
    skill_names[_] = re.sub("<br />", " ", skill_names[_])

  for skill in zip(skill_names, skill_effects):
    print(skill[0], skill[1], sep=": ", end="\n\n")

  return zip(skill_names, skill_effects)

def make_embed(title, description, fields, image=None):
  # Where fields is a list of tuples (field, value)
  embed = discord.Embed(title=title, description=description)
  for field in fields:
    embed.add_field(name=field[0], value=field[1], inline=False)
  embed.set_image(url=image)

  return embed

def get_aux(gear):
  # Add #Type_3 to request to get level 3 gear if applicable
  response = requests.get("https://azurlane.koumakan.jp/" + gear + "#Type_3")
  
  if response.status_code == 200:
    print("Successful get request!")
  else:
    print("Unsucessful get request!")
    return None
	
  results = {}
  
  # Find image of the equipment
  soup = bs.BeautifulSoup(response.text,'html.parser')
  img_url = soup.find('img')['src']
  results['img_url'] = "https://azurlane.koumakan.jp" + img_url
  print("image url:", img_url)

  # Get equipment name
  results['name'] = soup.find('h1').get_text()

  # Find stats of the equipment
  stats = soup.find_all("div", "eq-stats")

  stat_page = stats[-1]
  stat_data = stat_page.find_all('tr')
  extracted_stats = []
  print("Gear stats:")
  for row in stat_data[1:]:
    cell_header = row.find('img')
    if cell_header:
      title = cell_header['alt']
    else: 
      cell_header = row.find('th')
      title = cell_header.get_text().lstrip()    
    data = row.find('td').get_text()
    extracted_stats.append((title,data))
    print(title, data)
  
  results["stats"] = extracted_stats

  # Extract misc info  
  misc = soup.find_all("div", "eq-misc")
  misc_page = misc[-1]
  misc_data = misc_page.find_all('tr')
  extracted_misc = []
  # TODO: find hrefs and embed links
  for row in misc_data[1:]:
    cell_header = row.find('th')
    if cell_header:
      title = cell_header.get_text()
    else:
      continue
    data = row.find('td').get_text()

    extracted_misc.append((title,data))
    print(title, data)
  
  results["misc"] = extracted_misc

  return results

caffeinate()
client.run(os.getenv("TOKEN"))