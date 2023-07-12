import pandas as pd
import numpy as np
import os


#PARTICIPANT FRAMES

def part_frames(json_file,minute):

    data = pd.DataFrame(json_file["info"]["frames"][minute]["participantFrames"])

    data = data.transpose().drop(columns=["currentGold", "goldPerSecond", "participantId", "position", "timeEnemySpentControlled", "level"])
    data.reset_index(drop=True, inplace=True)

    damage_stats = pd.json_normalize(data["damageStats"])
    champion_stats = pd.json_normalize(data["championStats"])

    pf_all = pd.concat([data, damage_stats, champion_stats], axis=1).drop(columns=["championStats","damageStats"])
    pf_all = pf_all.astype(int)

    conditions = [
            (pf_all.index >= 0) & (pf_all.index <= 4),
            (pf_all.index >= 5) & (pf_all.index <= 9)
        ]
    values = [100, 200]

    pf_all['team'] = np.select(conditions, values, default=0)

    pf_all = pf_all.groupby("team").sum().reset_index()

    return pf_all


#EVENTS & TARGET

def find_indices(data,look_events):
    monster_indices = []
    for index, item in enumerate(data):
        if item.get('type') in look_events:
            monster_indices.append(index)
    return monster_indices

def get_events(json_file,minute,look_events):
    elements_filtered = []
    for i in range(minute + 1):
        try:
            events = json_file["info"]["frames"][int(i)]["events"]
        except IndexError:
            break
        monster_indices = find_indices(events,look_events)
        if monster_indices:
            new_elements = [events[e] for e in monster_indices]
            elements_filtered.extend(new_elements)

    events_filtered = pd.DataFrame(elements_filtered)
    return events_filtered


def transform_events(json_file,minute,look_events):
    required_columns = ["killerId", "type", "killType", "monsterSubType", "monsterType", "towerType","buildingType"]
    events = get_events(json_file,minute,look_events)
    missing_columns = [col for col in required_columns if col not in events.columns]
    for column in missing_columns:
        events[column] = np.nan
    events = events[required_columns]
    events = events[events["killerId"] != 0]
    events.loc[events["monsterType"] == "DRAGON", "monsterType"] = events.loc[events["monsterType"] == "DRAGON", "monsterSubType"]
    events = events.drop(columns=["monsterSubType"])
    events["buildingType"] = events["buildingType"].apply(lambda x: x if x == "INHIBITOR_BUILDING" else "")
    events["kills"] = (events["type"] == "CHAMPION_KILL").astype(int)
    one_hot_encoded = pd.get_dummies(events[['killType', "monsterType", "towerType","buildingType"]])
    events_encoded = pd.concat([events[['killerId', "kills"]], one_hot_encoded], axis=1)
    if 'killType' in events_encoded.columns:
        events_encoded.drop(columns=['killType'], inplace=True)
    if 'monsterType' in events_encoded.columns:
        events_encoded.drop(columns=['monsterType'], inplace=True)
    if 'towerType' in events_encoded.columns:
        events_encoded.drop(columns=['towerType'], inplace=True)
    if "buildingType" in events_encoded.columns:
        events_encoded.drop(columns=["buildingType"], inplace=True)
    events_encoded = events_encoded.groupby("killerId").sum().reset_index()
    events_encoded["killerId"] = events_encoded["killerId"] - 1
    events_encoded = events_encoded.groupby("killerId").sum().reset_index()
    conditions = [
        (events_encoded['killerId'] >= 0) & (events_encoded['killerId'] <= 4),
        (events_encoded['killerId'] >= 5) & (events_encoded['killerId'] <= 9)
    ]
    values = [100, 200]
    events_encoded['team'] = np.select(conditions, values, default=0)
    events_encoded = events_encoded.groupby("team").sum().reset_index().drop(columns=["killerId"])
    return events_encoded


def merge_dfs(json_file,minute,look_events):
    events = transform_events(json_file,minute,look_events)
    frames = part_frames(json_file,minute)

    dfs = frames.merge(events,how="left",on="team")

    dfs["matchId"] = json_file["metadata"]["matchId"]

    last_event = json_file["info"]["frames"][-1]["events"][-1]
    dfs["target"] = dfs["team"].apply(lambda x: 1 if x == last_event.get("winningTeam") else 0)

    dfs.drop(columns=["team"],inplace=True)

    return dfs

def process_folder(folder_path,minute,look_events):
    all_events = None
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            json_file = pd.read_json(file_path)
            try:
                if all_events is None:
                    all_events = merge_dfs(json_file,minute,look_events)
                else:
                    all_events = pd.concat([all_events, merge_dfs(json_file,minute,look_events)], ignore_index=True)
            except IndexError:
                continue
    columns_to_convert = all_events.columns[~all_events.columns.isin(['matchId', 'target'])]
    all_events[columns_to_convert] = all_events[columns_to_convert].fillna(0).astype(int)
    return all_events

def process_one_json(json_file,minute,look_events):
    json_file = pd.read_json(json_file)

    all_events = merge_dfs(json_file,minute,look_events)

    columns_to_convert = all_events.columns[~all_events.columns.isin(['matchId', 'target'])]
    all_events[columns_to_convert] = all_events[columns_to_convert].fillna(0).astype(int)
    return all_events


def check_and_create_columns(df, column_names):
    # Obtiene las columnas existentes en el DataFrame y las compara con column_names
    columns_to_drop = [col for col in df.columns if col not in column_names]
    # Elimina las columnas no presentes en column_names
    df = df.drop(columns_to_drop, axis=1)
    # Verifica y crea las columnas faltantes con valor 0
    for column in column_names:
        if column not in df.columns:
            df[column] = 0
    return df


def reduce_columns_pred(folder_path,minute,look_events,column_names):

    all_events_diff = process_folder(folder_path,minute,look_events)

    # Get columns that start with 'monsterType'
    monster_type_cols = all_events_diff.filter(like='monsterType', axis=1).columns.tolist()

    # Get columns that start with 'towerType'
    tower_type_cols = all_events_diff.filter(like='towerType', axis=1).columns.tolist()

    # Get columns that start with 'killType'
    kill_type_cols = all_events_diff.filter(like='killType', axis=1).columns.tolist()

    # Combine the columns into a single list
    all_cols = monster_type_cols + tower_type_cols + kill_type_cols + ["target","minionsKilled","totalGold"]

    all_df = all_events_diff[all_cols]

    check_and_create_columns(all_df, column_names)

    return all_df


def reduce_columns_train(all_events_diff):

    # Get columns that start with 'monsterType'
    monster_type_cols = all_events_diff.filter(like='monsterType', axis=1).columns.tolist()

    # Get columns that start with 'towerType'
    tower_type_cols = all_events_diff.filter(like='towerType', axis=1).columns.tolist()

    # Get columns that start with 'killType'
    kill_type_cols = all_events_diff.filter(like='killType', axis=1).columns.tolist()

    # Combine the columns into a single list
    all_cols = monster_type_cols + tower_type_cols + kill_type_cols + ["target","minionsKilled","totalGold"]

    all_df = all_events_diff[all_cols]

    return all_df

def iterate_files(folder_path_train):
    data_dict = {}

    # Iterate over files in the folder
    for filename in os.listdir(folder_path_train):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path_train, filename)

            # Extract the key from the filename
            key = filename.replace("Match_Diff_", "").replace(".csv", "")

            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Delete the first column from the DataFrame
            df = df.drop(df.columns[0], axis=1)

            # Add the DataFrame to the dictionary with the key
            data_dict[key] = df

    return data_dict
