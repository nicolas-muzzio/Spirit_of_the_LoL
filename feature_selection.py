import pandas as pd
from sklearn.preprocessing import RobustScaler
import numpy as np
import seaborn as sns

#df = read df from....

categorical_features = []


#Build functions

def duplicates(df):
    print(f"Duplicates droped: {df.duplicated().sum()}")

    df = df.drop_duplicates()

    return df

def missing_data_num(df_num): #TBD if needed

    return df_num

def missing_data_cat(df_cat):#TBD if needed

    return df_cat


def scale(df_num):

    #Standard or Robust if there are many otliers
    scaler = RobustScaler()

    df_num = scaler.fit_transform(df_num)

    return df_num


# Start script

#Remove duplicates
duplicates(df)

#Separate numerical features
df_num = df.drop(columns=categorical_features,inplace=True)

#Transform numerical features
df_num = missing_data_num(df_num)

df_num = scale(df_num)

#Separate categorical features
df_cat = df[categorical_features]

#Transform categorical features
df_cat = missing_data_cat(df_cat)

#Concat categorical and numerical processed features
df = pd.concat([df_num,df_cat],axis=1)


#correlation analysis to drop features that have high correlation
correlation_matrix = df.corr()
column_names = correlation_matrix.columns
#sns.heatmap(correlation_matrix, xticklabels=column_names, yticklabels=column_names,cmap= "bwr") remove comment to see chart

corr_df = correlation_matrix.stack().reset_index()
corr_df.columns = ['feature_1','feature_2', 'correlation']
no_self_correlation = (corr_df['feature_1'] != corr_df['feature_2'])
corr_df = corr_df[no_self_correlation]

corr_df['absolute_correlation'] = np.abs(corr_df['correlation'])
# corr_df.sort_values(by="absolute_correlation", ascending=False).head(5*2) remove comment to show df




from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.inspection import permutation_importance


X = df.drop(["win"])
y = df["win"]

# Instantiate model
log_reg = LogisticRegression(max_iter=5000)

# Scoring on multiple folds aka Cross Validation
scores = cross_val_score(log_reg, X, y, cv=10)
scores.mean()

# Fit model
log_model = LogisticRegression().fit(X, y)

# Performs Permutation
permutation_score = permutation_importance(log_model, X, y, n_repeats=10)

# Unstack results showing the decrease in performance after shuffling features
importance_df = pd.DataFrame(np.vstack((X.columns,
                                        permutation_score.importances_mean)).T)
importance_df.columns=['feature','score decrease']

# Show the important features
importance_df.sort_values(by="score decrease", ascending = False)
