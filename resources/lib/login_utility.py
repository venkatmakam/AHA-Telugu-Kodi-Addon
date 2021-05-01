from functools import wraps
from codequick.storage import PersistentDict, Script
import requests, json
try:  # Python 3
    import jwt
except ImportError:  # Python 2
    # The package is named pyjwt in Kodi 18: https://github.com/lottaboost/script.module.pyjwt/pull/1
    import pyjwt as jwt  
import time
from xbmcaddon import Addon
import xbmc

def check_and_login(func):
    @wraps(func)
    def check_and_login_wrapper(*args, **kwargs):
        if(check_token() == True):
            return func(*args, **kwargs)
        else:
            Script.notify("Error", "Unable to Login.Please check the credential", Script.NOTIFY_ERROR)
            return False

    return check_and_login_wrapper

def check_token():
    with PersistentDict("userdata.pickle") as db:
        encoded_token = db.get("token")

    if encoded_token is None:
        return generate_token()
    
    #else check the token validity if not valid generate again    
    try:
        decoded = jwt.decode(encoded_token, options={"verify_signature": False, "verify":False})
        exp_time_stamp = decoded["exp"]
        #print(exp_time_stamp)

        current_timestamp = time.time() 
        current_timestamp = round(current_timestamp)
        #print(current_timestamp)

        if current_timestamp < exp_time_stamp:
            return True
        else:
            return generate_token()
    except:
        return False
        
    return False

def generate_token():
    
    headers = {
        'authority': 'prod-api.viewlift.com',
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'x-api-key': 'dtGKRIAd7y3mwmuXGk63u3MI3Azl1iYX8w9kaeg3',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.aha.video',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.aha.video/',
        'accept-language': 'en-US,en-IN;q=0.9,en;q=0.8',
    }
    try:
        data = '{{"email":"{0}","password":"{1}"}}'.format(Addon().getSetting("email"), Addon().getSetting("password"))
        response = requests.post('https://prod-api.viewlift.com/identity/signin?site=aha-tv&deviceId=browser-6c83ee48-b374-5a1e-c1fe-8fbd579f1b7b', headers=headers, data=str(data))
        encoded_token = response.json()["authorizationToken"] 

        with PersistentDict("userdata.pickle") as db:
            db["token"] = encoded_token
        return True
    except Exception:
        Script.notify("Error", "Unable to Generate Token.Please check the credential", Script.NOTIFY_ERROR)
        return False