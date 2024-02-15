import streamlit as st
import pandas as pd
from func_top_n_movies import top_n_movies
from func_get_item_based_movies import get_movie_recommendations
from func_get_user_based_movies import recommend_movies
from func_get_user_based_movies import recommend_movies_by_genre
from tmdb_api import get_poster_url
from user_input import user_input_features
from displayposters import display_posters
import os
import random

# Load your data
links = pd.read_csv('links.csv')
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
tags = pd.read_csv('tags.csv')

# Add a logo to the top left corner
st.markdown(
        """
        <style>
        .logo-text {
            font-size:80px !important;
            color: mediumseagreen !important;
            position: absolute;
            top: 2%;
            left: 2%;
            z-index: 99999;
        }
        </style>
        <div class="logo-text">WBSFLIX</div>
        """, unsafe_allow_html=True
)

# Add line breaks
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# User inputs
movie_name = st.text_input('Search for a movie', key='movie_name')
user_id = st.text_input('Enter your user ID please', '42', key='user_id')
user_id = int(user_id)  # Convert the user ID to an integer
top_n = 10  # Define the number of recommendations to display

# Chatbot's header
st.header("Movie Recommendation Chatbot")

# Chatbot's greeting message
st.write("Hello, how can I help you today? Try entering a movie or a genre you liked or your user ID.")

# Use st.text_input for chatbot input
chatbot_input = st.text_input('Chatbot Input', help='Enter your user ID or a movie or a genre you liked', key='chatbot_input')

# Define the variable "genre" before using it
genre = None  

if chatbot_input:
    if chatbot_input.lower() == "banana!":
            # Easter egg for 'banana!'
            st.write("Maxguv minion! Aca nama tadda ka kaylay cama to: (Translation: Welcome minion! This is all I have of you:)")
            minion_movies = movies[movies['title'].str.lower().str.contains('despicable me') | movies['title'].str.lower().str.contains('minions')]
            minion_movies = minion_movies.merge(links, on='movieId')  # Merge with links DataFrame
            if not minion_movies.empty:
                display_posters(minion_movies)
            else:
                st.write("Sorry, no Minions movies found.")
    elif chatbot_input.isdigit():
            # If the user input is a number, assume it's a user ID and recommend a movie
            user_id = int(chatbot_input)
            recommendations = recommend_movies(user_id, ratings, movies, links, 1)
            # Use st.write for chatbot output
            st.write(f"I recommend the movie: {recommendations['title'].values[0]}")
            display_posters(recommendations)
    elif any(chatbot_input.lower() in genre.lower() for genre in ['Adventure', 'Animation', 'Children', 'Comedy', 'Fantasy', 'Romance', 'Drama',
    'Action', 'Crime', 'Thriller', 'Horror', 'Mystery', 'Sci-Fi', 'War', 'Musical',
    'Documentary', 'IMAX', 'Western', 'Film-Noir']):
        # If the user input is a genre, recommend a movie from that genre
        genre = next(genre for genre in ['Adventure', 'Animation', 'Children', 'Comedy', 'Fantasy', 'Romance', 'Drama',
        'Action', 'Crime', 'Thriller', 'Horror', 'Mystery', 'Sci-Fi', 'War', 'Musical',
        'Documentary', 'IMAX', 'Western', 'Film-Noir'] if chatbot_input.lower() in genre.lower())
        recommendations = recommend_movies_by_genre(genre, movies, links, 1)
        if not recommendations.empty:
            st.write(f"I recommend the movie: {recommendations['title'].values[0]}")
            display_posters(recommendations)
    elif any(chatbot_input.lower() in movie.lower() for movie in movies['title'].values):
        # If the user input is a substring of a movie title, recommend a similar movie
        movie_title = next(movie for movie in movies['title'].values if chatbot_input.lower() in movie.lower())
        recommendations = get_movie_recommendations(movie_title, 1, movies, links)
        st.write(f"If you liked {movie_title}, you might also like: {recommendations['title'].values[0]}")
        display_posters(recommendations)
else:
    st.write("Sorry, I didn't understand that. Please try again.")

# Merge the 'movies' and 'links' DataFrames on 'movieId'
movies_with_links = movies.merge(links, on='movieId')

# Filter the merged DataFrame for titles that contain the user input
search_results = movies_with_links[movies_with_links['title'].str.lower().str.contains(movie_name.lower())]

# If the user inputs something in the search field, filter the merged DataFrame for titles that contain the user input and display the results
if movie_name:
        search_results = movies_with_links[movies_with_links['title'].str.lower().str.contains(movie_name.lower())]

        # Check if any movies were found
        if search_results.empty:
            st.write("No movies found.")
        else:
            # Display the search results
            st.subheader(f"Search results for '{movie_name}':")
            display_posters(search_results)

# Display top n movies
st.subheader("Our customers' favourites")
top_movies = top_n_movies(top_n, movies, ratings, links)  # Add links as an argument
display_posters(top_movies)

# Filter the ratings DataFrame for rows where the userId is the specified user and the rating is 4 or 5
high_rated_movies = ratings[(ratings['userId'] == user_id) & (ratings['rating'] >= 4)]

# Randomly select one of these high-rated movies
random_high_rated_movie = high_rated_movies.sample(1)

# Get the title of the randomly selected high-rated movie from the movies DataFrame
random_high_rated_movie_title = movies[movies['movieId'] == random_high_rated_movie['movieId'].values[0]]['title'].values[0]

# Display item-based recommendations
st.subheader(f"Because you liked '{random_high_rated_movie_title}', you might also like...")
item_recommendations = get_movie_recommendations(random_high_rated_movie_title, top_n, movies, links)  # Add links as an argument
display_posters(item_recommendations)

# Display user-based recommendations
st.subheader('Specially for you')
user_recommendations = recommend_movies(user_id, ratings, movies, links, top_n)  # Add links as an argument
display_posters(user_recommendations)
