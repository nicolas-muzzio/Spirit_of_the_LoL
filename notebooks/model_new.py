#Compilación del modelo 06/07/20213

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
import pickle


def train_and_export_models(data_preprop):
    """Función recibe como parametro un diccionario con la data preprocesada
    y: 1) aplica el modelo, separa en train y test..."""
    fitted_models = {}

    for key, value in data_preprop.items():
        print(key)

        X_preprop = data_preprop[key][0]
        y = data_preprop[key][1]

        X_train, X_test, y_train, y_test = train_test_split(X_preprop, y, test_size=0.2, random_state=42)

        param_grid = {
            'C': [0.1, 1, 10],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }

        model = LogisticRegression(max_iter=5000)

        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            scoring='accuracy',
            cv=5
        )

        grid_search.fit(X_train, y_train)

        print("Best Hyperparameters: ", grid_search.best_params_)
        print("Best Score: ", grid_search.best_score_)

        best_model = LogisticRegression(
            C=grid_search.best_params_['C'],
            penalty=grid_search.best_params_['penalty'],
            solver=grid_search.best_params_['solver'],
            max_iter=5000
        )
        best_model.fit(X_train, y_train)

        # Save the fitted model in the dictionary using the key as the key
        fitted_models[key] = best_model

        # Export the model as a pickle file
        filename = "Models_trained/" + key + '_model.pkl'
        with open(filename, 'wb') as file:
            pickle.dump(best_model, file)
        print("Model exported as", filename)

    return fitted_models
