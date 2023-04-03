from .random import Random
from .recommender import Recommender
from typing import List
import random


class ContextualToppop(Recommender):
    def __init__(
            self, 
            tracks_redis, 
            catalog,
            history_redis,
            history,
            n_toppop: int = 100,
            tolerance: float = 0.8,
            ):
        
        self.tracks_redis = tracks_redis
        self.catalog = catalog
        self.history_redis = history_redis
        self.history = history
        self.tolerance = tolerance
        self.fallback = catalog.top_tracks_contextual[:n_toppop]
        self.second_fallback = Random(tracks_redis)

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        self.history.append(self.history_redis, user, prev_track)
        history_session = self.history.get(self.history_redis, user)

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            recommendations = list(self.fallback)
            filter_recommendations = self.filter(recommendations, history_session)
            if filter_recommendations:
                return self.shuffled(filter_recommendations)
            else:
                return self.second_fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if recommendations is None or prev_track_time <= self.tolerance:
            recommendations = list(self.fallback)
            filter_recommendations = self.filter(recommendations, history_session)
            if filter_recommendations:
                return self.shuffled(filter_recommendations)
            else:
                return self.second_fallback.recommend_next(user, prev_track, prev_track_time)

        filter_recommendations = self.filter(recommendations, history_session)
        if filter_recommendations:
            return self.shuffled(filter_recommendations) 
        else:
            recommendations = list(self.fallback)
            filter_recommendations = self.filter(recommendations, history_session)
            if filter_recommendations:
                return self.shuffled(filter_recommendations)
            else:
                return self.second_fallback.recommend_next(user, prev_track, prev_track_time)

    def shuffled(self, recommendations: List[int]) -> int:
        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]

    def filter(self, recommendations, history_session):
        return list(set(recommendations) - set(history_session))
