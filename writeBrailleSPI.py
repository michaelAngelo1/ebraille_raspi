import spidev
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
STR = 22 #pin used for STR signal Braille Display
GPIO.setup(STR,GPIO.OUT)

spi_ch = 0
# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.mode = 0
spi.max_speed_hz = 1000

#variable for braille display character
BDlen = 24
inputBDinbyte = int(round(BDlen/8,0))
listVal = []
button = 0

#braille dot pattern for [blank,!,",#,$,%,&,',(,),*,+,,,-,.,/,0,1,2,3,4,5,6,7,8,9,:,;,<,=,>,?,@,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,[,\,],^,_,`,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,{,|,},~,]

brfBdot_pattern=[0,0,0,60,0,0,0,4,
                 0,0,0,0,32,36,0,0,
                 0,2,0,18,50,0,22,54,
                 38,0,0,48,0,0,0,0,0,
                 1,3,9,25,17,11,27,19,
                 10,26,5,7,13,29,21,15,
                 31,23,14,30,37,39,58,45,
                 61,53,0,0,0,0,0,0,1,3,9,
                 25,17,11,27,19,10,26,5,7,
                 13,29,21,15,31,23,14,30,37,
                 39,58,45,61,53,0,0,0,0,0]#length of Braille Char in Braille Display



def solve(s):
    s = list(s)
    if (len(s) % 2 == 1):
        s += " "
    for i in range(0,len(s)-1,2):
        s[i], s[i+1] = s[i+1], s[i]
        
    return ''.join(s)

def readButton():
    global listVal, button
    GPIO.output(STR,GPIO.LOW)
    listVal = spi.readbytes(inputBDinbyte)
#     print(listVal)
    GPIO.output(STR,GPIO.HIGH)
    time.sleep(0.05)
    negated_list = [~x & 0xff for x in listVal]
    listBinary = [format(x,'08b') for x in negated_list]
    intVal = [int(num,2) for num in listBinary]
    concatIntVal = ((intVal[0] << 16) | (intVal[1] << 8) | (intVal[2]))
    intValButton = '{0:024b}'.format(concatIntVal)[::-1]
    button = int(intValButton,2)
#     print(button)

def writeBraille(brailleText):
    newList = []
    newList.clear()
    swapKata = solve(brailleText)
    length = len(swapKata)
    sisa = BDlen - length
    kalimat = swapKata
    for huruf in range(sisa): #for loop untuk menambahkan whitespace hingga jumlah karakter 'sentence' mencapai 42 karakter
        kalimat += " "
    
    ascii_list = [ord(char)-32 for char in kalimat]

    for x in ascii_list:
        newList.append(brfBdot_pattern[x])
    
    GPIO.output(STR,GPIO.HIGH)
    spi.writebytes(newList)
    GPIO.output(STR,GPIO.LOW)
    time.sleep(0.05)
    
def buttonPressed():
    readButton()
    if button != 0:
        while button != 0:
            pressedButton = button
            readButton()
        return pressedButton
# while True:
#     buttonPressed()
#     writeBraille("TEST")
    
    
# while True:
#     readButton()