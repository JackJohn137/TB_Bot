import discord
import os
import requests
import re
import bs4 as bs
import difflib
import traceback
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

# Get aux gear
aux_gear_list = init_gear_list(aux_url)
aux_gear_list += init_gear_list(asw_url)

# Get guns
dd_gun_list,dd_gun_info = init_gear_list(dd_gun_url, store_info=True)
cl_gun_list,cl_gun_info = init_gear_list(cl_gun_url, store_info=True)
ca_gun_list,ca_gun_info = init_gear_list(ca_gun_url, store_info=True)
bb_gun_list,bb_gun_info = init_gear_list(bb_gun_url, store_info=True)

# Merge gun information into single list/dict
gun_list = dd_gun_list + cl_gun_list + ca_gun_list + bb_gun_list
gun_info = {**dd_gun_info,**cl_gun_info,**ca_gun_info,**bb_gun_info}

# Get planes
fighter_list, fighter_info = init_gear_list(fighter_url, store_info=True, faction_only=True)
db_list, db_info = init_gear_list(dive_bomber_url, store_info=True, faction_only=True)
tb_list, tb_info = init_gear_list(torp_bomber_url, store_info=True, faction_only=True)
seaplane_list, seaplane_info = init_gear_list(seaplane_url, store_info=True, faction_only=True)

# Merge plane information into single list/dict
plane_list = fighter_list + db_list + tb_list + seaplane_list
plane_info = {**fighter_info,**db_info,**tb_info,**seaplane_info}

# Get torps
surf_torp_list, surf_torp_info = init_gear_list(surf_torp_url, store_info=True)
sub_torp_list, sub_torp_info = init_gear_list(sub_torp_url, store_info=True)

# Merge torp information into single list/dict
torp_list = surf_torp_list + sub_torp_list
torp_info = {**surf_torp_info, **sub_torp_info}

# Get AA guns
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
  ("squad tag","beaver badge","badge"):"Little Beaver Squadron Tag",

  # Guns
  ("georgia gun",):"Twin 457mm (Mark A Prototype)",
  ("pr3 ap gun","pr3 ap 406", "champagne gun", "champy gun"):"Triple 406mm (Mle 1938 Prototype)",
  ("cleve gun, brook gun"):'Triple 152mm (6"/47 MK16)',
  ("Surcouf gun",):"Twin 203mm (Mle 1924 Submarine-mount)",
  ("Leander gun",):'Twin 152mm (BL 6" Mk XXII)',
  ("Drake Gun",):'Triple 234mm (BL 9.2" Mk XII)',
  ("Roon Gun", "pr1 ap ca gun"):'Triple 203mm (SK C/34 Prototype)',
  ("Sanrui Gun","Louis Gun", "pr1 he ca gun"):'Triple 203mm (Mle 1934 Prototype)',
  ("Azuma Gun",):'Triple 310mm (Type 0 Prototype)',
  ("Zara Gun",):'Twin 203mm (Model 1927)',
  ("Algerie Gun",):'Twin 203mm (Mle 1924)',
  ("Cheshire Gun",):'Twin 234mm (BL 9.2" Mk XII Prototype)',
  ("Seattle Gun", "pr2 he gun", "pr2 cl gun"):'Triple 152mm (6"/47 Mk 17 DP Prototype)',
  ("Neptune Gun","Nep Gun", "pr1 cl gun", "pr1 ap cl gun"):'Triple 152mm (BL 6" Mk XXV Prototype)',
  ("Chappy Gun","Chapayev Gun"):'Triple 152mm (MK-5)',
  ("Jutland Gun","pr3 dd gun"):'Twin 114mm (QF Mk IV Prototype)',
  ("Baguette Gun",):'Single 138.6mm (Mle 1929)',
  ("JB Gun", "Jean Bart Gun"):'Quadruple 380mm (Mle 1935)',
  ("Izumo Gun",):'Triple 410mm (10th Year Type Prototype)',
  ("Monarch Gun",):'Triple 381mm (BL 15" Mk III Prototype)',
  ("FDG Gun",):'Twin 406mm (SK C/34 Prototype)',
  ("Odin Gun",):'Triple 305mm (SK C/39 Prototype)',
  ("Hood Gun",):'Twin 381mm (BL 15" Mk II)',
  ("Littorio Gun",):'Triple 381mm (Model 1934)',

  # Planes
  ("helldiver",):"Curtiss SB2C Helldiver",
  ("reppuu",):"Mitsubishi A7M Reppuu",

  # AA guns
  ("STAAG",):"Twin 40mm Bofors STAAG Mk II",
  ("Hazemeyer",):"Twin 40mm Bofors Hazemeyer Mount Mk IV",
  ("Roomba",):'',
  
  # Torps
  ("g7e",):'Submarine-mounted G7e Acoustic Homing Torpedo',
  ("bidder",):'Submarine-mounted Mark 20S "Bidder" Torpedo',
  ("mark 8 torp", "Mark VIII torp", "Mark VIII"):'Submarine-mounted Mark VIII Torpedo',
  ("Type 95","Type 95 torp"):'Submarine-mounted Type 95 Oxygen Torpedo',
  ("Type 96","Type 96 torp"):'Submarine-mounted Type 96 Oxygen Torpedo',
  ("Mark 12","Mark 12 torp"):'Submarine-mounted Mark 12 Torpedo',
  ("Mark 16","Mark 16 torp"):'Submarine-mounted Mark 16 Torpedo',
  ("Mark 18","Mark 18 torp"):'Submarine-mounted Mark 18 Torpedo',
  ("Mark 28","Mark 28 torp"):'Submarine-mounted Mark 28 Torpedo',
}

def unwrap_nicknames(input_dict):
  new_dict = {}
  for keys, value in input_dict.items():
    for key in keys:
      new_dict[key.lower()] = value
  return new_dict

common_nicknames = unwrap_nicknames(common_nicknames)

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
  #parsed_contents = ['_'.join([y.title() if not y[0].isdigit() else y for y in x.replace('_', ' ').split()]) for x in contents]
  parsed_contents = ' '.join(contents)
  print("\nReceived a message!")
  print(f'"{command}, {parsed_contents}"')
  exact_match = False
  try:
    # Attempt to determine if the user input is a common alias, or something similar to one
    keys = common_nicknames.keys()
    most_similar_key = difflib.get_close_matches(parsed_contents.lower(), keys, 1, cutoff=0.8)[0]
    parsed_contents = common_nicknames[most_similar_key]
    #parsed_contents = next(value in common_nicknames.items() if len(difflib.get_close_matches(parsed_contents.lower(), keys, 1, cutoff=0.8)) > 0)
    exact_match = True

    print(f"Replaced alias {' '.join(contents)} with {parsed_contents}.")
  except Exception:
    traceback.print_exc()
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
      # If we found a match based on common aliases
      gear = difflib.get_close_matches(parsed_contents, gear_list
    , 1, cutoff=match_cutoff)
    else:
      # Search our stored information
      # Simplify names and replace them with simple numbers to facilitate matching
      gear_list_mod = [x[1].split(splitter)[0] + '•' +str(x[0]) for x in enumerate(gear_list)]
      gear = difflib.get_close_matches(parsed_contents, gear_list_mod, 10, cutoff=match_cutoff)
      # Find actual names from gear list
      gear = [gear_list[int(item.split('•')[-1])] for item in gear]
  except:
    await message.channel.send("Error 404: Gear not found! Try a more detailed query.")
    return
  if len(gear) == 0:
    await message.channel.send("Error 404: Gear not found! Try a more detailed query.")
  elif len(gear) == 1:
    # If we resolved the request to a single piece of equipment, display it
    gear = gear[0]
    print(f"Found closest match to '{parsed_contents}' '{gear}'")
    await display_gear(gear, message)
  else:
    # Found multiple potential matches to the request, prompt the user for more information
    print(f"Found close matches to '{parsed_contents}' '{gear}'")
    await user_gear_query(gear, gear_info, message, contents)

    
async def display_gear(gear, message):
  # Retrieve information from the wiki
  info = get_gear(gear)
  if info is None:
    await message.channel.send("Error 404: Gear not found!")
  else:
    # Gather information to display to the user
    image_url = info['img_url']
    gear = info['name']
    stats = info['stats']
    misc = info['misc']
    description = ""
    for item in misc:
      # Other information specific to the gear, such as special effects or where it is obtained
      if item[0] == "Notes":
        description += item[1]
      else:
        description += item[0] + ' ' + item[1] + '\n'
    # Add link to wiki page
    base_url = "https://azurlane.koumakan.jp/" 
    if description[-1] != '\n':
      description += '\n'
    description += f"[Page Link]({base_url + gear.replace(' ','_') + '#Type_3'})"
    embed = make_embed(gear, description, stats, image_url)

    await message.channel.send(embed=embed)  

async def user_gear_query(gear, info, message, contents):
  # Display options availible for the user to pick from
  title = f"Search for '{' '.join(contents)}'"
  description = "I've found multiple results related to your query.\nPlease choose one from the list below with `!p <#>`"
  titles = [str(x[0]) + ' - ' + x[1] for x in enumerate(gear, 1)]
  subtitles = []
  for item in gear:
    # Retrieve stored information on each item in the query to help the user identify the equipment
    if item in info:
      data = ""
      first = True
      for key, value in info[item].items():
        # Concatenate information on the item into a string to be displayed beneath it
        if first:
          data += value
          first = False
        else:
          data += ', ' + value
      subtitles.append(data)
    else:
      subtitles.append("N/A")
  fields = zip(titles, subtitles)
  embed = make_embed(title, description, fields, image=None, thumbnail=query_thumbnail)

  # Update active queries with the requesting user and information related to their query
  user = message.author
  query_start = perf_counter()
  active_queries[message.author.id] = {"query_start":query_start, "user":user, "data":gear}
  await message.channel.send(embed=embed)
  pass

async def return_query(message, contents):
  # If the user tries to pick an item from a query
  if message.author.id not in active_queries:
    await message.channel.send("You have no active queries.")
    return
  # Retrieve information about the user's query
  query_data = active_queries[message.author.id]
  query_time = query_data["query_start"]
  response_time = perf_counter()
  if (response_time - query_time) > query_timeout:
    await message.channel.send("You have no active queries.")
    return

  # Take the index provided by the user and display information corresponding to it
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
  # Make an embed to display the information in discord
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
  # Scrape information from the wiki

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

  # Get last table, corresponding to the highest level of the equipment
  stat_page = stats[-1]
  stat_data = stat_page.find_all('tr')
  extracted_stats = []
  print("Gear stats:")
  # Get information from each row of the table
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
  for row in misc_data[1:]:
    cell_header = row.find('th')
    if cell_header:
      title = cell_header.get_text()
    else:
      continue
    data = row.find('td').get_text()
    hrefs = row.find('td').find_all('a')
    link = None
    base_url = "https://azurlane.koumakan.jp" 
    #print("hrefs:", hrefs)
    if hrefs:
      # Embed links in data text
      for href in hrefs:
        link = href.get('href')
        text = href.get_text()
        if text:
          print(f"text '{text}'")
          # Find if text is duplicated in the data, if so remove all but the first example
          substring_idx = data.find(text) + len(text)
          data = data[:substring_idx] + data[substring_idx:].replace(text, '')
          data = data.replace(text, f"[{text}]({base_url + link})")

    extracted_misc.append((title,data))
    print(title, data)
  
  results["misc"] = extracted_misc

  return results

caffeinate()
client.run(os.getenv("TOKEN"))