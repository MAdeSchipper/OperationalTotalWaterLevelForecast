from WaveWebScrapeRWS import request_deepwater  # script to grab wavedata from the web
from Waves2Nearshore import \
    Waves2Nearshore  # Script to translate waves from offshore to nearshore (Assumming linear wave theory and uniform depth contours)
from Tide import request_waterh2  # script to grab waterlevel from the web
from Formulas import L0_for, Set_up, Run_up21, Run_up22, not_nan, overlap, write_to_excel, exp_to_excel, obs_to_excel
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import time

## basic parameters
# Target beach properties
schev_or = 315    # [degrees N clockwise] the angle of the shore normal at scheveningen
beta_schev = 1 / 30

# Wave & waterlevel data
EPL = 'EPL'
d_euro = 32
SCHE = 'SCHE'

# Model parameters
gamma_b = 0.86
depth_stockdon = 10

# Download wave and waterlevel data
for iteration in range(10000):

    obs_water_height = 'Waterhoogte___20Oppervlaktewater___20t.o.v.___' \
                       '20Normaal___20Amsterdams___20Peil___20in___20cm'
    waveheight = '4'
    waveperiod = '5'


    # request data
    # Scrape water level at the coast
    date3, tide, wh_observed, surge_exp, wh_expected = request_waterh2(loc=SCHE)
    # Scrape the offshore waveheight
    date1, H0_exp, H0_obs = request_deepwater(loc=EPL, nr=waveheight)
    # Scrape offshore wave direction and period
    date2, T0, theta0 = request_deepwater(loc=EPL, nr=waveperiod)

    #Convert wave angles to shorenormal angles
    schev_or = np.ones(len(theta0)) * schev_or
    Theta0_SN_abs = 180 - abs(abs(theta0 - schev_or) - 180)


    # set H0 correct for data already been and yet to be

    # Get the timetags similar. As date1, date2, date3 are not the same arrays with same times, search there overlap with indexes.
    df1 = pd.DataFrame(data=list(zip(date1, H0_obs, H0_exp)), columns=['date', 'H0_obs', 'H0_exp'])
    df2 = pd.DataFrame(data=list(zip(date2, T0, theta0, Theta0_SN_abs)), columns=['date', 'T0', 'theta0', 'Theta0_SN_abs'])
    df3 = pd.DataFrame(data=list(zip(date3, tide, wh_observed, surge_exp, wh_expected)),
                       columns=['date', 'tide', 'wh_observed', 'surge_exp', 'wh_expected'])
    df4 = df1.merge(df2, on='date')
    df5 = df4.merge(df3, on='date')
    df5['date'] = pd.to_datetime(df5['date'], format='%Y-%M-%dT%H:%M:%S')
    df5['H0'] = np.where(df5['date'] < datetime.now(), df5['H0_obs'], df5['H0_exp'])

    # calculate wave parameters inshore using Waves2Nearshore function with depth at nan for wave break height
    df5['H_break'], df5['L0'] = Waves2Nearshore(d_buoy=d_euro, H0=df5['H0'].values, Theta0_SN=df5['Theta0_SN_abs'].values,
                                                T=df5['T0'].values,
                                                d_inshore_in=np.nan, gamma_b=gamma_b)[0:2]

    df5[f'H_{depth_stockdon}m'], df5[f'L_{depth_stockdon}m'] = Waves2Nearshore(d_buoy=d_euro, H0=df5['H0'].values,
                                                                               Theta0_SN=df5['Theta0_SN_abs'].values,
                                                                               T=df5['T0'].values,
                                                                               d_inshore_in=depth_stockdon,
                                                                               gamma_b=gamma_b)[0:2]

    # Calculate L0, Set-up, and the Run_up
    df5['Irribaren'] = (beta_schev) / np.sqrt(df5['H0'] / df5['L0'])
    df5['wave setup'] = Set_up(gamma_b=gamma_b, H_b=df5['H_break'].values)
    df5['R_2%'] = np.where(df5['Irribaren'] < 0.3,
                           Run_up22(H0=df5[f'H_{depth_stockdon}m'], L0=df5[f'L_{depth_stockdon}m']),
                           Run_up21(beta=beta_schev, H0=df5[f'H_{depth_stockdon}m'], L0=df5[f'L_{depth_stockdon}m']))

    # message
    print('--IGNORE ALL ERRORS ABOVE--')
    df5 = df5.fillna(0)
    df5['MWL'] = np.where(df5['date'] < datetime.now(), df5['wh_observed'] + df5['wave setup'],
                          df5['wh_expected'] + df5['wave setup'])
    df5['TWL'] = df5['MWL'] + df5['R_2%']

    # split between observed and expected
    df6 = df5[df5['date'] <= datetime.now()]
    df6 = df6[df6['H0'] != 0]
    df7 = df5[df5['date'] > datetime.now()]

    # make a plot
    plot = True  # False
    if plot:
        ax = df6.plot('date', 'MWL', color='deepskyblue', label='MWL observed')
        ax2 = df6.plot('date', 'TWL', color='steelblue', label='TWL observed', ax=ax)
        ax3 = df7.plot('date', 'MWL', color='b', label='MWL expected', ax=ax2)
        df7.plot('date', 'TWL', color='navy', label='TWL expected', ax=ax3)
        plt.axvline(datetime.now(), color='k', label=str(datetime.now())[:-10])
        plt.axhline(3, color='r', label='Critical value at 3m NAP')
        plt.ylabel('Waterlevel NAP (m)')
        plt.xlabel('Date')
        plt.legend()
        filename = "OutputImages/Scheveningen_"
        now = datetime.now()
        filename2 = now.strftime("%Y%m%d_%H%M%S")
        plt.savefig(filename + filename2)
        plt.savefig("OutputImages/LatestScheveningen.png")
        # plt.show()
        # The script only coninues automatially if you close the figre. fix that!
        # add a line to print the image as a filename and as a latest

    # Write the data to the Excel files
    write = True
    if write:
        write_to_excel("Excel/Write_to/exp/Horizon.xlsx", aft=df7['date'], TWL_exp=df7['TWL'].values)

        exp_to_excel('Excel/Write_to/exp/H0_exp.xlsx', datum=df7['date'].values, parameter=df7['H0'].values)
        exp_to_excel('Excel/Write_to/exp/T0_exp.xlsx', datum=df7['date'].values, parameter=df7['T0'].values)
        exp_to_excel('Excel/Write_to/exp/obsWL_exp.xlsx', datum=df7['date'].values, parameter=df7['wh_expected'].values)
        exp_to_excel('Excel/Write_to/exp/Theta_exp.xlsx', datum=df7['date'].values, parameter=df7['theta0'].values)

        obs_to_excel('Excel/Write_to/obs/H0_obs.xlsx', datum=df6['date'].values, parameter=df6['H0'].values, name='H0')
        obs_to_excel('Excel/Write_to/obs/T0_obs.xlsx', datum=df6['date'].values, parameter=df6['T0'].values, name='T0')
        obs_to_excel('Excel/Write_to/obs/obsWH_obs.xlsx', datum=df6['date'].values, parameter=df6['wh_observed'].values,
                     name='WH_observed')
        obs_to_excel('Excel/Write_to/obs/Theta0.xlsx', datum=df6['date'].values, parameter=df6['theta0'].values,
                     name='Theta0')
      #  obs_to_excel('Excel/Write_to/obs/Theta0.xlsx', datum=df6['date'].values, parameter=df6['Theta0_SN'].values,
        #             name='Theta0 wrt shorenormal')
        obs_to_excel('Excel/Write_to/obs/TWL.xlsx', datum=df6['date'].values, parameter=df6['TWL'].values, name='TWL')

    print(f'{iteration}st iteration')

    time.sleep(10800)  # wait three hours before updating the excel files

print('ENDED')
