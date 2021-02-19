# Read data from the long term wave model (~ 9 days ahead) from Rijkswaterstaat.
# website visible here: https://waterberichtgeving.rws.nl/water-en-weer/verwachtingen-water/water-en-weerverwachtingen-waternoordzee/wind-en-golven
# Example data: https://waterberichtgeving.rws.nl/wbviewer/maak_grafiek.php?loc=SCH&set=wigo&nummer=4&page_type=tabel

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import numpy as np


def request_deepwater(loc, nr):
    url = f'https://waterberichtgeving.rws.nl/wbviewer/maak_grafiek.php?loc={loc}&set=wigo&nummer={nr}&page_type=tabel'
    #print('even kijken welke we nu downloaden')
    #print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser').prettify()

    w = 'records'
    soup.replace('recid', "recid")
    i1 = soup.find(w)
    d = soup[i1+len(w)+3:]
    i2 = d.find(']') # end of webpage starts with the ] part
    data = d[:i2] # chopthat end part off
    # Remaining data is table with rows like this:   {recid: 1, datetime: '2020-04-15 11:00', col0: 1, col1: 6},
    datalist = data.split('},\n') # reformat tabledata from rows to a single string
    date1, date2 = [], []
    var1, var2 = [], []
    var3, var4 = [], []

    for line in datalist[:-1]:
        ls = line.strip()
        l2 = ls.split(',')
        date1.append(l2[1],)
        if nr == '4':
            var1.append(l2[2])
            var3.append(l2[4])
        if nr == '5':
            var3.append(l2[2])
            var1.append(l2[3])

    for v in var1:
        v2 = v.split(':')
        if nr == '4':
            var2.append(int(v2[1].strip()) / 100)
        else:
            var2.append(int(v2[1].strip()))

    if nr =='4': # Parser special for waveheight
        for v3 in var3:
            v2 = v3.split(':')
            try:
                var4.append(int(v2[1].lstrip())/100)
            except:
                var4.append(np.nan)

    if nr == '5': # Parser special for direction and period
        for t in var3:
            t2 = t.split(':')
           # var4.append(int(t2[1].strip()) - orientation)
            var4.append(int(t2[1].strip()))

    for d in date1:
        d2 = d.split(':')
        date = d2[1] +':'+ d2[2]
        date = datetime.strptime(date, "'%Y-%m-%d %H:%M'")
        date2.append(date)
    #print(var2)
    #print(var4)
    return date2, var2, var4


