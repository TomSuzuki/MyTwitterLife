# -*- coding:utf-8 -*-

import os
from os.path import expanduser
import tweepy
import sys
import json
import codecs
import datetime
import random
import subprocess


def getApiInstance(j):

    # 認証ロード
    UserIDData = j
    consumer_key = UserIDData['ConsumerKey']
    consumer_secret = UserIDData['ConsumerSecret']
    access_token_key = UserIDData['AccessToken']
    access_token_secret = UserIDData['AccessTokenSecret']

    # 認証組み立て
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    # 利用制限にひっかかた時に必要時間待機するか？（引っかからないはずなんだけどな...）
    api = tweepy.API(auth, wait_on_rate_limit=True)

    return api


if __name__ == "__main__":
    # 設定
    day_num = 14*2  # 最大の日数
    padding = [0, 2]  # どれくらい周りを起きている判定するか [前, 後]（30分単位 / 2は1時間）
    count_load = 6  # count_load×200ツイートさかのぼる
    time_zone = datetime.timedelta(hours=9)  # 補正時間（全部世界標準時なので）

    # 表示の初期化
    os.system('cls')

    # 設定ファイルの読み込み
    temp = open(expanduser("~") + "/Documents/twitter/mylife/key.json", 'r')
    temp = json.load(temp)
    targetUser = temp['targetUser']
    api = getApiInstance(temp)

    # コマンドラインからIDを指定
    xID = input("User ID: ")
    if(xID != ""):
        targetUser = xID

    # 表示
    print("取得中...", targetUser)

    # 今日は何日
    data = {}
    today = datetime.date.today() + datetime.timedelta(days=1)
    d = today
    for i in range(day_num):
        d = d - datetime.timedelta(days=1)
        data[str(d)] = {}
        data[str(d)]["count"] = 0
        for j in range(24):
            data[str(d)][j] = {}
            data[str(d)][j]["00"] = False
            data[str(d)][j]["30"] = False
    lastDay = datetime.datetime(d.year, d.month, d.day, 23, 59) - datetime.timedelta(days=1)

    # データの読み込み
    all_count = 0
    set_count = 0
    maxID = -1
    t_now = lastDay + datetime.timedelta(days=1)
    while(t_now >= lastDay):
        if maxID == -1:
            t = api.user_timeline(id=targetUser, count=200)
        else:
            t = api.user_timeline(id=targetUser, count=200, max_id=maxID)
        for status in t:
            t_now = time_zone + datetime.datetime(status.created_at.year,
                                                  status.created_at.month, status.created_at.day, status.created_at.hour, status.created_at.minute)
            maxID = status.id
            all_count = all_count + 1
            d = datetime.date(t_now.year, t_now.month, t_now.day)
            h = t_now.hour
            m = int(t_now.minute)
            if m < 30:
                mm = "00"
            else:
                mm = "30"
            # 現在を起きている判定
            if str(d) in data:
                set_count = set_count + 1
                data[str(d)]["count"] = data[str(d)]["count"] + 1
                data[str(d)][h][mm] = True
            # 前後を起きている判定にしていく
            for i in range(2):
                c_d = time_zone + datetime.datetime(status.created_at.year,
                                                    status.created_at.month, status.created_at.day, status.created_at.hour, status.created_at.minute)
                for j in range(padding[i]):
                    c_d = c_d + datetime.timedelta(minutes=30) * [-1, 1][i]
                    p_d = datetime.date(c_d.year, c_d.month, c_d.day)
                    p_h = c_d.hour
                    p_m = int(c_d.minute)
                    if p_m < 30:
                        mm = "00"
                    else:
                        mm = "30"
                    if str(p_d) in data:
                        data[str(p_d)][p_h][mm] = True

    # 表示
    os.system('cls')
    d = today
    line_num = 10 + 3 + 6 + 3 + 2*24 + 2
    weekday = ["月", "火", "水", "木", "金", "土", "日"]
    print("".rjust(line_num, '─'))
    print("".rjust(20, ' ') + "0" + "".rjust(23, ' ') +
          "12" + "".rjust(24, ' ') + "24")
    for i in range(day_num):
        d = d - datetime.timedelta(days=1)
        t = str(d) + " " + weekday[d.weekday()] + \
            " [" + str(data[str(d)]["count"]).rjust(3) + "] | "
        for j in range(24):
            for m in ["00", "30"]:
                if data[str(d)][j][m]:
                    t = t + "#"
                else:
                    t = t + "-"  # ここはコンソールのフォントによって返る
        t = t + " |"
        print(t)

    # 結果
    print("".rjust(line_num, '─'))
    print("ターゲットユーザー", targetUser)
    print("取得したツイート数", all_count)
    print("表示したツイート数", set_count)
    print("1日平均", int(set_count/day_num))
    print("".rjust(line_num, '─'))
    print("ツイート前の起きてる時間", 30*padding[0])
    print("ツイート後の起きてる時間", 30*padding[1])
    print("表示日数", day_num)
