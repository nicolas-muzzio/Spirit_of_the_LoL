#PARTICIPANT FRAMES

def part_frames(json_file):
    
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

def find_indices(data):
    monster_indices = []
    for index, item in enumerate(data):
        if item.get('type') in look_events:
            monster_indices.append(index)
    return monster_indices

def get_events(json_file):
    elements_filtered = []
    for i in range(minute + 1):
        try:
            events = json_file["info"]["frames"][i]["events"]
        except IndexError:
            break
        monster_indices = find_indices(events)
        if monster_indices:
            new_elements = [events[e] for e in monster_indices]
            elements_filtered.extend(new_elements)

    events_filtered = pd.DataFrame(elements_filtered)
    return events_filtered


def transform_events(json_file):
    required_columns = ["killerId", "type", "killType", "monsterSubType", "monsterType", "towerType"]

    events = get_events(json_file)

    missing_columns = [col for col in required_columns if col not in events.columns]

    for column in missing_columns:
        events[column] = np.nan

    events = events[required_columns]
    events = events[events["killerId"] != 0]

    events.loc[events["monsterType"] == "DRAGON", "monsterType"] = events.loc[events["monsterType"] == "DRAGON", "monsterSubType"]

    events = events.drop(columns=["monsterSubType"])

    events["kills"] = (events["type"] == "CHAMPION_KILL").astype(int)

    one_hot_encoded = pd.get_dummies(events[['killType', "monsterType", "towerType"]])

    events_encoded = pd.concat([events[['killerId', "kills"]], one_hot_encoded], axis=1)
    
    if 'killType' in events_encoded.columns:
        events_encoded.drop(columns=['killType'], inplace=True)
    if 'monsterType' in events_encoded.columns:
        events_encoded.drop(columns=['monsterType'], inplace=True)
    if 'towerType' in events_encoded.columns:
        events_encoded.drop(columns=['towerType'], inplace=True)
    
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


def merge_dfs(json_file):
    events = transform_events(json_file)
    frames = part_frames(json_file)
    
    dfs = frames.merge(events,how="left",on="team")
    
    dfs["matchId"] = json_file["metadata"]["matchId"]
    
    last_event = json_file["info"]["frames"][-1]["events"][-1]
    dfs["target"] = dfs["team"].apply(lambda x: 1 if x == last_event.get("winningTeam") else 0)
    
    dfs.drop(columns=["team"],inplace=True)
    
    return dfs

