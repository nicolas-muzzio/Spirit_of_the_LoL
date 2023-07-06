#Import needed packages
import pandas as pd
import requests

#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/


#Needed Functions for league_exp_v4

#100 requests every 120 sec
time_seconds = 10
max_requests = 8
@sleep_and_retry
@limits(calls = time_seconds, period = max_requests) #period is in seconds
def fetch_league_exp_v4(queue, tier, division, region, page, api_key):
    """
    Get LeagueEntryDTO from LEAGUE-EXP-V4 API
    """
    url = f'https://{region}.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_key}'

    response = requests.get(url)

    ###ASK HOW TO DO TO SKIP IT IF THERE IS AN ERROR###
    if response.status_code != 200:
                    raise Exception('API response: {}'.format(response.status_code))

    return response.json()


def iterate_league_exp_v4(tier_list, queue, region, api_key):
    """
    Get all LeagueEntryDTO from LEAGUE-EXP-V4 API for a certain tier.
    """
    #generates and empy DF to store and return the data
    complete_df = pd.DataFrame()

    #Loops over the Tier list
    for tier in tier_list:

        #Verifies tier to define possible divisions
        if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
            division_list = ["I"]
        else:
            division_list = ["IV", "III", "II", "I"]

        #Loops over divisions
        for division in division_list:

            #Creates page counter
            page = 1

            #Creates not empty DF
            response_df = pd.DataFrame({'not_empty': [1]})

            #Loops over pages until it finds and empty response
            while not response_df.empty:

                    response_df = pd.DataFrame(fetch_league_exp_v4(queue, tier, division, region, page, api_key))

                    complete_df = pd.concat([complete_df,response_df], ignore_index = True)

                    print(f"Tier: {tier}, Division: {division}, Page: {page}")

                    page = page + 1

                    if response_df.empty:
                        print("Empty")

    return complete_df


def save_to_csv_league_exp_v4(df, region, queue):
    """
    Saves the dataframe obtained from league_exp_v4 into a csv file
    Input: region, queue and the df
    """

    df.to_csv(f'Data/league_exp_v4_{region}_{queue}.csv')

    return print(f'Saved to Data/league_exp_v4_{region}_{queue}.csv')
