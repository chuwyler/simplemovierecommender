from flask import Flask, Response, render_template, request

# import recommender functionality
from recommender import Recommender
rec = Recommender()

app = Flask(__name__)
app.secret_key = b'_5#y2G"H7G8z\n\xec]/' # obviously changed in production webapp..

@app.route('/', methods=['GET', 'POST'])
def serve():

    # fetch query and find movies
    q = request.form.get("q")    
    if q is not None:
        search_results = rec.find(q, max_results=100)
        search_results['url'] = '<a href="?movie_id=' + search_results.movieId.astype(str) + '">' + search_results.movieTitle + '</a>'
        search_results = search_results.to_html( columns=["url"], header=False, index=False, escape=False )
        search_results = "The following movies were found. Click on any of them to get recommendations.<br><br>" + search_results
    else:
        search_results = ""

    # fetch movie id and show recommendations
    movie_id = request.args.get("movie_id")
    if movie_id is not None:
        movie_title, recommender_results = rec.recommend( int(movie_id), k=20 )
        recommender_results.movieTitle = '<a target="_blank" href="' + recommender_results.imdb_url.fillna("") + '">' + recommender_results["movieTitle"] + '</a>'
        recommender_results["Cover"] = '<img src="' + recommender_results.cover_url.fillna("static/blank.png") + '" width=50>'
        recommender_results = recommender_results[["Cover", "movieTitle", "similarity", "genres"]]
        recommender_results.columns = ["Cover", "Title", "Similarity", "Genres"]
        recommender_results.Genres = recommender_results.Genres.str.replace("|", " | ", regex=False)
        recommender_results = "<h3>Top 20 recommendations for {}</h3>".format( movie_title ) + recommender_results.to_html( header=True, index=False, justify="left", escape=False )
    else:
        recommender_results = ""
        
    # pass everything to template    
    return render_template(
        'index.html', 
        q=q,
        search_results=search_results,
        recommender_results=recommender_results
    )

if __name__ == '__main__':
    app.run()

