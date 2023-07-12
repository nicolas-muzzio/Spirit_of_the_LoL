import streamlit as st

#To work with requests and APIs
import json
import requests

#To operate with date and times
import datetime

#To open pickles with model and transformers info
import pickle

#For making plots
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
import numpy as np
from PIL import Image

#To load the key from .env and get access to stored variables
#from dotenv import load_dotenv
import os
import sys

sys.path.insert(0,os.path.abspath(".."))

#Packages to handle jsons and predicting
from preprocessing.get_json import process_one_json, check_and_create_columns

from preprocessing.get_diff import calculate_event_differences

from preprocessing.clean_preprocess import preprocess_pred

#Load .env file
#load_dotenv()

#Get value stored in variable
api_key = st.secrets["API_KEY"]

st.set_page_config(
            page_title="NoobMeter", # Adjust things later
            page_icon="🐍", #Change icon later
            layout="wide", # or centered, wide has more space
            initial_sidebar_state="auto") # collapsed

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

### ADJUST LATER WITH MODEL RESULTS
def diagnosis(proba, result):
    """
    Evaluates the probability and the result to give a diagnosis of the match
    """
    if proba > 60 and result == "Defeat":
        return ":orange[Diagnosis: GiT GuD] :clown_face:"
    if proba < 40 and result == "Victory":
        return ":green[Diagnosis: Defied the Odds] :heart_on_fire:"
    else:
        return "Diagnosis: Fair Result :handshake:"

def find_image(champion):
    """
    Try to find the champion image, if it does not exist return a poro image
    """
    if os.path.exists(f"../../images/champion/{champion}.png"):
        return f"../../images/champion/{champion}.png"
    return  f"../../images/champion/4155.png"

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

def prediction(pred_folder,minute,look_events,columns_of_interest,fitted_model, transformer):
        """
        Performs data preprocessing and returns prediction result
        """
        df = process_one_json(pred_folder,minute,look_events)
        df_dif = calculate_event_differences(df)
        df_dif.drop(columns="matchId",inplace=True)
        df_cc = check_and_create_columns(df_dif, columns_of_interest)
        X_pred_prep = preprocess_pred(df_cc, transformer)
        model = fitted_model
        #result = model.predict(X_pred_prep)
        proba = model.predict_proba(X_pred_prep)
        return  proba

def get_image(champion):
    """
    Get the champion image as an array into the script
    """
    path = find_image(champion).format(champion.title())
    #im = plt.imread(path)
    im = Image.open(path)
    return im

def offset_image(coord, name, ax):
    """
    Offsets an image
    """
    img = get_image(name)
    rez = img.resize((np.array(img.size)/3.5).astype(int))
    im = OffsetImage(rez, zoom=0.72)
    im.image.axes = ax
    ab = AnnotationBbox(im, (coord, 0),  xybox=(0., -16.), frameon=False,
                        xycoords='data',  boxcoords="offset points", pad=0)

    ax.add_artist(ab)

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

#Page Title
st.title('NoobMeter')

#Main Form to get data from user
with st.form(key='params_for_api'):

    columns = st.columns(3)

    summoner_name = columns[0].text_input("What is your Summoner Name?", value="hideonbush") #Default SummonerName corresponds to T1 Faker

    chosen_region = columns[1].selectbox("Choose your Region", region_dict.keys(), index= 10) #Default Index correspond to KR

    chosen_match_type = columns[2].selectbox("Choose the Match Type", match_type_list.keys(), index= 1) #Default Index correspond to Ranked

    st.form_submit_button('Make prediction')

#Converts user input to region ID
region = region_dict[chosen_region]

#Converts user input to region ID
match_type = match_type_list[chosen_match_type]

#puuid and encrypted_summonerID obtention
path_puuid = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}'
try:
    summoner_data = requests.get(path_puuid).json()
except:
    st.write("Summoner not found, please check Summoner Name and Region")
    st.stop()

puuid = summoner_data['puuid']
encrypted_summonerID = summoner_data['id']

#Tiers obtention -> needed to know which model we need to use
path_tier = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summonerID}?api_key={api_key}"
ranked_tiers = requests.get(path_tier).json()

#Obtain the tier info if the summoner has any
no_tier = False
solo_tier = 0
flex_tier = 0
if ranked_tiers == []:
    no_tier = True
else:
    for i in range(len(ranked_tiers)):
        if ranked_tiers[i]["queueType"] == "RANKED_SOLO_5x5":
            solo_tier = ranked_tiers[i]["tier"]
        else:
            flex_tier = ranked_tiers[i]["tier"]

#match id obtention
matches = fetch_match(puuid, api_key, region, match_type, count = 1)

#Display Ranks
if no_tier:
    st.markdown("##### You do not have a ranked tier")
else:
    columns2 = st.columns(4)
    if solo_tier != 0:
        columns2[0].markdown(f"##### Your Solo Queue Tier is {solo_tier}")
    if flex_tier != 0:
        columns2[2].markdown(f"##### Your Flex Queue Tier is {flex_tier}")

st.write(f" ")
st.write(f" ")

if matches == []:
    st.write("No matches found, please check introduced data")
    st.stop()

for match in range(len(matches)):

    #Obtain Match Timeline Data
    path_match_timeline =f"https://{macro_region[str(region)]}.api.riotgames.com/lol/match/v5/matches/{matches[match]}/timeline?api_key={api_key}"

    match_timeline = requests.get(path_match_timeline).json()

    #Obtain Match Final Data
    path_match_timeline =f"https://{macro_region[str(region)]}.api.riotgames.com/lol/match/v5/matches/{matches[match]}?api_key={api_key}"
    match_final = requests.get(path_match_timeline).json()

    #To find match type using queues_dict
    match_type_key = match_final["info"]["queueId"]

    #Obtains unx timestamp and converts it into date time
    formatted_date = datetime.datetime.fromtimestamp(match_final["info"]["gameStartTimestamp"]/1000).strftime('%Y-%m-%d %H:%M')

    #Generates columns for displaying match data
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1,1,0.18,1,1,1,0.18,1])

    #Determines the user number of participant (if 0-4 is team 1, if 5-9 is team 2)
    user_participant = match_final["metadata"]["participants"].index(puuid)

    #Determines the user champion
    user_champion = match_final["info"]["participants"][user_participant]["championName"]

    #Info for loading model
    minute = 10
    look_events=["CHAMPION_SPECIAL_KILL","CHAMPION_KILL","ELITE_MONSTER_KILL","BUILDING_KILL"]
    folder_path = "data/"
    league=unique_tier(solo_tier,flex_tier)
    pickle_file_path = f"../model/pickles_models/{league}_model.pkl"
    transformer_file_path = f"../preprocessing/pickles_transformers/{minute}/{league}_transformer.pkl"

    with open(pickle_file_path, "rb") as file:
        # Load the data from the pickle file
        fitted_model = pickle.load(file)
    with open(transformer_file_path, "rb") as transformer_file:
        # Load the transformer from the pickle file
        transformer = pickle.load(transformer_file)


    #####PREPO OF MATCH_TIMELINE
    with col1:
        st.markdown("##### Date")
        st.write(f"{formatted_date}")
        st.write("##### Player Side:")
        if user_participant < 5:
            st.write("##### :blue[Blue Team]")
        else:
            st.write("##### :red[Red Team]")
    with col2:
        st.write("##### Match Type")
        st.write(f"{queues_dict[match_type_key]}")
        st.write("##### Played Champion:")
        st.image(find_image(user_champion), caption = user_champion, width=90)
    with col3:
        st.write("##### :blue[Img]")
    with col4:
        st.write("##### :blue[Champion]")
    with col5:
        st.write("##### :blue[KDA]")
    with col6:
        st.write("##### :red[KDA]")
    with col7:
        st.write("##### :red[Img]")
    with col8:
        st.write("##### :red[Champion]")

    #Loops both teams at the same time
    for participant in range(5):
        #position1 = match_final["info"]["participants"][participant]["teamPosition"]
        champion1 = match_final["info"]["participants"][participant]["championName"]
        kill1 = match_final["info"]["participants"][participant]["kills"]
        assist1 = match_final["info"]["participants"][participant]["assists"]
        death1 = match_final["info"]["participants"][participant]["deaths"]
        #position1 = match_final["info"]["participants"][participant+5]["teamPosition"]
        champion2 = match_final["info"]["participants"][participant+5]["championName"]
        kill2 = match_final["info"]["participants"][participant+5]["kills"]
        assist2 = match_final["info"]["participants"][participant+5]["assists"]
        death2 = match_final["info"]["participants"][participant+5]["deaths"]

        with col3:
            st.image(find_image(champion1), width=25)
        with col4:
            if champion1 == user_champion:
                st.write(f"**:blue[{champion1}]** :arrow_left:")
            else:
                st.write(f":blue[{champion1}]")
        with col5:
            st.write(f":blue[{kill1}/{death1}/{assist1}]")
        with col6:
            st.write(f":red[{kill2}/{death2}/{assist2}]")
        with col7:
            st.image(find_image(champion2), width=25)
        with col8:
            if champion2 == user_champion:
                st.write(f"**:red[{champion2}]** :arrow_left:")
            else:
                st.write(f":red[{champion2}]")

    api_model_response = prediction(match_timeline,minute,look_events,columns_of_interest, fitted_model, transformer)

    if user_participant < 5:
        proba = round(api_model_response[0][1]*100,2)
    if user_participant > 4: #if player is from team 2, its probability of winning is equal to team 1 probability of losing
        proba = round(api_model_response[0][0]*100,2)

    columns3 = st.columns(3)

    gold_earned = [match_final["info"]["participants"][i]["goldEarned"] for i in range(10)]
    champ_list = [match_final["info"]["participants"][i]["championName"] for i in range(10)]
    colors = ['#008CBA'] * 5 + ['#E9422E'] * 5
    fig, ax = plt.subplots()
    #fig.set_facecolor('blue')
    ax.bar(champ_list, gold_earned, color=colors)
    ax.set_title('Total Gold Earned')
    ax.get_xaxis().set_visible(False)
    for i, c in enumerate(champ_list):
        offset_image(i, c, ax)
    columns3[0].pyplot(fig)

    if proba >= 50:
        st.write(f"##### Probability of your team winning at minute {minute} was {proba}% :chart_with_upwards_trend:")
    else:
        st.write(f"##### Probability of your team winning at minute {minute} was {proba}% :chart_with_downwards_trend:")

    result = match_result(match_final, user_participant)

    if result == "Victory":
        st.write(f"##### Your team result: {result} :trophy:")
    else:
        st.write(f"##### Your team result: {result} :thumbsdown:")

    st.write(f"##### {diagnosis(proba, result)}")

    st.write(f" ")
    st.write(f" ")
