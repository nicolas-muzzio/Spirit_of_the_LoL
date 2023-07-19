import streamlit as st


st.set_page_config(
            page_title="Spirit of the LoL", # Adjust things later
            page_icon="👥", #Change icon later
            layout="wide", # or centered, wide has more space
            initial_sidebar_state="auto") # collapsed

st.write("# The Team :mechanical_arm:")

st.write("#### We are Le Wagoners! Data Science Bootcamp Batch 1201")

st.write("#### ")

columns = st.columns([0.12,0.22,0.22,0.22,0.22], gap = "medium")

columns[0].write("#### :blue[Name]")
columns[1].write("#### Andy")
columns[2].write("#### Gonza")
columns[3].write("#### Santy")
columns[4].write("#### Nico")

columns[0].write("")
columns[0].write("")


columns[0].write("#### :red[A Champion]")
columns[1].image(f"images/champion/Veigar.png",caption="Veigar", width=105)
columns[2].image(f"images/champion/Garen.png",caption="Garen", width=105)
columns[3].image(f"images/champion/Heimerdinger.png",caption="Heimerdinger", width=105)
columns[4].image(f"images/champion/Ahri.png",caption="Ahri", width=105)

columns[0].write("")
columns[0].write("")
columns[0].write("")
columns[0].write("")

columns[0].write("#### :green[A Video Game]")
columns[1].write("#### Baldur's Gate 2")
columns[2].write("#### Chrono Trigger")

columns[3].write("#### Cloud Punk")

columns[4].write("#### Warcraft II")

columns[0].write("")
columns[1].write("")
columns[2].write("")
columns[3].write("")
columns[4].write("")

columns[0].write("")
columns[1].write("")
columns[2].write("")
columns[3].write("")
columns[4].write("")


columns[0].write("##### :orange[Linkedin]")
columns[1].write("www.linkedin.com/in/huespeandres/")
columns[2].write("www.linkedin.com/in/gflara")
columns[3].write("www.linkedin.com/in/santiago-i-pieretti/")
columns[4].write("www.linkedin.com/in/nicolasmuzzio/")

st.write("#### ")

st.write("#### :email:Contact: lwdatasciencefinalproject@gmail.com")
