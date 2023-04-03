import json
import logging
import time
from dataclasses import asdict
from datetime import datetime

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort, reqparse
from gevent.pywsgi import WSGIServer

from botify.data import DataLogger, Datum
from botify.experiment import Experiments, Treatment
from botify.recommenders.contextual_toppop import ContextualToppop
from botify.recommenders.contextual import Contextual
from botify.recommenders.indexed import Indexed
from botify.recommenders.toppop import TopPop
from botify.recommenders.sticky_artist import StickyArtist
from botify.recommenders.random import Random
from botify.track import Catalog, HistoryUsers

import numpy as np

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)

tracks_redis = Redis(app, config_prefix="REDIS_TRACKS")
artists_redis = Redis(app, config_prefix="REDIS_ARTIST")
recommendations_redis = Redis(app, config_prefix="REDIS_RECOMMENDATIONS")
history_redis = Redis(app, config_prefix="REDIS_HISTORY")

data_logger = DataLogger(app)

history = HistoryUsers(app)
catalog = Catalog(app).load(
    app.config["TRACKS_CATALOG"], 
    app.config["TOP_TRACKS_CATALOG"],
    app.config["TOP_TRACKS_CONTEXTUAL"],
    app.config["TOP_TRACKS_INDEXED"],
    app.config["TOP_TRACKS_TOP_POP"],
    app.config["TOP_TRACKS_STICKY_ARTIST"],
    app.config["TOP_TRACKS_RANDOM"]
)
catalog.upload_tracks(tracks_redis.connection)
catalog.upload_artists(artists_redis.connection)
catalog.upload_recommendations(recommendations_redis.connection)

parser = reqparse.RequestParser()
parser.add_argument("track", type=int, location="json", required=True)
parser.add_argument("time", type=float, location="json", required=True)


class Hello(Resource):
    def get(self):
        return {
            "status": "alive",
            "message": "welcome to botify, the best toy music recommender",
        }


class Track(Resource):
    def get(self, track: int):
        data = tracks_redis.connection.get(track)
        if data is not None:
            return asdict(catalog.from_bytes(data))
        else:
            abort(404, description="Track not found")


class NextTrack(Resource):
    def post(self, user: int):
        start = time.time()

        args = parser.parse_args()

        # TODO Seminar 5 step 3: Wire CONTEXTUAL A/B experiment
        experiment = Experiments.CONTEXTUAL_TOPPOP
        treatment = experiment.assign(user)
        recommender = StrategyExperiment().get_strategy_experiment(experiment.name, treatment)
        recommendation = recommender.recommend_next(user, args.track, args.time)

        data_logger.log(
            "next",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.track,
                args.time,
                time.time() - start,
                recommendation,
            ),
        )
        return {"user": user, "track": recommendation}


class StrategyExperiment:
    def get_strategy_experiment(self, name: str, treatment: Treatment):
        if name == "CONTEXTUAL":
            # T1 Contextual
            # C Contextual
            if treatment == Treatment.T1:
                return Contextual(tracks_redis.connection, catalog)
            else:
                return Contextual(tracks_redis.connection, catalog)

        elif name == "ALL_RECOMMENDERS":
            # T1 Contextual
            # T2 Indexed
            # T3 TopPop
            # T4 StickyArtist
            # C Random
            if treatment == Treatment.T1:
                return  Contextual(tracks_redis.connection, catalog)
            elif treatment == Treatment.T2:
                return Indexed(tracks_redis.connection, recommendations_redis.connection, catalog)
            elif treatment == Treatment.T3:
                return TopPop(recommendations_redis.connection, catalog.top_tracks[:100])
            elif treatment == Treatment.T4:
                return StickyArtist(tracks_redis.connection, artists_redis.connection, catalog)
            else:
                return Random(tracks_redis.connection)

        elif name == "TOP_TRACKS_RECOMMENDERS":
            # T1 Top tracks on Contextual 
            # T2 Top tracks on Indexed 
            # T3 Top tracks on TopPop 
            # T4 Top tracks on StickyArtist 
            # T5 Top tracks on Random 
            # C Random
            if treatment == Treatment.T1:
                return TopPop(recommendations_redis.connection, catalog.top_tracks_contextual[:100])
            elif treatment == Treatment.T2:
                return TopPop(recommendations_redis.connection, catalog.top_tracks_indexed[:100])
            elif treatment == Treatment.T3:
                return TopPop(recommendations_redis.connection, catalog.top_tracks_top_pop[:100])
            elif treatment == Treatment.T4:
                return TopPop(recommendations_redis.connection, catalog.top_tracks_sticky_artist[:100])
            elif treatment == Treatment.T5:
                return TopPop(recommendations_redis.connection, catalog.top_tracks_random[:100])
            else:
                return Random(tracks_redis.connection)

        elif name == "CONTEXTUAL_TOPPOP":
            # T1 New recommender (Contextual + TopPop)
            # C Contextual | Random
            if treatment == Treatment.T1:
                return ContextualToppop(
                    tracks_redis.connection,
                    catalog,
                    history_redis.connection,
                    history
                    )
            else:
                return Contextual(tracks_redis.connection, catalog) # Random(tracks_redis.connection)


class LastTrack(Resource):
    def post(self, user: int):
        start = time.time()
        args = parser.parse_args()
        data_logger.log(
            "last",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.track,
                args.time,
                time.time() - start,
            ),
        )
        history.clear(history_redis.connection, user)
        return {"user": user}


api.add_resource(Hello, "/")
api.add_resource(Track, "/track/<int:track>")
api.add_resource(NextTrack, "/next/<int:user>")
api.add_resource(LastTrack, "/last/<int:user>")


if __name__ == "__main__":
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
