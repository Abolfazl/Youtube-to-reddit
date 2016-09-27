# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 08:03:55 2015

@author: Sean.Titmarsh
"""

import praw
from prawoauth2 import PrawOAuth2Server

user_agent = 'OAuth token retrieval for /u/seantitmarsh'
reddit_client = praw.Reddit(user_agent=user_agent)
app_key = "Key"
app_secret = "Secret"
oauthserver = PrawOAuth2Server(reddit_client, app_key, app_secret,state=user_agent, scopes=['identity', 'edit', 'flair', 'history', 'modconfig', 'modflair', 'modlog', 'modposts', 'modwiki', 'mysubreddits', 'privatemessages', 'read', 'report', 'save', 'submit', 'subscribe', 'vote', 'wikiedit', 'wikiread'])

oauthserver.start()
tokens = oauthserver.get_access_codes()
print(tokens)

reddit_client.get_me()