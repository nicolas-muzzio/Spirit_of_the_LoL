#Import needed packages
import pandas as pd
import requests
import json
import numpy as np


#To limit the amount of requests per minute
from ratelimit import limits, sleep_and_retry #from https://pypi.org/project/ratelimit/

#100 requests every 120 sec
time_seconds = 10
max_function_calls = 4
@sleep_and_retry
@limits(calls= max_function_calls, period= time_seconds) #period is in seconds
def fetch_by_matchID(matchID, api_key):
    """
    #Get Match and Match_Timeline from Match_V5
    """
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchID}?api_key={api_key}'

    response = requests.get(url)

    if response.status_code != 200:
                    raise Exception('API response: {}'.format(response.status_code))

    url_timeline = f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchID}/timeline?api_key={api_key}'

    response_timeline = requests.get(url_timeline)

    if response_timeline.status_code != 200:
                    raise Exception('API response: {}'.format(response.status_code))

    return (response.json(), response_timeline.json())


def save_to_csv_matchID(response, tier, matchID):
    """
    Saves the dataframe obtained from MATCH_V5 by MatchID into a .json file
    """

    match_data = f'Data/{tier}/Final/{matchID}.json'

    with open(match_data, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

    return None


def save_to_csv_matchID_timeline(response_timeline, tier, matchID):
    """
    Saves the dataframe obtained from MATCH_V5 timeline by MatchID into a .json file
    """

    match_data_timeline = f'Data/{tier}/Timeline/{matchID}_timeline.json'

    with open(match_data_timeline, 'w', encoding='utf-8') as f:
        json.dump(response_timeline, f, ensure_ascii=False, indent=4)

    return None


def obtain_matches(tier, api_key, max_games = 5000, start = 0):
    """
    Iterates matchIDs to obtain match information
    """
    match_ids = pd.read_csv(f'Data/match_V5_{tier}.csv')["0"].drop_duplicates().dropna().to_numpy()

    count = 0

    for i in range(start,len(match_ids),int(len(match_ids)/max_games)):
        (response, response_timeline) = fetch_by_matchID(match_ids[i], api_key)
        save_to_csv_matchID(response, tier, match_ids[i])
        save_to_csv_matchID_timeline(response_timeline, tier, match_ids[i])
        print(f"Saved {count} matches, last row is {i}")
        count = count +1

    return print(f"Finished looping {len(match_ids)} in {tier}")
