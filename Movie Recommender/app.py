import pandas as pd
import streamlit as st
import pickle
import requests

# Fetch movie poster
def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=ba5ea588d0b4229427fbed49d7887a63&language=en-US')
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']

# Fetch actor/director image
def fetch_person_image(person_id):
    response = requests.get(f'https://api.themoviedb.org/3/person/{person_id}?api_key=ba5ea588d0b4229427fbed49d7887a63&language=en-US')
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['profile_path']

# Fetch movie details
def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=ba5ea588d0b4229427fbed49d7887a63&language=en-US')
    data = response.json()
    return {
        'release_date': data.get('release_date', 'N/A'),
        'genres': [genre['name'] for genre in data.get('genres', [])],
        'rating': data.get('vote_average', 'N/A')
    }

# Recommend movies by keywords
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []
    for i in movies_list:
        recommended_movies.append(movies.iloc[i[0]].title)
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_details.append(fetch_movie_details(movie_id))

    return recommended_movies, recommended_movies_posters, recommended_movies_details

# Recommend movies by actor or director
def recommend_by_actor1(movie, top_n=5):
    try:
        actor1 = teams[teams['title'] == movie]['actors'].values[0][0]
        actor1_id = teams[teams['title'] == movie]['actor_ids'].values[0][0]
        actor1_movies = teams[teams['actors'].apply(lambda x: actor1 in x)]['title'].tolist()
        actor1_movies.remove(movie)
        return actor1, actor1_id, actor1_movies[:top_n]
    except (IndexError, ValueError):
        return None, None, []

def recommend_by_actor2(movie, top_n=5):
    try:
        actor2 = teams[teams['title'] == movie]['actors'].values[0][1]
        actor2_id = teams[teams['title'] == movie]['actor_ids'].values[0][1]
        actor2_movies = teams[teams['actors'].apply(lambda x: actor2 in x)]['title'].tolist()
        actor2_movies.remove(movie)
        return actor2, actor2_id, actor2_movies[:top_n]
    except (IndexError, ValueError):
        return None, None, []

def recommend_by_director(movie, top_n=5):
    try:
        director = teams[teams['title'] == movie]['directors'].values[0][0]
        director_id = teams[teams['title'] == movie]['directors_ids'].values[0][0]
        director_movies = teams[teams['directors'].apply(lambda x: director in x)]['title'].tolist()
        director_movies.remove(movie)
        return director, director_id, director_movies[:top_n]
    except (IndexError, ValueError):
        return None, None, []

# Display movies with person image and posters
def display_movies(movies_list, person_name, person_id, flag):
    st.write(f"### Also {('starring' if flag == 'actor' else 'made by')} {person_name}:")

    # Create columns for person image and movie posters
    cols = st.columns(len(movies_list) + 1)  # +1 for the person's image

    # Display person's image in the first column
    with cols[0]:
        st.image(fetch_person_image(person_id), width=150)

    # Display movie posters in the remaining columns
    for i, movie in enumerate(movies_list):
        with cols[i + 1]:  # Start from the second column
            # Fetch poster for each movie in the list
            poster_url = fetch_poster(teams[teams['title'] == movie]['movie_id'].values[0])
            st.image(poster_url, width=150)


# Add custom CSS for the background image
def set_background_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://www.baltana.com/files/wallpapers-34/Hollywood-Sign-Los-Angeles-California-Desktop-Wallpaper-120639.jpg");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Importing files
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))
teams = pickle.load(open('teams.pkl', 'rb'))

# Streamlit app
st.set_page_config(page_title="Movie Recommender")
set_background_image()
st.title('🎬 Movie Recommender System')
st.markdown("### Find your next favorite movie!")
st.markdown("---")  # Divider

selected_movie_title = st.selectbox(
    "Select your movie",
    movies['title'].values
)

if st.button("Recommend"):
    # Content-based recommendations
    names, posters, details = recommend(selected_movie_title)

    st.header("Movies you might like:")
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.text(names[i])
            # st.write(f"**Release Date:** {details[i]['release_date']}")
            # st.write(f"**Genres:** {', '.join(details[i]['genres'])}")
            # st.write(f"**Rating:** {details[i]['rating']}")

    # Actor and director-based recommendations
    actor1, actor1_id, actor1_movies = recommend_by_actor1(selected_movie_title)
    actor2, actor2_id, actor2_movies = recommend_by_actor2(selected_movie_title)
    director, director_id, director_movies = recommend_by_director(selected_movie_title)

    if actor1_movies:
        display_movies(actor1_movies, actor1, actor1_id, 'actor')

    if actor2_movies:
        display_movies(actor2_movies, actor2, actor2_id, 'actor')

    if director_movies:
        display_movies(director_movies, director, director_id, 'director')

# Footer
st.markdown("---")  # Divider
st.markdown("###### Made by [Akhilesh](https://github.com/akhilk27)")