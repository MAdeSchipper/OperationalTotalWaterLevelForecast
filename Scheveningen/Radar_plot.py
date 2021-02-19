from Formulas import Run_up21, Run_up22, Set_up
import numpy as np
import matplotlib.pyplot as plt

#For run-up21
def Radar_plot21(var1, var2, var3, name):
    var2 = np.ones(len(var1)) * var2
    var3 = np.ones(len(var1)) * var3
    var1 = np.array(var1)
    if var1[0] == 0.02:
        R2 = Run_up21(var1,var2,var3)
    if var1[0] == 0.5:
        R2 = Run_up21(var2,var1,var3)
    else:
        R2 = Run_up21(var3, var2, var1)
    outcome = [1] * len(var1)
    varoutcome = [1] * len(var1)
    for i in range(0, len(R2)):
        if i < len(varoutcome) / 2:
            varoutcome[i] = (var1[i]/var1[len(var1)//2])
            outcome[i] = (R2[i]/R2[len(R2)//2])
        else:
            varoutcome[i] = (var1[i] / var1[len(var1) // 2])
            outcome[i] = (R2[i]/R2[len(R2)//2])
    plt.plot(varoutcome, outcome, 'ro')
    plt.title(f'Run-up sensibility w.r.t to {name}')
    plt.xlabel(f'{name}')
    plt.ylabel('TWL')
    plt.xticks(ticks= varoutcome)
    plt.show()

#For Run-up22
def Radar_plot22(var1, var2, name):
    var2 = np.ones(len(var1)) * var2
    var1 = np.array(var1)
    if var1[0] == 0.375:
        R2 = Run_up22(var1,var2)
    if var1[0] == 1.5:
        R2 = Run_up22(var2,var1)
    outcome = [1] * len(var1)
    varoutcome = [1] * len(var1)
    for i in range(0, len(R2)):
        if i < len(varoutcome) / 2:
            varoutcome[i] = (var1[i]/var1[len(var1)//2])
            outcome[i] = (R2[i]/R2[len(R2)//2])
        else:
            varoutcome[i] = (var1[i] / var1[len(var1) // 2])
            outcome[i] = (R2[i]/R2[len(R2)//2])
    varoutcome = np.array(varoutcome) * 100
    outcome = np.array(outcome) * 100
    plt.plot(varoutcome, outcome, 'ro')
    plt.title(f'Run-up sensibility w.r.t to {name}, 100% at {name} is {var1[len(var1)//2]} s')
    plt.xlabel(f'{name} %')
    plt.ylabel('R2 %')
    plt.xticks(ticks= varoutcome)
    plt.yticks(ticks= outcome)
    plt.show()

beta_l = [0.02, 0.03, 0.04, 0.05, 0.06]
H0_l = [0.375, 0.75, 1.5, 3, 6]
T0_l = [1.5, 3, 6, 12, 24]
beta = 0.4
H0 = 1.5
T0 = 6
name = 'T0'
#Radar_plot21(var1=beta_l, var2=H0, var3=T0, name= name)
Radar_plot22(var1=T0_l, var2= T0, name= name)
