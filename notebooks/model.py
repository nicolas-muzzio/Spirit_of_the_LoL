from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score, f1_score

def custom_predict(model, X, custom_threshold):
    probs = model.predict_proba(X) # Get likelihood of each sample being classified as 0 or 1
    expensive_probs = probs[:, 1] # Only keep expensive likelihoods (1)
    return (expensive_probs > custom_threshold).astype(int) # Boolean outcome converted to 0 or 1

def train_model(df):
    # Clean and fill missing values in the dataframe
    #df_cleaned = df.dropna()
    df_cleaned_filled = df.fillna(0)

    # Dividir el dataframe en conjuntos de entrenamiento y prueba
    X = df_cleaned_filled.drop(columns=["target", "matchId"])
    y = df_cleaned_filled['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=6)

    # Baseline model
    baseline_model = DummyRegressor(strategy="mean")
    baseline_model.fit(X_train, y_train)
    baseline_score = baseline_model.score(X_test, y_test)

    # Linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    model_score = model.score(X_test, y_test)

    # Logistic regression model
    logistic_model = LogisticRegression()
    logistic_model.fit(X, df['target'])
    updated_preds = custom_predict(logistic_model, X, custom_threshold=0.305539)

    # Evaluation metrics
    recall = recall_score(df['target'], updated_preds)
    precision = precision_score(df['target'], updated_preds)
    f1 = f1_score(df['target'], updated_preds)

    return {
        'baseline_score': baseline_score,
        'model_score': model_score,
        'recall': recall,
        'precision': precision,
        'f1': f1
    }
