import numpy as np
import pandas as pd
from datetime import time
from datetime import datetime

def L0_for(T0):
    return (9.81 * np.array(T0)**2) / (2 * np.pi)

def Set_up(gamma_b, H_b):
    return 5/16 * gamma_b * np.array(H_b)

def Run_up21(beta, H0, L0):
    return 1.1 * (0.35*beta*(np.array(H0)*np.array(L0))**0.5 +
                  (np.array(H0)*np.array(L0)*(0.563*beta**2+0.004))**0.5 / 2)

def Run_up22(H0, L0):
    return 0.043 * (H0 * L0) ** 0.5

def not_nan(lst):
    ind = []
    for i in range(len(lst)):
        if not np.isnan(lst[i]):
            ind.append(i)
    return ind

#assume l1 and l2 the same from request deep water and l3 from reqeust waterh2
def overlap(l1, l2, l3):
    overlap = set(l3).intersection(l1)
    ind1 = sorted([l1.index(x) for x in overlap])
    ind2 = sorted([l2.index(x) for x in overlap])
    ind3 = sorted([l3.index(x) for x in overlap])

    l1 = np.array(l1)[ind1]
    l2 = np.array(l2)[ind2]
    l3 = np.array(l3)[ind3]
    return ind1, ind2, ind3, sorted(l1), sorted(l2), sorted(l3)


def animation_frame(i):
    x1_data = []
    y1_data = []

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.set_xlim(0, len(ydata))
    ax.set_ylim(ydata.min(), ydata.max())
    line1, = ax.plot(0, 0, color= color)

    x1_data.append(i)
    y1_data.append(ydata[i])
    line1.set_xdata(x1_data)
    line1.set_ydata(y1_data)
    return line1,

def write_to_excel(file, aft, TWL_exp):
    try:
        sche = pd.read_excel(file, delimiter=',', index_col= 0)
    except:
        sche = pd.DataFrame()
    times = [time(2, 00, 00),time(6, 00, 00),time(10, 00, 00),time(14, 00, 00),
                   time(18, 00, 00),time(22, 00, 00)]
    dates = []
    index = []
    for time2 in times:
        for i in range(len(aft)):
            if time2 == aft.iloc[i].time():
                dates.append(aft.iloc[i])
                index.append(i)
    dates = sorted(dates)
    index = sorted(index)
    TWLexp_xl = np.array(TWL_exp)[index]
    df = pd.DataFrame([TWLexp_xl], columns=dates, index=[datetime.now()])
    df_new = pd.concat([sche, df], ignore_index= False)
    df_new.to_excel(excel_writer= file, header= True, index= True)
    print(f'Wrote to {file} succesfully')

def exp_to_excel(file,datum, parameter):
    try:
        old_data = pd.read_excel(file, delimiter=',', index_col= 0)
    except:
        old_data = pd.DataFrame()
    parameter_xl = np.array(parameter)
    df = pd.DataFrame([parameter_xl], columns=datum, index=[datetime.now()])
    df_new = pd.concat([old_data, df], ignore_index= False)
    df_new.to_excel(excel_writer= file, header= True, index= True)
    print(f'Wrote to {file} succesfully')

def obs_to_excel(file, datum, parameter, name):
    try:
        old_data = pd.read_excel(file, delimiter=',', index_col= 0)
        old_date = old_data['Date'].values
        ind = []
        for i in range(len(datum)):
            if datum[i] not in old_date:
                ind.append(i)
        parameter = parameter[ind]
        datum = datum[ind]
        df = pd.DataFrame(list(zip(datum, parameter)), columns= ['Date', name])
        df_new = old_data.append(df, ignore_index= True, sort='True')
        df_new.to_excel(excel_writer=file, header=True, index=True)
    except:
        df_new = pd.DataFrame(list(zip(datum, parameter)), columns= ['Date', name])
        df_new.to_excel(excel_writer=file, header=True, index=True)
    finally:
        print(f'Wrote to {file} succesfully')
