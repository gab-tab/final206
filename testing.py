import unittest
import json
import final_project as project
from ok import *

class TestDatabase(unittest.TestCase):
    def test_city(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        self.assertTrue(isvalidcity('Los Angeles'))

    def test_restaurant(self):
        sql = "SELECT DISTINCT name FROM Pizza"
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('The Brentwood',), result_list)

    def test_num_rests(self):
        sql = "SELECT DISTINCT name FROM Pizza"
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 933)

    def test_city_table(self):
        sql = "SELECT name FROM City"
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 673)

class TestYelp(unittest.TestCase):
    def test_yelp(self):
        restaurant = "Patsy's Pizzeria"
        user_city = "New York"
        z_json = get_data_from_yelp(restaurant, user_city)
        load_cache()
        z_json = z_json['businesses'][0]['rating']
        self.assertEqual(z_json, 4.5)


class TestTweets(unittest.TestCase):
    def test_tweets(self):
        rest1 = 'Mangia Mangia Café'
        rest2 = 'Crown Fried Chicken'

        tweets1 = get_tweets_for_rest(rest1)
        self.assertTrue(len(tweets1) > 0 and len(tweets1) < 10)

        tweets2 = get_tweets_for_rest(rest2)
        self.assertEqual(len(tweets2), 10)

        self.assertFalse(tweets2[2].is_retweet)
        self.assertTrue(tweets2[0].popularity_score >= tweets2[1].popularity_score)
        self.assertTrue(tweets2[3].popularity_score >= tweets2[7].popularity_score)

        tweet_string = str(tweets2[0])
        self.assertTrue('@' in tweet_string)
        self.assertTrue('retweeted' in tweet_string)
        self.assertTrue('favorited' in tweet_string)

class TestPlotly(unittest.TestCase):
    def test_pie(self):
        sql = "SELECT price_level, count(1) as count FROM ( "
        sql += "SELECT pricerangemax, case  "
        sql += "when pricerangemax < 15 then 'Very Cheap' "
        sql += "when pricerangemax < 30 then 'Cheap' "
        sql += "when pricerangemax < 50 or pricerangemax is NULL or pricerangemax = '' then 'Average' "
        sql += "when pricerangemax < 100 then 'Expensive' "
        sql += "else 'Very Expensive'  end as price_level "
        sql += "FROM Pizza) tmp group by price_level"

        cur.execute(sql)
        lst = cur.fetchall()
        self.assertEqual(len(lst),5)

    def test_ratings(self):
        user_city = 'Los Angeles'
        city_id = '2'
        sql = "SELECT ID FROM City WHERE name = ?;"
        cur.execute(sql, [user_city])
        city_id = cur.fetchall()
        city_id = city_id[0]
        city_id = city_id[0]
        sql = "SELECT DISTINCT name FROM Pizza WHERE city = ?;"
        cur.execute(sql, [city_id])
        lst = cur.fetchall()
        cities = []
        for item in lst:
            cities.append(item[0])
        self.assertEqual(len(cities),8)









# class TestTweets(unittest.TestCase):
#     restaurant1 =

unittest.main()
