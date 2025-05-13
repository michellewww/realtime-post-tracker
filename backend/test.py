import snscrape.modules.twitter as sntwitter

for tweet in sntwitter.TwitterUserScraper("elonmusk").get_items():
    print(tweet.date, tweet.user.username, tweet.content)