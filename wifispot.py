import urllib.parse
import requests
import json
import math

def getWifiSpot(cIdo, cKeido):
    url = "https://api.data.metro.tokyo.lg.jp/v1/WifiAccessPoint?limit=1000"

    data = requests.get(url)
    jsondata = json.loads(data.text)
    print(cIdo, cKeido)
    lst = {}
    for dat in jsondata[0]:
        id    = int(dat.get('ID')[0].get('識別値'))
        ssid  = dat.get('ID')[1].get('識別値')
        name  = dat.get('設置地点').get('名称')[0].get('表記')
        ido   = dat.get('設置地点').get('地理座標').get('緯度')
        keido = dat.get('設置地点').get('地理座標').get('経度')

        hs = {'ssid':ssid, 'name':name, 'ido':ido, 'keido':keido}
        lst[id] = hs

    sortedLst = sorted(lst.items(), key=lambda x:x[0])

    dist = {}
    for dic in sortedLst:
        ido = float(dic[1].get('ido'))
        keido = float(dic[1].get('keido'))

        a = pow(cIdo - ido, 2)
        b = pow(cKeido - keido, 2)
        c = math.sqrt(a + b)

        dist[dic[0]] = c
    
    sortedDist = sorted(dist.items(), key = lambda x:x[1])
    print(sortedDist[0])
    print(lst.get(sortedDist[0][0]))
    return (lst.get(sortedDist[0][0]), lst.get(sortedDist[1][0]), lst.get(sortedDist[2][0]))