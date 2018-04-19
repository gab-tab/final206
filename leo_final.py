# #final project
# #Gaby Tabachnik

import secrets
import sqlite3
import csv
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import pprint
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
from requests_oauthlib import OAuth1
from requests.packages.urllib3.exceptions import InsecureRequestWarning

'''
Database Class
'''
class SQLiteDatabase:
    def __init__(self):
        pass

    def open(self, databasename):
        self.conn = sqlite3.connect(databasename)
        self.cur = self.conn.cursor()

    def executeSQL(self, sql, value=None):
        if value:
            self.cur.execute(sql, [value])
        else:
            self.cur.execute(sql)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()

# This statement remains to instantiate the class
db = SQLiteDatabase()

'''
Routine to create the database
'''
def create_database(databasename):
    PIZZACSV = 'pizza.csv'

    conn = sqlite3.connect(databasename)
    cur = conn.cursor()
    statement_drop_pizza = 'DROP TABLE IF EXISTS "Pizza"'
    cur.execute(statement_drop_pizza)
    conn.commit()

    statement_drop_city = "DROP TABLE IF EXISTS 'City'"
    cur.execute(statement_drop_city)
    conn.commit()

    statement_drop_yelp = "DROP TABLE IF EXISTS 'Yelp'"
    cur.execute(statement_drop_yelp)
    conn.commit()

    statement_drop_twitter = "DROP TABLE IF EXISTS 'Twitter'"
    cur.execute(statement_drop_yelp)
    conn.commit()


    create_pizza = '''
    CREATE TABLE IF NOT EXISTS 'Pizza' (
    'id' TEXT,
    'address' TEXT,
    'categories' TEXT,
    'city' INTEGER,
    'country' TEXT,
    'keys' TEXT,
    'latitude' INTEGER,
    'longitude' INTEGER,
    'menuPageURL' INTEGER,
    'menus_amountMax' INTEGER,
    'menus_amountMin' INTEGER,
    'menus_dateSeen' TEXT,
    'menus_name' TEXT,
    'name' TEXT,
    'postalCode' INTEGER,
    'priceRangeCurrency' TEXT,
    'priceRangeMin' INTEGER,
    'priceRangeMax' INTEGER,
    'province' TEXT);
    '''
    cur.execute(create_pizza)

    create_city = '''
    CREATE TABLE IF NOT EXISTS 'City' (
    'id' TEXT,
    'name' TEXT);
    '''
    cur.execute(create_city)
    conn.commit()



    city_count = 0
    city_ids = {}

    pizza_file = open("pizza.csv", "r")
    data = csv.DictReader(pizza_file)
    cache = open("cache_data.txt", "w")
    for info in data:
        id = info["id"]
        address = info["address"]
        categories = info["categories"]
        city = info["city"]
        if not city in city_ids:
            city_count += 1
            city_ids[city] = city_count
            insert_to_table = (city_ids[city],city)
            statement = '''
            INSERT INTO 'City'
            VALUES (?,?)
            '''
            cur.execute(statement, insert_to_table)
        country = info["country"]
        keys = info["keys"]
        latitude = info["latitude"]
        longitude = info["longitude"]
        menuPageURL = info["menuPageURL"]
        menus_amountMax = info["menus.amountMax"]
        menus_amountMin = info["menus.amountMin"]
        menus_dateSeen = info["menus.dateSeen"]
        menus_name = info["menus.name"]
        name = info["name"]
        postalCode = info["postalCode"]
        priceRangeCurrency = info["priceRangeCurrency"]
        priceRangeMin = info["priceRangeMin"]
        priceRangeMax = info["priceRangeMax"]
        province = info["province"]

        # INSERT INTO pizza(id, address) VALUES (?, ?);
        insert_to_table = (id,address,categories,city_ids[city],country,keys,latitude,longitude,menuPageURL,menus_amountMax,menus_amountMin,menus_dateSeen,menus_name,name,postalCode,priceRangeCurrency,priceRangeMin,priceRangeMax,province)
        statement = '''
        INSERT INTO 'Pizza'
        Values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        '''
        cur.execute(statement, insert_to_table)
    conn.commit()

'''
routines to get data from yelp
'''
def params_unique_combination(url, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return url + "_".join(res)

def save_cache():
    full_text = json.dumps(CACHE_DICTION)
    cache_file_ref = open(CACHE_FNAME, 'w')
    cache_file_ref.write(full_text)
    cache_file_ref.close()

def load_cache():
    global CACHE_DICTION
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

def make_request_using_cache(url, headers, params, verify=False):
    unique_ident = params_unique_combination(url, params)
    if unique_ident in CACHE_DICTION:
        print('Getting cached data...')
        return CACHE_DICTION[unique_ident]
    else:
        print('Making request for new data...')
        resp = requests.get('GET', url, headers=headers, params=params)
        CACHE_DICTION[unique_ident] = resp.text
        save_cache()
        return CACHE_DICTION[unique_ident]

def get_data_from_yelp(term, location, limit=50):
    url = 'https://api.yelp.com/v3/businesses/search'
    API_KEY = secrets.YELP_API_KEY
    headers = {
    'Authorization': 'Bearer {}'.format(API_KEY)
        }
    params = {'term': term, 'location': location, 'limit':50}
    uniq = params_unique_combination(url, params)
    if uniq in CACHE_DICTION:
        text = CACHE_DICTION[uniq]
        return text
    else:
        response = requests.get(url, headers=headers, params=params, verify=False)
        yelpinfo = json.loads(response.text)
        CACHE_DICTION[uniq] = yelpinfo
        save_cache()
        return yelpinfo

'''
get data from Twitter
'''
# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params= {}, auth = {}):
    unique_ident = params_unique_combination(baseurl,params)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        #print("Fetching cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(baseurl, params, auth=auth)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class Tweet:
    def __init__(self, tweet_dict_from_json):
        if 'retweeted_status' in tweet_dict_from_json:
            self.is_retweet = True
        else:
            self.is_retweet = False
        self.text = tweet_dict_from_json['text']
        self.username = tweet_dict_from_json['user']['screen_name']
        self.creation_date = tweet_dict_from_json['created_at']
        self.num_retweets = tweet_dict_from_json['retweet_count']
        self.num_favorites = tweet_dict_from_json['favorite_count']
        self.popularity_score = self.num_retweets * 2 + self.num_favorites * 3
        self.id = tweet_dict_from_json['id']

    def __str__(self):
        return "@{}:{}\n[retweeted {} times]\n[favorited {} times]\n[tweeted on {}] | id: {}]".format(self.username, self.text, self.num_retweets, self.num_favorites, self.creation_date, self.id)

def get_tweets_for_rest(restaurant):
    tweet_list = []
    baseurl = 'https://api.twitter.com/1.1/search/tweets.json'
    req = make_request_using_cache(baseurl, params = {'q': restaurant, "count" : 60}, auth=auth)
    data = json.loads(req)

    for tweet_data in data["statuses"]:
        inst = Tweet(tweet_data)
        tweet_list.append(inst)
    original_tweets = [t for t in tweet_list]
    return sorted(original_tweets, key = lambda tweet: tweet.popularity_score, reverse = True)[0:10]

'''
Routines for verification of user data
'''
def yes_no(value):
    if value in ['y','n']:
        return True
    return False

def isvalidcity(value):
    result = db.executeSQL("SELECT ID FROM City WHERE name = ?;",value)

    if result:
        return True
    return False

def is_restaurant(value):
    value = int(value)
    global size_of_list
    if value < 1:
        return False
    if value > size_of_list:
        return False
    return True

def ischoice(value):
    if value in ['Rating','Tweets','Maps']:
        return True
    return False

'''
Routines for maps
'''
def show_map(city_id):
    lst = db.executeSQL("SELECT name, latitude, longitude FROM Pizza WHERE city = ?;",city_id)

    df = pd.DataFrame(lst, columns=['name', 'lat', 'lon'])

    mean_lat = np.mean(df.lat)
    mean_lon = np.mean(df.lon)

    mapbox_access_token = 'pk.eyJ1IjoiZ2FidGFiIiwiYSI6ImNqZzRoNmYxNTAxbHAycG80bzBseWV3cGwifQ.7hdk2woauWSMkMQVudmPcw'
    data = Data([
    Scattermapbox(
        lat=df.lat,
        lon=df.lon,
        mode='markers',
        marker=Marker(
            size=9
        ),
        text=df.name,
        )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=mean_lat,
                lon=mean_lon
            ),
            pitch=0,
            zoom=10
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='Restaurants')

'''
Routine for rating chart
'''
def show_rating_chart():
    sql = "SELECT price_level, count(1) as count FROM ( "
    sql += "SELECT pricerangemax, case  "
    sql += "when pricerangemax < 15 then 'Very Cheap' "
    sql += "when pricerangemax < 30 then 'Cheap' "
    sql += "when pricerangemax < 50 or pricerangemax is NULL or pricerangemax = '' then 'Average' "
    sql += "when pricerangemax < 100 then 'Expensive' "
    sql += "else 'Very Expensive'  end as price_level "
    sql += "FROM Pizza) tmp group by price_level"

    lst = db.executeSQL(sql)

    labels = [x[0]for x in lst]
    values = [x[1]for x in lst]

    trace = go.Pie(labels=labels, values=values)

    py.plot([trace], filename='basic_pie_chart')

'''
Routines to process user input
'''
def userinput(prompt, default_val='n', validation = yes_no):
    while True:
        response = input(prompt)
        if response:
            pass
        else:
            response = default_val
        if response == 'New':
            break
        if response == 'Exit':
            break
        if response == 'Map':
            break
        if validation(response):
            break
        print (response, 'is not a valid response')
    return response

'''
MAIN ROUTINE
'''
#	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#	auth = OAuth1(secrets.twitter_api_key, secrets.twitter_api_secret, secrets.twitter_access_token, secrets.twitter_access_token_secret)
def mainProgram():
    global size_of_list
    DBNAME = 'pizza_info.db'

    create_database(DBNAME)

    # access cached json
    CACHE_FNAME = 'final_project_cache.json'
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    # access Twitter
    CACHE_FNAME = "twitter.json"
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()

    # if there was no file, no worries. There will be soon!
    except:
        CACHE_DICTION = {}

    # Do user interface
    db.open(DBNAME)


    user_ans = input('Do you want to see the price distributions of all the pizza restraunts in America? Y/N ')
    if user_ans == "Y":
        show_rating_chart()
    else:
        continue

    print ('Enter a City, pick a restaurant, and request either a Yelp rating, the ten most recent tweets, or 4 maps.')
    while True:
        user_city = userinput('Enter a city to recieve a list of pizza restaurants within the city. To exit, enter Exit. ','Provo', isvalidcity)
        if user_city == 'New':
            continue
        if user_city == "Exit":
            break
        print (user_city)
        city_id = db.executeSQL("SELECT ID FROM City WHERE name = ?;",user_city)
        city_id = city_id[0]
        city_id = city_id[0]

        #now display the restrauants
        lst = db.executeSQL("SELECT DISTINCT name FROM Pizza WHERE city = ?;", city_id)
        size_of_list = len(lst)
        count = 0
        for line in lst:
            count = count + 1
            line = line[0]
            print (count, line)

        user_ans = input('Do you want to see the map? Y/N')
        if user_ans == "Y":
            show_map(city_id)

        user_number = userinput(
            'Enter the number of the restaurant you want. Enter New for a new City. To exit, enter Exit. ',
            1, is_restaurant)
        if user_number == 'New':
            continue
        if user_number == "Exit":
            break

        print (user_number)
        restaurant = lst[int(user_number) - 1]
        restaurant = restaurant[0]


        while True:
            user_choice = userinput('Enter Rating, Tweets, or Maps. Enter New for a new City. To exit, enter Exit. ','Rating', ischoice)
            if user_choice == 'New':
                continue
            if user_choice == "Exit":
                break
            print (user_choice)
            if user_choice == 'Rating':
                z_json = get_data_from_yelp(restaurant, user_city)
                load_cache()
                pp = pprint.PrettyPrinter(indent = 2)
                # pp.pprint(z_json)
                z_json = z_json['businesses'][0]['rating']
                print(restaurant, 'Yelp Rating:', z_json)

            if user_choice == 'Tweets':
                tweets = get_tweets_for_rest(restaurant)
                if len(tweets) > 0:
                    for x in tweets:
                        print(x)
                else:
                    print("No tweets found")
                print("--------------------")
            if user_choice == 'Maps':
                pass

    db.close()

if __name__=="__main__":
    mainProgram()
