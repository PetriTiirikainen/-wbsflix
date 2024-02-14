import requests
import os
from dotenv import load_dotenv

def get_poster_url(tmdbId):
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    response = requests.get(f'https://api.themoviedb.org/3/movie/{tmdbId}?api_key={api_key}')
    print("Response status code:", response.status_code)
    data = response.json()
    print("Response data:", data)
    poster_path = data.get('poster_path')
    if poster_path:
        return f'https://image.tmdb.org/t/p/w500{poster_path}'
    else:
        return None