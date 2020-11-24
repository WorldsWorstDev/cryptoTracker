import requests
import time
from influxdb import InfluxDBClient as idcb
from dateutil.parser import parse

class label:
    def __init__(self,coins,currency):
        self.coins = coins
        self.currency = currency

    def build(self):
        i = 0
        l = []
        sep = '-'
        for things in self.coins:
            l.append(self.coins[i]+'btc')
            i = i+1

        builtLabel = sep.join(l)
        return builtLabel

def cd_get_price():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    r = requests.get(url)
    jsonObj = r.json()
    price_flt = jsonObj['bpi']['USD']['rate_float']
    lastUpdateTime = jsonObj['time']['updated']
    lastUpdateTime = parse(lastUpdateTime)
    current_price = (price_flt,lastUpdateTime)
    return current_price

def wci_get_price(coins, currency):
    key = '' #get this key from worldcoinindex.com off of their API page. NOTE they only let you hit their API 70x/hour. Don't over do it!!!
    x = label(coins, currency)
    constructedlabel = x.build()
    url = f'https://www.worldcoinindex.com/apiservice/ticker?key={key}&label={constructedlabel}&fiat={currency}'
    r = requests.get(url)
    jsonObj = r.json()
    return jsonObj

def create_connection(database):
    client = idcb(host='', port=8086) #Place the IP of your InfluxDB host in the quotes
    client.switch_database(database)
    return client

def cd_write_price(client, cd_current_price):
    priceObj = [{"measurement": "btc","time":cd_current_price[1],"fields":{"price":cd_current_price[0]}}]
    client.write_points(priceObj, protocol=u'json', time_precision='s')
    #if client.write_points(priceObj, protocol=u'json', time_precision='s'):
    #    print(f'Wrote {priceObj} to DB')

def wci_write_price(client, wci_current_price):
    for coin in wci_current_price['Markets']:
        priceObj = [{"measurement": coin['Name'],"time": coin['Timestamp'],"fields":{"price":coin['Price']}}]
        client.write_points(priceObj, protocol=u'json', time_precision='s')
        #if client.write_points(priceObj, protocol=u'json', time_precision='s'):
        #    print(f'Wrote {priceObj} to DB')

client = create_connection('cryptoprice')
coins = ['eth','ltc'] #fill in this with the three letter code for the coins you want prices for
currency = 'usd' #do the same for the currency you want prices in.
while True:
    cd_current_price = cd_get_price()
    wci_current_price = wci_get_price(coins, currency)
    cd_write_price(client, cd_current_price)
    wci_write_price(client, wci_current_price)
    time.sleep(60) #Coindesk's api updates every minute. Wait 60 seconds before getting the prices again
