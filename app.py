from flask import Flask, jsonify, request
from flask_cors import CORS
import yahooquery as yq
import finnhub as fh
import pandas as pd


app = Flask(__name__)
CORS(app)


# https://yahooquery.dpguthrie.com/guide/misc/#search
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    data = yq.search(query)
    quotes = data.get('quotes', [])
    filteredQuotes = list(filter(lambda result: result.get('exchange', '') in [
        'NYQ', 'NMS'] and result.get('quoteType', '') == 'EQUITY', quotes))
    formattedQuotes = list(map(lambda result: {
        'symbol': result.get('symbol', ''),
        'name': result.get('shortname', ''),
        'exchange': result.get('exchDisp', ''),
    }, filteredQuotes))
    return jsonify(formattedQuotes), 200


# https://yahooquery.dpguthrie.com/guide/misc/#get_trending
@app.route('/trending', methods=['GET'])
def trending():
    def get_price(ticker):
        data = yq.Ticker(ticker)
        price = data.price[ticker]
        return {
            'symbol': price.get('symbol', ''),
            'quoteType': price.get('quoteType', ''),
            'price': round(price.get('regularMarketPrice', 0), 2),
            'change': round(price.get('regularMarketChange', 0), 2),
            'changePercent': round(price.get('regularMarketChangePercent', 0) * 100, 2),
            'exchange': price.get('exchange', ''),
        }

    country = request.args.get('country') or 'united states'
    data = yq.get_trending(country=country)
    quotes = data.get('quotes', [])
    formattedQuotes = list(
        map(lambda result: get_price(result.get('symbol', '')), quotes))
    filteredQuotes = list(
        filter(lambda result: result.get('quoteType', '') == 'EQUITY' and result.get('exchange', '') in ['NYQ', 'NMS'], formattedQuotes))
    return jsonify(filteredQuotes), 200


# https://yahooquery.dpguthrie.com/guide/misc/#get_market_summary
@app.route('/market-summary', methods=['GET'])
def market_summary():
    country = request.args.get('country') or 'united states'
    data = yq.get_market_summary(country=country)
    formattedSummaries = list(map(lambda result: {
        'name': result.get('shortName', ''),
        'price': result.get('regularMarketPrice', {}).get('raw', 0),
        'change': round(result.get('regularMarketChange', {}).get('raw', 0), 2),
        'changePercent': round(result.get('regularMarketChangePercent', {}).get('raw', 0), 2)
    }, data))
    return jsonify(formattedSummaries), 200


# https://yahooquery.dpguthrie.com/guide/screener/#available_screeners
@app.route('/screener', methods=['GET'])
def screener():
    screener_type = request.args.get('type')
    s = yq.Screener()
    data = s.get_screeners(screener_type)
    return jsonify(data[screener_type]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/historical/#history
@app.route('/history', methods=['GET'])
def history():
    ticker = request.args.get('ticker')
    period = request.args.get('period')
    interval = request.args.get('interval')
    data = yq.Ticker(ticker)
    history_df = data.history(period=period, interval=interval)
    history_dict = history_df.to_dict(orient='records')
    return jsonify(history_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#price
@app.route('/price', methods=['GET'])
def price():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.price[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#news
@app.route('/news', methods=['GET'])
def news():
    ticker = request.args.get('ticker')
    count = request.args.get('count') or 10
    data = yq.Ticker(ticker)
    return jsonify(data.news(count)), 200


# https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#quotes
@app.route('/quotes', methods=['GET'])
def quotes():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.quotes), 200


# https://yahooquery.dpguthrie.com/guide/ticker/miscellaneous/#recommendations
@app.route('/recommendations', methods=['GET'])
def recommendations():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.recommendations), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#summary_detail
@app.route('/summary-detail', methods=['GET'])
def summary_detail():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.summary_detail[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#asset_profile
@app.route('/profile', methods=['GET'])
def profile():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.asset_profile[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#financial_data
@app.route('/financial-data', methods=['GET'])
def financial_data():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.financial_data[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#key_stats
@app.route('/key-stats', methods=['GET'])
def key_stats():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.key_stats[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#esg_scores
@app.route('/esg', methods=['GET'])
def esg():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.esg_scores[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/financials/#balance_sheet
@app.route('/balance-sheet', methods=['GET'])
def balance_sheet():
    ticker = request.args.get('ticker')
    period = request.args.get('period')
    data = yq.Ticker(ticker)
    balance_sheet_df = data.balance_sheet(frequency=period)
    balance_sheet_dict = balance_sheet_df.to_dict(orient='records')
    return jsonify(balance_sheet_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/financials/#cash_flow
@app.route('/cash-flow', methods=['GET'])
def cash_flow():
    ticker = request.args.get('ticker')
    period = request.args.get('period')
    data = yq.Ticker(ticker)
    cash_flow_df = data.cash_flow(frequency=period)
    cash_flow_dict = cash_flow_df.to_dict(orient='records')
    return jsonify(cash_flow_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/financials/#income_statement
@app.route('/income-statement', methods=['GET'])
def income_statement():
    ticker = request.args.get('ticker')
    period = request.args.get('period')
    data = yq.Ticker(ticker)
    income_statement_df = data.income_statement(frequency=period)
    income_statement_dict = income_statement_df.to_dict(orient='records')
    return jsonify(income_statement_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/financials/#valuation_measures
@app.route('/valuation-measures', methods=['GET'])
def valuation_measures():
    ticker = request.args.get('ticker')
    period = request.args.get('period')
    data = yq.Ticker(ticker)
    valuation_measures_df = data.valuation_measures(frequency=period)
    valuation_measures_dict = valuation_measures_df.to_dict(orient='records')
    return jsonify(valuation_measures_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/options/#option_chain
@app.route('/option-chain', methods=['GET'])
def option_chain():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    option_chain_df = data.option_chain
    option_chain_dict = option_chain_df.to_dict(orient='records')
    return jsonify(option_chain_dict), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_performance
@app.route('/fund-performance', methods=['GET'])
def fund_performance():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.fund_performance[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_profile
@app.route('/fund-profile', methods=['GET'])
def fund_profile():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.fund_profile[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings
@app.route('/fund-sector-weightings', methods=['GET'])
def fund_sector_weightings():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.fund_sector_weightings[ticker]), 200


# https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings
@app.route('/fund-top-holdings', methods=['GET'])
def fund_top_holdings():
    ticker = request.args.get('ticker')
    data = yq.Ticker(ticker)
    return jsonify(data.fund_top_holdings[ticker]), 200


if __name__ == '__main__':
    app.run(debug=True)
