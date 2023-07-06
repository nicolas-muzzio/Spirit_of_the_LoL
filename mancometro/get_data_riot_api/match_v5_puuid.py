#Import needed packages
import pandas as pd
import requests


#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/


#100 requests every 120 sec
time_seconds = 10
max_requests = 8
"""Parameters
puuid : unique globally IDs
api_key
type: Filter the list of match ids by the type of match. This filter
is mutually inclusive of the queue filter meaning
any match ids returned must match both the queue and type filters.
count: Number of match ids to return.
"""
@sleep_and_retry
@limits(calls= max_requests, period= time_seconds) #period is in seconds
def fetch_match_V5(puuid, api_key, count = 100, match_type = "ranked"):
    """
    Get Match IDs from Match_V5
    """
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?&count={count}&type={match_type}&api_key={api_key}'

    response = requests.get(url)

    if response.status_code != 200:
                    raise Exception('API response: {}'.format(response.status_code))

    return response.json()


def iterate_match_V5(summoner_v4_df, api_key):
    """
    Get all MatchID from Match_V5 API
    """
    #Takes de series I need with the summoner name and converts it into an array to loop
    puuid_name_array = summoner_v4_df["puuid"].dropna().to_numpy()

    #generates and empy DF to store and return the data
    complete_df = pd.DataFrame()

    #Inicio un contador en 0
    count = 0

    #Loops over summoner name
    for i in range(0,len(puuid_name_array)):

        response_df = pd.DataFrame((fetch_match_V5(puuid_name_array[i], api_key)))

        complete_df = pd.concat([complete_df,response_df], ignore_index = True)

        print(f"Count: {count}")

        count = count + 1

        if count % 100 == 0:

            print(f"Checkpoint!")#Prints when we send 100 requests)

    return complete_df


def save_to_csv_match_V5(df, tier):
    """
    Saves the dataframe obtained from MATCH_V5 into a csv file
    """
    df.to_csv(f'Data/match_V5_{tier}.csv')

    return print(f'\nSaved to Data/summoner_v4_{tier}.csv\n')


def loop_match_V5_all_tiers(tier_lister):
    """
    Loops MATCH_V5 for all tiers
    """

    for tier in tier_lister:
        summoner_v4_df = pd.read_csv(f"Data/summoner_v4_{tier}.csv")

        df = iterate_match_V5(summoner_v4_df)

        save_to_csv_match_V5(df, tier)


def save_to_csv_match_V5_lite(df, tier):
    """
    Saves the dataframe obtained from MATCH_V5 into a csv file
    """
    df.to_csv(f'Data/match_V5_lite_{tier}.csv')

    return print(f'\nSaved to Data/summoner_v4_lite_{tier}.csv\n')


def loop_match_V5_all_tiers_lite(tier_list):
    """
    Loops MATCH_V5 for all tiers
    """

    for tier in tier_list:
        summoner_v4_lite_df = pd.read_csv(f"Data/summoner_v4_lite_{tier}.csv")

        df = iterate_match_V5(summoner_v4_lite_df)

        save_to_csv_match_V5(df, tier)
