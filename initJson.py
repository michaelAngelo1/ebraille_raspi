import json

jsonData = ""
pathJson = "/home/pi/Desktop/tauri/API/UI_Content.json"

with open(pathJson, 'r') as file:
    jsonData = json.load(file)

def initializeJson(pathJson):
    jsonData["mode"] = 0
    jsonData["content_0"]["errorState"] = ""
    jsonData["content_0"]["status"] = ""
    jsonData["content_0"]["nik"] = ""
    jsonData["content_1"]["Author"] = ""
    jsonData["content_1"]["avail"] = ""
    jsonData["content_1"]["BookCover"] = ""
    jsonData["content_1"]["Edition"] = ""
    jsonData["content_1"]["Langguage"] = ""
    jsonData["content_1"]["Title"] = ""
    jsonData["content_1"]["brailleCell"] = ""
    jsonData["content_1"]["Year"] = ""
    jsonData["content_2"]["line"] = 0
    jsonData["content_2"]["maxLine"] = 0
    jsonData["content_2"]["maxPage"] = 0
    jsonData["content_2"]["page"] = 0
    jsonData["content_2"]["pageContent"] = ""
    jsonData["content_2"]["titleBook"] = ""
    jsonData["content_2"]["popup"] = False
    jsonData["content_3"]["ListBookData"] = []
    jsonData["content_3"]["index"] = "0"
    jsonData["content_3"]["title"] = ""
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass