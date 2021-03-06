# Libraries
import pandas as pd
from collections import OrderedDict
from Recommendation import AnimeRecommendation
from flask import make_response, jsonify
from model import Ratings

# Load the Dataset
dataframe = pd.read_csv('data/cleaned_anime_data.csv')
dataframe = dataframe.reset_index()
dataframe = dataframe.drop('index', axis = 1)

# Initialize the Class
anime = AnimeRecommendation(dataframe)

# Get the Mappings
indices = anime.getMapping()

# Get Similarity Matrix
simMatrix = anime.getSimilartiyMatrix()

# Create a Ratings
ratings = Ratings()

def homePage():
	'''
		:return:

	'''

	homepage_animes = OrderedDict([('animes', list())])

	try:
		anime_idxs = anime.getAnimeSample()

		for idx in anime_idxs:
			homepage_animes['animes'].append(anime.build_AnimeDict(idx))

		return homepage_animes
	except Exception as e:
		return make_response(jsonify({'Success': False}), 404)


def returnRecommended(anime_name):
	'''
		Parameters:
			anime_name: Name of the Anime to get Recommendation.

		:return:
			JSON Formatted response of recommended anime.
	'''

	recommended_animes = OrderedDict()

	recommended_animes['input'] = list()
	recommended_animes['output'] = OrderedDict()
	recommended_animes['output']['animes'] = list()

	anime_name = anime_name.lower()

	anime_Idx = anime.getID(anime_name)#dataframe[dataframe.Title.str.lower().str.contains(anime_name)]['Anime_ID'].values

	try:
		if len(anime_Idx) > 1:
			for idx in anime_Idx:
				recommended_animes['output']['animes'].append(anime.build_AnimeDict(idx))

		else:
			# Get Anime ID
			anime_id = anime.getID(anime_name)[0]
			recommended_animes['input'].append(anime.build_AnimeDict(anime_id))

			g = anime.getRecommendation(anime_id, simMatrix, indices)

			for idx in g:
				recommended_animes['output']['animes'].append(anime.build_AnimeDict(idx))

		return recommended_animes
	except Exception as e:
		return make_response(jsonify({'Success': False}), 404)

def readGenre(genre):
	'''
		Parameters:
			genre: One of the Genres.

		:return:
			JSON Formatted reponse with animes.
	'''
	animes_by_genre = OrderedDict([
		('output', OrderedDict([
			('animes', list())
		]))
	])
	genre = genre.lower()

	try:
		anime_idxs = anime.getAnime_byGenre(genre)

		for idx in anime_idxs:
			animes_by_genre['output']['animes'].append(anime.build_AnimeDict(idx))

		return animes_by_genre
	except Exception as e:
		return make_response(jsonify({'Success': False}), 404)

def createRatings(anime_ratings):
	'''
		Create Ratings for the given Anime and recommended Anime.
			- 1: Both are Similar
			- 0: Not Similar

		Parameters:
			anime_ratings: JSON Formatted Data with
							- Name of the given Anime
							- Name of the recommended Anime
							- Rating (1 or 0).

		:return:
			201 Succes or 400 Error
	'''

	main_anime = anime_ratings.get('main_anime_name', None)
	recomm_anime = anime_ratings.get('recomm_anime_name', None)
	rating = anime_ratings.get('rating', None)

	try:
		# Get the ID
		idx_1 = anime.getID(main_anime.lower())[0]
		idx_2 = anime.getID(recomm_anime.lower())[0]

		counts = ratings.addRating(rating_data = (idx_1, idx_2, rating))

		if counts == 10:
			ratings.saveRating()
			ratings.__reset__()

		return 201
	except Exception as e:
		return make_response(jsonify({'Success': False}), 400)
