import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
import requests

def get_data(movie_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    }
    response = requests.get(movie_url, headers=headers)
    imdb = BeautifulSoup(response.text, 'html.parser')

    title_element = imdb.find('h1')
    title = title_element.text.strip() if title_element else 'Title not found'

    poster_element = imdb.find('img', class_='ipc-image')
    poster_url = poster_element['src'] if poster_element else 'Poster Not Found'

    genres = [genre.text for genre in imdb.select('.ipc-chip__text')]
    genres = [g for g in genres if g != 'Back to top']

    storyline = imdb.find('span', {'data-testid': 'plot-xs_to_m'})
    storyline = storyline.text if storyline else 'No storyline available.'

    rating_element = imdb.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
    total_ratings_element = imdb.find('div', class_='sc-d541859f-3 dwhNqC')
    
    rating = rating_element.text.strip() if rating_element else 'N/A'
    total_ratings = total_ratings_element.text.strip() if total_ratings_element else 'N/A'

    trailer_element = imdb.find('a', attrs={'data-testid': lambda x: x and 'video' in x})
    trailer_url = f"http://www.imdb.com{trailer_element['href']}" if trailer_element and trailer_element.has_attr('href') else None

    box_office_data = {}
    gross_domestic = imdb.find('li', {'data-testid': 'title-boxoffice-grossdomestic'})
    box_office_data['Gross US & Canada'] = gross_domestic.find('span', class_='ipc-metadata-list-item__list-content-item').text.strip() if gross_domestic else 'Data not available'

    opening_weekend = imdb.find('li', {'data-testid': 'title-boxoffice-openingweekenddomestic'})
    if opening_weekend:
        opening_weekend_value = opening_weekend.find_all('span', class_='ipc-metadata-list-item__list-content-item')[0].text.strip()
        opening_weekend_date = opening_weekend.find_all('span', class_='ipc-metadata-list-item__list-content-item')[1].text.strip()
        box_office_data['Opening Weekend US & Canada'] = f"{opening_weekend_value} on {opening_weekend_date}"
    else:
        box_office_data['Opening Weekend US & Canada'] = 'Data not available'

    gross_worldwide = imdb.find('li', {'data-testid': 'title-boxoffice-cumulativeworldwidegross'})
    box_office_data['Gross Worldwide'] = gross_worldwide.find('span', class_='ipc-metadata-list-item__list-content-item').text.strip() if gross_worldwide else 'Data not available'

    data = {
        'Title': title,
        'Poster Url': poster_url,
        'Genres': genres,
        'Storyline': storyline,
        'Rating': rating,
        'Total Ratings': total_ratings,
        **box_office_data
    }

    return data

st.title("IMDB Movie and Series Scraper")
user_input = st.text_input("Enter movie / web-series link")

if st.button("Get Data"):
    if user_input:
        if "imdb.com/title/" in user_input:
            movie_data = get_data(user_input)
            if movie_data:
                st.subheader(movie_data['Title'])
                st.image(movie_data['Poster Url'], width=300)
                st.write(f"**Genres:** {', '.join(movie_data['Genres'])}")
                st.write(f"**Storyline:** {movie_data['Storyline']}")
                st.write(f"**IMDb Rating:** {movie_data['Rating']} from {movie_data['Total Ratings']} ratings")
                st.write(f"**Gross US & Canada:** {movie_data['Gross US & Canada']}")
                st.write(f"**Opening Weekend US & Canada:** {movie_data['Opening Weekend US & Canada']}")
                st.write(f"**Gross Worldwide:** {movie_data['Gross Worldwide']}")
                
                if movie_data['Trailer']:
                    st.write("**Trailer:**")
                    st.markdown(f"[Click here to watch the trailer and video gallery]({movie_data['Trailer']})", unsafe_allow_html=True)
                else:
                    st.write("Trailer not available.")
            else:
                st.error("Failed to retrieve data, please check URL.")
