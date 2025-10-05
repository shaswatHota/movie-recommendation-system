import streamlit as st
import pickle
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv('OMDB_API_KEY')


STANDBY_POSTER = "https://c.tenor.com/NM05_o_jGqAAAAAd/tenor.gif"

if 'final_movie' not in st.session_state:
    st.session_state.final_movie = None

try:
    movies_df = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
    movie_list = movies_df['title'].values
except FileNotFoundError:
    st.error("Model files not found. Please make sure 'movie_list.pkl' and 'similarity.pkl' are in the 'artifacts' directory.")
    st.stop()


def fetch_details(movie_title):
    url = f"https://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data if data.get('Response') == 'True' else None
    except requests.exceptions.RequestException as e:
        return None


def get_recommended_titles(movie):
    """Get only the recommended movie titles (fast, no API calls)"""
    try:
        index = movies_df[movies_df['title'] == movie].index[0]
    except IndexError:
        return []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_titles = []
    
    
    for i in distances[1:6]:
        movie_title = movies_df.iloc[i[0]].title
        recommended_titles.append(movie_title)
    
    return recommended_titles


def set_movie_from_recommendation(movie_title):
    st.session_state.final_movie = movie_title
    st.session_state.search_bar = ""
    st.session_state.select_box = None


def set_movie_from_inputs():
    if st.session_state.search_bar:
        st.session_state.final_movie = st.session_state.search_bar
    elif st.session_state.select_box:
        st.session_state.final_movie = st.session_state.select_box


# ui start
st.title("Movie Recommendation System")

col1, col2 = st.columns([3, 1])
with col1:
    st.text_input(
        "Search for a movie:",
        key="search_bar",
        on_change=set_movie_from_inputs
    )
with col2:
    st.selectbox(
        'Or browse the database:',
        [''] + list(movie_list),
        key="select_box",
        on_change=set_movie_from_inputs
    )


if st.session_state.final_movie:
    if st.session_state.final_movie in movie_list:
        st.subheader("Your Searched Result")

        movie_details = fetch_details(st.session_state.final_movie)

        if movie_details:
            col1_details, col2_details = st.columns([1, 2])
            with col1_details:
                poster_url = movie_details.get('Poster')
                if poster_url and poster_url != 'N/A':
                    st.image(poster_url, caption=st.session_state.final_movie)
                else:
                    st.write("No Poster Available")
            with col2_details:
                st.markdown(f"**Plot:** {movie_details.get('Plot', 'N/A')}")
                st.markdown(f"**Genre:** {movie_details.get('Genre', 'N/A')}")
                st.markdown(f"**Director:** {movie_details.get('Director', 'N/A')}")
                st.markdown(f"**Cast:** {movie_details.get('Actors', 'N/A')}")
                st.markdown(f"**Country:** {movie_details.get('Country', 'N/A')}")
                st.markdown(f"**Rotten Tomatoes:** {movie_details.get('Ratings', 'N/A')[1].get('Value', 'N/A') if len(movie_details.get('Ratings', [])) > 1 else 'N/A'}")
                st.markdown(f"**Metacritic:** {movie_details.get('Ratings', 'N/A')[2].get('Value', 'N/A') if len(movie_details.get('Ratings', [])) > 1 else 'N/A'}")
            
            st.subheader("You May Also Like")
            
            
            recommended_titles = get_recommended_titles(st.session_state.final_movie)
            
            if recommended_titles:
                
                cols = st.columns(5)
                
                
                poster_placeholders = []
                for idx, movie_title in enumerate(recommended_titles):
                    with cols[idx]:
                        
                        poster_placeholder = st.empty()
                        poster_placeholders.append(poster_placeholder)
                        
                        
                        poster_placeholder.image(STANDBY_POSTER, use_container_width=True)
                        
                        
                        st.button(
                            label=movie_title,
                            key=f"rec_{movie_title}",
                            on_click=set_movie_from_recommendation,
                            args=(movie_title,)
                        )
                
                
                for idx, movie_title in enumerate(recommended_titles):
                    details = fetch_details(movie_title)
                    
                    
                    if details and details.get('Poster') != 'N/A':
                        poster_placeholders[idx].image(details.get('Poster'), use_container_width=True)
                    else:
                        
                        poster_placeholders[idx].image(STANDBY_POSTER, use_container_width=True)
                
            else:
                st.warning("Could not find recommendations for this movie.")
        else:
            st.error(f"Could not fetch details for '{st.session_state.final_movie}'.")
    else:
        st.error("This movie may not be in the database, or you may have spelled it wrong.")