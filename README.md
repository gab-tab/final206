# 206_final
1. Data sources used, including instructions for a user to access the data sources (e.g., API keys or client secrets needed, along with a pointer to instructions on how to obtain these and instructions for how to incorporate them into your program (e.g., secrets.py file format))

This program pulls information from a CSV file into a database containing data about 3510 pizza restaurants in America. It uses the yelp API to pull out the rating for the restaurant and twitter API to pull out 10 tweets that mention the restaurant. You will need an API key for Twitter and Yelp. You also need a key to access ploty, my form of data presentation. Plotly shows 4 graphs: a map of all the restaurants in the database, a pie chart of the average cost of all the pizza restraunts, a map of all the restrauants in the city you choose, and a bar graph of the ratings for each restaurant in the city you choose.

2. Any other information needed to run the program (e.g., pointer to getting started info for plotly)
You will need to have a Plotly account set up on your computer and have a credentials file, as well as a token for mapbox.

3. Brief description of how your code is structured, including the names of significant data processing functions (just the 2-3 most important functions--not a complete list) and class definitions. If there are large data structures (e.g., lists, dictionaries) that you create to organize your data for presentation, briefly describe them.

The code starts with the creation of the database, moves on to API requests, and then finishes with the plotly graphs and the
user input commands.

4. Brief user guide, including how to run the program and how to choose presentation options.
The program is pretty self explanatory. Follow directions exactly and make sure everything is spelled correctly. For example, if you want the city Los Angeles, you cannot type LA or los angeles. The program will prompt you for the plotly graphs.
