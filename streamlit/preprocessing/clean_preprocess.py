import pandas as pd
from sklearn.preprocessing import RobustScaler, MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.exceptions import NotFittedError


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
def scale_train(df):
    scaler = RobustScaler()
    transformer = scaler.fit(df)
    scaled_array = transformer.transform(df)
    scaled_df = pd.DataFrame(scaled_array, columns=df.columns)
    return scaled_df,transformer

def scale_pred(df,transformer):
    scaled_array = transformer.transform(df)
    scaled_df = pd.DataFrame(scaled_array, columns=df.columns)
    return scaled_df

def remove_nan_rows(df):
    df_cleaned = df.dropna()
    return df_cleaned

#Función que debemos llamar para aplicar el preproceso al df deseado ----> Cambiar esto por Pipeline
def preprocess_train(df):
    df = df.sort_index(axis=1)
    #df = specify_interest_featuresl
    #df = remove_duplicates(df)
    df,transformer = scale_train(df)
    df = remove_nan_rows(df)
    return df, transformer

def preprocess_pred(df,transformer):
    df = df.sort_index(axis=1)
    #df = specify_interest_featuresl
    #df = remove_duplicates(df)
    df = scale_pred(df,transformer)
    df = remove_nan_rows(df)
    return df


class CustomStandardizer(TransformerMixin, BaseEstimator):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        '''
        Stores what needs to be stored as instance attributes.
        ReturnS "self" to allow chaining fit and transform.
        '''
        # $CHALLENGIFY_BEGIN
        self.means = X.mean()
        self.stds = X.std(ddof=0)

        # Return self to allow chaining & fit_transform
        return self
        # $CHALLENGIFY_END

    def transform(self, X, y=None):
        # $CHALLENGIFY_BEGIN
        if not (hasattr(self, "means") and hasattr(self, "stds")):
            raise NotFittedError("This CustomStandardScaler instance is not fitted yet. Call 'fit' with the appropriate arguments before using this estimator.")

        # Standardization
        standardized_features = (X - self.means) / self.stds

        return standardized_features
        # $CHALLENGIFY_END

    # $DELETE_BEGIN
    def inverse_transform(self, X, y=None):
        if not (hasattr(self, "means") and hasattr(self, "stds")):
            raise NotFittedError("This CustomStandardScaler instance is not fitted yet. Call 'fit' with the appropriate arguments before using this estimator.")

        return X * self.stds + self.means
    # $DELETE_END

#Función que llamaremos para aplicar el preproceso
def create_preprocessor():
    # Preprocessing pipeline with lambda function to remove duplicates
    preprocessor = Pipeline([
        ('remove_duplicates', lambda df: df.drop_duplicates()),
        ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
        ('scaling', RobustScaler())
    ])

    return preprocessor
