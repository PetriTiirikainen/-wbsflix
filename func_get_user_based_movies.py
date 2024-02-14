import pandas as pd
from surprise import Reader, Dataset, KNNBasic
import random

def recommend_movies(userId, ratings, movies, links, n=10):
    # Use your ratings dataframe
    df_1 = ratings[['userId', 'movieId', 'rating']]
    reader = Reader(rating_scale=(1, 5))  # Here, we assume the ratings go from 1 to 5
    data = Dataset.load_from_df(df_1, reader)

    sim_options = {
        'name': 'cosine',
        'user_based': True  # compute  similarities between users
    }

    full_train = data.build_full_trainset()
    algo = KNNBasic(sim_options=sim_options)
    algo.fit(full_train)
    testset = full_train.build_anti_testset()

    top_n_df = get_top_n(testset, userId, n, algo)

    # Creating a DataFrame from the top_n with columns 'movieId' and 'estimated_rating'
    reduced_top_n_df = top_n_df.loc[:, ["iid", "est"]].rename(columns={"iid": "movieId", "est": "estimated_rating"})

    # Creating a copy of the original DataFrame with duplicate 'movieId' entries removed
    reduced_original_df = movies.drop_duplicates(subset='movieId').copy()

    # Merging the movies DataFrame with the links DataFrame
    merged_movies_links_df = pd.merge(reduced_original_df, links, on='movieId', how='left')

    # Merging the top_n DataFrame with the merged movies and links DataFrame
    merged_df = pd.merge(reduced_top_n_df, merged_movies_links_df, on="movieId", how='left')

    # Selecting specific columns from the merged DataFrame to include in the final result
    final_df = merged_df[['movieId', 'title', 'genres', 'estimated_rating', 'tmdbId']]

    # Define the genres to be included in the recommendations
    genres = ['comedy', 'drama', 'thriller', 'sci-fi', 'children']

    # Filter the recommendations to include at least one movie from each genre
    genre_recommendations = []
    for genre in genres:
        genre_df = final_df[final_df['genres'].str.lower().str.contains(genre.lower(), na=False)]
        if not genre_df.empty:
            genre_recommendations.append(genre_df.sample(1))

    # Concatenate the genre recommendations
    genre_recommendations_df = pd.concat(genre_recommendations)

    # If the number of genre recommendations is less than n, fill the rest with random recommendations
    if len(genre_recommendations_df) < n:
        remaining_df = final_df[~final_df['movieId'].isin(genre_recommendations_df['movieId'])]
        additional_recommendations = remaining_df.sample(n - len(genre_recommendations_df))
        genre_recommendations_df = pd.concat([genre_recommendations_df, additional_recommendations])

    return genre_recommendations_df

def get_top_n(testset, user_id, n, algo, randomness=2): 
    # Filter the testset to include only rows with the specified user_id 
    filtered_testset = [row for row in testset if row[0] == user_id]
    # Make predictions on the filtered testset
    predictions = algo.test(filtered_testset)

    # Convert the list of predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['uid', 'iid', 'r_ui', 'est', 'details'])

    # Convert the 'est' column to a numeric type
    predictions_df['est'] = pd.to_numeric(predictions_df['est'])

    # Get the top n*randomness predictions based on the estimated ratings ('est')
    top_n_predictions_df = predictions_df.nlargest(n*randomness, 'est')

    # Shuffle the DataFrame
    top_n_predictions_df = top_n_predictions_df.sample(frac=1)

    # Return the top n predictions
    return top_n_predictions_df.head(n)