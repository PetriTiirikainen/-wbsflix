import pandas as pd

def top_n_movies(n, movies, ratings, links):
    # Merge movies and ratings on 'movieId'
    merged_df = pd.merge(movies, ratings, on='movieId')
    
    # Merge merged_df and links on 'movieId'
    merged_df = pd.merge(merged_df, links, on='movieId')
    
    # Calculate average rating and number of ratings for each movie
    ratings_stats = merged_df.groupby(['title', 'tmdbId'])['rating'].agg(['mean', 'count'])
    
    # Calculate C
    C = ratings_stats['mean'].mean()
    
    # Calculate m
    m = ratings_stats['count'].quantile(0.9)
    
    # Filter movies that have number of ratings more than m
    qualified_movies = ratings_stats[ratings_stats['count'] >= m]
    
    # Calculate weighted rating for each qualified movie
    qualified_movies['weighted_rating'] = (qualified_movies['count'] / (qualified_movies['count'] + m) * qualified_movies['mean']) + (m / (qualified_movies['count'] + m) * C)
    
    # Sort movies by weighted rating and select top n movies
    top_movies = qualified_movies.sort_values('weighted_rating', ascending=False).head(n)
    
    # Reset index
    top_movies = top_movies.reset_index()
    
    return top_movies