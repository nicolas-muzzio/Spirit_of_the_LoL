import streamlit as st

#To work with requests and APIs
import requests

#To operate with date and times
import datetime

#To open pickles with model and transformers info
import pickle

#For making plots
import matplotlib.pyplot as plt


#To load the key from .env and get access to stored variables
#from dotenv import load_dotenv
import os
import sys

from streamlit_functions.functions import fetch_match, unique_tier, find_image, offset_image, prediction, match_result_team, diagnosis,event_types_dict, queues_dict, region_dict, columns_of_interest,macro_region,match_type_list, tier_list

sys.path.insert(0,os.path.abspath(".."))

#Get value stored in variable
api_key = st.secrets["API_KEY"]

st.set_page_config(
            page_title="Oldies", # Adjust things later
            page_icon=":hourglass_flowing_sand:", #Change icon later
            layout="wide", # or centered, wide has more space
            initial_sidebar_state="auto") # collapsed

#Page Title
st.title('Oldies :hourglass_flowing_sand:')

#Main Form to get data from user
with st.form(key='params_for_api'):

    columns = st.columns(4)

    match_id = columns[0].text_input("Game ID", help = "You can find the Game ID in League of Legends -> Profile -> Match History", value= "1316687991")

    chosen_region = columns[1].selectbox("Region", region_dict.keys(), help = "Region for this Game ID", index= 0) #Default Index correspond to KR

    league = columns[2].selectbox("Choose the Tier for this Match", tier_list, help = "The Tier defines de Trained Model used to Predict the result", index= 1) #Default Index correspond to Ranked

    team = columns[3].selectbox("Choose team to analyse", ["Blue","Red"], help = "The team to analyze", index= 0)

    st.form_submit_button('Make prediction')

#Converts user input to region ID
region = region_dict[chosen_region]


st.write(f" ")
st.write(f" ")

#Obtain Match Final Data
try:
    path_match_timeline =f"https://{macro_region[str(region)]}.api.riotgames.com/lol/match/v5/matches/{region_dict[chosen_region]}_{match_id}?api_key={api_key}"
    match_final = requests.get(path_match_timeline).json()
    #To find match type using queues_dict
    match_type_key = match_final["info"]["queueId"]
except:
    st.write("Could not find match, please verify Match ID and Region")
    st.stop()



if match_type_key in [450, 720]:
    st.write("Model not optimized for ARAM games")
    st.stop()

#Obtain Match Timeline Data
try:
    path_match_timeline =f"https://{macro_region[str(region)]}.api.riotgames.com/lol/match/v5/matches/{region_dict[chosen_region]}_{match_id}/timeline?api_key={api_key}"
    match_timeline = requests.get(path_match_timeline).json()
    match_length = len(match_timeline["info"]['frames'])
except:
    st.write("Could not find match, please verify Match ID and Region")
    st.stop()


if match_length < 10:
    st.write("Match to short, :notes:No retreat, baby, no surrender	:musical_note:")
    st.stop()

#Obtains unx timestamp and converts it into date time
formatted_date = datetime.datetime.fromtimestamp(match_final["info"]["gameStartTimestamp"]/1000).strftime('%Y-%m-%d %H:%M')

#Generates columns for displaying match data
col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1.2,1.2,0.18,1,0.5,0.5,0.18,1,1.4])


#Info for loading model
look_events=["CHAMPION_SPECIAL_KILL","CHAMPION_KILL","ELITE_MONSTER_KILL","BUILDING_KILL"]
pickle_file_path = f"model/pickles_models/{league}_model.pkl"
with open(pickle_file_path, "rb") as file:
    # Load the data from the pickle file
    fitted_model = pickle.load(file)


#For setting the columns to display results
with col1:
    st.markdown("##### Date")
    st.write(f"{formatted_date}")
    st.write("##### Studied Side:")
    if team == "Blue":
        st.write("##### :blue[Blue Team]")
    else:
        st.write("##### :red[Red Team]")
with col2:
    st.write("##### Match Type")
    st.write(f"{queues_dict[match_type_key]}")

with col3:
    st.write("##### :blue[Img]")
with col4:
    st.write("##### :blue[Champion]")
with col5:
    st.write("##### :blue[KDA]")
with col6:
    st.write("##### :red[KDA]")
with col7:
    st.write("##### :red[Img]")
with col8:
    st.write("##### :red[Champion]")

#Evaluates match lenght and create a list of minutes
minute = 10 #This is arbitrary were we are evaluating if it was a comeback or not
#match_length = len(match_timeline["info"]['frames'])
minute_list = list(range(match_length))

#Loops both teams at the same time
for participant in range(5):
    #position1 = match_final["info"]["participants"][participant]["teamPosition"]
    champion1 = match_final["info"]["participants"][participant]["championName"]
    kill1 = match_final["info"]["participants"][participant]["kills"]
    assist1 = match_final["info"]["participants"][participant]["assists"]
    death1 = match_final["info"]["participants"][participant]["deaths"]
    #position1 = match_final["info"]["participants"][participant+5]["teamPosition"]
    champion2 = match_final["info"]["participants"][participant+5]["championName"]
    kill2 = match_final["info"]["participants"][participant+5]["kills"]
    assist2 = match_final["info"]["participants"][participant+5]["assists"]
    death2 = match_final["info"]["participants"][participant+5]["deaths"]


    with col3:
        st.image(find_image(champion1), width=25)
    with col4:
        st.write(f":blue[{champion1}]")
    with col5:
        st.write(f":blue[{kill1}/{death1}/{assist1}]")
    with col6:
        st.write(f":red[{kill2}/{death2}/{assist2}]")
    with col7:
        st.image(find_image(champion2), width=25)
    with col8:
        st.write(f":red[{champion2}]")


#Defines user team and color for plots
if team == "Blue":
    proba_position = 1
    color = "royalblue"
    color1 = "blue"
if team == "Red": #if player is from team 2, its probability of winning is equal to team 1 probability of losing
    proba_position = 0
    color = "red"
    color1 = "red"

api_model_response = prediction(match_timeline,minute_list,look_events,columns_of_interest, fitted_model, proba_position, league)

proba = round(api_model_response[minute],2)

columns3 = st.columns([0.35, 0.05,0.60])

gold_earned = [match_final["info"]["participants"][i]["goldEarned"] for i in range(10)]
champ_list = [match_final["info"]["participants"][i]["championName"] for i in range(10)]
colors = ['#008CBA'] * 5 + ['#E9422E'] * 5

columns3[0].write("")

columns3[0].write(f" ")
columns3[0].write(f" ")


fig2, ax = plt.subplots() #figsize=(6, 2)
#fig.set_facecolor('blue')
#fig2.set_size_inches(5, 5)
ax.figure.set_size_inches(3.5, 3.5)
ax.bar(champ_list, gold_earned, color=colors)
ax.set_title('Total Gold Earned')
ax.get_xaxis().set_visible(False)
for i, c in enumerate(champ_list):
    offset_image(i, c, ax)
col9.pyplot(fig2)

#fig1, ax1 = plt.subplots()
#ax1.plot(minute_list, api_model_response, color=color, marker='o')
#ax1.set_title('Winning Propability (%) vs Match Time (min)')
#ax1.set_ylim([0, 100])
#columns3[1].pyplot(fig1)

# ---------------------------------- Prueba combinada -----------------------------

# Crear el gráfico de líneas con Plotly
import plotly.graph_objects as go

#--------------------------------------------------------PROBAR MARCADORES DE TOOLTIP CON COLORES --------------------------------------------------------------------
fig = go.Figure()

fig.update_layout(
        autosize=False,
        width=825,
        height=425)

dragon_objectives = ["AIR_DRAGON", "CHEMTECH_DRAGON", "EARTH_DRAGON", "FIRE_DRAGON", "HEXTECH_DRAGON", "WATER_DRAGON", "ELDER_DRAGON"]

# Agregar la línea
fig.add_trace(go.Scatter(x=minute_list, y=api_model_response, mode='lines',marker=dict(color=color), name='Winning Probability (%)'))


fig.add_trace(go.Scatter(x=minute_list, y=api_model_response, mode='markers', marker=dict(color=color, symbol='circle')))

# Definir los intervalos de interés
intervalos = list(range(match_length))  # Lista continua desde 10 hasta 30 (incluyendo ambos extremos)

# Crear listas para almacenar los valores de x e y de los tooltips
x_values_j = []
y_values_j = []

x_values_b = []
y_values_b = []

tooltips_j = []  # Lista para almacenar los tooltips agrupados por intervalo
tooltips_b = []  # Lista para almacenar los tooltips agrupados por intervalo

colors_j = []  # Lista para almacenar los colores de los puntos
colors_b = []  # Lista para almacenar los colores de los puntos



color_dict = {"Blue Team" : "rgb(0, 0, 255)" , "Red Team" : "rgb(255, 0, 0)"}

team_dict = {100 : "Red Team" ,200: "Blue Team"} #for buildings the team_id is the color of the building destroyed

multicolor = "rgb(125, 0, 125)"

jungle_y_value = 114
buildings_y_value = 106




for intervalo in intervalos:

    # Acceder a la lista de eventos del intervalo actual
    events_list = match_timeline["info"]["frames"][intervalo]["events"]

    # Filtrar los eventos con 'type' igual a 'ELITE_MONSTER_KILL'
    filtered_events = [event for event in events_list if event.get("type") in ["ELITE_MONSTER_KILL", "BUILDING_KILL"]]

    team_events_j = []

    team_events_b = []

    event_j = False
    event_b = False

    # Obtener los valores para 'killerId' y 'monsterSubType' de cada evento
    interval_tooltips_j = []  # Lista para almacenar los tooltips del intervalo actual
    interval_tooltips_b = []  # Lista para almacenar los tooltips del intervalo actual
    for event in filtered_events:
        killer_id = event.get("killerId")
        monster_sub_type = event.get("monsterSubType")
        monster_type = event.get("monsterType")
        if killer_id == 0:
            killer_name = "Minion"
        else:
            killer_name = match_final["info"]["participants"][killer_id-1]["championName"]
        building_type = event.get("buildingType")
        tower_type = event.get("towerType")

        # Determinar el equipo correspondiente según el 'killerId'
        team = "Blue Team" if 1 <=  killer_id < 6 else "Red Team"

        # Determinar el color según el 'killerId'
        color = "rgb(0, 0, 255)"  if 1 <= killer_id < 6 else "rgb(255, 0, 0)"

        team_id = event.get("teamId")

        if team_id != None:
            team_b = team_dict[team_id]

            # Crear el texto del tooltip según las condiciones mencionadas
        if monster_type in ["BARON_NASHOR", "RIFTHERALD"]:
            tooltip_text_j = f"{killer_name} from {team} killed {event_types_dict[monster_type]}"
            #y_value_j  = jungle_y_value
            # Agregar los valores a las listas correspondientes
            # Agregar los tooltips del intervalo actual a la lista
            interval_tooltips_j.append(tooltip_text_j)
            #x_values_j.append(intervalo)
            #y_values_j.append(y_value_j)  # Valor de y arbitrario para la ubicación del punto en el gráfico
            #tooltips_j.append("<br>".join(interval_tooltips_j))  # Agrupar los tooltips del intervalo actual

            team_events_j.append(team)
            event_j = True
            #st.write(f"{intervalo} jungle {team}")

        elif monster_sub_type in dragon_objectives:
            tooltip_text_j = f"{killer_name} from {team} killed {event_types_dict[monster_sub_type]}"
            #y_value_j = jungle_y_value
            # Agregar los valores a las listas correspondientes
            # Agregar los tooltips del intervalo actual a la lista
            interval_tooltips_j.append(tooltip_text_j)
            #x_values_j.append(intervalo)
            #y_values_j.append(y_value_j)  # Valor de y arbitrario para la ubicación del punto en el gráfico

            #tooltips_j.append("<br>".join(interval_tooltips_j))  # Agrupar los tooltips del intervalo actual
            team_events_j.append(team)
            event_j = True
            #st.write(f"{intervalo} jungle {team}")

        elif building_type in ["TOWER_BUILDING"]:
            tooltip_text_b = f"{killer_name} from {team_b} destroyed {event_types_dict[tower_type]}"
            #y_value_b = buildings_y_value
            interval_tooltips_b.append(tooltip_text_b)
            #x_values_b.append(intervalo)
            #y_values_b.append(y_value_b)  # Valor de y arbitrario para la ubicación del punto en el gráfico
            #tooltips_b.append("<br>".join(interval_tooltips_b))  # Agrupar los tooltips del intervalo actual
            team_events_b.append(team_b)
            event_b = True
            #st.write(f"{intervalo} build {team_b}")

        elif building_type in ["INHIBITOR_BUILDING"]:
            tooltip_text_b = f"{killer_name} from {team_b} destroyed {event_types_dict[building_type]}"
            #y_value_b = buildings_y_value
            interval_tooltips_b.append(tooltip_text_b)
            #x_values_b.append(intervalo)
            #y_values_b.append(y_value_b)  # Valor de y arbitrario para la ubicación del punto en el gráfico
            #tooltips_b.append("<br>".join(interval_tooltips_b))  # Agrupar los tooltips del intervalo actual
            team_events_b.append(team_b)
            event_b = True
            #st.write(f"{intervalo} build {team_b}")

    if event_j:
        x_values_j.append(intervalo)
        y_values_j.append(jungle_y_value)  # Valor de y arbitrario para la ubicación del punto en el gráfico
        #st.write(f"{intervalo} jungle , {team}, {team_events_j}")
        tooltips_j.append("<br>".join(interval_tooltips_j))
        if len(set(team_events_j)) == 1:
            colors_j.append(color_dict[team_events_j[0]])  # Agregar el color correspondiente al punto
        elif len(set(team_events_j)) == 2:
            colors_j.append(multicolor)

    if event_b:
        x_values_b.append(intervalo)
        y_values_b.append(buildings_y_value)  # Valor de y arbitrario para la ubicación del punto en el gráfico
        #st.write(f"{intervalo} build , {team_b}, {team_events_b}")
        tooltips_b.append("<br>".join(interval_tooltips_b))  # Agrupar los tooltips del intervalo actual
        if len(set(team_events_b)) == 1:
            colors_b.append(color_dict[team_events_b[0]])  # Agregar el color correspondiente al punto
        elif len(set(team_events_b)) == 2:
            colors_b.append(multicolor)

#x_values_j2 = list(sorted(set(x_values_j)))
#x_values_b2 = list(sorted(set(x_values_b)))

#y_values_j = [jungle_y_value for i in x_values_j2]

#y_values_b = [buildings_y_value for i in x_values_j2]

#st.write(colors_j)
#st.write(tooltips_j)
#st.write(x_values_j2)
#st.write(y_values_j)

# Agregar los tooltips al gráfico con los colores correspondientes
fig.add_trace(go.Scatter(x=x_values_j, y=y_values_j, mode='markers', marker=dict(size=10, color=colors_j), text=tooltips_j, hoverinfo='text', name='Tooltips'))
fig.add_trace(go.Scatter(x=x_values_b, y=y_values_b, mode='markers', marker=dict(size=10, color=colors_b), text=tooltips_b, hoverinfo='text', name='Tooltips'))

# Actualizar el diseño del gráfico
fig.update_layout(title='Winning Probability (%) and Objectives', title_pad_l=275,xaxis=dict(range=[-0.5, match_length]), yaxis=dict(range=[0, 119]), showlegend=False)

# Agregar títulos a la izquierda y a la altura de los valores de Y
fig.add_annotation(x=2, y=jungle_y_value, text='Jungle Objectives', showarrow=False, font=dict(size=12))
fig.add_annotation(x=2, y=buildings_y_value, text='Building Objectives', showarrow=False, font=dict(size=12))

# Mostrar el gráfico interactivo en Streamlit
columns3[2].plotly_chart(fig)

columns3[0].write(f" ")
columns3[0].write(f" ")
columns3[0].write(f" ")
columns3[0].write(f" ")
columns3[0].write(f" ")
columns3[0].write(f" ")

if proba >= 50:
    columns3[0].write(f"##### Probability of :{color1}[{team}] team winning at minute {minute} was {proba}% :chart_with_upwards_trend:")
else:
    columns3[0].write(f"##### Probability of :{color1}[{team}] team winning at minute {minute} was {proba}% :chart_with_downwards_trend:")

result = match_result_team(match_final, team)

columns3[0].write(f" ")
columns3[0].write(f" ")

if result == "Victory":
    columns3[0].write(f"##### :{color1}[{team}] team result: {result} :trophy:")
else:
    columns3[0].write(f"##### :{color1}[{team}] team result: {result} :thumbsdown:")

columns3[0].write(f" ")
columns3[0].write(f" ")

columns3[0].write(f"##### {diagnosis(proba, result)}")
