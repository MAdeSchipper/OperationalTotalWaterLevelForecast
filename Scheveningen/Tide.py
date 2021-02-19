import requests
import numpy as np
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def request_waterh(par, loc):
    url = f'https://waterinfo.rws.nl/api/chart?expertParameter={par}&locationCode={loc}&values=-48,48'
    r = requests.get(url).json()

    r2 = r['series'][0]['data']

    dateTime = []
    values = []

    for i in range(len(r2)):
        for key, value in r2[i].items():
            if key == 'dateTime':
                value = value.replace('T', '')
                value = value.replace('Z', '')
                value = datetime.strptime(value, '%Y-%m-%d%H:%M:%S')
                value = value + timedelta(hours=1)
                dateTime.append(value)
            if key == 'value':
                values.append(int(value) / 100)
    return dateTime, values



def request_waterh2(loc):
    url = f'https://waterberichtgeving.rws.nl/wbviewer/maak_grafiek.php?loc={loc}' \
          f'&set=eindverwachting&nummer=1&format=dygraph'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find_all('script', type="text/javascript")

    for d in data:
        d = d.getText()
        k1 = d.find('var unix_times')
        k2 = d.find('var gmt_offset')
        k3 = d.find('var data_')
        k4 = d.find('// add timestamp')
        if k1 > 0:
            unix_times = d[k1:k2]
            wh = d[k3:k4]
    k5 = unix_times.find('[')
    k6 = unix_times.find(']')
    unix_times = unix_times[k5+1:k6].split(',')

    dates = []
    tide = []
    obs_whr = []
    surge_exp = []
    obs_whe = []
    for data in unix_times:
        date = datetime.fromtimestamp(int(data))
        dates.append(date)
    k7 = wh.find('=')
    k8 = wh.find(';')
    wh = wh[k7+4:k8-2].split('],[')
    for w in wh:
        lst = w.split(',')
        tide.append(int(lst[0])/100)
        surge_exp.append(int(lst[2])/100)
        obs_whe.append(int(lst[3])/100)
        try:
            obs_whr.append(int(lst[1])/100)
        except:
            obs_whr.append(np.nan)
    return dates, tide, obs_whr, surge_exp, obs_whe

