from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def get_movie_recommendations(title, n, movies, tags, links):
    # Merge movies and tags dataframes
    merged_df = pd.merge(movies, tags, on='movieId', how='left')

    # Merge the merged_df DataFrame with the links DataFrame
    merged_df = pd.merge(merged_df, links, on='movieId', how='left')

    # Fill NA values in tag with an empty string
    merged_df['tag'] = merged_df['tag'].fillna('')

    # Create a new column metadata that combines genres and tag
    merged_df['metadata'] = merged_df[['genres', 'tag']].apply(lambda x: ' '.join(x), axis = 1)

    # Create a TF-IDF vectorizer
    tfidf = TfidfVectorizer(stop_words='english')

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(merged_df['metadata'])

    # Compute the cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Convert the title to lowercase
    title = title.lower()

    # Get the DataFrame of movies that match the title
    matching_movies = merged_df[merged_df['title'].str.lower() == title]

    # Check if the DataFrame is not empty
    if not matching_movies.empty:
        # Get the indices of the movies that match the title
        matching_indices = matching_movies.index.tolist()

        # Get the pairwise similarity scores of all movies with the first matching movie
        sim_scores = list(enumerate(cosine_sim[matching_indices[0]]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Filter out the input movie from the similarity scores
        sim_scores = [sim_score for sim_score in sim_scores if sim_score[0] not in matching_indices]

        # Get the scores of the n most similar movies
        sim_scores = sim_scores[:n]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Get the top n most similar movies along with their tmdbId
        recommendations = merged_df[['title', 'tmdbId', 'genres']].iloc[movie_indices]

        # Drop duplicates based on 'title'
        recommendations = recommendations.drop_duplicates(subset='title')

        # Get the genres of the input movie
        input_genres = matching_movies['genres'].iloc[0].split('|')

        # Filter the recommendations to include at least two movies from the same genre as the input movie
        genre_recommendations = recommendations[recommendations['genres'].apply(lambda x: any(genre in x for genre in input_genres))]

        if len(genre_recommendations) >= 2:
            return genre_recommendations
        else:
            return recommendations
    else:
        # Return an empty DataFrame if no matching movie is found
        return pd.DataFrame()