import json
from googleapiclient.discovery import build
import googleapiclient.errors
import pandas as pd
import os
import argparse
import sys

api_key="None"

def get_data(apikey, search_phrase, broad_tag):
	youtube = build("youtube", "v3", developerKey = api_key)
	numres=25
	searchres = youtube.search().list(part="snippet", maxResults=numres, q=search_phrase).execute()
	vidids = []
	for i in range(len(searchres["items"])):
	    try:
	        vidids.append(searchres["items"][i]["id"]["videoId"])
	    except KeyError:
	        continue
	df = []
	#parse and take only data we want
	for i in range(len(vidids)):
	    response = youtube.videos().list(part="snippet,statistics", id=vidids[i]).execute()
	    try:
	        df.append(pd.DataFrame({"title": response["items"][0]["snippet"]["title"],\
	                           "tags": [response["items"][0]["snippet"]["tags"][:5]],\
	                          "likes": response["items"][0]["statistics"]["likeCount"],\
	                          "dislikes": response["items"][0]["statistics"]["dislikeCount"],\
	                          "views": response["items"][0]["statistics"]["viewCount"],\
	                            "Broad Tag": broad_tag}))
	    except KeyError:         #some videos do not have tags apparently
	        continue
	return df

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-q', "--query", default=None, type=str, help="search query")
	parser.add_argument('-t', "--tag", default=None, type=str, help="broad category of search query")

args = parser.parse_args()

if args.query == None or args.tag == None:
	print("require query and broad tag")
	sys.exit()

if os.path.isfile("vids.pkl"):
    vids = pd.read_pickle("vids.pkl")
    new = pd.concat(get_data(api_key, args.query, args.tag))
    vids = pd.concat([vids,new], ignore_index=True)
    vids.to_pickle("vids.pkl")
else:
    vids = pd.concat(get_data(api_key, args.query, args.tag))
    vids.to_pickle("vids.pkl")
