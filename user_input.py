# user_input.py

import streamlit as st
import random

def user_input_features():
    movie_name = st.sidebar.text_input('Search for a movie', '', key='movie_name', help='Enter the name of a movie you are looking for')
    user_id = int(st.sidebar.text_input('User Id', '1', key='user_id', help='Enter your user ID'))  # Adjust the range according to your data
    top_n = random.randint(10, 50)  # Set top_n to a random number between 10 and 50
    return movie_name, user_id, top_n