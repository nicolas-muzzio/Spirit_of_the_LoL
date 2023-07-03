import pandas as pd
from sklearn.preprocessing import RobustScaler, MinMaxScaler, StandardScales
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


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

def remove_nan_rows(df):
    df_cleaned = df.dropna()
    return df_cleaned

#Función que debemos llamar para aplicar el preproceso al df deseado ----> Cambiar esto por Pipeline
"""def preprocess(df):
    #df = specify_interest_featuresl
    df = remove_duplicates(df)
    df = scale(df)
    df = remove_nan_rows(df)
    return df"""

#Función que llamaremos para aplicar el preproceso 
def create_preprocessor():
    # Preprocessing pipeline with lambda function to remove duplicates
    preprocessor = Pipeline([
        ('remove_duplicates', lambda df: df.drop_duplicates()),
        ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
        ('scaling', RobustScaler())
    ])

    return preprocessor
