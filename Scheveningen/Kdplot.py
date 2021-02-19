import pandas as pd
from Formulas import L0_for, Set_up, Run_up22, Run_up21
from Waves2Nearshore import Waves2Nearshore
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sbn

beta_schev = 1/30

obs_WL = pd.read_csv('Excel/OBS_WL_2017_2020.csv', delimiter = ';', encoding = "ISO-8859-1")
WL = obs_WL['NUMERIEKEWAARDE'].values
obs_WL['Datum'] = obs_WL['WAARNEMINGDATUM'] + ' ' + obs_WL['WAARNEMINGTIJD']
d1 = obs_WL['Datum'].values

Theta0 = pd.read_csv('Excel/Theta0_2017_2020.csv', delimiter = ';')
Th0 = Theta0['NUMERIEKEWAARDE'].values
Theta0['Datum'] = Theta0['WAARNEMINGDATUM'] + ' ' + Theta0['WAARNEMINGTIJD']
d2 = Theta0['Datum'].values

df1 = pd.DataFrame(list(zip(d1, WL)), columns=['Datum', 'Water level'])
df2 = pd.DataFrame(list(zip(d2, Th0)), columns=['Datum', 'Theta0'])

df3 = df1.merge(df2, on='Datum')
df3['Datum'] = pd.to_datetime(df3['Datum'], format= '%d-%m-%Y %H:%M:%S')

H0 = pd.read_excel('Excel/H0_matroos.xlsx', skiprows = 4)
del H0['analysis time']
df4 = pd.DataFrame.rename(H0, columns= {'reference time': 'Datum', 'Unnamed: 1': 'H0'})

T0 = pd.read_excel('Excel/T0_matroos.xlsx', skiprows = 4)
del T0['analysis time']
df5 = pd.DataFrame.rename(T0, columns= {'reference time': 'Datum', 'Unnamed: 1': 'T0'})


df6 = df4.merge(df5, on='Datum')
df6['Datum'] = pd.to_datetime(df6['Datum'], format= '%Y-%m-%d %H-%M-%S')

total = df6.merge(df3, on= 'Datum')

total['H0'] = total['H0'].astype(float)
total['T0'] = total['T0'].astype(float)
total['L0'] = L0_for(T0= total['T0'])
total['Theta0'] = total['Theta0'].astype(float) - 310
total['Water level'] = total['Water level'].astype(float) / 100
total = total.drop((total[(total['Water level'] > 1000) | (total['Theta0'] > 1000) | (total['H0'] > 100) | (total['T0'] > 100)].index))

total['Irribaren'] = (beta_schev) / np.sqrt(total['H0']/total['L0'])
Irb_03 = ((total[total["Irribaren"] >= 0.3]["Irribaren"].count())/len(total))*100


total['gamma_b'] = 1.062 + 0.137 * np.log(total['Irribaren'])
gb = total['gamma_b'].mean()

H_inshore, d_inshore, Theta_inshore = Waves2Nearshore(d_buoy= 32, H0 = total['H0'].values,
                                                      Theta0 = total['Theta0'].values, T= total['T0'].values,
                                                      d_inshore_in = np.nan, gamma_b= gb)
print('-- IGNORE ALL ERRORS ABOVE --')
total['H_inshore'] = H_inshore
total.loc[np.isnan(total['H_inshore']), 'H0'] = 0
total.loc[np.isnan(total['H_inshore']), 'T0'] = 0
total.loc[np.isnan(total['H_inshore']), 'H_inshore'] = 0

total['Set up'] = Set_up(gamma_b= 0.88, H_b= total['H_inshore'])
total['MWL'] = total['Water level'] + total['Set up']

total['Run-up_2'] = np.where(total['Irribaren'] < 0.3, Run_up22(H0= total['H0'], L0= total['L0']),
                             Run_up21(beta= beta_schev, H0= total['H0'], L0= total['L0']))

total['TWL'] = total['MWL'] + total['Run-up_2']

plt.hist(total['TWL'], bins= np.arange(-2, 6, 0.2), density= True, color= 'b')
plt.title(f'Probability histogram from {total["Datum"].iloc[0]}'
          f' till {total["Datum"].iloc[0-1]}')
x = np.linspace(-2, 4, 1000)
mu = np.mean(total['TWL'])
sig = np.std(total['TWL'])
y = norm.pdf(x, mu, sig)
plt.plot(x, y, 'r')
plt.axvline(4.5, color= 'r')
sbn.kdeplot(total['TWL'], color= 'k', shade= True)
plt.xlabel('Total water level NAP (m)')
plt.ylabel('probability')
plt.show()

plt.hist(total['TWL'], bins= np.arange(-2, 6, 0.01), density= True, color= 'b', cumulative= -1)
plt.xlabel('Total water level NAP (m)')
plt.ylabel('probability')
plt.title('Probability of exceeding a certain TWL')
plt.show()

print(f'The percentage with the Irribaren number bigger than 0.3 is: '
      f'{round(Irb_03,3)}%')

print(f'The mean value for gamma_b is {round(gb,2)}')

print(f'The maximum value of the TWL is: {max(total["TWL"])}')
print(f'The minimum value of the TWL is: {min(total["TWL"])}')

def probexc(mNAP):
    count = total[total['TWL'] >= mNAP]['TWL'].count()
    perc = count / len(total) * 100
    return round(perc, 3)

perc4_5 = probexc(4.5)
print(f'The probability of exceeding 4.5m NAP is {perc4_5} %')
perc1 = probexc(1)
print(f'The probability of exceeding 1m NAP is {perc1} %')
