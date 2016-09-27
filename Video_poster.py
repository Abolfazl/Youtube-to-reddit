#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0105
"""
Created on Sat Jan 09 21:56:32 2016

@author: sean
"""

import requests
import json
import praw
from prawoauth2 import PrawOAuth2Mini
import sqlite3 as lite

"""
SETTINGS
"""
channels = [["Channel Name", "Channel ID", ["Subreddit"]],
            ["Channel Name", "Channel ID", ["Subreddit", "Subreddit 2"]]]



"""
AUTHENTICATION FUNCTIONS
"""


"""
Youtube Oauth function.
Not currently needed, but may be useful for future features.
If not required, feel free to cut out lines 45 to 111 and line ...
"""

def youtube_oauth():
    """
    If "refresh_token" is empty, the Oauth process will need to be run again.
    This must be done on a machine with a web browser, as you will need to
    grant the app access to your account.
    Once access is granted, you will be directed to http://127.0.0.1/code=.
    The code is a string beginning with "4/". Occasionally the URL is appended
    with a "#", this is not part of the code, and can be safely ignored.
    Once that code is obtained, paste it into the "code" variable below,
    and run the script again.
    This time you will recieve an access_token and a refresh_token.
    Paste the refresh token into the "refresh_token" and Youtube's Oauth will
    be ready to use.
    You should not have to repeat this setup flow unless the refresh_token
    becomes invalid
    """
    client_id = "From Google API Console"
    client_secret = "From Google API Console"
    redirect_uri = "http://127.0.0.1"
    response_type = "code"
    code = ""
    refresh_token = "From API Response URL"
    if refresh_token == "" and code == "":
        youtube_get_code(client_id, response_type, redirect_uri)
        print "Got code"
    elif refresh_token == "" and code != "":
        youtube_get_refresh_token(code, client_id, client_secret, redirect_uri)
        print "Got tokens"
    else:
        token = youtube_refresh_access(client_id, client_secret, refresh_token)
        print "Refreshed Youtube tokens"
    return token

def youtube_get_code(c_id, r_type, r_uri):
    """Get Oauth token from youtube"""
    uri = "https://accounts.google.com/o/oauth2/auth"
    payload = {"client_id":c_id,
               "response_type":r_type,
               "redirect_uri":r_uri,
               "access_type":"offline",
               "scope":"https://www.googleapis.com/auth/youtube"}
    token = requests.get(uri, params=payload)
    print token.url

def youtube_get_refresh_token(cde, cl_id, cl_secret, re_uri):
    """use Auth Token to get Access and Refresh Tokens"""
    uri = "https://accounts.google.com/o/oauth2/token"
    payload = {"code":cde,
               "client_id":cl_id,
               "client_secret":cl_secret,
               "redirect_uri":re_uri,
               "grant_type":"authorization_code"}
    r_t = requests.post(uri, data=payload, verify=True)
    access_token = json.loads(r_t.text)
    print access_token["refresh_token"]

def youtube_refresh_access(client_id, client_secret, refresh_token):
    """Refresh the access token using Refresh token"""
    uri = "https://accounts.google.com/o/oauth2/token"
    payload = {"client_id":client_id,
               "client_secret":client_secret,
               "refresh_token":refresh_token,
               "grant_type":"refresh_token"}

    a_t = requests.post(uri, data=payload)
    access_token = json.loads(a_t.text)
    return access_token["access_token"]


"""
Reddit OAuth Implementation
This is provided by Avanassh's PrawOAuth library, found here:
https://github.com/avinassh/prawoauth2/
To get access and refresh tokens, run oauth.py on a local machine, 
then transfer those values to the variables in this function
"""
def reddit_oauth():
    """
    Get a new refresh token to ensure that access will be granted.
    No need to append the access key to the requests, PRAW handles that.
    """
    #Set Variables
    user_agent = 'Custom user_agent'
    reddit = praw.Reddit(user_agent=user_agent)
    app_key = "See https://github.com/reddit/reddit/wiki/OAuth2"
    app_secret = "See https://github.com/reddit/reddit/wiki/OAuth2"
    access_token = "From OAUTH API"
    refresh_token = "From OAUTH API"

    #Refresh OAuth access
    oauth_helper = PrawOAuth2Mini(reddit,
                                  app_key=app_key,
                                  app_secret=app_secret,
                                  access_token=access_token,
                                  refresh_token=refresh_token,
                                  scopes=['identity', 'edit', 'read',
                                          'history', 'modconfig', 'modflair',
                                          'modlog', 'modposts', 'modwiki',
                                          'mysubredits', 'privatemessages',
                                          'read', 'report', 'save', 'submit',
                                          'subscribe', 'vote', 'wikiedit', 'wikiread'])
    oauth_helper.refresh()
    return reddit


"""
YOUTUBE FUNCTIONS
"""

def get_video_id(channel_id):
    """
    Takes the currentc channelId, and returns the five ids in
    a list for the next function to use
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    payload = {"part":"id, snippet",
               "channelId":channel_id,
               "order":"date",
               "access_type":"offline",
               "type":"video",
               "fields":"items(id(videoId),snippet(title, liveBroadcastContent))",
               "key":"AIzaSyC2BRE3w0edcLe500romdSXSSYP5ICXD44"}
    videos = requests.get(url, params=payload)
    items = json.loads(videos.text)
    return items


def read_position(ch_name):
    """
    #TO DO: Use this function to read each file and see what's been uploaded
    Also, make script work if file doesn't exist.
    """
    vid_ids = []
    with lite.connect('RT.db',detect_types=lite.PARSE_DECLTYPES|lite.PARSE_COLNAMES,isolation_level=None) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM %s" % ch_name)
        rows = cur.fetchall()
        for row in rows:
            vid_ids.append(row[0])
    return vid_ids

def save_position(ch_name, vid_id, title):
    """
    TO DO: Use this function to write the new video to the file.
    Have a file per channel, and append the video with ID.
    Also, make script work if file doesn't exist.
    """
    with lite.connect('RT.db',detect_types=lite.PARSE_DECLTYPES|lite.PARSE_COLNAMES,isolation_level=None) as con:
        cur = con.cursor()
        new_title = title.encode('utf-8')
        new_id = str(vid_id).encode('utf-8')
        cur.execute("INSERT INTO %s VALUES (?, ?)" % ch_name, (new_title, new_id))
        con.commit()

"""
REDDIT FUNCTIONS
Note, to work, pass reddit to each function. Otherwise, the praw instance won't be initiated.
"""
def submit_to_subreddit(subreddit, name, link, reddit):
    """
    Submit each YouTube feed entry and submit to Reddit.
    Iteration is handled by the external loop.
    """
    reddit.submit(subreddit, title=name, url=link, resubmit="True")

#def update_wiki(subreddit, name, link, reddit):
    """
    TO DO: Save the link and video title to a page in the wiki. Probably
    append to the top of the list, ah lah /r/brownman/wiki/archive
    """


def run_bot():
    """Start a run of the bot."""
    youtube_oauth()
    reddit = reddit_oauth()
    print "Logged into Reddit"
    for channel in channels:
        print ""
        print "Now running " + channel[0]
        items = get_video_id(channel[1])
        ids = read_position(channel[0])
        for i in items['items']:
            name = i['snippet']['title']
            live = i['snippet']['liveBroadcastContent']
            link = 'http://www.youtube.com/watch?v=' + i['id']['videoId']
            print name + ', ' + link
            if i['id']['videoId'] in ids:
                print "skipped"
            elif live != "none":
                save_position(channel[0], i['id']['videoId'], i['snippet']['title'])
                print "Live content, skipped"
            else:
                print 'submit'
                for sub in channel[2]:
                    submit_to_subreddit(sub, name, link, reddit)
                    #update_wiki(sub, name, link, reddit)
                save_position(channel[0], i['id']['videoId'], i['snippet']['title'])

if __name__ == "__main__":

    try:
        run_bot()
    except SystemExit:
        print "Exit called."
