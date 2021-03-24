import discord
import os
import requests
import re
import bs4 as bs
import difflib
from caffeinate import caffeinate
from time import perf_counter

def init_gear_list(url, store_info = False, faction_only = False):
  response = requests.get(url)

  if response.status_code == 200:
    pass
  else:
    print("Failed gear list initialization!")
    return None

  soup = bs.BeautifulSoup(response.text,'html.parser')
  tables = soup.find_all("tbody")  
  page = tables[-1]
  data = page.find_all('tr')
  gear_list = []
  gear_info = {}

  for row in data[1:]:
    table_data = row.find('td')
    if not table_data:
      continue
    data = table_data.get_text().strip()
    gear_list.append(data)

    if store_info:
      extra_data = row.find_all('td')
      faction = extra_data[-1].find('a').get('title', 'None').strip()
      gear_info[data] = {"Faction":faction}
      if not faction_only:
        attribute = extra_data[-2].get_text().strip()
        gear_info[data] = {"Attribute":attribute}

  print("Successfully initialized gear list.")
  print(gear_list)
  if store_info:
    return gear_list, gear_info
  return gear_list

'''
Initialize reference data
'''
print("Beginning initialization.")
query_thumbnail = "https://cdn.discordapp.com/emojis/790024684934266930.png?v=1"

aux_url = "https://azurlane.koumakan.jp/List_of_Auxiliary_Equipment"
dd_gun_url = "https://azurlane.koumakan.jp/List_of_Destroyer_Guns"
cl_gun_url = "https://azurlane.koumakan.jp/List_of_Light_Cruiser_Guns"
ca_gun_url = "https://azurlane.koumakan.jp/List_of_Heavy_Cruiser_Guns"
bb_gun_url = "https://azurlane.koumakan.jp/List_of_Battleship_Guns"
surf_torp_url = "https://azurlane.koumakan.jp/List_of_Torpedoes"
sub_torp_url = "https://azurlane.koumakan.jp/List_of_Submarine_Torpedoes"
fighter_url = "https://azurlane.koumakan.jp/List_of_Fighters"
dive_bomber_url = "https://azurlane.koumakan.jp/List_of_Dive_Bombers"
torp_bomber_url = "https://azurlane.koumakan.jp/List_of_Torpedo_Bombers"
seaplane_url = "https://azurlane.koumakan.jp/List_of_Seaplanes"
aa_url = "https://azurlane.koumakan.jp/List_of_AA_Guns"
asw_url = "https://azurlane.koumakan.jp/List_of_ASW_Equipment"

aux_gear_list = init_gear_list(aux_url)
aux_gear_list += init_gear_list(asw_url)

dd_gun_list,dd_gun_info = init_gear_list(dd_gun_url, store_info=True)
cl_gun_list,cl_gun_info = init_gear_list(cl_gun_url, store_info=True)
ca_gun_list,ca_gun_info = init_gear_list(ca_gun_url, store_info=True)
bb_gun_list,bb_gun_info = init_gear_list(bb_gun_url, store_info=True)

# Merge gun information into single list/dict
gun_list = dd_gun_list + cl_gun_list + ca_gun_list + bb_gun_list
gun_info = {**dd_gun_info,**cl_gun_info,**ca_gun_info,**bb_gun_info}

fighter_list, fighter_info = init_gear_list(fighter_url, store_info=True, faction_only=True)
db_list, db_info = init_gear_list(dive_bomber_url, store_info=True, faction_only=True)
tb_list, tb_info = init_gear_list(torp_bomber_url, store_info=True, faction_only=True)
seaplane_list, seaplane_info = init_gear_list(seaplane_url, store_info=True, faction_only=True)

plane_list = fighter_list + db_list + tb_list + seaplane_list
plane_info = {**fighter_info,**db_info,**tb_info,**seaplane_info}

surf_torp_list, surf_torp_info = init_gear_list(surf_torp_url, store_info=True)
sub_torp_list, sub_torp_info = init_gear_list(sub_torp_url, store_info=True)

torp_list = surf_torp_list + sub_torp_list
torp_info = {**surf_torp_info, **sub_torp_info}

aa_list, aa_info = init_gear_list(aa_url, store_info = True, faction_only=True)

# Keys must be tuples, single element keys must have a ','
common_nicknames = {
  # Aux gear
  ("oxytorp", "rainbow dildo"):"Pure Oxygen Torpedo", 
  ("wheel", "gold wheel", "gold steering gear", "High Performance Hydraulic Steering Gear"):"improved hydraulic rudder",
  ("sg",):"SG Radar",
  ("gold air radar",):"High Performance Anti-Air Radar",
  ("gold fire control radar",):"High Performance Fire Control Radar",
  ("white shell",):"Type 1 Armor Piercing Shell",
  ("black shell",):"Super Heavy Shell",

  # Guns
  ("georgia gun",):"Twin 457mm (Mark A Prototype)",
  ("pr3 ap gun","pr3 ap 406"):"Triple 406mm (Mle 1938 Prototype)",

  # Planes
  ("helldiver",):"Curtiss SB2C Helldiver"
}

# Stores information related to ongoing user queries
query_timeout = 60
active_queries = {}

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
  command = split_msg[0].lower()
  contents = split_msg[1:]
  # Convert underscore separated text to title case except for numbers
  parsed_contents = ['_'.join([y.title() if not y[0].isdigit() else y for y in x.replace('_', ' ').split()]) for x in contents]
  parsed_contents = ' '.join(parsed_contents)
  print("\nReceived a message!")
  print(f'"{command}, {parsed_contents}"')
  exact_match = False
  try:
    # Attempt to determine if the user input is a common alias, or something similar to one
    parsed_contents = next(value for keys, value in common_nicknames.items() if len(difflib.get_close_matches(parsed_contents.lower(), keys, 1, cutoff=0.8)) > 0)
    exact_match = True

    print(f"Replaced alias {' '.join(contents)} with {parsed_contents}.")
  except:
    pass
  if command == "!info" or command == "!help":
    print("Asked for info!")
    title = "How can I help?"

    description =  "Please use one of the following commands:\n> `!stats <ship_name>`\n> `!skills <ship_name>`\n> `!aux <gear>`\n> `!gun <gear>`\n> `!plane <gear>`\n> `!torp <gear>`\n> `!aa <gear>`"


    embed = make_embed(title, description, fields=None, image=None, thumbnail=query_thumbnail)
    await message.channel.send(embed=embed)
    #await message.channel.send("What info do you want?\nUse !stats <ship_name>, !skills <ship_name>, !aux <gear>, !gun <gear>, !plane <gear>, !torp <gear>, or !aa <gear>")
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
  elif command == "!gun":
    await execute_gun(message, parsed_contents, contents, exact_match)
  elif command == "!plane":
    await execute_plane(message, parsed_contents, contents, exact_match)
  elif command == "!torp":
    await execute_torp(message, parsed_contents, contents, exact_match)
  elif command == "!aa" or command == "!aagun":
    await execute_aa(message, parsed_contents, contents, exact_match)
     
  elif command == "!p":
    await return_query(message, contents)
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
  try:
    gear = difflib.get_close_matches(parsed_contents, aux_gear_list, 1, cutoff=0.2)[0]
  except:
    await message.channel.send("Error 404: Gear not found!")
    return
  print(f"Found closest match to '{parsed_contents}' '{gear}'")
  await display_gear(gear, message)

async def execute_gun(message, parsed_contents, contents, exact_match=False):
  if parsed_contents.strip() == "":
    await message.channel.send("Please enter an gun to serach for.\n> !gun <name>")
    return

  print("Asked for gun")
  await general_query_execute(parsed_contents, gun_list, gun_info, message, contents, exact_match, match_cutoff=.65)

async def execute_plane(message, parsed_contents, contents, exact_match=False):
  if parsed_contents.strip() == "":
    await message.channel.send("Please enter a plane to serach for.\n> !plane <name>")
    return

  print("Asked for plane")
  await general_query_execute(parsed_contents, plane_list, plane_info, message, contents, exact_match, match_cutoff=.4)

async def execute_torp(message, parsed_contents, contents, exact_match=False):
  if parsed_contents.strip() == "":
    await message.channel.send("Please enter a torpedo to serach for.\n> !torp <name>")
    return

  print("Asked for torp")

  await general_query_execute(parsed_contents, torp_list, torp_info, message, contents, exact_match, match_cutoff=.45, splitter='Torpedo')

async def execute_aa(message, parsed_contents, contents, exact_match=False):
  if parsed_contents.strip() == "":
    await message.channel.send("Please enter an aa gun to serach for.\n> !aa <name>")
    return

  print("Asked for aa gun")
  await general_query_execute(parsed_contents, aa_list, aa_info, message, contents, exact_match, match_cutoff=.45)

async def general_query_execute(parsed_contents, gear_list, gear_info, message, contents, exact_match, match_cutoff=.6, splitter='('):
  try:
    if exact_match:
      gear = difflib.get_close_matches(parsed_contents, gear_list
    , 1, cutoff=match_cutoff)
    else:
      # Simplify names and replace them with simple numbers to facilitate matching
      gear_list_mod = [x[1].split(splitter)[0] + '•' +str(x[0]) for x in enumerate(gear_list)]
      gear = difflib.get_close_matches(parsed_contents, gear_list_mod, 10, cutoff=match_cutoff)
      # Find actual names from gear list
      gear = [gear_list[int(item.split('•')[-1])] for item in gear]
  except:
    await message.channel.send("Error 404: Gear not found!")
    return
  if len(gear) == 0:
    await message.channel.send("Error 404: Gear not found!")
  elif len(gear) == 1:
    gear = gear[0]
    print(f"Found closest match to '{parsed_contents}' '{gear}'")
    await display_gear(gear, message)
  else:
    print(f"Found close matches to '{parsed_contents}' '{gear}'")
    await user_gear_query(gear, gear_info, message, contents)

    
async def display_gear(gear, message):
  info = get_gear(gear)
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

async def user_gear_query(gear, info, message, contents):
  title = f"Search for '{' '.join(contents)}'"
  description = "I've found multiple results related to your query.\nPlease choose one from the list below with `!p <#>`"
  titles = [str(x[0]) + ' - ' + x[1] for x in enumerate(gear, 1)]
  subtitles = []
  for item in gear:
    if item in info:
      data = ""
      first = True
      for key, value in info[item].items():
        if first:
          data += f"{value}"
          first = False
        else:
          data += f", {value}"
      subtitles.append(data)
    else:
      subtitles.append("N/A")
  fields = zip(titles, subtitles)
  embed = make_embed(title, description, fields, image=None, thumbnail=query_thumbnail)

  user = message.author
  query_start = perf_counter()
  active_queries[message.author.id] = {"query_start":query_start, "user":user, "data":gear}
  await message.channel.send(embed=embed)
  pass

async def return_query(message, contents):
  if message.author.id not in active_queries:
    await message.channel.send("You have no active queries.")
    return
  query_data = active_queries[message.author.id]
  query_time = query_data["query_start"]
  response_time = perf_counter()
  if (response_time - query_time) > query_timeout:
    await message.channel.send("You have no active queries.")
    return

  index = int(contents[0]) - 1
  if index + 1 > len(query_data["data"]):
    await message.channel.send("Invalid index.")
    return
  gear = query_data["data"][index]
  await display_gear(gear, message)
  
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

def make_embed(title, description, fields, image=None, thumbnail=None):
  if image == None:
    image = discord.Embed.Empty
  if thumbnail == None:
    thumbnail = discord.Embed.Empty
  # Where fields is a list of tuples (field, value)
  embed = discord.Embed(title=title, description=description)
  if fields:
    for field in fields:
      embed.add_field(name=field[0], value=field[1], inline=False)
  embed.set_image(url=image)
  embed.set_thumbnail(url=thumbnail)

  return embed

def get_gear(gear):
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