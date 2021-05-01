import sys
import os
import requests, json
from requests.sessions import session
from codequick.storage import PersistentDict,Script
from xbmcaddon import Addon
import xbmc
import urlquick



#hoichoi
#base_content_url = "https://prod-api-cached-2.viewlift.com/content/pages?&site=hoichoitv&"
#shows=base_content_url+"path=/shows&"
#movies=base_content_url+"path=/categories&"
#home=base_content_url+"path=/&site=hoichoi&"

#https://prod-api-cached-2.viewlift.com/content/pages?path=/originals/drm/11th-hour&site=aha-tv&includeContent=true&moduleOffset=1&moduleLimit=1
#https://prod-api-cached-2.viewlift.com/search/v1?site=aha-tv&searchTerm={0}&types=VIDEO,SERIES,EVENT&languageCode=en
class viewlift:
    url_info = {}
    def __init__(self, url_info):
        self.url_info = url_info
    
    def list_curated_content(self, section):
        curated_content = []
        resp = urlquick.get(self.url_info[section]+"includeContent=false").json()
        i = 0
        for module in resp["modules"]:
            if( "title" in module ):
                curated_content.append({"title":module["title"], "index":i})
            i = i+1
        return curated_content

    def list_originals(self):
        resp = urlquick.get(self.url_info["shows"]+"includeContent=true").json()
        shows_map={}
        for module in resp["modules"]:
            if module["contentData"] != None:
                for contentData in module["contentData"]:
                    if "streamingInfo" in contentData:
                        break
                    if contentData["gist"]["title"] in shows_map:
                        continue
                    genre = ''
                    try:
                        contentData["gist"]["description"]['primaryCategory'][0]['title']
                    except:
                        genre = ''
                    shows_map[contentData["gist"]["title"]] = {
                        "title": contentData["gist"]["title"],
                        "url" : contentData["gist"]["permalink"],
                        "art":{"thumb" : contentData["gist"]["posterImageUrl"],
                                "fanart":contentData["gist"]["videoImageUrl"],
                                "icon" : contentData["gist"]["videoImageUrl"],
                                "poster" : contentData["gist"]["posterImageUrl"]},
                        "plot":contentData["gist"]["description"],
                        "genre":genre
                    }
        return shows_map

    def list_movies(self):
        resp = urlquick.get(self.url_info["movies"]+"includeContent=true").json()
        shows_map={}
        for module in resp["modules"]:
            if module["contentData"] != None:
                for contentData in module["contentData"]:
                    if "streamingInfo" in contentData:
                        if (contentData["gist"]["title"] in shows_map) or (contentData["gist"]["isTrailer"] == True):
                            continue
                        genre = ''
                        try:
                            contentData["gist"]["description"]['primaryCategory'][0]['title']
                        except:
                            genre = ''
                        shows_map[contentData["gist"]["title"]] = {
                            "title": contentData["gist"]["title"],
                            "url" : contentData["gist"]["permalink"],
                            "art":{"thumb" : contentData["gist"]["posterImageUrl"],
                                    "fanart":contentData["gist"]["videoImageUrl"],
                                    "icon" : contentData["gist"]["videoImageUrl"],
                                    "poster" : contentData["gist"]["posterImageUrl"]},
                            "plot":contentData["gist"]["description"],
                            "genre":genre
                        }
        return shows_map

    def list_seasons(self, url):
        season_list={}
        resp = urlquick.get(self.url_info["shows"]+"includeContent=true&moduleOffset=1&moduleLimit=1&path="+url).json()
        for season in resp["modules"][0]["contentData"][0]["seasons"]:
            season_list[season["title"]] ={
                "title":season["title"],
                "art":{"thumb":resp["metadataMap"]["image"], "fanart":resp["metadataMap"]["image"]},
                "plot":resp["metadataMap"]["description"]
            }
        return season_list

    def list_episodes(self, url, season_name):
        season_list={}
        resp = urlquick.get(self.url_info["shows"]+"includeContent=true&moduleOffset=1&moduleLimit=1&path="+url).json()
        for season in resp["modules"][0]["contentData"][0]["seasons"]:
            if(season["title"]==season_name):
                for episode in season["episodes"]:
                    season_list[episode["gist"]["title"]] ={
                        "title":episode["gist"]["title"],
                        "art":{"thumb":episode["gist"]["videoImageUrl"], "fanart":episode["gist"]["videoImageUrl"]},
                        "url":episode["gist"]["permalink"],
                        "plot":episode["gist"]["description"]
                    }
        return season_list
    
    def search(self, search_query):
        search_req = self.url_info["base_search_url"]+"&searchTerm="+(search_query)
        resp = urlquick.get(search_req).json()
        search_results={}
        for result in resp:
            search_results[result["gist"]["title"]] = {
                "title":result["gist"]["title"],
                "art":{"thumb":result["gist"]["videoImageUrl"], "fanart":result["gist"]["videoImageUrl"]},
                "url":result["gist"]["permalink"],
                "plot":result["gist"]["description"],
            }
        return search_results

    

    def list_curated_show(self, index, show_type):
        
        url = self.url_info[show_type]+"includeContent=true&moduleOffset="+str(index)+"&moduleLimit=1"
        
        resp = urlquick.get(url).json()
        curated_show_item = []

        for content in resp["modules"][0]["contentData"]:
            curated_show_item.append({
                "title" : content["gist"]["title"],
                "art":{"thumb" : content["gist"]["posterImageUrl"],"fanart":content["gist"]["videoImageUrl"]},
                "url":content["gist"]["permalink"],
                "isVideo": True  if ("isFullEpisode" in content["gist"]) else False,
                "plot":content["gist"]["description"] if content["gist"]["description"] else ""
            })
        return curated_show_item

    def get_video_stream(self, video_input, video_resolution):
        Script.log("get_video_stream video_input : {0} video_resolution {1} ".format(video_input, video_resolution), 
                                                                                        lvl=Script.DEBUG)
        with PersistentDict("userdata.pickle") as db:
            auth_token = db["token"]
        
        session = requests.Session()

        
        video_info = {}

        headers = {
            "authorization": auth_token,
        }
        
        video_path = video_input
        params = {
            'path': video_path,
            'site': 'aha-tv',
            'includeContent': 'true',
            'moduleOffset': '0',
            'moduleLimit': '5',
            'languageCode': 'default',
            'countryCode': 'IN',
        }

        response = requests.get('https://prod-api-cached-2.viewlift.com/content/pages', params=params)
        result = response.json()
        video_id = result["modules"][1]["contentData"][0]["gist"]["id"]
    

        url = "https://prod-api.viewlift.com/entitlement/video/status?deviceType=web_browser&contentConsumption=web&id={id}".format(id = video_id)
        res = session.get(url, headers = headers)
        result = res.json()
        
        try:
            try:
                result_url =  result["video"]["streamingInfo"]["videoAssets"]["hls"]
            except:
                #other than m3u8. widewine, fairplay and playready includes licenseToken and licenseUrl. A tiny change will help to m3u8.
                result_url =  result["video"]["streamingInfo"]["videoAssets"]["fairPlay"]["url"]
                result_url = result_url.split("fairplay")
                result_url = "hls".join(result_url)
            video_info["url"] = self.resolution(result_url, video_resolution)
            video_info["title"] = result["video"]["gist"]["title"]
            video_info["plot"] = result["video"]["gist"]["description"]
            video_info["date"] = result["video"]["gist"]["publishDate"]
            video_info["art"]={"thumb" : result["video"]["gist"]["posterImageUrl"],
                                "fanart":result["video"]["gist"]["videoImageUrl"],
                                "icon" : result["video"]["gist"]["videoImageUrl"],
                                "poster" : result["video"]["gist"]["posterImageUrl"]}
            video_info["subtitles"] =""

        except Exception as e:
            Script.log("Error While extarcting video stream"+str(e), lvl=Script.ERROR)
            Script.notify("Error", "Error While extarcting video stream"+e, icon=Script.NOTIFY_ERROR)
            
        try:
            video_info["subtitles"] = result["video"]["contentDetails"]["closedCaptions"][0]["url"]
            Script.log("subtitles="+video_info["subtitles"], lvl=Script.DEBUG)
        except:
            return video_info
        return video_info
    
    def resolution(self, result_url, resolution):
        Script.log("resolution url : {0} resolution {1} ".format(result_url, resolution), lvl=Script.DEBUG)
        if resolution == "1080p":
            video_url = result_url.split(".m3u8")
            video_url = "_1080.m3u8".join(video_url)
        elif resolution == "720p":
            video_url = result_url.split(".m3u8")
            video_url = "_720.m3u8".join(video_url)
        elif resolution == "480p":
            video_url = result_url.split(".m3u8")
            video_url = "_480.m3u8".join(video_url)
        elif resolution == "360p":
            video_url = result_url.split(".m3u8")
            video_url = "_360.m3u8".join(video_url)
        elif resolution == "270p":
            video_url = result_url.split(".m3u8")
            video_url = "_270.m3u8".join(video_url)   
        else:
            video_url = result_url.split(".m3u8")
            video_url = "_720.m3u8".join(video_url)
        return video_url