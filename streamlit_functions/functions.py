import requests
import pickle
import os
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
from PIL import Image
import numpy as np

#Packages to handle jsons and predicting
from preprocessing.get_json import process_one_json, check_and_create_columns
from preprocessing.get_diff import calculate_event_differences
from preprocessing.clean_preprocess import preprocess_pred

#List of Tiers
tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

#Dict with code and game modes
queues_dict = {
    0: None,
    2: '5v5 Blind Pick games',
    4: '5v5 Ranked Solo games',
    6: '5v5 Ranked Premade games',
    7: 'Co-op vs AI games',
    8: '3v3 Normal games',
    9: '3v3 Ranked Flex games',
    14: '5v5 Draft Pick games',
    16: '5v5 Dominion Blind Pick games',
    17: '5v5 Dominion Draft Pick games',
    25: 'Dominion Co-op vs AI games',
    31: 'Co-op vs AI Intro Bot games',
    32: 'Co-op vs AI Beginner Bot games',
    33: 'Co-op vs AI Intermediate Bot games',
    41: '3v3 Ranked Team games',
    42: '5v5 Ranked Team games',
    52: 'Co-op vs AI games',
    61: '5v5 Team Builder games',
    65: '5v5 ARAM games',
    67: 'ARAM Co-op vs AI games',
    70: 'One for All games',
    72: '1v1 Snowdown Showdown games',
    73: '2v2 Snowdown Showdown games',
    75: '6v6 Hexakill games',
    76: 'Ultra Rapid Fire games',
    78: 'One For All: Mirror Mode games',
    83: 'Co-op vs AI Ultra Rapid Fire games',
    91: 'Doom Bots Rank 1 games',
    92: 'Doom Bots Rank 2 games',
    93: 'Doom Bots Rank 5 games',
    96: 'Ascension games',
    98: '6v6 Hexakill games',
    100: '5v5 ARAM games',
    300: 'Legend of the Poro King games',
    310: 'Nemesis games',
    313: 'Black Market Brawlers games',
    315: 'Nexus Siege games',
    317: 'Definitely Not Dominion games',
    318: 'ARURF games',
    325: 'All Random games',
    400: '5v5 Draft Pick games',
    410: '5v5 Ranked Dynamic games',
    420: '5v5 Ranked Solo games',
    430: '5v5 Blind Pick games',
    440: '5v5 Ranked Flex games',
    450: '5v5 ARAM games',
    460: '3v3 Blind Pick games',
    470: '3v3 Ranked Flex games',
    600: 'Blood Hunt Assassin games',
    610: 'Dark Star: Singularity games',
    700: "Summoner's Rift Clash games",
    720: 'ARAM Clash games',
    800: 'Co-op vs. AI Intermediate Bot games',
    810: 'Co-op vs. AI Intro Bot games',
    820: 'Co-op vs. AI Beginner Bot games',
    830: 'Co-op vs. AI Intro Bot games',
    840: 'Co-op vs. AI Beginner Bot games',
    850: 'Co-op vs. AI Intermediate Bot games',
    900: 'ARURF games',
    910: 'Ascension games',
    920: 'Legend of the Poro King games',
    940: 'Nexus Siege games',
    950: 'Doom Bots Voting games',
    960: 'Doom Bots Standard games',
    980: 'Star Guardian Invasion: Normal games',
    990: 'Star Guardian Invasion: Onslaught games',
    1000: 'PROJECT: Hunters games',
    1010: 'Snow ARURF games',
    1020: 'One for All games',
    1030: 'Odyssey Extraction: Intro games',
    1040: 'Odyssey Extraction: Cadet games',
    1050: 'Odyssey Extraction: Crewmember games',
    1060: 'Odyssey Extraction: Captain games',
    1070: 'Odyssey Extraction: Onslaught games',
    1090: 'Teamfight Tactics games',
    1100: 'Ranked Teamfight Tactics games',
    1110: 'Teamfight Tactics Tutorial games',
    1111: 'Teamfight Tactics test games',
    1200: 'Nexus Blitz games',
    1300: 'Nexus Blitz games',
    1400: 'Ultimate Spellbook games',
    1900: 'Pick URF games',
    2000: 'Tutorial 1',
    2010: 'Tutorial 2',
    2020: 'Tutorial 3'}

#Dict with code and region names
region_dict = {
    "Latin America South": "LA2",
    "Brazil": "BR1",
    "Europe Nordic & East": "EUN1",
    "Europe West": "EUW1",
    "Latin America North": "LA1",
    "North America": "NA1",
    "Oceania": "OCE",
    "Russia": "RU",
    "Turkey": "TR",
    "Japan": "JP",
    "Republic of Korea": "KR",
    "The Philippines": "PH",
    "Singapore, Malaysia, & Indonesia": "SG",
    "Taiwan, Hong Kong, and Macao": "TW",
    "Thailand": "TH",
    "Vietnam": "VN"
    }

event_types_dict = {'KILL_ACE': "Ace",
        'FIRST_BLOOD': "First Blood",
        '_KILL_MULTI': "Multi Kill",
        'minionsKilled': "minions",
        'AIR_DRAGON': "Air Dragon",
        'CHEMTECH_DRAGON' : "Chemtech Dragon",
        'EARTH_DRAGON' :"Earth Dragon",
        'FIRE_DRAGON' :"Fire Dragon",
        'HEXTECH_DRAGON' :"Hextech Dragon",
        'RIFTHERALD' :"Rift Herald",
        'WATER_DRAGON' :"Water Dragon",
        'ELDER_DRAGON' :"Elder Dragon",
        'BARON_NASHOR' :"Baron Nashor",
        'totalGold' : "Total Gold",
        'INNER_TURRET' : "Inner Turret",
        'OUTER_TURRET' : "Outer Turret",
        'BASE_TURRET' : "Base Turret",
        'INHIBITOR_BUILDING' : "Inhibitor",
        'NEXUS_TURRET' : "Nexus Turret"}

#List with columns of interest for data preprocessing
columns_of_interest = ['killType_KILL_ACE',
        'killType_KILL_FIRST_BLOOD',
        'killType_KILL_MULTI',
        'minionsKilled',
        'monsterType_AIR_DRAGON',
        'monsterType_CHEMTECH_DRAGON',
        'monsterType_EARTH_DRAGON',
        'monsterType_FIRE_DRAGON',
        'monsterType_HEXTECH_DRAGON',
        'monsterType_RIFTHERALD',
        'monsterType_WATER_DRAGON',
        'monsterType_ELDER_DRAGON',
        'monsterType_BARON_NASHOR',
        'totalGold',
        'towerType_INNER_TURRET',
        'towerType_OUTER_TURRET',
        'towerType_BASE_TURRET',
        'buildingType_INHIBITOR_BUILDING']

#Dict with region code and its corresponding continent
macro_region = {
    "BR1" : "AMERICAS",
    "EUN1" : "EUROPE",
    "EUW1" : "EUROPE",
    "LA1" : "AMERICAS",
    "LA2" : "AMERICAS",
    "NA1" : "AMERICAS",
    "OCE" : "SEA",
    "RU" : "EUROPE",
    "TR" : "EUROPE",
    "JP" : "ASIA",
    "KR" : "ASIA",
    "PH" : "SEA",
    "SG" : "SEA",
    "TW" : "SEA",
    "TH" : "SEA",
    "VN" : "SEA"
    }

#Dict with match types
match_type_list = {
    "Normal - Model not optimized for ARAMs" : "normal",
    "Ranked" : "ranked",
    "Tourney" : "tourney",
    }

#Dict with max values for columns of interests
columns_of_interest_dict = {5: {'killType_KILL_ACE': 0,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 3,
        'minionsKilled': 40,
        'monsterType_AIR_DRAGON': 0,
        'monsterType_CHEMTECH_DRAGON' :0,
        'monsterType_EARTH_DRAGON' :0,
        'monsterType_FIRE_DRAGON' :0,
        'monsterType_HEXTECH_DRAGON' :0,
        'monsterType_RIFTHERALD' :0,
        'monsterType_WATER_DRAGON' :0,
        'monsterType_ELDER_DRAGON' :0,
        'monsterType_BARON_NASHOR' :0,
        'totalGold' : 4000,
        'towerType_INNER_TURRET' : 0,
        'towerType_OUTER_TURRET' : 0,
        'towerType_BASE_TURRET' : 0,
        'buildingType_INHIBITOR_BUILDING' : 0},

                            10: {'killType_KILL_ACE': 2,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 5,
        'minionsKilled': 80,
        'monsterType_AIR_DRAGON': 1,
        'monsterType_CHEMTECH_DRAGON' :1,
        'monsterType_EARTH_DRAGON' :1,
        'monsterType_FIRE_DRAGON' :1,
        'monsterType_HEXTECH_DRAGON' :1,
        'monsterType_RIFTHERALD' :1,
        'monsterType_WATER_DRAGON' :1,
        'monsterType_ELDER_DRAGON' :0,
        'monsterType_BARON_NASHOR' :0,
        'totalGold' : 12000,
        'towerType_INNER_TURRET' : 3,
        'towerType_OUTER_TURRET' : 3,
        'towerType_BASE_TURRET' : 0,
        'buildingType_INHIBITOR_BUILDING' : 0},

                            15: {'killType_KILL_ACE': 3,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 8,
        'minionsKilled': 120,
        'monsterType_AIR_DRAGON': 1,
        'monsterType_CHEMTECH_DRAGON' :1,
        'monsterType_EARTH_DRAGON' :1,
        'monsterType_FIRE_DRAGON' :1,
        'monsterType_HEXTECH_DRAGON' :1,
        'monsterType_RIFTHERALD' :2,
        'monsterType_WATER_DRAGON' :1,
        'monsterType_ELDER_DRAGON' :0,
        'monsterType_BARON_NASHOR' :0,
        'totalGold' : 20000,
        'towerType_INNER_TURRET' : 3,
        'towerType_OUTER_TURRET' : 3,
        'towerType_BASE_TURRET' : 3,
        'buildingType_INHIBITOR_BUILDING' : 3},

                            20: {'killType_KILL_ACE': 4,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 15,
        'minionsKilled': 160,
        'monsterType_AIR_DRAGON': 1,
        'monsterType_CHEMTECH_DRAGON' :1,
        'monsterType_EARTH_DRAGON' :1,
        'monsterType_FIRE_DRAGON' :1,
        'monsterType_HEXTECH_DRAGON' :1,
        'monsterType_RIFTHERALD' :2,
        'monsterType_WATER_DRAGON' :1,
        'monsterType_ELDER_DRAGON' :0,
        'monsterType_BARON_NASHOR' :0,
        'totalGold' : 25000,
        'towerType_INNER_TURRET' : 3,
        'towerType_OUTER_TURRET' : 3,
        'towerType_BASE_TURRET' : 3,
        'buildingType_INHIBITOR_BUILDING' : 6},

                            25: {'killType_KILL_ACE': 5,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 20,
        'minionsKilled': 200,
        'monsterType_AIR_DRAGON': 2,
        'monsterType_CHEMTECH_DRAGON' :2,
        'monsterType_EARTH_DRAGON' :2,
        'monsterType_FIRE_DRAGON' :2,
        'monsterType_HEXTECH_DRAGON' :2,
        'monsterType_RIFTHERALD' :2,
        'monsterType_WATER_DRAGON' :2,
        'monsterType_ELDER_DRAGON' :1,
        'monsterType_BARON_NASHOR' :1,
        'totalGold' : 30000,
        'towerType_INNER_TURRET' : 3,
        'towerType_OUTER_TURRET' : 3,
        'towerType_BASE_TURRET' : 3,
        'buildingType_INHIBITOR_BUILDING' : 9},

                            30: {'killType_KILL_ACE': 6,
        'killType_KILL_FIRST_BLOOD': 1,
        'killType_KILL_MULTI': 25,
        'minionsKilled': 240,
        'monsterType_AIR_DRAGON': 3,
        'monsterType_CHEMTECH_DRAGON' :3,
        'monsterType_EARTH_DRAGON' :3,
        'monsterType_FIRE_DRAGON' :3,
        'monsterType_HEXTECH_DRAGON' :3,
        'monsterType_RIFTHERALD' :2,
        'monsterType_WATER_DRAGON' :3,
        'monsterType_ELDER_DRAGON' :2,
        'monsterType_BARON_NASHOR' :2,
        'totalGold' : 35000,
        'towerType_INNER_TURRET' : 3,
        'towerType_OUTER_TURRET' : 3,
        'towerType_BASE_TURRET' : 3,
        'buildingType_INHIBITOR_BUILDING' : 12}
                            }

def fetch_match(puuid, api_key, region, match_type, count = 3):
    """
    Function to get the list of match IDs
    """
    url = f'https://{macro_region[str(region)]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type={match_type}&count={count}&api_key={api_key}'
    return requests.get(url).json()

def match_result(match_final, user_participant):
    """
    Function to evaluate if the user's team lost or won the match
    """
    result_dic = {"True" : "Victory", "False" : "Defeat"}
    if user_participant < 5:
        return result_dic[str(match_final["info"]["teams"][0]["win"])]
    else:
        return result_dic[str(match_final["info"]["teams"][1]["win"])]

def match_result_team(match_final, team):
    """
    Function to evaluate if the team team lost or won the match
    """
    result_dic = {"True" : "Victory", "False" : "Defeat"}
    if team == "Blue":
        return result_dic[str(match_final["info"]["teams"][0]["win"])]
    else:
        return result_dic[str(match_final["info"]["teams"][1]["win"])]

### ADJUST LATER WITH MODEL RESULTS
def diagnosis(proba, result):
    """
    Evaluates the probability and the result to give a diagnosis of the match
    """
    if proba > 60 and result == "Defeat":
        return ":orange[Diagnosis: Afraid to Win] :collision:"
    if proba < 40 and result == "Victory":
        return ":green[Diagnosis: Defied the Odds] :heart_on_fire:"
    else:
        return "Diagnosis: Fair Result :handshake:"

def find_image(champion):
    """
    Try to find the champion image, if it does not exist return a poro image
    """
    if os.path.exists(f"images/champion/{champion}.png"):
        return f"images/champion/{champion}.png"
    return  f"images/champion/4155.png"

def unique_tier(solo_tier,flex_tier):
    """
    Defines a unique tier for the user in order to get the correct model
    If the user does not have a ranked or solo tier, it returns "SILVER"
    """
    if solo_tier != 0:
        return solo_tier
    elif flex_tier != 0:
        return flex_tier
    return "SILVER"

def find_transformer(minute,league):
    """
    Calculate the closest transformer, load the transformer from the pickle file and returns it
    """
    if minute > 24:
        transformer_file_path = f"preprocessing/pickles_transformers/30/{league}_transformer.pkl"
        with open(transformer_file_path, "rb") as transformer_file:
        # Load the transformer from the pickle file
            transformer = pickle.load(transformer_file)
        return transformer
    else:
        minute_t = (24//5 + 1) * 5
        transformer_file_path = f"preprocessing/pickles_transformers/{minute_t}/{league}_transformer.pkl"
        with open(transformer_file_path, "rb") as transformer_file:
            transformer = pickle.load(transformer_file)
        return transformer

def prediction(json,minute_list,look_events,columns_of_interest,fitted_model,proba_position,league):
        """
        Performs data preprocessing and returns prediction result for all frames in match
        """
        result = []
        for minute in minute_list:
            transformer = find_transformer(minute,league)
            df = process_one_json(json,minute,look_events)
            df_dif = calculate_event_differences(df)
            df_dif.drop(columns="matchId",inplace=True)
            df_cc = check_and_create_columns(df_dif, columns_of_interest)
            X_pred_prep = preprocess_pred(df_cc, transformer)
            model = fitted_model
            proba = model.predict_proba(X_pred_prep)
            #If user is team 1 we need to save proba_position 1, the probability of victory
            #If user is team 2 we need to save proba_position 2, the probability of defeat for team 1
            result.append(round(proba[0][proba_position]*100,2))
        return  result

def get_image(champion):
    """
    Get the champion image as an array into the script
    """
    image_path = find_image(champion).format(champion.title())
    im = Image.open(image_path)
    return im

def offset_image(coord, name, ax):
    """
    Offsets an image
    """
    img = get_image(name)
    rez = img.resize((np.array(img.size)/5).astype(int))
    im = OffsetImage(rez, zoom=0.72)
    im.image.axes = ax
    ab = AnnotationBbox(im, (coord, 0),  xybox=(0., -16.), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=0)

    ax.add_artist(ab)
