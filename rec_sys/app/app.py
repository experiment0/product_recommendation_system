from recommender_factory import recommender_factory

recommend_items = recommender_factory.get_recommender_items(1222911)
print(recommend_items())
# -> [26477, 20017, 103127]