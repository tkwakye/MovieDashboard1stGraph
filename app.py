import pandas as pd
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.express as px

#################################################################################
######################### CREATES CLEAN DATA SET ################################
#################################################################################

# load the movie ratings
ratings_url = "http://files.grouplens.org/datasets/movielens/ml-100k/u.data"
ratings_cols = ['user_id', 'movie_id', 'rating', 'timestamp']
df_ratings = pd.read_csv(ratings_url, sep='\t', names=ratings_cols)

# load the details of the movie
movies_url = "http://files.grouplens.org/datasets/movielens/ml-100k/u.item"
movies_cols = ['movie_id', 'title', 'release_date', 'video_release_date', 'imdb_url', 'unknown', 'Action', 'Adventure',
               'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
               'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
df_movies = pd.read_csv(movies_url, sep='|', encoding='latin-1', names=movies_cols, usecols=range(24))

# drop unnecessary columns from movies dataframe
df_movies.drop(['video_release_date', 'imdb_url'], axis=1, inplace=True)

df_movies['release_year'] = pd.to_datetime(df_movies['release_date']).dt.year

# count the number of movies released each year in different genres
genres = ['unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama',
          'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
movies_per_year_genre = df_movies.groupby('release_year')[genres].sum()

###################################################################################
####################### CREATES THE INTERACTIVE LINE CHART ########################
###################################################################################

# initialize Dash app
app = Dash(__name__)

# define external stylesheet
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']

# Apply external stylesheet to app
app = Dash(__name__, external_stylesheets=external_stylesheets)

# define app layout
app.layout = html.Div([
    html.H1("Number of Movies Released Each Year in Different Genres", className="mt-5 mb-4 text-center",
            style={'font-family': 'Arial', 'font-size': '30px', 'color': 'black'}),
    html.Div([
        html.Label("Select Genre(s):", className="font-weight-bold",
                   style={'font-family': 'Arial', 'font-size': '20px', 'color': 'black'}),
        dcc.Dropdown(
            id='genre-dropdown',
            options=[{'label': genre, 'value': genre} for genre in genres],
            value=['Action'],  # Default value is a list containing 'Action'
            multi=True,  # Allow multiple selection
            className="form-control"
        )
    ], className="container"),
    dcc.RangeSlider(
        id='year-slider',
        min=int(df_movies['release_year'].min()),
        max=int(df_movies['release_year'].max()),
        value=[int(df_movies['release_year'].min()), int(df_movies['release_year'].max())],
        marks={year: str(year) for year in
               range(int(df_movies['release_year'].min()), int(df_movies['release_year'].max()) + 1, 5)},
        step=1,
        className="container my-4",
    ),
    dcc.Graph(id='movies-line-chart', className="container")
])


@app.callback(
    Output('movies-line-chart', 'figure'),
    [Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_line_chart(selected_genres, selected_years):
    filtered_movies_per_year_genre = movies_per_year_genre.loc[selected_years[0]:selected_years[1]]

    fig = px.line(
        filtered_movies_per_year_genre.reset_index(),
        x='release_year',
        y=selected_genres,
        title="",
        labels={'release_year': 'Year', 'value': 'Number of Movies Released Per Year'}
    )

    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        plot_bgcolor='brown',
        font=dict(color='#424242'),
        xaxis=dict(title_font=dict(family='Arial', size=20, color='black')),
        yaxis=dict(title_font=dict(family='Arial', size=20, color='black')),
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
######################################################################################