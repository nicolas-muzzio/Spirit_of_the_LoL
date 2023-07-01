import pandas as pd
from sklearn.preprocessing import RobustScaler
import numpy as np


#esta no funciona
def specify_interest_features(df):
    # Get columns that start with 'monsterType'
    monster_type_cols = df.filter(like='monsterType', axis=1).columns.tolist()

    # Get columns that start with 'towerType'
    tower_type_cols = df.filter(like='towerType', axis=1).columns.tolist()

    # Get columns that start with 'killType'
    kill_type_cols = df.filter(like='killType', axis=1).columns.tolist()

    # Combine the columns into a single list
    all_cols = monster_type_cols + tower_type_cols + kill_type_cols + ["target","minionsKilled","totalGold"]

    all_df = df[all_cols]
    
    return all_df

def remove_duplicates(df):
    print(f"Duplicates dropped: {df.duplicated().sum()}")
    df = df.drop_duplicates()
    return df

def normalize(df):
    normalized_array = df.div(df.sum(axis=1), axis=0)
    return normalized_array

def replace_nan_with_zero(df):
    df_cleaned = df.replace(np.nan, 0)
    return df_cleaned

def preprocess(df):
    df = remove_duplicates(df)
    df_cleaned = replace_nan_with_zero(df)
    #normalized_array = normalize(df_cleaned.drop("target", axis=1))
    return df_cleaned, df_cleaned["target"]