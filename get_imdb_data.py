# --- preprocessing: get imdb urls and cover urls for all movies in the dataset --

# load libraries
import pandas as pd
import numpy as np
import imdb

from pandarallel import pandarallel # for speedup..
pandarallel.initialize(progress_bar=True, nb_workers=4)

# create search interface
ia = imdb.Cinemagoer()

# load movie data
movie_data = pd.read_csv("data/movies.csv")

# function to lookup movie given a title and extract necessary items
def find_movie( title ):
    try:
        movie = ia.search_movie( title )[0]
        id = movie.getID()
        imdb_url = "https://www.imdb.com/title/tt" + id
        cover_url = movie['full-size cover url']
    except:
        imdb_url = None
        cover_url = None
        
    return {'imdb_url': imdb_url, 'cover_url': cover_url}
    
# glue year and string back together for the search
year_str = movie_data.year.map( lambda x: " (" + str(int(x)) + ")" if not np.isnan(x) else "" )
movie_data['movieTitle'] = movie_data.title + year_str

# run the search (will take a while)
res = movie_data['movieTitle'].parallel_map( find_movie )

# store to csv
res = pd.DataFrame.from_records( res )
res = res.set_index( movie_data.index )
res = movie_data.join( res )
res.to_csv("data/movie_data_with_imdb.csv", index=False)
