from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def get_movie_recommendations(title, n, movies, links):
    # Merge movies DataFrame with the links DataFrame
    merged_df = pd.merge(movies, links, on='movieId', how='left')

    # Split the genres into a list of genres
    merged_df['genres'] = merged_df['genres'].apply(lambda x: x.split('|'))

    # Create MultiLabelBinarizer object
    mlb = MultiLabelBinarizer()

    # One-hot encode the genres
    genres_df = pd.DataFrame(mlb.fit_transform(merged_df.pop('genres')),
                             columns=mlb.classes_,
                             index=merged_df.index)

    # Compute the cosine similarity matrix
    cosine_sim = cosine_similarity(genres_df, genres_df)

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
        recommendations = merged_df[['title', 'tmdbId']].iloc[movie_indices]

        # Drop duplicates based on 'title'
        recommendations = recommendations.drop_duplicates(subset='title')

        return recommendations
    else:
        # Return an empty DataFrame if no matching movie is found
        return pd.DataFrame()
