from chalice import Chalice, Response
import json, datetime, requests, math, jinja2, os
from chalicelib import config, functions

app = Chalice(app_name='blaxmythbot') #initialize chalice app
app.debug = True

response = {} #initialize dictionary for response data

@app.route('/') #root route homepage
def index():
    template = functions.render("chalicelib/templates/index.html", response)
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

@app.route('/account') #get account information - profile, balances
def get_account():
    profile_url = "{}/v1/user/profile".format(config.base_url)
    profile_response = requests.get(profile_url, headers=config.headers).json()

    balance_url = "{}/v1/accounts/{}/balances".format(config.base_url, config.ACCOUNT_ID)
    balance_response = requests.get(balance_url, headers=config.headers).json()

    response["profile"] = profile_response["profile"]
    response["profile"]["balances"] = balance_response["balances"]

    template = functions.render("chalicelib/templates/account.html", response)
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

@app.route('/activity') #get account activity - positions, orders, gain/loss
def get_activity():
    orders_url = "{}/v1/accounts/{}/orders".format(config.base_url, config.ACCOUNT_ID)
    orders_response = requests.get(orders_url, headers=config.headers).json()

    #TRADIER BUG - positions response can be a dictionary or a list, breaking how it is displayed in the template
    positions_url = "{}/v1/accounts/{}/positions".format(config.base_url, config.ACCOUNT_ID)
    positions_response = requests.get(positions_url, headers=config.headers).json()

    gainloss_url = "{}/v1/accounts/{}/gainloss".format(config.base_url, config.ACCOUNT_ID)
    gainloss_response = requests.get(gainloss_url, headers=config.headers).json()

    # response["orders"] = orders_response["orders"] #unsorted dictionary of orders
    if orders_response['orders'] != 'null': #sort orders and store sorted list if orders is not null
        sorted_orders = sorted(orders_response['orders']['order'], key = lambda i: i['id'], reverse=True) #sort in descending order to show the latest order
        response["orders"] = sorted_orders #sorted list of orders
    
    response["positions"] = positions_response["positions"]
    response["gainloss"] = gainloss_response["gainloss"]

    template = functions.render("chalicelib/templates/activity.html", response)
    return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

@app.route('/quote/{symbol}') #get stock quote
def get_quote(symbol):
    quote_url = "{}/v1/markets/quotes".format(config.base_url)
    quote_params = {'symbols': symbol, 'greeks': 'true'}
    response = requests.get(quote_url, params=quote_params, headers=config.headers)
    return response.json()

@app.route('/option/chain/{symbol}/{expiration}') #get option chain
def get_option_chain(symbol, expiration):
    option_chain_url = "{}/v1/markets/options/chains".format(config.base_url)
    option_chain_params = {'symbol': symbol, 'expiration': expiration, 'greeks': 'true'}
    response = requests.get(option_chain_url, params=option_chain_params, headers=config.headers)
    return response.json()

@app.route('/option/strike/{symbol}/{expiration}') #get option strikes
def get_option_strike(symbol, expiration):
    option_strike_url = "{}/v1/markets/options/strikes".format(config.base_url)
    option_strike_params = {'symbol': symbol, 'expiration': expiration}
    response = requests.get(option_strike_url, params=option_strike_params, headers=config.headers)
    return response.json()

@app.route('/option/expiry/{symbol}') #get option expirations
def get_option_expiry(symbol):
    option_expiry_url = "{}/v1/markets/options/expirations".format(config.base_url)
    option_expiry_params = {'symbol': symbol, 'includeAllRoots': 'true', 'strikes': 'true'}
    response = requests.get(option_expiry_url, params=option_expiry_params, headers=config.headers)
    return response.json()

@app.route('/option/symbols/{symbol}') #get option symbols
def get_option_symbols(symbol):
    option_symbols_url = "{}/v1/markets/options/lookup".format(config.base_url)
    option_symbols_params = {'underlying': symbol}
    response = requests.get(option_symbols_url, params=option_symbols_params, headers=config.headers)
    return response.json()

@app.route('/order/{order_id}') #get individual order
def get_order(order_id):
    order_url = "{}/v1/accounts/{}/orders/{}".format(config.base_url, config.ACCOUNT_ID, order_id)
    response = requests.get(order_url, headers=config.headers)
    return response.json()

@app.route('/orders') #get orders
def get_orders():
    orders_url = "{}/v1/accounts/{}/orders".format(config.base_url, config.ACCOUNT_ID)
    response = requests.get(orders_url, headers=config.headers)
    return response.json()

@app.route('/positions') #get positions
def get_positions():
    positions_url = "{}/v1/accounts/{}/positions".format(config.base_url, config.ACCOUNT_ID)
    response = requests.get(positions_url, headers=config.headers)
    return response.json()

@app.route('/gainloss') #get gainloss
def get_gain_loss():
    gainloss_url = "{}/v1/accounts/{}/gainloss".format(config.base_url, config.ACCOUNT_ID)
    response = requests.get(gainloss_url, headers=config.headers)
    return response.json()

@app.route('/{asset}/order', methods=['POST']) #place order
def order(asset):
    webhook_message = app.current_request.json_body #store webhook message from the post
    order_url = "{}/v1/accounts/{}/orders".format(config.base_url, config.ACCOUNT_ID)
    quantity = 10 #initialize asset quantity
    ticker = webhook_message["ticker"] #store ticker
    close = webhook_message["close"] #store close price
    open = webhook_message["open"] #store open price

    #if asset class equals option
    if asset == "option":
        #convert webhook message to option_symbol GDX+200619+C+00033000 (ticker+date+call/put+strike)
        time = webhook_message["time"] #store time from webhook
        date = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") #convert time into datetime object
        day = date.weekday() #store weekday number

        #convert date into following friday
        if day == 0:
            tdelta = datetime.timedelta(days=4)
            expiration_date = date + tdelta
        elif day == 1:
            tdelta = datetime.timedelta(days=3)
            expiration_date = date + tdelta
        elif day == 2:
            tdelta = datetime.timedelta(days=2)
            expiration_date = date + tdelta
        elif day == 3:
            tdelta = datetime.timedelta(days=1)
            expiration_date = date + tdelta
        else:
            tdelta = datetime.timedelta(days=7)
            expiration_date = date + tdelta

        #call or put
        if close - open > 0:
            otm_strike = math.ceil(close) #round close price up to store out of the money call option strike price
            itm_strike = math.floor(close) #round close price down to store in the money call option strike price
            option_type = 'call'
          
        elif close - open < 0:
            itm_strike = math.ceil(close) #round close price up to store in the money put option strike price
            otm_strike = math.floor(close) #round close price down to store out the money put option strike price
            option_type = 'put'

        strike = (otm_strike + itm_strike) / 2 #calculate at the money strike price
        expiration = expiration_date.strftime('%Y-%m-%d') #convert date to expiration format used to get ask price from option chain

        option_chain_url = "{}/v1/markets/options/chains".format(config.base_url)
        option_chain_params = {'symbol': ticker, 'expiration': expiration, 'greeks': 'true'}

        chain_response = requests.get(option_chain_url, params=option_chain_params, headers=config.headers) #get option chain for ticker
        chain_response = chain_response.json()

        # option_symbols = [chain['symbol'] for chain in chain_response['options']['option']] #build option symbols list using list comprehension
    
        #calculate option symbol from option chain based on strike and option type
        for chain in chain_response['options']['option']: #loop through chain response
            if strike == chain['strike'] and option_type == chain['option_type']: #if the strike and option type matches one of the chains, set option symbol and ask price
                option_symbol = chain['symbol']
                ask = chain['ask']
                break
            elif itm_strike == chain['strike'] and option_type == chain['option_type']: #if data did not match one of the available symbols, atm strike does not exist, so use itm or otm
                option_symbol = chain['symbol']
                ask = chain['ask']

        #calculate limit and stop
        limit = round(ask * 1.1, 2)
        stop = round(ask * 0.75, 2)

        otoco_order = {
                        "class":"otoco",
                        "duration":"gtc",
                        "type[0]":"limit",
                        "price[0]": ask,
                        "option_symbol[0]": option_symbol,
                        "side[0]":"buy_to_open",
                        "quantity[0]": quantity,
                        "type[1]":"limit",
                        "price[1]": limit,
                        "option_symbol[1]": option_symbol,
                        "side[1]":"sell_to_close",
                        "quantity[1]": quantity,
                        "type[2]":"stop",
                        "stop[2]": stop,
                        "option_symbol[2]": option_symbol,
                        "side[2]":"sell_to_close",
                        "quantity[2]": quantity
                     }

        request = requests.post(order_url, data=otoco_order, headers=config.headers) #send otoco order to tradier and store the response
        response = json.loads(request.content) #convert otoco response into python object
        response["order"].update(otoco_order) #update response with otoco order data

    #if asset class equals equity
    elif asset == "equity":
        buy_order = {
                        'class': asset,
                        'symbol': ticker,
                        'side': 'buy',
                        'quantity': quantity,
                        'type': 'limit',
                        'duration': 'gtc',
                        'price': ask
                    }

        request = requests.post(order_url, data=buy_order, headers=config.headers) #send post request to tradier
        response = json.loads(request.content) #convert response into python object
        response["order"].update(buy_order) #update response with buy order data

    functions.send_email(response)

    return response #return order data