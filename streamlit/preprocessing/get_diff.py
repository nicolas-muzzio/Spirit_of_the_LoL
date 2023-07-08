import numpy as np
import pandas as pd

def calculate_event_differences(df):
    """Recibe un df y resta sucesivamente las filas 1 y 2, agrupando en un nuevo df el resultante de la resta.
    La función es utilizada para agrupar los datos de una partida por equipo para obtener la diferencia de las estadísticas.
    Mantiene el target de la primera fila"""    
    # Seleccionar todas las columnas excepto "matchId" y "target"
    columnas_no_matchId = df.columns[~df.columns.isin(["matchId", "target"])]

    # Seleccionar solo las columnas numéricas
    if "target" in df.columns:
        columnas_numericas = df.select_dtypes(include=[np.number]).drop(columns="target")
    else:
        columnas_numericas = df.select_dtypes(include=[np.number])

    # Crear un nuevo DataFrame vacío con la misma columna "matchId" y las columnas numéricas
    all_events_diff = pd.DataFrame(columns=["matchId"] + list(columnas_numericas.columns))

    # Obtener el número total de filas en columnas_numericas
    total_filas = columnas_numericas.shape[0]

    # Iterar a través de las filas de columnas_numericas
    for i in range(0, total_filas - 1, 2):
        # Obtener las dos filas a restar
        fila1 = columnas_numericas.iloc[i]
        fila2 = columnas_numericas.iloc[i+1]

        # Calcular la resta de las dos filas
        resta_filas = fila1 - fila2

        # Agregar la resta al nuevo DataFrame all_events_diff
        all_events_diff = all_events_diff.append(resta_filas, ignore_index=True)

    # Asignar el primer valor de las columnas booleanas en cada fila del nuevo DataFrame
    for columna in df.select_dtypes(include=[bool]):
        all_events_diff[columna] = all_events_diff[columna].iloc[::2].reset_index(drop=True)

    # Asignar el primer valor de la columna "matchId" en cada fila del nuevo DataFrame
    all_events_diff["matchId"] = df["matchId"].iloc[::2].reset_index(drop=True)

    # Asignar el primer valor de la columna "target" en cada fila del nuevo DataFrame
    if "target" in df.columns:
        all_events_diff["target"] = df["target"].iloc[::2].reset_index(drop=True)

    return all_events_diff
