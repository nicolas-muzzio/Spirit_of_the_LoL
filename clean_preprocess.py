import pandas as pd
from sklearn.preprocessing import RobustScaler



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

#Remover duplicados
def remove_duplicates(df):
    print(f"Duplicates dropped: {df.duplicated().sum()}")
    df = df.drop_duplicates()
    return df

#Escalar
def scale(df):
    scaler = RobustScaler()
    scaled_array = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_array, columns=df.columns)
    return scaled_df

#Función que debemos llamar para aplicar el preproceso al df deseado
def preprocess(df):
    #df = specify_interest_featuresl
    df = remove_duplicates(df)
    df = scale(df)
    return df
