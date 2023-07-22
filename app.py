from flask import Flask, jsonify, request
from flask_cors import CORS
import yahooquery as yq
import yfinance as yf
import finnhub
import pandas as pd


app = Flask(__name__)
CORS(app)


def check_exchange_and_quote_type(result):
    if type(result) == str:
        return False
    return result.get('exchange', '') in ('NYQ', 'NMS') and result.get('quoteType', '') == 'EQUITY'


def filter_exchange_and_quote_type(results):
    return list(filter(lambda result: check_exchange_and_quote_type(result), results))


# https://yahooquery.dpguthrie.com/guide/misc/#search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    data = yq.search(query)
    quotes = data.get('quotes', [])
    filteredQuotes = filter_exchange_and_quote_type(quotes)
    return jsonify(filteredQuotes), 200


# https://yahooquery.dpguthrie.com/guide/misc/#get_trending
@app.route('/trending', methods=['GET'])
def trending():
    country = request.args.get('country')
    data = yq.get_trending(country or 'united states')
    quotes = data.get('quotes', [])
    symbols = list(map(lambda result: result.get('symbol', ''), quotes))
    tickers = yq.Ticker(symbols)
    trending = tickers.price
    for value in trending.values():
        if value == 'Invalid Cookie':
            return jsonify([]), 200
    filteredTrending = filter_exchange_and_quote_type(trending.values())
    return jsonify(filteredTrending), 200


# https://yahooquery.dpguthrie.com/guide/misc/#get_market_summary
@app.route('/market-summary', methods=['GET'])
def market_summary():
    country = request.args.get('country')
    data = yq.get_market_summary(country or 'united states')
    return jsonify(data), 200


# https://finnhub.io/docs/api/market-news
@app.route('/market-news', methods=['GET'])
def market_news():
    finnhub_client = finnhub.Client(
        api_key="ch56jm9r01quc2n554i0ch56jm9r01quc2n554ig")
    news = finnhub_client.general_news('general', min_id=0)
    filteredNews = list(
        filter(lambda article: article.get('image', ''), news))[:20]
    return jsonify(filteredNews), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#price
@app.route('/price', methods=['GET'])
def price():
    symbol = request.args.get('symbol')
    symbols = request.args.get('symbols')
    if symbol:
        data = yq.Ticker(symbol)
        price = data.price.get(symbol, None)
        if not check_exchange_and_quote_type(price):
            return jsonify({}), 404
        return jsonify(price), 200
    else:
        symbolsArray = symbols.split(',')
        data = yq.Ticker(symbolsArray)
        prices = data.price
        filteredPrices = filter_exchange_and_quote_type(prices.values())
        return jsonify(filteredPrices), 200


# https://yahooquery.dpguthrie.com/guide/screener/#get_screeners
@app.route('/screener', methods=['GET'])
def screener():
    screener_type = request.args.get('type')
    s = yq.Screener()
    data = s.get_screeners([screener_type])
    quotes = data.get(screener_type, {}).get('quotes', [])
    filteredQuotes = filter_exchange_and_quote_type(quotes)
    return jsonify(filteredQuotes), 200


# https://yahooquery.dpguthrie.com/guide/screener/#available_screeners
@app.route('/available-screeners', methods=['GET'])
def available_screeners():
    s = yq.Screener()
    return jsonify(s.available_screeners), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#summary_detail
# https://yahooquery.dpguthrie.com/guide/ticker/modules/#key_stats
@app.route('/summary', methods=['GET'])
def summary_detail():
    symbol = request.args.get('symbol')
    data = yq.Ticker(symbol)
    summary = data.summary_detail[symbol]
    summary.update(data.key_stats[symbol])
    return jsonify(summary), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#asset_profile
@app.route('/profile', methods=['GET'])
def profile():
    symbol = request.args.get('symbol')
    data = yq.Ticker(symbol)
    return jsonify(data.asset_profile[symbol]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#news
@app.route('/news', methods=['GET'])
def news():
    symbol = request.args.get('symbol')
    data = yf.Ticker(symbol)
    return jsonify(data.news), 200


# https://yahooquery.dpguthrie.com/guide/ticker/historical/#history
@app.route('/history', methods=['GET'])
def history():
    symbol = request.args.get('symbol')
    period = request.args.get('period')
    interval = request.args.get('interval')
    data = yf.Ticker(symbol)
    history_df = data.history(period=period, interval=interval)
    history_df.reset_index(inplace=True)
    history_dict = history_df.to_dict(orient='records')
    return jsonify(history_dict), 200

# # https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#quotes
# @app.route('/quotes', methods=['GET'])
# def quotes():
#     ticker = request.args.get('ticker')
#     data = yq.Ticker(ticker)
#     return jsonify(data.quotes), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#recommendations
# @app.route('/recommendations', methods=['GET'])
# def recommendations():
#     ticker = request.args.get('ticker')
#     data = yq.Ticker(ticker)
#     return jsonify(data.recommendations), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/modules/#financial_data
# @app.route('/financial-data', methods=['GET'])
# def financial_data():
#     ticker = request.args.get('ticker')
#     data = yq.Ticker(ticker)
#     return jsonify(data.financial_data[ticker]), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/modules/#esg_scores
# @app.route('/esg', methods=['GET'])
# def esg():
#     ticker = request.args.get('ticker')
#     data = yq.Ticker(ticker)
#     return jsonify(data.esg_scores[ticker]), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/financials/#balance_sheet
# @app.route('/balance-sheet', methods=['GET'])
# def balance_sheet():
#     ticker = request.args.get('ticker')
#     period = request.args.get('period')
#     data = yq.Ticker(ticker)
#     balance_sheet_df = data.balance_sheet(frequency=period)
#     balance_sheet_dict = balance_sheet_df.to_dict(orient='records')
#     return jsonify(balance_sheet_dict), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/financials/#cash_flow
# @app.route('/cash-flow', methods=['GET'])
# def cash_flow():
#     ticker = request.args.get('ticker')
#     period = request.args.get('period')
#     data = yq.Ticker(ticker)
#     cash_flow_df = data.cash_flow(frequency=period)
#     cash_flow_dict = cash_flow_df.to_dict(orient='records')
#     return jsonify(cash_flow_dict), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/financials/#income_statement
# @app.route('/income-statement', methods=['GET'])
# def income_statement():
#     ticker = request.args.get('ticker')
#     period = request.args.get('period')
#     data = yq.Ticker(ticker)
#     income_statement_df = data.income_statement(frequency=period)
#     income_statement_dict = income_statement_df.to_dict(orient='records')
#     return jsonify(income_statement_dict), 200


# # https://yahooquery.dpguthrie.com/guide/ticker/options/#option_chain
# @app.route('/option-chain', methods=['GET'])
# def option_chain():
#     ticker = request.args.get('ticker')
#     data = yq.Ticker(ticker)
#     option_chain_df = data.option_chain
#     option_chain_dict = option_chain_df.to_dict(orient='records')
#     return jsonify(option_chain_dict), 200

if __name__ == '__main__':
    app.run(debug=True)
