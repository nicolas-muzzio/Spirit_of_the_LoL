#Import needed packages
import pandas as pd
import requests

#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/

#To load the key from .env and more
from dotenv import load_dotenv
import os


#Needed Functions for summoner_v4


time_seconds = 10
max_requests = 8
@sleep_and_retry
@limits(calls= max_requests, period= time_seconds) #period is in seconds
def fetch_summoner_v4(region, summoner_name, api_key):
    """
    Get SummonerDTO from SUMMONER_V4 API
    """
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}"

    response = requests.get(url)

    print(f"Summoner Name: {summoner_name}, 'API response: {response.status_code}")

    return response.json()


def iterate_summoner_v4(league_exp_v4_df, region, api_key):
    """
    Get all SummonerDTO from SUMMONER-V4 API, it takes a long time because of API limit
    """
    #Takes de series I need with the summoner name and converts it into an array to loop
    summoner_name_array = league_exp_v4_df["summonerName"].to_numpy()

    #generates and empy DF to store and return the data
    complete_df = pd.DataFrame()

    #Inicio un contador en 0
    count = 0

    #Loops over summoner name
    for i in range(0,1000):

        response_df = pd.DataFrame((fetch_summoner_v4(region, summoner_name_array[i], api_key)),index=[0])

        complete_df = pd.concat([complete_df,response_df], ignore_index = True)

        count = count + 1

        if count % 100 == 0:

            print(f"Count: {count}")#Prints when we send 100 requests)

    return complete_df


def iterate_summoner_v4_lite(league_exp_v4_df, tier, region, api_key, max_data):
    """
    Get max_data SummonerDTO from SUMMONER-V4 API
    """
    number_summoners= len(league_exp_v4_df[league_exp_v4_df["tier"] == tier])

    print(f"\nNumber of Summoners in tier {tier}: {number_summoners}\n")

    #Takes de series I need with the summoner name and converts it into an array to loop
    summoner_name_array = league_exp_v4_df[league_exp_v4_df["tier"] == tier]["summonerName"].to_numpy()

    #generates and empy DF to store and return the data
    complete_df = pd.DataFrame()

    #Inicio un contador en 0
    count = 0

    #Loops over summoner name
    if number_summoners < max_data:
        for i in range(0,number_summoners):

            print(f"Summoner {i+1} from {number_summoners}")

            response_df = pd.DataFrame((fetch_summoner_v4(region, summoner_name_array[i], api_key)),index=[0])

            complete_df = pd.concat([complete_df,response_df], ignore_index = True)

            count = count + 1

            if count % 50 == 0:

                print(f"\nCount: {count}\n")#Prints when we send 100 requests)

    else:
        for i in range(0,number_summoners,int(number_summoners/max_data)):

            print(f"Summoner {i+1} from {number_summoners}")

            response_df = pd.DataFrame((fetch_summoner_v4(region, summoner_name_array[i], api_key)),index=[0])

            complete_df = pd.concat([complete_df,response_df], ignore_index = True)

            count = count + 1

            if count % 50 == 0:

                print(f"\nCount: {count}\n")#Prints when we send 100 requests)

    return complete_df


def save_to_csv_summoner_v4_lite(df, tier):
    """
    Saves the dataframe obtained from summoner_v4_lite into a csv file
    """
    df.to_csv(f'Data/summoner_v4_lite_{tier}.csv')

    return print(f'\nSaved to Data/summoner_v4_lite_{tier}.csv\n')
