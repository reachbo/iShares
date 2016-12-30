#!/usr/bin/env python

import urllib
import json
import os
import csv

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
        result = urllib.urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res
    elif req.get("result").get("action") == "tellMeAbout":
        result = req.get("result")
        parameters = result.get("parameters")
        fund_name = parameters.get("Fund")
        if fund_name is None:
            return None
        res = tellMeAbout(fund_name)
        return res
    elif req.get("result").get("action") == "findStrategy":
        result = req.get("result")
        parameters = result.get("parameters")
        strategy = parameters.get("strategy")
        if strategy is None:
            return None
        res = findStrategy(strategy)
        return res


def findStrategy(strategy):
    with open('ProductScreener.csv', 'rbU') as f:
        reader = csv.reader(f)
        your_list = list(reader)
        #now split the strategy column into its own list & strip leading whitespaces
        #   so that later we can find if a strategy exists in that list for a fund
        for row in your_list:
            row[9] = row[9].split(",")
            row[9] = [strategy_string.lstrip() for strategy_string in row[9]]
    # Strategy is column 10 or index 9 in the list
    list_of_funds_in_this_strategy = [x for x in your_list if strategy in x[9]]
    list_of_included_asset_classes = []
    for fund in list_of_funds_in_this_strategy:
        if fund[8] not in list_of_included_asset_classes:
            list_of_included_asset_classes.append(fund[8])
    print list_of_included_asset_classes
    print isinstance(list_of_included_asset_classes[1],str)
    speech = "Actually, we have an entire strategy built around " + strategy + \
        ". There are " + str(len(list_of_funds_in_this_strategy)) + \
        " ETFs that implement this strategy covering everything from " + \
        list_of_included_asset_classes[0] + " to " + \
        list_of_included_asset_classes[1] + "."
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "bolu-iShares-webhook-mvp"
    }


def tellMeAbout(fund_name):
    with open('ProductScreener.csv', 'rbU') as f:
        reader = csv.reader(f)
        your_list = list(reader)
    for fund in your_list:
        if fund[1] == fund_name:
            speech = "The " + fund_name + " is a " + fund[7] + " " + fund[8] + \
                " ETF created on " + fund[6] + " with a trailing 5 year monthly return of " + \
                fund[38] + "% that costs " + fund[47] + "% annually."
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "bolu-iShares-webhook-mvp"
    }



def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')

def secYield(fund_name):
    for fund in your_list:
        if fund[1] == fund_name:
            print fund[42]

