import requests as req
import RPi.GPIO as GPIO
import writeBrailleSPI as rw
from pathlib import Path
import linecache
import re
import os
import json
import asciiconvert as asc
# import math
# import websocket
import pygame
# import time
# import psutil
# import tkinter as tk
# import keyboard

from initJson import *
from readLoginStatus import *
from callHelp import *
from buttons import *

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ip = "192.168.137.254:3001"

books = [] #menampung judul buku dari database
booksid = [] #menampung isbn buku dari database
bookCount = [] #menampung availability dari buku
booksLanguage = [] #menampung bahasa dari buku
booksAuthor = [] #menampung penulis dari buku
booksYear = [] #menampung tahun publikasi buku
booksCategories = [] #menampung kategori buku
booksEdition = [] #menampung edisi buku

bookmarkedISBN = []
bookmarkList = {}
pageNumber = [] #menampung nomor baris terakhir pada masing-masing halaman
pageLineList = [] #jumlah baris pada masing-masing halaman
pageBooks = 0 #
bookNumber = -1 #menentukan buku ke-berapa yang sedang dilihat judulnya
maxLine = 0 #baris terakhir pada buku
line = 0
lineDisplay = 0
pageIndex = 0 #menunjuk halaman ke berapa
accessToken = ""
refreshToken = ""
status = False
brailleCells = 24
splited = []
element = 0
isbnIndex = -1
searchEnter = False
searchIndex = 0
searchedList = []
USBin = False
USBpath = ""
modeFD = False
choosenBook = ""
book_files = []
choosenNumber = -1



mode = 0
path = "/home/pi/Desktop/E-Braille/Downloads/" #path folder buku yang didownload

GPIO.setup(buttonUp, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonDown, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonLeft, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonRight, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def getBook():
    global books, booksid, bookCount, booksLanguage, booksAuthor, booksYear, booksCategories, booksEdition, accessToken, refreshToken
    output = req.get("http://" + ip + "/book/getBook", params = {"accessToken": accessToken, "refreshToken": refreshToken}).json()
    valid = output.get('status')
    print(output)
    if valid == False:
        getAccessToken()
        output = req.get("http://" + ip + "/book/getBook", params = {"accessToken": accessToken, "refreshToken": refreshToken}).json()
    print("access: " + accessToken)
    print("refresh: " + refreshToken)
    print("getting book")
    i = 0
    books.clear()
    booksid.clear()
    bookCount.clear()
    booksLanguage.clear()
    booksAuthor.clear()
    booksYear.clear()
    booksCategories.clear()
    booksEdition.clear()
    bookList = output.get('data')
    
    while(True):
        data = bookList[i]
        books.insert(i, data.get('titles'))
        booksid.insert(i, data.get('isbn'))
        bookCount.insert(i, data.get('availability'))
        booksLanguage.insert(i, data.get('languages'))
        booksAuthor.insert(i, data.get('authors'))
        booksYear.insert(i, data.get('year'))
        booksCategories.insert(i, data.get('categories'))
        booksEdition.insert(i, data.get('editions'))
        print("judul")
        print(books)
        i += 1
        if i >= len(bookList):
            break

def getBookSearched(titleSearched):
    global accessToken, refreshToken, bookSearchedTotal, searchIndex
#     output = req.get("http://" + ip + "/book/getBook", params = {"accessToken": token, "refreshToken": refreshToken, "title": "a"}).json().get('data')
    print(titleSearched)
    output = req.get("http://" + ip + "/book/getBook", params = {"accessToken": accessToken, "refreshToken": refreshToken, "title": titleSearched}).json()
    print(json.dumps(output, indent = 2))
    valid = output.get('status')
    print(valid)
    if valid == False:
        getAccessToken()
        output = req.get("http://" + ip + "/book/getBook", params = {"accessToken": accessToken, "refreshToken": refreshToken, "title": titleSearched}).json()
    searchIndex = 0
    booklistJson = output.get('data')
    bookSearchedTotal = len(booklistJson)
    if bookSearchedTotal > 0:
        for item in booklistJson:
#             print(item)
#             item['Author'] = item.pop('authors')
#             item['Availability'] = item.pop('availability')
#             item['Edition'] = item.pop('editions')
#             item['Language'] = item.pop('languages')
#             item['Title'] = item.pop('titles')
#             item['Year'] = item.pop('year')
#             if 'publishers' in item:
#                 del item['publishers']
#             if 'categories' in item:
#                 del item['categories']
            if 'isbn' in item:
                item["BookCoverUri"] = "http://" + ip + "/book/getCover?isbn=" + item['isbn']

    if bookSearchedTotal <= 0:
        rw.writeBraille("JUDUL TIDAK ADA")
        jsonData['content_3']['errorState'] = True
    jsonData['content_3']['index'] = searchIndex
    jsonData['content_3']['ListBookData'] = booklistJson
    jsonData['content_3']['status'] = False
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    print("judul")
    print("BOOKLIST JSON: ", booklistJson)
    return booklistJson

def getAccessToken():
    global accessToken, refreshToken, nik
    response = req.get("http://" + ip + "/token/byNIK", params={"nik": nik, "accessToken": accessToken, "refreshToken": refreshToken}).json()
    print("Token updated")
    
    accessToken = response.get('accessToken')
    refreshToken = response.get('refreshToken')
    rw.writeBraille("PLEASE WAIT")
    
def logout():
    global nik, mode, books, booksid, bookCount, booksLanguage, booksAuthor, booksYear, booksCategories, booksEdition, bookNumber
    response = req.get("http://" + ip + "/logout", params={"nik": nik}).json()
    nik = ""
    mode = 0
    bookNumber = -1
    print(response)
    jsonData['mode'] = mode
    jsonData['content_0']['nik'] = nik
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
    jsonData["content_3"]["ListBookData"] = []
    jsonData["content_3"]["index"] = "0"
    books = []
    booksid = [] 
    bookCount = []
    booksLanguage = [] 
    booksAuthor = [] 
    booksYear = [] 
    booksCategories = []
    booksEdition = []
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille("LOGOUT BERHASIL")
        
#fuction to split text
def split(txt):
    convTxt = []
    tempStr = ""
    element = 0
    count = 0
    seperate = int(len(txt)/brailleCells)
    for i in txt:
        tempStr += i
        count  += 1
        if len(tempStr) == brailleCells:
            convTxt.append(tempStr)
            tempStr = ""
            element += 1
        elif len(txt) == count:
            convTxt.append(tempStr)
            tempStr = ""
    return convTxt

def checkFiles(File):
    global pageBooks, maxLine
    linesInFile = 0
    linesInPage = 0
    linesInEachPage = 0
    pageBooks = 0
    print ("masuk cekfiles")
    try:
        with open(File, "r") as f:

            for Page in f:
                linesInFile += 1
                content = linecache.getline(File, linesInFile)
                if checkItsPageSign(content) == True:  # PageSignContent
                    pageNumber.append(linesInFile)
                else:  # TextContent
                    linesInPage += 1
                    linesInEachPage += 1
    except Exception as error:
        print ("DBEUG:",error)

    for idx, methData in enumerate(pageNumber):
        nextIndex = idx + 1
        if nextIndex < len(pageNumber):
            pageLineList.append((pageNumber[nextIndex] - pageNumber[idx]))
    pageLineList.append(linesInFile - pageNumber[-1])
    maxLine = linesInFile
    print("\nlinesInFile: " + str(linesInFile))
    print("linesInTotalPage: " + str(linesInPage))
    print("linesineachpage: " + str(linesInEachPage))
    print("Page Number: " )
    print(pageNumber)

def checkItsPageSign(content):
    global pageBooks
    charCounter = 0
    for char in content:
        if char == " ":
            charCounter += 1

    if charCounter >= 30:
        pageBooks += 1
        print("page: " + str(pageBooks))
        return True
    else:
        return False

# REVIEWED
def nextPrevBook(string):
    global bookNumber,splited, choosenBook, USBin, choosenNumber
    print("ISI SPLITED: ", splited)
    splited.clear()
    print("ISI SPLITED.CLEAR(): ", splited)
    element = 0
    
    # titleBraille is a variable splited[element] written to writeBrailleSPI AND UI_Content
    # UI_Content.json overwrites the content on the E-braille V2 desktop app based on the hardware input
    titleBraille = ""
    tempChoosenBook = ""
    
    if USBin:
        if string == "next":
            if choosenNumber < len(book_files)-1:
                choosenNumber +=1
            
        elif string == "prev":
            choosenNumber -= 1
            if choosenNumber < 0:
                choosenNumber = 0
                rw.writeBraille("INI BUKU PERTAMA")
        
        print("choosen number: " +str(choosenNumber))
        tempChoosenBook = str(book_files[choosenNumber])
        print("Judul Buku:" + tempChoosenBook)
        for letter in tempChoosenBook:
            titleBraille = titleBraille + str(asc.convert(letter))
            
        jsonData['content_1']['Author'] = ""
        jsonData['content_1']['BookCover'] = ""
        jsonData['content_1']['Edition'] = ""
        jsonData['content_1']['Langguage'] = ""
        jsonData['content_1']['Title'] = tempChoosenBook[0:len(tempChoosenBook)-4]
        jsonData['content_1']['Year'] = ""
        jsonData['content_1']['avail'] = ""
        
    else:
        if string == "next":
            bookNumber += 1
        elif string == "prev":
            bookNumber -= 1
            if bookNumber < 0:
                bookNumber = 0
                rw.writeBraille("INI BUKU PERTAMA")
            
        print("booknumber: " +str(bookNumber))
        print("Judul Buku:" +str(books[bookNumber]))
        print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
        
        for letter in books[bookNumber]:
            titleBraille = titleBraille + str(asc.convert(letter))
            
        jsonData['content_1']['Author'] = booksAuthor[bookNumber]
        jsonData['content_1']['BookCover'] = "http://" + ip + "/book/getCover?isbn=" + booksid[bookNumber]
        jsonData['content_1']['Edition'] = booksEdition[bookNumber]
        jsonData['content_1']['Langguage'] = booksLanguage[bookNumber]
        jsonData['content_1']['Title'] = books[bookNumber]
        jsonData['content_1']['Year'] = booksYear[bookNumber]
        jsonData['content_1']['avail'] = bookCount[bookNumber]
            
        
    printedText = str(titleBraille).strip()
    print(printedText)
    
    if len(printedText) == 0:
        printedText += " "
        splited.append(printedText)
    elif len(printedText) <= brailleCells:
        splited.append(printedText)
    else:
        splited = split(printedText)
        
    print("Sentence: ")
    print(splited)
    print("Element :" + str(element))
    print("JUDUL (SPLITED[ELEMENT])", splited[element])
    
    if USBin:
        jsonData['content_1']['brailleCell'] = splited[element][0:len(splited[element])-4]
    else:
        jsonData['content_1']['brailleCell'] = splited[element]
        
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    
    # This writes to E-braille the currently viewed Book on the Main Page
    rw.writeBraille(splited[element])

def prevBook():
    global bookNumber, splited
    splited.clear()
    element = 0
    titleBraille = ""
    bookNumber -= 1
    if bookNumber < 0:
        bookNumber = 0
        rw.writeBraille("INI BUKU PERTAMA")
    print("booknumber: " +str(bookNumber))
    for letter in books[bookNumber]:
        titleBraille = titleBraille + str(asc.convert(letter))
    printedText = str(titleBraille).strip()
    if len(printedText) == 0:
        printedText += " "
        splited.append(printedText)
    elif len(printedText) <= brailleCells:
        splited.append(printedText)
    else:
        splited = split(printedText)
    print("Judul Buku:" +str(books[bookNumber]))
    print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
    jsonData['content_1']['Author'] = booksAuthor[bookNumber]
    jsonData['content_1']['BookCover'] = "http://" + ip + "/book/getCover?isbn=" + booksid[bookNumber]
    jsonData['content_1']['Edition'] = booksEdition[bookNumber]
    jsonData['content_1']['Langguage'] = booksLanguage[bookNumber]
    jsonData['content_1']['Title'] = books[bookNumber]
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_1']['Year'] = booksYear[bookNumber]
    jsonData['content_1']['avail'] = bookCount[bookNumber]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille(splited[element])

def nextBookmark():
    global bookNumber,splited, isbnIndex
    splited.clear()
    element = 0
    titleBraille = ""
    if isbnIndex >= len(bookmarkedISBN)-1:
        rw.writeBraille("BOOKMARK TERAKHIR")
    else:
        isbnIndex = isbnIndex + 1
    
    bookmarkSearchIndex = bookmarkedISBN[isbnIndex]
    print(bookmarkSearchIndex)
    print("ini apa")
    bookNumber = booksid.index(bookmarkSearchIndex)
    print(bookNumber)
    print("Judul Buku:" +str(books[bookNumber]))
    print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
    for letter in books[bookNumber]:
        titleBraille = titleBraille + str(asc.convert(letter))
    printedText = str(titleBraille).strip()
    if len(printedText) == 0:
        printedText += " "
        splited.append(printedText)
    elif len(printedText) <= brailleCells:
        splited.append(printedText)
    else:
        splited = split(printedText)
    jsonData['content_1']['Author'] = booksAuthor[bookNumber]
    jsonData['content_1']['BookCover'] = "http://" + ip + "/book/getCover?isbn=" + booksid[bookNumber]
    jsonData['content_1']['Edition'] = booksEdition[bookNumber]
    jsonData['content_1']['Langguage'] = booksLanguage[bookNumber]
    jsonData['content_1']['Title'] = books[bookNumber]
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_1']['Year'] = booksYear[bookNumber]
    jsonData['content_1']['avail'] = bookCount[bookNumber]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille(splited[element])

def prevBookmark():
    global bookNumber,splited, isbnIndex
    splited.clear()
    element = 0
    titleBraille = ""
    if isbnIndex <= 0:
        rw.writeBraille("BOOKMARK PERTAMA")
    else:
        isbnIndex = isbnIndex - 1
    
    bookmarkSearchIndex = bookmarkedISBN[isbnIndex]
    print(bookmarkSearchIndex)
    print("ini apa")
    bookNumber = booksid.index(bookmarkSearchIndex)
    print(books)
    print(booksid)
    print(bookNumber)
    print("Judul Buku:" +str(books[bookNumber]))
    print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
    for letter in books[bookNumber]:
        titleBraille = titleBraille + str(asc.convert(letter))
    printedText = str(titleBraille).strip()
    if len(printedText) == 0:
        printedText += " "
        splited.append(printedText)
    elif len(printedText) <= brailleCells:
        splited.append(printedText)
    else:
        splited = split(printedText)
    jsonData['content_1']['Author'] = booksAuthor[bookNumber]
    jsonData['content_1']['BookCover'] = "http://" + ip + "/book/getCover?isbn=" + booksid[bookNumber]
    jsonData['content_1']['Edition'] = booksEdition[bookNumber]	
    jsonData['content_1']['Langguage'] = booksLanguage[bookNumber]
    jsonData['content_1']['Title'] = books[bookNumber]
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_1']['Year'] = booksYear[bookNumber]
    jsonData['content_1']['avail'] = bookCount[bookNumber]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille(splited[element])
    
def prevNextUSB():
    global bookNumber,splited, usbIndex
    print("ISI SPLITED: ", splited)
    splited.clear()
    print("ISI SPLITED.CLEAR(): ", splited)
    element = 0
    titleBraille = ""
    if usbIndex <= 0:
        rw.writeBraille("file USB PERTAMA")
    else:
        usbIndex = usbIndex - 1
    
    usbBookSearchIndex = listOfUSBbooks[usbIndex]
    print(usbBookSearchIndex)
    print("ini apa")
    bookNumber = booksid.index(usbBookSearchIndex)
    print(books)
    print(booksid)
    print(bookNumber)
    print("Judul Buku:" +str(books[bookNumber]))
    print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
    
    for letter in books[bookNumber]:
        titleBraille = titleBraille + str(asc.convert(letter))
    printedText = str(titleBraille).strip()
    
    if len(printedText) == 0:
        printedText += " "
        splited.append(printedText)
        
    elif len(printedText) <= brailleCells:
        splited.append(printedText)
        
    else:
        splited = split(printedText)
        
    jsonData['content_1']['Author'] = booksAuthor[bookNumber]
    jsonData['content_1']['BookCover'] = ""
    jsonData['content_1']['Edition'] = booksEdition[bookNumber]
    jsonData['content_1']['Langguage'] = booksLanguage[bookNumber]
    jsonData['content_1']['Title'] = books[bookNumber]
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_1']['Year'] = booksYear[bookNumber]
    jsonData['content_1']['avail'] = bookCount[bookNumber]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille(splited[element])
def on_button_click():
    global pageJump
    pageJump = entry.get()
    app.quit


def gotoPage():
    global pageBooks, pageJump, angkaPage, pageNumber, pageIndex,jsonData, maxLine, line, splited
    element = 0

    if pageBooks < 2:
        print("Hanya ada 1 page")
        rw.writeBraille("Hanya ada 1 page")
    else:
        print('lebih dari 1 page')
        rw.writeBraille("masukan halaman")
        buttonClicked == rw.buttonPressed()
        entry = None
        while True:
#             pageJump = input("masukan halaman : ")
#             print(pageJump)
#             print(pageBooks)
#             try:
#                 print('listening for keyboard input...')
#                 while True:
#                     event = keyboard.read_event(suppress=True)
#                     event.append(key)
#                     if event.name == 'enter':
#                         print(f'captured key: {event}')
#                         pageJump = key
#                         print (pageJump)
#                         break
#             except keyboard.KeyboardEvent:
#                 break
#             finally:
#                 keyboard.unhook_all()
            try:
                angkaPage = int(pageJump)
                if angkaPage <= pageBooks:
                    rw.writeBraille('hanya ada satu page')
                    break
                else:
                    rw.writeBraille('input melebihi jmlh page')
            except ValueError:
                rw.writeBraille('input hrs berupa angka')
            
        line=1
        jumpPage(angkaPage-1)
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
            with open(pathJson, 'r') as file:
                jsonData = json.load(file)
        except:
            pass
        

def jumpPage(x):
    global line, lineDisplay, printedText, pageIndex, splited, USBpath, choosenBook, USBin
    splited.clear()  # Clear the list for the new line
    
    element = 0
    print("ini maxline : ",maxLine)
    # Check if it's the last line
    if line == maxLine:
        rw.writeBraille("INI BARIS TERAKHIR BUKU")
    else:
        
        line += 27*x
        pageIndex = x+1
                
        # Check if current line matches a page number
        if pageIndex != len(pageNumber) and line == pageNumber[pageIndex]:
            pageInfo = pageNumber.index(line)
            print("masuk Check if current line matches a page number")
            pageIndex += 1
        
        # Get the text for the current line
#         print("PATH:", USBpath + choosenBook + '.brf')
        if USBin:
            print("MASUK USBIN")
            printedText = str(linecache.getline(USBpath + choosenBook, line)).strip()
        else: 
            printedText = str(linecache.getline(path + booksid[bookNumber] + '.brf', line)).strip()
        print("DEBUK:", printedText)
        print("CURRENT PAGE: ", pageIndex)
        # Split the text if it's too long
        if len(printedText) <= brailleCells:
            splited.append(printedText)
        else:
            splited = split(printedText)
        
        # Display current line and page index
        print("isi baris:", splited[element])
        print("page:", pageIndex)
        
        # Update JSON data
        jsonData['content_2'].update({
            'line': line,
            'maxLine': maxLine,
            'maxPage': pageBooks,
            'page': pageIndex,
            'pageContent': splited[element]
        })
        
        # Write the Braille representation
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData, file, indent=2)
        except:
            pass
        
        rw.writeBraille(splited[element])
     
        
def downloadBook(filename):
    global mode, splited, isBookAvailable, pageIndex
    splited.clear()
    
    if bookNumber == -1:
        rw.writeBraille("SILAHKAN PILIH BUKU")
    else:
        if bookCount[bookNumber] == '0':
#             response = req.patch("http://" + ip + "/book/returnBook", params = {"accessToken": accessToken, "refreshToken": refreshToken, "isbn": filename})
            isBookAvailable = False
            rw.writeBraille("BUKU TIDAK TERSEDIA")
            jsonData['content_1']['Author'] = ""
            jsonData['content_1']['BookCover'] = ""
            jsonData['content_1']['Edition'] = ""
            jsonData['content_1']['Langguage'] = ""
            jsonData['content_1']['Title'] = "BUKU TIDAK TERSEDIA"
            jsonData['content_1']['brailleCell'] = "BUKU TIDAK TERSEDIA"
            jsonData['content_1']['Year'] = ""
            jsonData['content_1']['avail'] = ""
            try:
                with open(pathJson, 'w') as file:
                    json.dump(jsonData,file, indent = 2)
            except:
                pass
        else:
            isBookAvailable = True
            print(filename)
            print(type(filename))
            url = "http://" + ip + "/book/downloadBook"
            destination = Path(path + filename + '.brf')
            response = req.get(url,params = {"accessToken": accessToken, "refreshToken": refreshToken, "isbn": filename})
            valid = response.status_code
            if valid == 404:
                getAccessToken()
                response = req.get(url,params = {"accessToken": accessToken, "refreshToken": refreshToken, "isbn": filename})
            print(len(response.content))
            if len(response.content) == 0:
                pass
            else:
                destination.write_bytes(response.content)
                print(type(response.status_code))
                checkFiles(path +  filename + '.brf')
                string = open(destination).read()
                replace_char = re.sub('', '', string)
                open(destination,'w').write(replace_char)
                print("num line on each page: " + str(pageLineList))
                line = 0
                pageIndex = 0
                page = pageNumber[pageIndex]
                data_line = linecache.getline( path + filename + '.brf', line)
                mode = 2
                jsonData['mode'] = mode
                jsonData['content_2']['line'] = line
                jsonData['content_2']['maxLine'] = maxLine
                jsonData['content_2']['maxPage'] = pageBooks
                jsonData['content_2']['page'] = pageIndex
                jsonData['content_2']['pageContent'] = "selamat membaca"
                jsonData['content_2']['titleBook'] = books[bookNumber]
                try:
                    with open(pathJson, 'w') as file:
                        json.dump(jsonData,file, indent = 2)
                except:
                    pass
                file_path = '/home/pi/Desktop/E-Braille/backupbooks.json'
                try:
                    with open(file_path, 'w') as file:
                        json.dump(filename,file)
                except:
                    pass
                rw.writeBraille("SELAMAT MEMBACA")
    
def quitBook():
    global stateBaca, bookNumber, pageIndex, line, pageLineList, pageNumber, mode, USBin, USBPath, choosenBook
    stateBaca = False
    
    maxLine = 0 
    pageLineList.clear()
    pageNumber.clear()
#     bookNumber = -1
#     page = 1
    pageIndex = 0
    line = 0
    i = 0
    
    print("DECLARE MODE 1")
    print("ERROR BALIK MAIN DISINI")
    
    mode = 1
    jsonData['mode'] = mode
    jsonData['content_1']['Author'] = ""
    jsonData['content_1']['BookCover'] = ""
    jsonData['content_1']['Edition'] = ""
    jsonData['content_1']['Langguage'] = ""
    jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU"
    jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU"
    jsonData['content_1']['Year'] = ""
    jsonData['content_1']['avail'] = ""
    
    print("LEWAT JSON ASSIGNMENT")
    
    rw.writeBraille("SILAHKAN PILIH BUKU")
    
    if USBin:
        jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU di USB"
        jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU di USB"
        rw.writeBraille("SILAHKAN PILIH BUKU di USB")
    else:
        file = path + booksid[bookNumber] + ".brf"
        print(1)
        response = req.patch("http://" + ip + "/book/returnBook", params = {"isbn": booksid[bookNumber]})
        print(2)
    #     valid = response.status_code
    #     if valid == 404:
    #         getAccessToken()
    #         response = req.get(url,params = {"accessToken": accessToken, "refreshToken": refreshToken, "isbn": filename})
    #     print(response)
        print(3)
        os.remove(file)
        
        
#     print("retry")
#     try:
    getBook()
#     except:
#         pass
#     print("done retry")
    file_path = '/home/pi/Desktop/E-Braille/backupbooks.json'
    backupBookData = ""
    try:
        with open(file_path, 'w') as file:
            json.dump(backupBookData,file, indent = 2)
    except Exception as e:
        print("ERROR BACKUPBOOKS:", e)
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except Exception as e:
        print("ERROR OPEN PATH JSON:", e)
    print("file has been deleted.")


def nextLine():
    global line, lineDisplay, printedText, pageIndex, splited, USBpath, choosenBook, USBin
    splited.clear()  # Clear the list for the new line
    
    element = 0
    print("ini maxline : ",maxLine)
    # Check if it's the last line
    if line == maxLine:
        rw.writeBraille("INI BARIS TERAKHIR BUKU")
    else:
        
        line += 1
                
        # Check if current line matches a page number
        if pageIndex != len(pageNumber) and line == pageNumber[pageIndex]:
            pageInfo = pageNumber.index(line)
            print("pageIndex before in nextLine(): ",pageIndex)
            pageIndex += 1
        
        # Get the text for the current line
        print("PATH:", USBpath + choosenBook + '.brf')
        if USBin:
            print("MASUK USBIN")
            printedText = str(linecache.getline(USBpath + choosenBook, line)).strip()
        else: 
            printedText = str(linecache.getline(path + booksid[bookNumber] + '.brf', line)).strip()
        print("DEBUK:", printedText)
        
        # Split the text if it's too long
        if len(printedText) <= brailleCells:
            splited.append(printedText)
        else:
            splited = split(printedText)
        
        # Display current line and page index
        print("isi baris:", splited[element])
        print("page:", pageIndex)
        
        # Update JSON data
        jsonData['content_2'].update({
            'line': line,
            'maxLine': maxLine,
            'maxPage': pageBooks,
            'page': pageIndex,
            'pageContent': splited[element]
        })
        
        # Write the Braille representation
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData, file, indent=2)
        except:
            pass
        
        rw.writeBraille(splited[element])  # Write Braille output for the current line


# def nextLine():
#     global line, lineDisplay, printedText, pageIndex, splited
#     splited.clear()
#     element = 0
#     if line == maxLine:
#         rw.writeBraille("INI BARIS TERAKHIR BUKU")
#     else:
#         line += 1
# 
#         if pageIndex != len(pageNumber) and line == pageNumber[pageIndex]:
#             pageInfo = pageNumber.index(line)
#             pageIndex += 1
#         data_line = linecache.getline( path + booksid[bookNumber] + '.brf', line)
#         printedText = str(data_line).strip()
#         if len(printedText) == 0:
#             printedText += " "
#             splited.append(printedText)
#         elif len(printedText) <= brailleCells:
#             splited.append(printedText)
#         else:
#             splited = split(printedText)
#         
# #         lineDisplay = line % (math.ceil(maxLine / pageBooks))
# #         if lineDisplay == 0:
# #             lineDisplay = lineDisplay + math.ceil(maxLine/pageBooks)
# #         print(lineDisplay)
#         print("isi baris: " + str(splited[element]))
#         print("page: " + str(pageIndex))
#         jsonData['content_2']['line'] = line
#         jsonData['content_2']['maxLine'] = maxLine
#         jsonData['content_2']['maxPage'] = pageBooks
#         jsonData['content_2']['page'] = pageIndex
#         jsonData['content_2']['pageContent'] = splited[element]
#         try:
#             with open(pathJson, 'w') as file:
#                 json.dump(jsonData,file, indent = 2)
#         except:
#             pass
#         rw.writeBraille(splited[element])

def prevLine():
    global line, lineDisplay, printedText, pageIndex,splited
    splited.clear()
    element = 0
    if line > 1:
        if line == pageNumber[pageIndex - 1]:
            pageIndex -= 1
        line -= 1
        
        if USBin:
            print("MASUK USBIN")
            data_line = linecache.getline(USBpath + choosenBook, line)
        else:
            data_line = linecache.getline( path + booksid[bookNumber] + '.brf', line)
        printedText = str(data_line).strip()
        if len(printedText) == 0:
            printedText += " "
            splited.append(printedText)
        elif len(printedText) <= brailleCells:
            splited.append(printedText)
        else:
            splited = split(printedText)
        print("isi baris: " + str(splited[element]))
        print("baris buku: " + str(line))
        print("page: " + str(pageIndex))
        
#         lineDisplay = line % (math.ceil(maxLine / pageBooks))
#         if lineDisplay == 0:
#             lineDisplay = lineDisplay + math.ceil(maxLine/pageBooks)
        jsonData['content_2']['line'] = line
        jsonData['content_2']['maxLine'] = maxLine
        jsonData['content_2']['maxPage'] = pageBooks
        jsonData['content_2']['page'] = pageIndex
        jsonData['content_2']['pageContent'] = splited[element]
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
        except:
            pass
        rw.writeBraille(splited[element])
    else:
        rw.writeBraille("INI BARIS PERTAMA BUKU")

def nextPart():
    global element
    print(element)
    if element < len(splited) - 1:
        print("kondisi 1")
        element += 1
        rw.writeBraille(splited[element])
    if element <= len(splited) - 1:
        print("kondisi 2")
        rw.writeBraille(splited[element])
    if bookNumber < 0:
        print("kondisi 3")
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_2']['pageContent'] = splited[element]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    

def prevPart():
    global element
    if element > 0:
        element -= 1
    if element >= 0:
        print(splited[element])
    if len(splited) < 1:
        splited.append("")
    jsonData['content_1']['brailleCell'] = splited[element]
    jsonData['content_2']['pageContent'] = splited[element]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    rw.writeBraille(splited[element])
    

def bookmark(isbn, bookPage, bookLine):
    global bookmarkList, line, accessToken, refreshToken
    valid = False
    registeredBookmark = False
    print(bookmarkList)
    for i in bookmarkList:
        if isbn in i:
            print("isbn ada")
            i[isbn]["bookPage"] = bookPage
            i[isbn]["bookLine"] = bookLine
            registeredBookmark = True
            output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
            print("bookmark set")
            valid = output.get('status')
            if valid == False:
                getAccessToken()
                print("retry")
                output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
                print("done retry")

            jsonData['content_2']['pageContent'] = "bookmark berhasil"
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
            rw.writeBraille("BOOKMARK BERHASIL")
    if (not registeredBookmark):
        if len(bookmarkList) < 10:
            newBookmark = {isbn:{"bookPage": bookPage, "bookLine": bookLine}}
            bookmarkList.append(newBookmark)
            output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
            valid = output.get('status')
            if valid == False:
                getAccessToken()
                print("retry")
                output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
                print("done retry")
            valid = output.get('status')
            if valid == False:
                getAccessToken()
                print("retry")
                output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
                print("done retry")
            jsonData['content_2']['pageContent'] = "bookmark berhasil"
            try:
                with open(pathJson, 'w') as file:
                    json.dump(jsonData,file, indent = 2)
            except:
                pass
            rw.writeBraille("BOOKMARK BERHASIL")
        elif len(bookmarkList) >= 10:
            rw.writeBraille("apakah anda yakin?")
            jsonData['content_2']['pageContent'] = "apakah anda yakin?"
            try:
                with open(pathJson, 'w') as file:
                    json.dump(jsonData,file, indent = 2)
            except:
                pass
            while True:
                buttonClicked = rw.buttonPressed()
                if buttonClicked == approveBookmark:
                    del bookmarkList[0]
                    newBookmark = {isbn:{"bookPage": bookPage, "bookLine": bookLine}}
                    bookmarkList.append(newBookmark)
                    output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
                    valid = output.get('status')
                    if valid == False:
                        getAccessToken()
                        print("retry")
                        output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkList}).json()
                        print("done retry")
                    jsonData['content_2']['pageContent'] = "bookmark berhasil"
                    try:
                        with open(pathJson, 'w') as file:
                            json.dump(jsonData,file, indent = 2)
                    except:
                        pass
                    rw.writeBraille("BOOKMARK BERHASIL")
                    break
                elif buttonClicked == cancelBookmark:
                    line = line - 1
                    nextLine()
                    break
    
    

def openBookmark():
    global line, pageIndex
    bookmarkAvail = False
    for i in bookmarkList:
        if booksid[bookNumber] in i:
            line = (i[booksid[bookNumber]]["bookLine"]) - 1
            pageIndex = i[booksid[bookNumber]]["bookPage"]
            nextLine()
            bookmarkAvail = True
            break
        else:
            bookmarkAvail = False
    if bookmarkAvail == False:
        rw.writeBraille("BOOKMARK TIDAK ADA")
        jsonData['content_2']['pageContent'] = "BOOKMARK TIDAK ADA"
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
        except:
            pass
    
def nextSearch():
    global bookNumber,splited, searchIndex, bookSearchedTotal, element
    element = 0
    splited.clear()
    titleBraille = ""
    print(bookSearchedTotal)
    if searchIndex >= len(searchedBookTitle)-1:
        rw.writeBraille("BUKU TERAKHIR")
    elif len(searchedBookTitle) == 0:
        rw.writeBraille("TIDAK ADA BUKU")
    else:
        searchIndex = searchIndex + 1
        titleChoosed = searchedBookTitle[searchIndex]
        print("ini apa")
        print(titleChoosed)
        bookNumber = books.index(titleChoosed)
        print(bookNumber)
        print("Judul Buku:" +str(books[bookNumber]))
        print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
        for letter in books[bookNumber]:
            titleBraille = titleBraille + str(asc.convert(letter))
        printedText = str(titleBraille).strip()
        if len(printedText) == 0:
            printedText += " "
            splited.append(printedText)
        elif len(printedText) <= brailleCells:
            splited.append(printedText)
        else:
            splited = split(printedText)
        jsonData['content_3']['index'] = searchIndex
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
        except:
            pass
        rw.writeBraille(splited[element])

def prevSearch():
    global bookNumber,splited, searchIndex, element
    element = 0
    splited.clear()
    titleBraille = ""
    if searchIndex <= 0:
        rw.writeBraille("BUKU PERTAMA")
    elif len(searchedBookTitle) == 0:
        rw.writeBraille("TIDAK ADA BUKU")
    elif searchIndex == -1:
        pass
    else:
        searchIndex = searchIndex - 1
        print(searchIndex)
        print(searchedBookTitle)
        print(searchedBookTitle[searchIndex])
        titleChoosed = searchedBookTitle[searchIndex]
        print("ini apa")
        print(titleChoosed)
        bookNumber = books.index(titleChoosed)
        print(bookNumber)
        print("Judul Buku:" +str(books[bookNumber]))
        print("Ketersediaan Buku:" + str(bookCount[bookNumber]))
        for letter in books[bookNumber]:
            titleBraille = titleBraille + str(asc.convert(letter))
        printedText = str(titleBraille).strip()
        if len(printedText) == 0:
            printedText += " "
            splited.append(printedText)
        elif len(printedText) <= brailleCells:
            splited.append(printedText)
        else:
            splited = split(printedText)
        jsonData['content_3']['index'] = searchIndex
        try:
            with open(pathJson, 'w') as file:
                json.dump(jsonData,file, indent = 2)
        except:
            pass
        rw.writeBraille(splited[element])

def playLegend_SearchBook():
    print("masuk playlegend")
    sound = ""
    playSound("Mode_legend")
    back = 0
    while(True):
        print("masuk while true 1")
        while True:
            tombol = rw.buttonPressed()
            if (tombol):
                break
        if tombol == escButton:
            sound="main_page"
            back = 0
            print("halaman utama")
            print(back)
        elif tombol == showSearched:
            sound="menampilkan_ketikan"
            back = 0
            print(back)
        elif tombol == helpButton:
            sound="help_button"
            back = 0
            print("tombol bantu")
            print(back)
        elif tombol == logoutButton:
            sound="log_out"
            back = 0
            print(back)
        elif tombol == downloadButton:
            sound="read_book"
            back = 0
            print(back)
        elif tombol == legendButtons:
            sound="Mode_membaca"
            back += 1
            print(back)
            #todo-kasih info kalo udah keluar mode legend
            #outro_legend
            if back == 1:
                playSound(sound)
                break
            # sound outro_legend salah, harusnya "keluar dari mode legend."
        elif tombol == showTitle:
            sound = "show_title"
            back = 0
        else:
            sound = "No_function"
            back = 0
            
        
        print(sound)
        playSound(sound)

def playLegend_MainPage():
    print("masuk playlegend_main")
    sound = ""
    playSound("Mode_legend")
    back = 0
    while(True):
        print("masuk while true 1")
        while True:
            tombol = rw.buttonPressed()
            if (tombol):
                break
        if tombol == escButton:
            sound="main_page"
            back = 0
            print("halaman utama")
            print(back)
        elif tombol == searchButton:
            sound="cari_buku"
            back = 0
            print("cari buku")
            print(back)
        elif tombol == openListBookmark:
            sound="show_bookmark"
            back = 0
            print("Tampilkan bookmark")
            print(back)
        elif tombol == helpButton:
            sound="help_button"
            back = 0
            print("tombol bantu")
            print(back)
        elif tombol == usbButton:
            sound="usb_button"
            back = 0
            print("flashdisk")
            print(back)
        elif tombol == usbButton:
            sound="usb_button"
            back = 0
            print("flashdisk")
            print(back)
        elif tombol == logoutButton:
            sound="logout_akun"
            back = 0
            print("keluar akun")
            print(back)
        elif tombol == usbButton:
            sound="usb_button"
            back = 0
            print("flashdisk")
            print(back)
        elif tombol == downloadButton:
            sound="read_book"
            back = 0
            print(back)

        elif tombol == legendButtons:
            sound="Mode_membaca"
            back += 1
            print(back)
            #todo-kasih info kalo udah keluar mode legend
            #outro_legend
            if back == 1:
                playSound(sound)
                break
            # sound outro_legend salah, harusnya "keluar dari mode legend."
        else:
            sound = "No_function"
            back = 0
            
        print(sound)
        playSound(sound)
        
def playLegend_ReadMode():
    print("masuk playlegend")
    sound = ""
    playSound("Mode_legend")
    back = 0
    while(True):
        print("masuk while true 1")
        while True:
            tombol = rw.buttonPressed()
            if (tombol):
                break
        if tombol == escButton:
            sound="main_page"
            back = 0
            print("halaman utama")
            print(back)
        elif tombol == bookmarkButton:
            sound="bookmark_button"
            back = 0
            print(back)
            #BUTTON 4 6?
        elif tombol == openBookmarkButton:
            sound="markline_button"
            back = 0
            print(back)
        elif tombol == showTitle:
            sound="book_content"
            back = 0
            print(back)
        elif tombol == showSearched:
            sound="show_linepage"
            back = 0
            print(back)
        elif tombol == helpButton:
            sound="help_button"
            back = 0
            print("tombol bantu")
            print(back)
        elif tombol == gotopage:
            sound="gotopage_button"
            back = 0
            print(back)
        elif tombol == cancelBookmark:
            sound="cancel_button"
            back = 0
            print(back)
        elif tombol == approveBookmark:
            sound="confirm_button"
            back = 0
            print(back)
        elif tombol == legendButtons:
            sound="Mode_membaca"
            back += 1
            print(back)
            #todo-kasih info kalo udah keluar mode legend
            #outro_legend
            if back == 1:
                playSound(sound)
                break
            # sound outro_legend salah, harusnya "keluar dari mode legend."
        else:
            sound = "No_function"
            back = 0
            
        print(sound)
        playSound(sound)
        
def playSound(mp3Name):
    if mp3Name == "unused":
        print("unused button")
    else:
        pygame.init()
        print(mp3Name)
        file = "/home/pi/Desktop/E-Braille/LegendSound/" + mp3Name + ".mp3" #masuk ke mode legend, tekan tombol untuk mengetahui fungsinya
        print("piiip_mp3")
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.9)

#3173080406010003
    
def detect_flash_drives():
    
    drives = []
    
    for root,dirs,files in os.walk('/media/pi'):
        for directory in dirs:
            if os.path.ismount(os.path.join(root, directory)):
                drives.append(os.path.join(root, directory))
    
    return drives

def searching_usb_book(dir):
    global USBpath, choosenBook, book_files
    books_folder = os.path.join(dir, "books/")
    
    if not os.path.exists(books_folder):
        print("No 'books' folder found.")
        return
    
    book_files = [f for f in os.listdir(books_folder) if f.endswith(".brf")]
    
    if not book_files:
        print("No txt files found in 'books' folder.")
        return
    
    for index, book_file in enumerate(book_files):
        print("[", index, "]", book_file)
    
    # CHECKPOINT 1: BUAT MODE USB, NAMPILIN PILIHAN BUKU
    # ini kebawah diapus
    
    mode = 1
    USBpath = books_folder
    print("bok folder:" , books_folder)
    print("usbparh folder:" , USBpath)

#     choosenBook = book_files[user_int]
#     path = os.path.join(books_folder, choosenBook)
#     print("Reading:", path)
    

    
    
def downloadUSBBook(filename):
    global mode, splited, isBookAvailable, pageIndex
    splited.clear()
    filename = filename[0:len(filename)-4]
    choosenBook = filename

    isBookAvailable = True
    print(filename)
    print(type(filename))
    print("usbparh folder:" , USBpath)
    destination = Path(USBpath + filename + '.brf')
    print (destination)

    print("file cekfile:", USBpath + filename + '.brf')    
    checkFiles(USBpath + filename + '.brf')
    string = open(destination).read()
    replace_char = re.sub('', '', string)
    try:
        open(destination,'w').write(replace_char)
        print("num line on each page: " + str(pageLineList))
    except Exception as error:                    
        print("DEBOK:",error)
    
    line = 0
    pageIndex = 0
    page = pageNumber[pageIndex]
    data_line = linecache.getline( USBpath + filename + '.brf', line)
    mode = 2
    jsonData['mode'] = mode
    jsonData['content_2']['line'] = line
    jsonData['content_2']['maxLine'] = maxLine
    jsonData['content_2']['maxPage'] = pageBooks
    jsonData['content_2']['page'] = pageIndex
    jsonData['content_2']['pageContent'] = "selamat membaca"
    jsonData['content_2']['titleBook'] = books[bookNumber]
    try:
        with open(pathJson, 'w') as file:
            json.dump(jsonData,file, indent = 2)
    except:
        pass
    file_path = '/home/pi/Desktop/E-Braille/backupbooks.json'
    try:
        with open(file_path, 'w') as file:
            json.dump(filename,file)
    except:
        pass
    rw.writeBraille("SELAMAT MEMBACA")
            

            
            
def buttonUp_released_callback(channel):
    #use for previous book or previous line
    print("UP")
    if mode == 1:
        nextPrevBook("prev")
    elif mode == 2:
        prevLine()
    elif mode == 3:
        prevSearch()
    elif mode == 4:
        prevBookmark()

def buttonDown_released_callback(channel):
    #use for next book or next line
    print("Down")
    if mode == 1:
        nextPrevBook("next")
    elif mode == 2:
        nextLine()
    elif mode == 3:
        nextSearch()
    elif mode == 4:
        nextBookmark()

def buttonLeft_released_callback(channel):
    #use for next part
    print("Left")
    prevPart()
    

def buttonRight_released_callback(channel):
    #use for previous part
    print("Right")
    nextPart()
    
GPIO.add_event_detect(buttonUp, GPIO.FALLING,
                      callback=buttonUp_released_callback, bouncetime=1000)
GPIO.add_event_detect(buttonDown, GPIO.FALLING,
                      callback=buttonDown_released_callback, bouncetime=1000)
GPIO.add_event_detect(buttonLeft, GPIO.FALLING,
                      callback=buttonLeft_released_callback, bouncetime=1000)
GPIO.add_event_detect(buttonRight, GPIO.FALLING,
                      callback=buttonRight_released_callback, bouncetime=1000)

if __name__ == '__main__':
    #     MODE:
    #     1. mode 0 = Login Page
    #     2. mode 1 = Select Book
    #     3. mode 2 = Read Book
    #     4. mode 3 = Search Book
    
    #PING ke server sampai terhubung
    print("masuk sini dulu")
    connectionResponse = 1
    while connectionResponse != 0:
        hostname = "192.168.137.254"  
        print("retry")
        connectionResponse = os.system("ping -c 1 " + hostname)
        print("tros masuk sini")
            
        while True:
            print("apakah masuk sini?")
            try:         
                initializeJson(pathJson)
                print("Welcome to Braille Display Ver 1.0")
                mode = 0
                while True:
#                     print("halo")
                    
                        
                    buttonClicked = rw.buttonPressed()
                    #MODE 1
                    if mode == 0: #login process
                        print("masuk sini ga?")
                        file_path = '/home/pi/Desktop/E-Braille/backupbooks.json'
                        try:
                            with open(file_path, 'r') as file:
                                loadedData = json.load(file)
                        except Exception as e:
                            print("Error login page: ", e)
                        req.patch("http://" + ip + "/book/returnBook", params = {"isbn": str(loadedData)})
        #                 print(loadedData)
                        result = readLoginStatus(pathJson)
                        accessToken = result.get("accessToken")
                        refreshToken = result.get("refreshToken")
                        bookmarkListISBN = ((result["bookmarkList"]["msg"]))
                        bookmarkList = list((result["bookmarkList"]["msg"]))
                        print(bookmarkListISBN)
                        print(bookmarkList)
                        getBook()
                        lastBookmark = []
                        for i in bookmarkList:
                            lastBookmark.append(list(i.keys())[0])
                        print(lastBookmark)
                        print(booksid)
                        print(bookmarkListISBN)
                        for i in lastBookmark:
                            if i not in booksid:
                                print(type(i))
                                for j,k in enumerate(bookmarkListISBN):
                                    print(j)
                                    print(k)
                                    if list(k.keys())[0] == i:
                                        bookmarkListISBN.pop(j)
                        print("test")
                        print(bookmarkListISBN)
                        bookmarkList = bookmarkListISBN
                        output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkListISBN}).json()
                        print("sampe sini")
                        print(output)
                        
                        mode = 1
                        jsonData['mode'] = mode
                        jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU"
                        jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU"
                        rw.writeBraille("SILAHKAN PILIH BUKU")
                        try:
                            with open(pathJson, 'w') as file:
                                json.dump(jsonData,file, indent = 2)
                        except:
                            pass
                    
                    # MAINPAGE
                    elif mode == 1: #mode 1 utk ver usb ilangin akses bookmark
                        #Choose your Book
                        if modeFD:
                            print("masuk function USB button")
                            flash_drives = detect_flash_drives()
                            if flash_drives:
                                print("Connected flash drives: ", flash_drives[0])
                                if not USBin:
                                    USBin = True
                                    jsonData['content_1']['Author'] = ""
                                    jsonData['content_1']['BookCover'] = ""
                                    jsonData['content_1']['Edition'] = ""
                                    jsonData['content_1']['Langguage'] = ""
                                    jsonData['content_1']['Title'] = "USB ditemukan, silahkan pilih buku"
                                    jsonData['content_1']['brailleCell'] = "USB ditemukan, silahkan pilih buku"
                                    jsonData['content_1']['Year'] = ""
                                    jsonData['content_1']['avail'] = ""                                    
                                    rw.writeBraille("USB ditemukan, silahkan pilih buku")
                                    
                                    try:
                                        with open(pathJson, 'w') as file:
                                            json.dump(jsonData,file, indent = 2)
                                    except:
                                        pass
                                    searching_usb_book(flash_drives[0])
                                    print("keluar test_usb_book")
                            else:
                                print("tidak ada USB")
                                USBin = False
                                jsonData['content_1']['Author'] = ""
                                jsonData['content_1']['BookCover'] = ""
                                jsonData['content_1']['Edition'] = ""
                                jsonData['content_1']['Langguage'] = ""
                                jsonData['content_1']['Title'] = "PASANG USB ANDA"
                                jsonData['content_1']['brailleCell'] = "PASANG USB ANDA"
                                jsonData['content_1']['Year'] = ""
                                jsonData['content_1']['avail'] = ""        
                                rw.writeBraille("PASANG USB ANDA")
                                try:
                                    with open(pathJson, 'w') as file:
                                        json.dump(jsonData,file, indent = 2)
                                except:
                                    pass
                                    
                            
                        if buttonClicked == downloadButton:
                            if USBin:
                                choosenBook = book_files[choosenNumber]
                                downloadUSBBook(choosenBook)
                            else:
                                print("book downloaded")
                                downloadBook(booksid[bookNumber])
                        elif buttonClicked == helpButton:
                            callHelp()
                        # usb button = 10
                        elif buttonClicked == usbButton or buttonClicked == escButton: #kembali ke mode tanpa USB
                            if buttonClicked == usbButton:
                                modeFD = not modeFD
                            else:
                                modeFD = False
                            
                            if not modeFD:
                                USBin = False
                                book_files.clear()
                                choosenNumber = -1
                                choosenBook = ""
                                
                                mode = 1
                                jsonData['mode'] = mode
                                jsonData['content_1']['Author'] = ""
                                jsonData['content_1']['BookCover'] = ""
                                jsonData['content_1']['Edition'] = ""
                                jsonData['content_1']['Langguage'] = ""
                                jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU"
                                jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU"
                                jsonData['content_1']['Year'] = ""
                                jsonData['content_1']['avail'] = ""
                                rw.writeBraille("SILAHKAN PILIH BUKU")
                                
                                getBook()
                                file_path = '/home/pi/Desktop/E-Braille/backupbooks.json'
                                backupBookData = ""
                                try:
                                    with open(file_path, 'w') as file:
                                        json.dump(backupBookData,file, indent = 2)
                                except:
                                    pass
                                try:
                                    with open(pathJson, 'w') as file:
                                        json.dump(jsonData,file, indent = 2)
                                except:
                                    pass
                                
                        
                        elif buttonClicked == openListBookmark:
                            if not USBin: #pun10  
                                lastBookmark = []
                                getBook()
                                for i in bookmarkList:
                                    lastBookmark.append(list(i.keys())[0])
                                print(lastBookmark)
                                print(booksid)
                                print(bookmarkListISBN)
                                for i in lastBookmark:
                                    if i not in booksid:
                                        print(type(i))
                                        for j,k in enumerate(bookmarkListISBN):
                                            print(j)
                                            print(k)
                                            if list(k.keys())[0] == i:
                                                bookmarkListISBN.pop(j)
                                
                                print(bookmarkListISBN)
                                bookmarkList = bookmarkListISBN
                                output = req.post("http://" + ip + "/book/setBookmark", json = {"accessToken": accessToken, "refreshToken": refreshToken, "userId": nik, "bookmarkInformation": bookmarkListISBN}).json()
                                print("sampe sini")
                                print(output)
                                for i in bookmarkList:
                                    bookmarkedISBN.extend(i.keys())
                                print(bookmarkList)
                                print(bookmarkedISBN)
                                if len(bookmarkList) > 0:
                                    isbnIndex = -1
                                    mode = 4
                                    jsonData['content_1']['Author'] = ""
                                    jsonData['content_1']['BookCover'] = ""
                                    jsonData['content_1']['Edition'] = ""
                                    jsonData['content_1']['Langguage'] = ""
                                    jsonData['content_1']['Title'] = "SILAHKAN PILIH BOOKMARK"
                                    jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BOOKMARK"
                                    jsonData['content_1']['Year'] = ""
                                    jsonData['content_1']['avail'] = ""
                                    rw.writeBraille("SILAHKAN PILIH BOOKMARK")
                                    try:
                                        with open(pathJson, 'w') as file:
                                            json.dump(jsonData,file, indent = 2)
                                    except:
                                        pass
                                    while True:
                                        buttonClicked = rw.buttonPressed()
                                        if buttonClicked == downloadButton:
                                            mode = 2
                                            jsonData['mode'] = mode
                                            try:
                                                with open(pathJson, 'w') as file:
                                                    json.dump(jsonData,file, indent = 2)
                                            except:
                                                pass
                                            print(bookmarkedISBN[isbnIndex])
                                            downloadBook(bookmarkedISBN[isbnIndex])
                                            bookmarkedISBN.clear()
                                            openBookmark()
                                            break
                                        elif buttonClicked == helpButton:
                                            callHelp()
                                        elif buttonClicked == escButton:
                                            mode = 1
                                            jsonData['mode'] = mode
                                            jsonData['content_1']['Author'] = ""
                                            jsonData['content_1']['BookCover'] = ""
                                            jsonData['content_1']['Edition'] = ""
                                            jsonData['content_1']['Langguage'] = ""
                                            jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU"
                                            jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU"
                                            jsonData['content_1']['Year'] = ""
                                            jsonData['content_1']['avail'] = ""
                                            rw.writeBraille("SILAHKAN PILIH BUKU")
                                            bookNumber = -1
                                            bookmarkedISBN.clear()
                                            try:
                                                with open(pathJson, 'w') as file:
                                                    json.dump(jsonData,file, indent = 2)
                                            except:
                                                pass
                                            break
                                else:
                                    jsonData['content_1']['Author'] = ""
                                    jsonData['content_1']['BookCover'] = ""
                                    jsonData['content_1']['Edition'] = ""
                                    jsonData['content_1']['Langguage'] = ""
                                    jsonData['content_1']['Title'] = "Tidak ada BOOKMARK"
                                    jsonData['content_1']['brailleCell'] = "Tidak ada bookmark"
                                    jsonData['content_1']['Year'] = ""
                                    jsonData['content_1']['avail'] = ""
                                    rw.writeBraille("Tidak ada BOOKMARK")
                                    try:
                                        with open(pathJson, 'w') as file:
                                            json.dump(jsonData,file, indent = 2)
                                    except:
                                        pass
                        elif buttonClicked == logoutButton:
                            print("logout")
                            logout()
                            mode = 0
                            #legend button = 9
                        elif buttonClicked == legendButtons:
                            print("masuk function legend button")
                            # legend button audioplay
                            playLegend_MainPage()
                        elif buttonClicked == searchButton:
                            if not USBin: #pun10  
                                mode = 3
                                jsonData['mode'] = mode
                                jsonData["content_3"]["status"] = False
                                jsonData["content_3"]["errorState"] = False
                                jsonData["content_3"]["ListBookData"] = []
                                jsonData["content_3"]["index"] = bookNumber
                                jsonData["content_3"]["title"] = ""
                                rw.writeBraille("masukkan judul")
                                try:
                                    with open(pathJson, 'w') as file:
                                        json.dump(jsonData,file, indent = 2)
                                except:
                                    pass
                        elif buttonClicked == showTitle:
                            bookNumber = bookNumber - 1
                            nextPrevBook("next")
                        else:
                            mode = 1                     
                    #READING PAGE       
                    elif mode == 2:
                        #Reading Mode
                        jsonData["content_2"]["popup"] = False
#                         print("popup false")
                            
                        try:
                            with open(pathJson, 'w') as file:
                                json.dump(jsonData,file, indent = 2)
                        except:
                            pass
                            
                        if buttonClicked == escButton:
                            print("masuk ke halaman utama")
                            quitBook()
                            print("book deleted")
                        elif buttonClicked == helpButton:
                            print("masuk ke help")
                            callHelp()
                        elif buttonClicked == bookmarkButton:
                            bookmark(booksid[bookNumber], pageIndex, line)
                            print("bookmark")
                        elif buttonClicked == openBookmarkButton:
                            openBookmark()
                        elif buttonClicked == showTitle:
                            line = line - 1
                            nextLine()
                        elif buttonClicked == showSearched:
                            tampilanBaris = ""
                            tampilanBarisBraille = ""
                            tampilanHalaman = ""
                            tampilanHalamanBraille = ""
                            for letter in str(line):
        #                     for letter in str(lineDisplay):
                                tampilanBaris = tampilanBaris + str(asc.convert(letter))
                            for letter in str(pageIndex):
                                tampilanHalaman = tampilanHalaman + str(asc.convert(letter))
                            tampilanBarisBraille = "Page #" + re.sub('#', '', tampilanHalaman) + "  Baris #" + re.sub('#', '', tampilanBaris)
                            rw.writeBraille(tampilanBarisBraille)
                            jsonData["content_2"]["pageContent"] = tampilanBarisBraille
                            try:
                                with open(pathJson, 'w') as file:
                                    json.dump(jsonData,file, indent = 2)
                            except:
                                pass
                        #PageButton
                        elif buttonClicked == gotopage:
                            jsonData["content_2"]["popup"] = True                            
                            jsonData['content_2']['pageContent'] = "MASUKKAN HALAMAN"
                            rw.writeBraille("MASUKKAN HALAMAN")

                            print("popup true")
                            
                            try:
                                with open(pathJson, 'w') as file:
                                    json.dump(jsonData,file, indent = 2)
                            except:
                                pass
                            
                            while True:
                                try:
                                    with open(pathJson, 'r') as file:
                                        jsonData = json.load(file)
                                except:
                                    pass
                                gotopageEnter = jsonData['content_2']['popup']
                                if gotopageEnter == False:
                                    pageJump = jsonData['content_2']['gotopage']
                                    gotoPage()
                                    break
                            
                            
                        #legend button = 9
                        elif buttonClicked == legendButtons:
                            print("masuk function legend button")
                            # legend button audioplay
                            playLegend_ReadMode()
                    #SEARCHBOOK PAGE
                    elif mode == 3	:
                        searchedBookTitle = []
                        print("balik kesini")
                        titleSearched = ""
                        rw.writeBraille
                        while True:
                            buttonClicked = rw.buttonPressed()
                            try:
                                with open(pathJson, 'r') as file:
                                    jsonData = json.load(file)
                            except:
                                pass
                            searchEnter = jsonData['content_3']['status']
                            if buttonClicked == escButton:
                                bookNumber = -1
                                mode = 1
                                jsonData['mode'] = mode
                                jsonData['content_1']['Author'] = ""
                                jsonData['content_1']['BookCover'] = ""
                                jsonData['content_1']['Edition'] = ""
                                jsonData['content_1']['Langguage'] = ""
                                jsonData['content_1']['Title'] = "SILAHKAN PILIH BUKU"
                                jsonData['content_1']['brailleCell'] = "SILAHKAN PILIH BUKU"
                                jsonData['content_1']['Year'] = ""
                                jsonData['content_1']['avail'] = ""
                                rw.writeBraille("SILAHKAN PILIH BUKU")
                                try:
                                    with open(pathJson, 'w') as file:
                                        json.dump(jsonData,file, indent = 2)
                                except:
                                    pass
                                break
                            # helpButton = 8
                            elif buttonClicked == helpButton:
                                callHelp()
                            #legend button = 9
                            elif buttonClicked == legendButtons:
                                print("masuk function legend button")
                                # legend button audioplay
                                playLegend_SearchBook()
                            
        
                            elif buttonClicked == downloadButton:
                                if (len(searchedBookTitle)) == 0:
                                    rw.writeBraille("BUKU TIDAK ADA")
                                else:
                                    bookNumber = books.index(searchedBookTitle[searchIndex])
                                    downloadBook(booksid[bookNumber])
                                    if isBookAvailable:
                                        break
                                    else:
                                        pass
                            elif buttonClicked == showSearched:
                                titleConverted = ""
                                for letter in titleSearched:
                                    titleConverted = titleConverted + str(asc.convert(letter))
                                rw.writeBraille(titleConverted)
                            elif buttonClicked == showTitle:
                                searchIndex = searchIndex - 1
                                nextSearch()
                                print(2)
                            if searchEnter == True:
                                getBook()
                                titleSearched = jsonData['content_3']['title']
                                searchedList = getBookSearched(titleSearched)
                                if bookSearchedTotal <= 0:
                                    rw.writeBraille("Tidak ada buku")
                                else:
                                    searchedBookTitle = [item['titles'] for item in searchedList]
                                    searchIndex = -1
                                    nextSearch()
#                         print(searchedBookTitle)        
            except Exception as error:
                req.get("http://" + ip + "/logout", params={"nik": nik}).json()
                initializeJson(pathJson)
                print("ERROR BALIK UTAMA: ", error)



