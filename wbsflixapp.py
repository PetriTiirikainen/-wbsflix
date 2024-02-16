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

st.set_page_config(layout="wide")

# Add a logo to the top left corner
st.markdown(
        """
        <style>
        .logo-text {
            font-size:80px !important;
            color: #E50914 !important;
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


user_id = st.text_input('Enter your user ID please', '42', help='Type in a User Id number between 1 and 610', key='user_id')
user_id = int(user_id)  # Convert the user ID to an integer
top_n = 15  # Define the number of recommendations to display

# Chatbot's header
st.header("Movie Recommendation Chatbot")

# Chatbot's greeting message
st.write("Hello, how can I help you today? Try entering a movie or a genre you liked or just type in the word recommend.")

# Use st.text_input for chatbot input
chatbot_input = st.text_input('Chatbot Input', help='You can type in the word recommend, a movie title or a movie genre to get a recommendation', key='chatbot_input')

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
    elif chatbot_input.lower() == "recommend":
        # If the user input is "recommend", recommend a movie for the user ID
        recommendations = recommend_movies(user_id, ratings, movies, links, top_n)  # Get top_n recommendations
        # Select a random movie from the recommendations
        random_recommendation = recommendations.sample(1)
        # Use st.write for chatbot output
        st.write(f"I recommend the movie: {random_recommendation['title'].values[0]}")
        display_posters(random_recommendation)
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

# Display top n movies
st.subheader("Our customers' favourites")
top_movies = top_n_movies(top_n, movies, ratings, links)  # Add links as an argument
display_posters(top_movies)

st.markdown("<br>", unsafe_allow_html=True)

# Merge the 'movies' and 'links' DataFrames on 'movieId'
movies_with_links = movies.merge(links, on='movieId')

movie_name = st.text_input('Search for a movie', help='Type in a movie title or a part of a movie title', key='movie_name')

# Initialize a flag to track whether the movie title was obtained from the search bar
from_search_bar = False

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

        # Use the first result from the search results as the input for the item-based recommendations
        movie_title_for_recommendations = search_results.iloc[0]['title']

        # Set the flag to True since the movie title was obtained from the search bar
        from_search_bar = True
else:
    # Filter the ratings DataFrame for rows where the userId is the specified user and the rating is 4 or 5
    high_rated_movies = ratings[(ratings['userId'] == user_id) & (ratings['rating'] >= 4)]

    # Randomly select one of these high-rated movies
    random_high_rated_movie = high_rated_movies.sample(1)

    # Get the title of the randomly selected high-rated movie from the movies DataFrame
    movie_title_for_recommendations = movies[movies['movieId'] == random_high_rated_movie['movieId'].values[0]]['title'].values[0]

st.markdown("<br>", unsafe_allow_html=True)

# Display item-based recommendations
if from_search_bar:
    st.subheader(f"Because you searched for '{movie_title_for_recommendations}', you might also like...")
else:
    st.subheader(f"Because you liked '{movie_title_for_recommendations}', you might also like...")
item_recommendations = get_movie_recommendations(movie_title_for_recommendations, top_n, movies, links)  # Add links as an argument
display_posters(item_recommendations)

st.markdown("<br>", unsafe_allow_html=True)

# Display user-based recommendations
st.subheader('Specially for you')
user_recommendations = recommend_movies(user_id, ratings, movies, links, top_n)  # Add links as an argument
display_posters(user_recommendations)
