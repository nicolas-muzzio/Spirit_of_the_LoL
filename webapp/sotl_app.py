import time
import streamlit as st

st.title('SPIRIT OF THE LOL')

"""

##### Who we are
"""
st.write({"About Us":"A project done by a group of passionate and nerdy students ","Team Lead":"Nicolas Muzzio","Backend Developers":"Andres Huespe and Santiago Pieretti","Frontend Developer":"Gonzalo Lara",})


elements = st.container()
summoner_name = elements.text_input("Speak friend, what is your username")

#here goes the output of data modeling
with st.spinner(f'Please wait a minute {summoner_name}'):
 if len(summoner_name)== 0:
     st.write("nothing to see here")
 else:
     time.sleep(5)
     st.success('Done')
