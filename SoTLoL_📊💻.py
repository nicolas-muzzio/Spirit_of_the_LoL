import streamlit as st


st.set_page_config(
            page_title="Spirit of the LoL", # Adjust things later
            page_icon=":bar_chart:", #Change icon later
            layout="wide", # or centered, wide has more space
            initial_sidebar_state="auto") # collapsed

st.write("# Welcome to Spirit of the LoL! 👋")

st.sidebar.success("Select an app above")

st.write("#### Spirit of the LoL is a project that aims to apply Data Science and Machine Learning tools to League of Legends")

st.write("")

st.write("")

st.write("#### **👈 Select an app from the sidebar**")

st.write("")

st.write("")

st.write("##### **NoobMeter** :video_game:: know the winning odds of your last games and if you were :orange[Afraid to Win] :collision: or you :green[Defied the Odds] :heart_on_fire:")
st.write("##### :link: https://spirit-of-the-lol.streamlit.app/NoobMeter")

st.write("")

st.write("")

st.write("##### **Predictor** :dart:: select team objective differences to predict if your team will end in Victory :trophy: or Defeat :thumbsdown:")
st.write("##### :link: https://spirit-of-the-lol.streamlit.app/Predictor")

st.write("")

st.write("")

st.write("##### **Oldies** :hourglass_flowing_sand:: know the winning odds of old games :open_file_folder:")
st.write("##### :link: https://spirit-of-the-lol.streamlit.app/Oldies")

st.write("")

st.write("")

st.write("##### **The Team** :busts_in_silhouette::busts_in_silhouette:: to know more about us")
st.write("##### :link: https://spirit-of-the-lol.streamlit.app/The_Team")
