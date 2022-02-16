# -*- coding: utf-8 -*-

# 建物の状態は1のときsleep, 0のとき通常動作, 2の時センサ反応とする
#センサが反応したらR○○○の形で受信する
#android windows が初回起動したらそれぞれ'star'と受信されることとする
#管理端末からのon offはそれぞれ"'建物番号'+'1'or'2'"とする(全建物は000)
#建物はB〇〇〇の形とする

import im_wireless as imw
import csv
import pandas as pd
from datetime import datetime
import time
import requests

SLAVE_ADR = 0x30

iwc = imw.IMWireClass(SLAVE_ADR)

url = "https://notify-api.line.me/api/notify"
token =  "cwhEuTbWg72E6CbRD0sO8SCjNRTvpVM5C5mYHftXsGO"  #トークン番
headers = {'Authorization': 'Bearer ' +token}

def SendLineMessage(message):
    payload = {"message" : message}
    res = requests.post(url, headers = headers, data=payload)
    print(res)
    print("lineに通知しました")

def Send(data):                        #データ送信の関数
    iwc.Write_920('txda'+data)
    print(data)
    
def ChangeBldState(bldnumber,state):             #建物の状態を変化させる関数 引数はstr型 2つのcsv書き換え

    if bldnumber == 'B000':                  #建物全体の場合
        df  = pd.read_csv('datasheet.csv',encoding="utf-8")     #datasheetのcsv書き換え
        df2  = pd.read_csv('bldstate.csv',encoding="utf-8")      #bldstateのcsv書き換え
        print(df)
        print(df2)
        if state == '0':
            df['state'] = 0
            df2['state'] = 0
            
        else:
            df['state'] = 1
            df2['state'] = 1

       
            
    else:                                #各建物の場合
        df  = pd.read_csv('datasheet.csv',encoding="utf-8")
        df2  = pd.read_csv('bldstate.csv',encoding="utf-8")

        df1 = df.query('bldnumber == @bldnumber')          #列を抽出
        df3 = df2.query('bldnumber == @bldnumber')          #列を抽出
        
        if state == '0':
            df.loc[df1.index,"state"] = 0                #状態を0に書き換え
            df2.loc[df3.index,"state"] = 0                #状態を0に書き換え
        elif state == '1':
            df.loc[df1.index,"state"] = 1                #状態を1に書き換え
            df2.loc[df3.index,"state"] = 1                #状態を1に書き換え
        elif state == '2':
            df.loc[df1.index,"state"] = 2                #状態を2に書き換え
            df2.loc[df3.index,"state"] = 2                #状態を2に書き換え

    df.to_csv('datasheet.csv',index=False)              #datasheetのcsv書き換え
    df2.to_csv('bldstate.csv',index=False)             #bldstateのcsv書き換え

    print(df)
    print(df2)

def ChangeSensorState(sensornumber,state):             #センサの状態を変化させる関数

    df  = pd.read_csv('datasheet.csv',encoding="utf-8")
    print(df)
    df1 = df.query('sensornumber == @sensornumber') #行を抽出
    if state == 0:
        df.loc[df1.index,"state"] = 0
        print(df)
    elif state == 1:
        df.loc[df1.index,"state"] = 1
        print(df)
    elif state == 2:
        df.loc[df1.index,"state"] = 2
        print(df)

    df.to_csv('datasheet.csv',index=False)
    print(df)

def CheckBldState(number):        #建物の状態を監視する関数 引数はstr型

    bldnumber = 'B'+number
    df  = pd.read_csv('datasheet.csv',encoding="utf-8")
    df1 = df.query('bldnumber == @bldnumber') #行を抽出
    data = df1.iat[0,3]                #状態を抽出
    return data

def CheckSensorState(sensornumber):        #センサの状態を監視する関数

    df  = pd.read_csv('datasheet.csv',encoding="utf-8")
    df1 = df.query('sensornumber == @sensornumber') #行を抽出
    data = df1.iat[0,3]                #状態を抽出
    return data

def RoomName(sensornumber):        #センサ番号から部屋名を抽出する関数

    df  = pd.read_csv('datasheet.csv',encoding="utf-8")
    df1 = df.query('sensornumber == @sensornumber') #行を抽出
    data = df1.iat[0,2]                #部屋名を抽出
    return data

def BldName(bldnumber):        #建物番号から建物名を抽出する関数

    df  = pd.read_csv('bldstate.csv',encoding="utf-8")
    df1 = df.query('bldnumber == @bldnumber') #行を抽出
    data = df1.iat[0,1]                #建物名を抽出
    return data

def SendSensorData():            #管理端末が起動したときセンサの状態を一括確認し、2の場合その部屋番号を送信する関数

    df  = pd.read_csv('datasheet.csv',encoding="utf-8")
    df1 = df.query('state == 2')       #状態が2の行を抽出
    a = len(df1)                       #抽出した行数
    b = df1.empty                      #データ抽出の結果空かどうか
    print(df1)
    #print(a)
    #print(b)
    if b == False:                    #抽出条件に当てはまるのがある場合
        for num in range(a):          #抽出した行数だけ繰り返す
            data = df1.iat[num,1]     #状態が2の部屋番号を抽出
            #print('2は'+data)
            time.sleep(2)
            Send(data)

def SendBldState():            #管理端末が起動したとき建物の状態を一括確認し、状態を送信する関数
    list = []
    df  = pd.read_csv('bldstate.csv',encoding="utf-8")
    a = len(df)                       #行数
    for num in range(a):          #抽出した行数だけ繰り返す
        data = df.iat[num,2]     #建物の状態を抽出
        list.append(str(data))
    
    print(list)
    data = "".join(list)
    print(data)
    time.sleep(3)
    Send("st"+data)             #st〇〇〇〇の形で状態を送信する


def log(number,name,state):              #データのlogを取る関数
    today = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
    data = [today,number,name,state]
    with open ('log.csv','a',newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data)

    
    

def main():
    print("start")
    while True:
        try:
            rx_data = iwc.Read_920()                    
            if len(rx_data) >= 11:                         
                if (rx_data[2]==',' and    
                    rx_data[7]==',' and rx_data[10]==':'):
                    rx_message = rx_data[11:15]        #受信内容
                    print(rx_data)

                    if rx_message[0] == 'S':     #センサが反応したら
                        sensornumber = rx_message
                        state = CheckSensorState(sensornumber)   #反応した部屋がON状態かOFF状態かの確認
                        if state == 0:                    
                            Send(sensornumber)               #反応したセンサ番号を端末に送信
                            ChangeSensorState(sensornumber,2)            #受信したセンサの状態を2へ変化させる
                            roomname = RoomName(sensornumber)
                            log(sensornumber,roomname,'センサ反応')              #データのログを取る
                            print(roomname)
                            message = '\n『'+roomname+'』で侵入検知しました。'
                            SendLineMessage(message)
                            
                        elif state == 1:                                     
                            print("sleep中です")
                            
                        elif state == 2:
                            print("sensor反応中")
                            
                    elif rx_message =='star':                   #Windows端末が起動したら
                        SendBldState()
                        SendSensorData()                          #部屋の状態を一括確認し、2の場合その部屋番号を送信する

                    else:                                          #端末からonoffが操作されたら
                        bldnumber = 'B'+rx_message[:3]
                        bldstate = rx_message[3]
                        ChangeBldState(bldnumber,bldstate)   #建物の状態を変化させる。ここで状態を'0'か'1'に変化させる
                        Send(rx_message)                            #全体に再送信する
            
                        if bldnumber == 'B000':
                            if bldstate == '0':
                                log(bldnumber,'全体','監視開始')
                            elif bldstate == '1':
                                log(bldnumber,'全体','監視停止')
                        else:
                            bldname = BldName(bldnumber)
                            if bldstate == '0':
                                log(bldnumber,bldname,'監視開始')
                            elif bldstate == '1':
                                log(bldnumber,bldname,'監視停止')

        except Exception as e:
            print(e)

        #finally:                     
            #iwc.gpio_clean()
            #print ('END')

if __name__ == '__main__':
    main()