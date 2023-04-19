import pandas as pd
import numpy as np

# hardcoded paths
MOVIE_DATA = "data/movie_data_with_imdb.csv"
MOVIE_IDS = "data/movie_ids.csv"
INTERACTION_MATRIX = "data/normalized_interaction_matrix.npy"

class Recommender:
    def __init__( self ):
        # load data
        print("Loading data.. ", end="", flush=True)
        self.movie_data = pd.read_csv( MOVIE_DATA )
        self.movie_ids = pd.read_csv( MOVIE_IDS )
        self.X = np.load( INTERACTION_MATRIX )
        print("done")
        
        # glue movie name and year back together for output 
        year_str = self.movie_data.year.map( lambda x: " (" + str(int(x)) + ")" if not np.isnan(x) else "" )
        self.movie_data['movieTitle'] = self.movie_data.title + year_str


    # find movies whose titel contains a given search query        
    def find( self, search_query, max_results=100 ):
        return self.movie_data\
                   [self.movie_data.movieTitle.str.contains(search_query, case=False, regex=False)]\
                   .sort_values(by="year", ascending=False)\
                   .head(max_results)
        
    # provide recommendations for a given movie id
    def recommend( self, movie_id, k=10 ):
        # find actual index value of movie
        idx = np.where( self.movie_ids.movieId == movie_id )[0][0]
        
        # fetch movie title
        movie_title = self.movie_data.iloc[idx,:].movieTitle
        
        # predict similarities of all movies with this movie
        s = self.X.T.dot( self.X[:,idx] )
        
        # extract index values of recommended movies by finding k largest values of s
        # (omitting the similarity with the movie itself)
        recommended_idx = np.argsort( s )[::-1][1:k+1]
        
        # convert to movie ids
        recommended_movie_ids = self.movie_ids.movieId[recommended_idx]
        
        # put into a data frame and merge with movie data
        ibcf_rec = pd.DataFrame( {
            'movieId': recommended_movie_ids, 
            'similarity': np.round( s[recommended_idx], 4) 
        } )
        ibcf_rec = ibcf_rec.merge(self.movie_data, on="movieId")        
        
        return movie_title, ibcf_rec