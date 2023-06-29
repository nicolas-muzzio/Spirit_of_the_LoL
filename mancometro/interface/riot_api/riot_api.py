#######################################################################
#Import needed packages
#######################################################################
import pandas as pd

#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/

#To load the key from .env and more
from dotenv import load_dotenv
import os

#Load functions from other .py files
from league_exp_v4 import iterate_league_exp_v4, save_to_csv_league_exp_v4
from summoner_v4 import iterate_summoner_v4_lite, save_to_csv_summoner_v4_lite
from match_v5_puuid import loop_match_V5_all_tiers_lite
from match_v5_id import obtain_matches

#######################################################################
#Define variables
#######################################################################


#Spirit of the LoL api key
# Cargar el archivo .env
load_dotenv()

# Acceder al valor de una variable
api_key = os.getenv("API_KEY")

#Code for LAS region
region = "LA2"

#Code for queue Solo
queue = "RANKED_SOLO_5x5"

queue_list = ["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]

#Tiers
tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]

#Remember that from Master rank and above, only division I is valid
division_list = ["IV", "III", "II", "I"]


#######################################################################
#Creates complete dataset with all summoner ids from certain queue and region
#######################################################################
league_exp_v4_df = iterate_league_exp_v4()
save_to_csv_league_exp_v4(league_exp_v4_df, queue)


#######################################################################
#Obtains the PUUID with the summoner ID
#######################################################################
league_exp_v4_df = pd.read_csv("Data/league_exp_v4_LA2_RANKED_SOLO_5x5.csv")

max_data = 1000
for tier in tier_list:
    df = iterate_summoner_v4_lite(league_exp_v4_df, tier, max_data)
    save_to_csv_summoner_v4_lite(df, tier)

#######################################################################
#Obtains MatchID with the summoner ID
#######################################################################
loop_match_V5_all_tiers_lite(tier_list)


#######################################################################
#Obtains Match_Final and Match_Timeline with MatchID
#######################################################################
for tier in tier_list:
    obtain_matches(tier,api_key)
