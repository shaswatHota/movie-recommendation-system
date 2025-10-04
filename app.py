import streamlit as st
import pickle
import requests



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
    url = f"https://www.omdbapi.com/?t={movie_title}&apikey=8257f4e2"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data if data.get('Response') == 'True' else None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching details: {e}")
        return None

def recommend(movie):
    
    try:
        index = movies_df[movies_df['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_title = movies_df.iloc[i[0]].title
        details = fetch_details(movie_title) 
        if details and details.get('Poster') != 'N/A':
             recommended_movie_names.append(movie_title)
             recommended_movie_posters.append(details.get('Poster'))
    return recommended_movie_names, recommended_movie_posters



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
                st.markdown(f"**Rotten Tomatoes :** {movie_details.get('Ratings', 'N/A')[1].get('Value', 'N/A') if len(movie_details.get('Ratings', [])) > 1 else 'N/A'}")
                st.markdown(f"**Metacritic :** {movie_details.get('Ratings', 'N/A')[2].get('Value', 'N/A') if len(movie_details.get('Ratings', [])) > 1 else 'N/A'}")
                
            st.subheader("You May Also Like")
            with st.spinner('Please wait a moment...'):
                names, posters = recommend(st.session_state.final_movie)
                if names:
                    cols = st.columns(5)
                    for i in range(len(names)):
                        with cols[i]:
                            st.image(posters[i])
                            
                            st.button(
                                label=names[i],
                                key=f"rec_{names[i]}",
                                on_click=set_movie_from_recommendation,
                                args=(names[i],)
                            )
                else:
                    st.warning("Could not find recommendations for this movie.")
        else:
            st.error(f"Could not fetch details for '{st.session_state.final_movie}'.")
    else:
        st.error("This movie may not be in the database, or you may have spelled it wrong.")