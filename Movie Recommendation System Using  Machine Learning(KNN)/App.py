import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests, io
import PIL.Image
from urllib.request import urlopen

with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
hdr = {'User-Agent': 'Mozilla/5.0'}


# def movie_poster_fetcher(imdb_link):
#     ## Display Movie Poster
#     url_data = requests.get(imdb_link, headers=hdr).text
#     s_data = BeautifulSoup(url_data, 'html.parser')
    
#     # Find meta tag with property="og:image"
#     imdb_dp = s_data.find("meta", property="og:image")
    
#     if imdb_dp is None:
#         # Handle case where poster link is not found
#         st.warning("Movie poster not found.")
#         return
    
#     # Extract the content attribute from the meta tag
#     movie_poster_link = imdb_dp.get('content')
    
#     if not movie_poster_link:
#         # Handle case where poster link is empty or not valid
#         st.warning("Movie poster link is invalid.")
#         return
    
#     try:
#         # Open the URL of the movie poster
#         u = urlopen(movie_poster_link)
#         raw_data = u.read()
        
#         # Open the image using PIL and resize
#         image = PIL.Image.open(io.BytesIO(raw_data))
#         image = image.resize((158, 301))  # Adjust the desired size
        
#         # Display the image in the Streamlit app
#         st.image(image, use_column_width=False)
        
#     except Exception as e:
#         # Handle any exceptions that may occur during image retrieval or processing
#         st.error(f"Error fetching movie poster: {str(e)}")



def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    
    # Check if meta tag with property "og:description" exists
    imdb_content = s_data.find("meta", property="og:description")
    if imdb_content is None:
        return "Director not available", "Cast not available", "Story not available", "Rating not available"

    movie_descr = imdb_content.attrs['content']
    movie_descr = str(movie_descr).split('.')
    
    # Handle possible IndexError if content split does not produce expected results
    movie_director = movie_descr[0] if len(movie_descr) > 0 else "Director not available"
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip() if len(movie_descr) > 1 else "Cast not available"
    movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.' if len(movie_descr) > 2 else "Story not available"

    # Extract rating
    rating_element = s_data.find("span", class_="sc-bde20123-1 iZlgcd")
    movie_rating = 'Total Rating count: ' + str(rating_element.text) if rating_element else "Rating not available"

    return movie_director, movie_cast, movie_story, movie_rating


def set_background():
    # Define the path to your background image
    page_bg_img = '''
        <style>
            body {
                background-image: url("https://t4.ftcdn.net/jpg/00/92/82/47/360_F_92824780_60mM0MW8H3bdTfyPHaaavjyXtqDa1Asx.jpg");
                background-size: cover;
            }
        </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def KNN_Movie_Recommender(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Print list of 10 recommendations < Change value of k for a different number >
    table = []
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2], data[i][-1]])
    print(table)
    return table


st.set_page_config(
    page_title="Movie Recommendation System Using Machine Learning(KNN)",
)


def run():
    set_background()
    img1 = Image.open('./meta/logo.jpg')
    img1 = img1.resize((700, 300), )
    st.image(img1, use_column_width=False)
    st.title("Movie Recommendation System Using Machine Learning ")
    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Data is based "IMDB 5000 Movie Dataset"</h4>''',
                unsafe_allow_html=True)
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']
    cat_op = st.selectbox('Select Recommendation Type', category)
    if cat_op == category[0]:
        st.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Select movie: (Recommendation will be based on this selection)',
                                    ['--Select--'] + movies)
        # dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        dec = "no"
        # st.markdown(
        #     '''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Posters will take a time."</h4>''',
        #     unsafe_allow_html=True)
        if dec == 'No':
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=10, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(f"({c})[ {movie}]({link})")
                    st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if select_movie == '--Select--':
                st.warning('Please select Movie!!')
            else:
                no_of_reco = st.slider('Number of movies you want Recommended:', min_value=5, max_value=10, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    # movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        # dec = st.radio("Want to Fetch Movie Poster?", ('Yes', 'No'))
        dec = "no"
        # st.markdown(
        #     '''<h4 style='text-align: left; color: #d73b5c;'>* Fetching a Movie Posters will take a time."</h4>''',
        #     unsafe_allow_html=True)
        if dec == 'No':
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=10, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if sel_gen:
                imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('Some of the movies from our Recommendation, have a look below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    # movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    # st.markdown(cast)
                    # st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')


run()
