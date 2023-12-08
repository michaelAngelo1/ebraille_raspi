import writeBrailleSPI as rw
import requests as req
import time
import json
from callHelp import *
from buttons import *

ip = "192.168.137.254:3001"
nik = ""
jsonData = ""
pathJson = "/home/pi/Desktop/tauri/API/UI_Content.json"

with open(pathJson, 'r') as file:
    jsonData = json.load(file)

def readLoginStatus(pathJson):
    global nik
    rw.writeBraille("ketik nik dan enter")
    while True:
        buttonClicked = rw.buttonPressed()
        if buttonClicked == helpButton:
            callHelp()
        try:
            with open(pathJson, 'r') as file:
                jsonData = json.load(file)
        except:
            pass
        time.sleep(5/100)
        clicked = jsonData['content_0']['status']
#         print(clicked)
        if clicked == True:
            nik = jsonData['content_0']['nik']
            
            response = req.get("http://" + ip + "/login/byNIK", params={"nik": nik}).json()
            print(response)
            status = response.get("loginStatus")
            if status == True:
                break
            elif status == False:
                msg = response.get("msg")
                if msg == "akun sudah login!":
                    req.get("http://" + ip + "/logout", params={"nik": nik}).json()
                    rw.writeBraille("KETIK ULANG NIK")
                    print("going here")
#                     response = req.get("http://" + ip + "/login/byNIK", params={"nik": nik}).json()
                else:
                    rw.writeBraille("USER TIDAK DITEMUKAN")
                    jsonData['content_0']['errorState'] = True
                    jsonData['content_0']['status'] = False
                    try:
                        with open(pathJson, 'w') as file:
                            json.dump(jsonData,file, indent = 2)
                    except:
                        pass
                
#             except:
#                 pass
    return response