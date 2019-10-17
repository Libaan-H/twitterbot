#!/usr/bin/python3

import tweepy
import logging
import json
import time
import random
import feedparser
import random

#for RSS feeds
rss_urls = ["http://something.com/feeds/posts/default", "https://somewhere-else.com/feed/"]

# Authenticate to Twitter
auth = tweepy.OAuthHandler("",
    "")
auth.set_access_token("",
    "")

# Random number selection, 1 out of x
# 432 is on average once every 3 days (assuming 600 second intervals)
# 720 is once every 5 days
randy = 600

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

# Search Like Follow
def slf():
    db = open("processed.db","r")
    seenids = db.readlines()
    db.close
    db = open("processed.db","w+")
    tweetnum=1
    # print symbol to indicate start
    print("-", end = "")
    #for tweet in api.search(q=["learn", "python"], lang="en", rpp=50, count=20):
    for tweet in api.search(q=["learn python"], lang="en", rpp=50, count=20):
        skip = 0
        #print(f"Tweet # {tweetnum}")
        for seenid in seenids:
            #print(f"looping, seenid {seenid} and tweetid {tweet.id}")
            if int(seenid) == tweet.id:
                print(".", end = '')
                skip=1
            #print (f"skip = {skip}")
        if skip != 1:
            # {tweet.text}
            #print("")
            print(f"\nNew: {tweet.user.name}:{tweet.id}:{tweet.user.screen_name}:{tweet.text})")
            if not tweet.favorited and tweet.user.screen_name != "myname":
                # Mark it as Liked
                try:
                    print ("- Liking")
                    tweet.favorite()
                except Exception as e:
                    print(f"Error on like, {tweet.id}")
                    # Check if we're following, if not, follow - not working correctly?
                print(f"Checking friendship with {tweet.user.screen_name} ..")
                if (api.show_friendship(source_screen_name="myname",target_screen_name=tweet.user.screen_name)):
                    print("- Following")
                try:
                     api.create_friendship(tweet.user.screen_name)
                #except tweepy.TweepError as e:
                except  Exception as e:
                    #print(e.message[0]['code'])
                    print (f"Error: {e}")
            #print (f"WRITING {tweet.id}")
        db.write("%s\r\n" % (tweet.id))
        time.sleep(1)
        tweetnum=tweetnum+1
    db.close

def follow_followers():
    # Follow followers
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            try:
                print(f"Following new follower {follower.name}")
                follower.follow()
            except Exception as e:
                print(f"Error following {follower.name} : {e}")

# Shall we tweet?
def maybe_tweet():
    ranPost = random.randint(1,randy)    # randy
    if ranPost == 1:
        tweetsdb = open("tweets.db","r")
        tweets = tweetsdb.readlines()
        tweetsdb.close
        tweetssz = len(tweets)-1
        print ("\nTweeting \o/")
        ranTweet = random.randint(1,tweetssz)
        print (f"ranpost:{ranTweet} content: {tweets[ranTweet]}")
        api.update_status(tweets[ranTweet])

def maybe_rss():
    # Should we post an RSS tweet?
    if random.randint(1,randy) == 1:    #randy
        # calculate number of feeds
        rss_url_sz = len(rss_urls)
        # choose random feed
        rss_feed = random.randint(0,rss_url_sz-1)
        print (f"\nRandom RSS: {rss_feed} {rss_urls[rss_feed]}")
        # extract title and link of latest
        feed = feedparser.parse( rss_urls[rss_feed] )
        # find number of posts and choose one randomly
        feed_sz = len(feed)
        #print (f"Feed size = {feed_sz}")
        entry_id = random.randint(0,feed_sz-1)
        toptitle = feed.entries[entry_id].title
        toplink = feed.entries[entry_id].link
        # Tweet
        print(f"Tweeting RSS, entry: {entry_id}, {toptitle} {toplink} #python")
        tweet_data = toptitle+" "+toplink+" #python"
        api.update_status(tweet_data)

# Search, Like, Follow
slf()
# Follow our own followers
follow_followers()
# Maybe tweet
maybe_tweet()
# Maybe post an RSS?
maybe_rss()
