import os

hostname = "192.168.137.253"
response = os.system("ping -c 1 " + hostname)

if response == 0:
    print("success")
else:
    print("failed")