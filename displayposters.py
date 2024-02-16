# displayposters.py
import pandas as pd
import streamlit as st
from tmdb_api import get_poster_url

def display_posters(df):
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df = df.copy()

    # Check if 'tmdbId' column exists in the DataFrame, if not, create it with null values
    if 'tmdbId' not in df.columns:
        df['tmdbId'] = pd.NA

    # Start of the HTML string
    html = '<div style="display: flex; overflow-x: auto;">'
    
    for _, row in df.iterrows():
        if pd.isnull(row['tmdbId']):
            print(f"tmdbId is null for movie: {row['title']}")
            html += f'<div style="flex: 0 0 auto; width: 200px; margin: 10px;"><a href="https://www.themoviedb.org/movie/{row["tmdbId"]}" target="_blank"><p>{row["title"]}</p></a></div>'
        else:
            poster_url = get_poster_url(row['tmdbId'])
            print(f"Poster URL for movie {row['title']}: {poster_url}")
            if poster_url:
                # Add each poster to the HTML string
                html += f'<div style="flex: 0 0 auto; width: 200px; margin: 10px;"><a href="https://www.themoviedb.org/movie/{row["tmdbId"]}" target="_blank"><img src="{poster_url}" style="max-width: 100%;"><p>{row["title"]}</p></a></div>'
            else:
                html += f'<div style="flex: 0 0 auto; width: 200px; margin: 10px;"><a href="https://www.themoviedb.org/movie/{row["tmdbId"]}" target="_blank"><p>{row["title"]}</p></a></div>'
    
    # End of the HTML string
    html += '</div>'
    
    # Display the HTML string
    st.markdown(html, unsafe_allow_html=True)
