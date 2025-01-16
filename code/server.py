from flask import Flask, jsonify
from flask_cors import CORS
import http

from scraping.bloomberg_com import bloomberg_com
from scraping.actionforex_com import actionforex_com
from scraping.investing_com import investing_com
from api.oanda_api import OandaApi
from api.web_options import get_options

app = Flask(__name__)
CORS(app)

def get_pair(pair_name, tf):

    data1 = actionforex_com(pair_name, tf)
    data2 = investing_com(pair_name)
    
    return {**data1, **data2}

def get_response_data(data):
    if data is None:
        return jsonify(dict(message='error getting data')), http.HTTPStatus.NOT_FOUND
    else:
        return jsonify(data)

@app.route("/api/test")
def test():
    return jsonify(dict(message='hello'))

@app.route("/api/account")
def account():
    return get_response_data(OandaApi().get_account_summary())

@app.route("/api/options")
def options():
    return get_response_data(get_options())

@app.route("/api/headlines")
def headlines():
    return get_response_data(bloomberg_com())

@app.route("/api/technicals/<pair>/<tf>")
def technicals(pair, tf):
    return get_response_data(get_pair(pair, tf))

@app.route("/api/prices/<pair>/<granularity>/<count>")
def prices(pair, granularity, count):
    return get_response_data(OandaApi().web_api_candles(pair, granularity, count))


if __name__ == "__main__":
    app.run(debug=True)