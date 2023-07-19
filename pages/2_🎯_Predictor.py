import streamlit as st

#To open pickles with model and transformers info
import pickle

import pandas as pd

from preprocessing.clean_preprocess import preprocess_pred

from streamlit_functions.functions import columns_of_interest_dict, find_transformer, tier_list

st.set_page_config(
            page_title="Spirit of the LoL", # Adjust things later
            page_icon="🎯", #Change icon later
            layout="wide", # or centered, wide has more space
            initial_sidebar_state="auto") # collapsed

st.write("# Predictor 🎯")

time_list = [None, 5,10,15,20,25,30]

columns = st.columns(3)

columns[0].write("#### Match Time in minutes")
time = columns[0].selectbox("",time_list , help = "The time point at which you want to predict the winning odds for the game",index=0, label_visibility = "visible")

columns[1].write("#### Tier")

league = columns[1].selectbox("",tier_list , help = "The average Tier of the players in the game",index=2, label_visibility = "visible")


if time == None:
    st.stop()

#Main Form to get data from user
with st.form(key='params_for_api'):

    st.write("""Explanation: -A positive value means Team 1 has taken more of that particular objective than the Team 2.
              -A negative value means Team 2 has taken more of that particular objective.
             -A value of 0 means there are not differences with respecto to that value.""")
    st.write("""Disclaimer:
             -This model does not account for side difference.
             -Some combinations of inputs may not be possible in the game (e.g.: having more than 3 elemental dragons)""")

    columns2 = st.columns(3)

    columns2[0].write("#### Total Gold Differences")
    totalGold = columns2[0].slider("",
                                    min_value=-columns_of_interest_dict[time]["totalGold"],
                                    max_value=columns_of_interest_dict[time]["totalGold"],
                                    value=0, step=None,
                                    format=None, key=None, help="Total gold of Team 1 minus Total gold in Team 2", on_change=None, args=None, kwargs=None, disabled=False,
                                    label_visibility="visible")

    columns2[1].write("#### Minions Killed Difference")
    minionsKilled = columns2[1].slider("",
                                        min_value=-columns_of_interest_dict[time]["minionsKilled"],
                                        max_value=columns_of_interest_dict[time]["minionsKilled"],
                                        value=0, step=None,
                                        format=None, key=None, help="Minions killed by Team 1 minus Minions killed by Team 2", on_change=None, args=None, kwargs=None, disabled=False,
                                        label_visibility="visible")

    st.write("")

    st.write("#### Building Objectives Differences")
    columns5 = st.columns(4)

    outer_turret_list = list(range(-columns_of_interest_dict[time]["towerType_OUTER_TURRET"],columns_of_interest_dict[time]["towerType_OUTER_TURRET"]+1))
    towerType_OUTER_TURRET = columns5[0].selectbox("Outer Turret", outer_turret_list,index=columns_of_interest_dict[time]["towerType_OUTER_TURRET"],
                                                   help = "Outer Turrets destroyed by Team 1 minus Outer Turrets destroyed by Team 2")

    inner_turret_list = list(range(-columns_of_interest_dict[time]["towerType_INNER_TURRET"],columns_of_interest_dict[time]["towerType_INNER_TURRET"]+1))
    towerType_INNER_TURRET = columns5[1].selectbox("Innter Turret",inner_turret_list ,index=columns_of_interest_dict[time]["towerType_INNER_TURRET"],
                                                   help = "Inner Turrets destroyed by Team 1 minus Inner Turrets destroyed by Team 2")
    #inhibitort = columns5[2].selectbox("inhibitort",tier_list ,index=0)

    base_turret_list = list(range(-columns_of_interest_dict[time]["towerType_BASE_TURRET"],columns_of_interest_dict[time]["towerType_BASE_TURRET"]+1))
    towerType_BASE_TURRET = columns5[2].selectbox("Inhibitor Turret",base_turret_list ,index=columns_of_interest_dict[time]["towerType_BASE_TURRET"],
                                                  help = "Base Turrets destroyed by Team 1 minus Base Turrets destroyed by Team 2")

    inhibitor_list = list(range(-columns_of_interest_dict[time]["buildingType_INHIBITOR_BUILDING"],columns_of_interest_dict[time]["buildingType_INHIBITOR_BUILDING"]+1))
    buildingType_INHIBITOR_BUILDING = columns5[3].selectbox("Inhibitor",inhibitor_list ,index=columns_of_interest_dict[time]["buildingType_INHIBITOR_BUILDING"],
                                                            help = "Inhibitors destroyed by Team 1 minus Inhibitors destroyed by Team 2")

    st.write("")

    st.write("#### Jungle Objectives Differences")
    st.write("##### Dragons")
    columns3 = st.columns(7)

    dragon_list = list(range(-columns_of_interest_dict[time]["monsterType_AIR_DRAGON"],columns_of_interest_dict[time]["monsterType_AIR_DRAGON"]+1))


    monsterType_FIRE_DRAGON = columns3[0].selectbox("Fire",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])
    monsterType_WATER_DRAGON = columns3[1].selectbox("Water",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])
    monsterType_EARTH_DRAGON = columns3[2].selectbox("Earth",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])
    monsterType_CHEMTECH_DRAGON = columns3[3].selectbox("Chemtech",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])
    monsterType_HEXTECH_DRAGON = columns3[4].selectbox("Hextech",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])
    monsterType_AIR_DRAGON = columns3[5].selectbox("Air",dragon_list ,index=columns_of_interest_dict[time]["monsterType_AIR_DRAGON"])

    elder_dragon_list = list(range(-columns_of_interest_dict[time]["monsterType_ELDER_DRAGON"],columns_of_interest_dict[time]["monsterType_ELDER_DRAGON"]+1))
    monsterType_ELDER_DRAGON = columns3[6].selectbox("Elder",elder_dragon_list ,index=columns_of_interest_dict[time]["monsterType_ELDER_DRAGON"])

    st.write("")

    columns4 = st.columns(6)

    herald_list = list(range(-columns_of_interest_dict[time]["monsterType_RIFTHERALD"],columns_of_interest_dict[time]["monsterType_RIFTHERALD"]+1))
    columns4[0].write("##### Hearld")
    monsterType_RIFTHERALD = columns4[0].selectbox("Rift Herald",herald_list ,index=columns_of_interest_dict[time]["monsterType_RIFTHERALD"],label_visibility="collapsed")

    nashor_list = list(range(-columns_of_interest_dict[time]["monsterType_BARON_NASHOR"],columns_of_interest_dict[time]["monsterType_BARON_NASHOR"]+1))
    columns4[1].write("##### Baron")
    monsterType_BARON_NASHOR = columns4[1].selectbox("Baron Nashor",nashor_list ,index=columns_of_interest_dict[time]["monsterType_BARON_NASHOR"],label_visibility="collapsed")

    #st.write("#### Champion Kills Differences")
    ############ Kills were removed from the user input, they do not change considerable the prediction
    #columns6 = st.columns(3)
    #columns6[0].write("##### First Blood")
    killType_KILL_FIRST_BLOOD = 0 #columns6[0].selectbox("First Blood",[-1,0,1] ,index=1,label_visibility="collapsed")

    #multi_kill_list = list(range(-columns_of_interest_dict[time]["killType_KILL_MULTI"],columns_of_interest_dict[time]["killType_KILL_MULTI"]+1))
    #columns6[1].write("##### Multi Kills")
    killType_KILL_MULTI = 0 #columns6[1].selectbox("Multi Kills",multi_kill_list ,index=columns_of_interest_dict[time]["killType_KILL_MULTI"],label_visibility="collapsed")

    #multi_kill_list = list(range(-columns_of_interest_dict[time]["killType_KILL_ACE"],columns_of_interest_dict[time]["killType_KILL_ACE"]+1))
    #columns6[1].write("##### Aces")
    killType_KILL_ACE = 0 #columns6[1].selectbox("Aces",multi_kill_list ,index=columns_of_interest_dict[time]["killType_KILL_ACE"],label_visibility="collapsed")

    st.form_submit_button('Make prediction')

data_dict = {'killType_KILL_ACE': killType_KILL_ACE,
        'killType_KILL_FIRST_BLOOD': killType_KILL_FIRST_BLOOD,
        'killType_KILL_MULTI': killType_KILL_MULTI,
        'minionsKilled': minionsKilled,
        'monsterType_AIR_DRAGON': monsterType_AIR_DRAGON,
        'monsterType_CHEMTECH_DRAGON' :monsterType_CHEMTECH_DRAGON,
        'monsterType_EARTH_DRAGON' :monsterType_EARTH_DRAGON,
        'monsterType_FIRE_DRAGON' :monsterType_FIRE_DRAGON,
        'monsterType_HEXTECH_DRAGON' :monsterType_HEXTECH_DRAGON,
        'monsterType_RIFTHERALD' :monsterType_RIFTHERALD,
        'monsterType_WATER_DRAGON' :monsterType_WATER_DRAGON,
        'monsterType_ELDER_DRAGON' :monsterType_ELDER_DRAGON,
        'monsterType_BARON_NASHOR' :monsterType_BARON_NASHOR,
        'totalGold' : totalGold,
        'towerType_INNER_TURRET' : towerType_INNER_TURRET,
        'towerType_OUTER_TURRET' : towerType_OUTER_TURRET,
        'towerType_BASE_TURRET' : towerType_BASE_TURRET,
        'buildingType_INHIBITOR_BUILDING' : buildingType_INHIBITOR_BUILDING}

data_df = pd.DataFrame(data_dict, index=[0])

pickle_file_path = f"model/pickles_models/{league}_model.pkl"
with open(pickle_file_path, "rb") as file:
        # Load the data from the pickle file
        fitted_model = pickle.load(file)

transformer = find_transformer(time, league)

#st.write(data_df)

X_pred_prep = preprocess_pred(data_df, transformer)

model = fitted_model

proba = round(model.predict_proba(X_pred_prep)[0][1]*100,2)

#To compensate for side difference that we are not taking ino account, correct in the future
if (data_df == 0).all(axis=1).all():
    proba = 50.0

st.write(f"### The propability of Team 1 winning is {proba}")
