import sys
from sys import version_info
if version_info[0] < 3:
    from urllib import urlencode
else:
    from urllib.parse import urlencode
if version_info[0] < 3:        
    from urlparse import parse_qsl
else:    
    from urllib.parse import urlparse
from resources.lib.viewlift import viewlift
from resources.lib import login_utility
from resources.lib.search_listitem import search_listitem
from codequick import Route, Resolver, Listitem, run, storage, Script
from codequick.utils import urljoin_partial, bold
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon


aha_base_content_url = "https://prod-api-cached-2.viewlift.com/content/pages?&site=aha-tv&"
aha_url = { 
    "base_content_url" : aha_base_content_url,
    "home" : aha_base_content_url+"path=/&site=aha-tv&",
    "shows" : aha_base_content_url+"path=/shows&",
    "movies" : aha_base_content_url+"path=/movies&",
    "base_search_url":"https://prod-api-cached-2.viewlift.com/search/v1?site=aha-tv&types=VIDEO,SERIES,EVENT&languageCode=en"
}
resolution_list=["270p", "360p", "480p", "720p", "1080p"]
view_lift = viewlift(aha_url)

@Route.register
def root(plugin, content_type="segment"):

    HomeItems = {"label": "Home", 
    "info":{"plot":"Watch Telugu Movies From AHA.video"}, 
    "art":{"thumb":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png",
    "fanart":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png"},
    "callback":list_home_content}

    MoviesItem = {"label": "Curated Movies", 
    "info":{"plot":"Watch Telugu Movies From AHA.video"}, 
    "art":{"thumb":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png",
    "fanart":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png"},
    "callback":list_curated_movies}

    ShowsItem = {"label": "Curated Shows", 
    "info":{"plot":"Watch Telugu Shows From AHA.video"}, 
    "art":{"thumb":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png",
    "fanart":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png"},
    "callback":list_curated_shows}

    AllMoviesItem = {"label": "All Movies", 
    "info":{"plot":"Watch Telugu Movies From AHA.video"}, 
    "art":{"thumb":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png",
    "fanart":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png"},
    "callback":list_all_movies}

    AllShowsItem = {"label": "All Shows", 
    "info":{"plot":"Watch AHA Original & Shows"},
    "art":{"thumb":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png",
    "fanart":"https://appcmsprod.viewlift.com/38c1e2aa-64c1-41c3-8b5e-674247d490c8/images/aha_logo.png"}, 
    "callback":list_all_shows}

    

    yield Listitem.from_dict(**HomeItems)
    yield Listitem.from_dict(**MoviesItem)
    yield Listitem.from_dict(**ShowsItem)
    yield Listitem.from_dict(**AllMoviesItem)
    yield Listitem.from_dict(**AllShowsItem)
    yield Listitem.search(search_content)

@Route.register
def list_home_content(plugin):
    show_list = view_lift.list_curated_content("home")
    for i in show_list:
        item = build_xbmc_item(i, list_curated_show, i["index"], "home")
        yield item

@Route.register
def list_curated_movies(plugin):
    curated_movie_list = view_lift.list_curated_content("movies")
    for i in curated_movie_list:
        item = build_xbmc_item(i, list_curated_show, i["index"], "movies")
        yield item

@Route.register
def list_curated_shows(plugin):
    show_list = view_lift.list_curated_content("shows")
    for i in show_list:
        item = build_xbmc_item(i, list_curated_show, i["index"], "shows")
        yield item
        
@Route.register
def list_all_shows(plugin):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_LABEL)
    show_list = view_lift.list_originals()
    for show in show_list:
        yield build_xbmc_item(show_list[show], list_seasons)
    

@Route.register(autosort=True)
def list_all_movies(plugin):
    plugin.add_sort_methods(xbmcplugin.SORT_METHOD_LABEL)
    show_list = view_lift.list_movies()
    for show in show_list:
        yield build_xbmc_item(show_list[show], playVideo)

@Route.register
def list_curated_show(plugin, index, show_type):
    show_items = view_lift.list_curated_show(index, show_type)
    for item in show_items:
        yield build_xbmc_item(item, list_seasons)

@Route.register
def list_seasons(plugin, url):
    season_list = view_lift.list_seasons(url)
    for season in season_list:
        xbmc_item = build_xbmc_item(season_list[season], list_episodes, url = url, season=season_list[season]["title"])
        yield xbmc_item

@Route.register
def list_episodes(plugin, url, season):
    episodes = view_lift.list_episodes(url, season)
    for episode in episodes:
        yield build_xbmc_item(episodes[episode], playVideo)

@Route.register
def search_content(plugin, search_query):
    search_results = view_lift.search(search_query)
    for result in search_results:
        yield build_xbmc_item(search_results[result], playVideo)


@Resolver.register
@login_utility.check_and_login
def playVideo(plugin,url):
    video_info = view_lift.get_video_stream(url, resolution_list[int(Addon().getSetting("resolution"))])
    Script.log("url="+video_info["url"], lvl=Script.DEBUG)
    return Listitem().from_dict(**{
            "label":video_info["title"],
            "info":{"plot":video_info["plot"]},
            "callback": video_info["url"],
            "art":video_info["art"],
            "subtitles":[video_info["subtitles"]]
        })

 


def build_xbmc_item(show_item, next_call_back, *args, **kwargs):
    xbmc_item = Listitem()
    xbmc_item.label = show_item["title"]
    
    if 'url' in show_item:
        xbmc_item.params["url"] =  show_item["url"]
    
    if 'art' in show_item:
        xbmc_item.art.update(show_item['art'])
    
    xbmc_item.info['plot'] = show_item.get("plot", "")
    
    if(show_item.get("isVideo", False) == True):
        xbmc_item.set_callback(playVideo)    
    else:
        xbmc_item.set_callback(next_call_back, *args, **kwargs)

    return xbmc_item       
    


