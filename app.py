from flask import Flask, jsonify, request
from flask_cors import CORS
import yahooquery as yq
import pandas as pd


app = Flask(__name__)
CORS(app)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_type = request.args.get('type')
    data = yq.search(query)
    if search_type == 'quotes':
        return jsonify(data.get('quotes', [])), 200
    elif search_type == 'news':
        return jsonify(data.get('news', [])), 200
    else:
        return jsonify(data), 200
    

@app.route('/trending', methods=['GET'])
def trending():
    country = request.args.get('country') or 'united states'
    data = yq.get_trending(country=country)
    return jsonify(data.get('quotes', [])), 200


@app.route('/market-summary', methods=['GET'])
def market_summary():
    country = request.args.get('country') or 'united states'
    data = yq.get_market_summary(country=country)
    return jsonify(data), 200


# https://yahooquery.dpguthrie.com/guide/screener/#available_screeners
@app.route('/screener', methods=['GET'])
def screener():
    screener_type = request.args.get('type')
    s = yq.Screener()
    data = s.get_screeners(screener_type)
    return jsonify(data[screener_type]), 200


if __name__ == '__main__':
    app.run(debug=True)