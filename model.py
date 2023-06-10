import pandas as pd
import numpy as np
import string
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from data_base import DataBase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib


vectorizer = joblib.load('best1_vectorizer.joblib')
cos_sim = joblib.load('best_cos_sim.joblib')
matrix = joblib.load('matrix.joblib')

Anime = DataBase()
df = Anime.show_data()
anime_names = df['name']
indices = pd.Series(df.index, index = df['name']).drop_duplicates()

def recommendations_title(title, cosine_similarity=cos_sim):
    index = indices[title]
    similarity_scores = list(enumerate(cosine_similarity[index]))
    similarity_scores_sorted = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    recommendations_indices = []
    name_list = df[['name', 'link']].iloc[[t[0] for t in similarity_scores_sorted[1:]]]['name'].astype(str).tolist()
    for i, name in enumerate(name_list):
        score = fuzz.token_sort_ratio(title, name)
        if score <= 20:
            recommendations_indices.append(similarity_scores_sorted[i + 1][0])
            if len(recommendations_indices) == 5:
                break
    recommendations_df = df[['name', 'link']].iloc[recommendations_indices]
    recommendations_list = recommendations_df.apply(lambda row: (row['name'], row['link']), axis=1).tolist()
    return recommendations_list


def recommendations_by_description2(user_description, similarity_matrix=cos_sim):
    translator = str.maketrans('', '', string.punctuation)
    cleaned_description = user_description.lower().strip().translate(translator)
    user_vector = vectorizer.transform([cleaned_description])
    similarity_scores = cosine_similarity(user_vector, matrix).flatten()
    similarity_scores_sorted = sorted(enumerate(similarity_scores), key=lambda x: x[1], reverse=True)
    recommendations_indices = []
    recommended_anime_titles = []

    for i, (anime_index, similarity_score) in enumerate(similarity_scores_sorted):
        anime_name = df.iloc[anime_index]['name']
        anime_link = df.iloc[anime_index]['link']
        recommendations_indices.append(anime_index)
        recommended_anime_titles.append((anime_name, anime_link))
        if len(recommendations_indices) == 5:
            break

    return recommended_anime_titles


def find_anime(user_input, i):
    if i == 0:
        best_match = process.extractOne(user_input, anime_names)
        return best_match[0]
    else:
        suggestions = process.extract(user_input, anime_names, scorer=fuzz.token_set_ratio, limit = 5)
        return suggestions[i][0]

def get_description(name):
    row = df[df['name'] == name]
    anime_data = 'Назва: {} \nПосилання: {} \nРік виходу: {} \nЖанри: {}  \nОпис: {}'.format(
        row['name'].values[0], row['link'].values[0], row['year'].values[0],
        row['category'].values[0], row['description'].values[0])
    return anime_data
