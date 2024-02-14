def chatbot():
    print("Hello! I can recommend movies for you.")
    while True:
        user_input = input("Please enter your user ID, a movie you liked, or a genre you like: ")
        if user_input.isdigit():
            # If the user input is a number, assume it's a user ID and recommend a movie
            user_id = int(user_input)
            recommendation = recommend_movies(user_id, ratings, movies, links, 1)
            print(f"I recommend the movie: {recommendation['title'].values[0]}")
        elif user_input in movies['title'].values:
            # If the user input is a movie title, recommend a similar movie
            similar_movie = recommend_similar_movie(user_input, movies)
            print(f"If you liked {user_input}, you might also like: {similar_movie}")
        elif user_input in ['comedy', 'drama', 'thriller', 'sci-fi', 'children']:
            # If the user input is a genre, recommend a movie from that genre
            genre_recommendation = recommend_genre_movie(user_input, movies)
            print(f"As a fan of {user_input} movies, you might like: {genre_recommendation}")
        else:
            print("Sorry, I didn't understand that. Please try again.")