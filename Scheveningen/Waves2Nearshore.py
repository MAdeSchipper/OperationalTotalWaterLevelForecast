import math
import numpy as np

def Waves2Nearshore(d_buoy, H0, Theta0_SN, T, d_inshore_in, gamma_b):
    w = np.ones(len(T))*(2 * np.pi) / T
    k0 = disper(w, d_buoy, 9.81)
    L0 = (2 * math.pi) / k0
    C0 = L0 / T
    n0 = 0.5 * (1 + 2 * k0 * 87. / np.sinh(2 * k0 * d_buoy))
    Cg0 = n0 * C0
    H_inshore = np.zeros(len(H0))
    L_inshore = np.zeros(len(H0))
    d_inshore = np.zeros(len(H0))
    Theta_inshore = np.zeros(len(H0))

    if not np.isnan(d_inshore_in): # for finite values of d_inshore
        #disp('---Nearshore values calculated ---')
        k = disper(w, d_inshore_in, 9.81)
        L = (2 * np.pi) / k
        C = L / T
        n = 0.5 * (1 + 2 * k * d_inshore_in / np.sinh(2 * k * d_inshore_in))
        Cg = n * C
        Theta_inshore = np.arcsin(C / C0 * np.sin(np.deg2rad(Theta0_SN)))

        Ks = np.real(np.sqrt(Cg0 / Cg)) #shoalingcoeff
        Kr = np.real(np.sqrt(np.cos(np.deg2rad(Theta0_SN)) / np.cos(np.deg2rad(Theta_inshore)))) #refcoeff
        H_inshore = Kr * Ks * H0 # waveheight inshore
        if np.isnan(gamma_b):
            H_inshore = min(Kr * Ks * H0, gamma_b * d_inshore_in) # if waves are breaking at 5m waterdepth take the gamma h as waveheight
        d_inshore = np.ones(len(H_inshore)) * d_inshore_in

        L_inshore = ((9.81*np.array(T)**2) / (2*np.pi)) * np.tanh((2*np.pi*d_inshore_in)/L0)

        while any(abs(L0 - L_inshore) > 0.01):
            L_inshore_new = ((9.81*np.array(T)**2) / (2*np.pi)) * np.tanh((2*np.pi*d_inshore_in)/L_inshore)
            L0 = L_inshore_new
            L_inshore = ((9.81*np.array(T)**2) / (2*np.pi)) * np.tanh((2*np.pi*d_inshore_in)/L0)

        return H_inshore, L_inshore, d_inshore, Theta_inshore


    else: # for NaN value of d_inshore calculate values at breakpoint (solved iteratively).
        #disp('--- values at Breakpoint calculated ---')
        h_table = np.arange(0.05, max(H0) / gamma_b * 3, 0.05,) # rangetosearch for breakerdepth
        for i_day in range(0, len(T)):

            if abs(Theta0_SN[i_day]) < 90:
                k_i = disper(w[i_day], h_table, 9.81)
                L_i = (2 * math.pi) / k_i
                C_i = L_i / T[i_day]
                n_i = 0.5 * (1 + 2 * k_i * h_table / np.sinh(2 * k_i * h_table)) #Handle the nan value?!?!?!
                Cg_i = n_i * C_i
                Theta_i = np.arcsin(C_i / C0[i_day] * np.sin(np.deg2rad(Theta0_SN[i_day])))
                Theta_i[np.where(h_table == 0)] = 0 # avoid problems with for depths being equal to 0
                Ks_i = np.sqrt(Cg0[i_day] / Cg_i) #shoalingcoefficient
                Kr_i = np.sqrt(np.cos(np.deg2rad(Theta0_SN[i_day])) / np.cos(np.deg2rad(Theta_i))) #refraction coefficient
                Hs_i = Kr_i * Ks_i * H0[i_day]
                Hs_i[np.where(np.isnan(Hs_i) == True)] = float('inf')

                error = abs(np.array(Hs_i) - gamma_b * np.array(h_table))
                ind = np.argmin(error)

                H_inshore[i_day] = Hs_i[int(ind)]
                d_inshore[i_day] = h_table[int(ind)]
                Theta_inshore[i_day] = Theta_i[int(ind)]
            else:
                H_inshore[i_day] = np.nan
                d_inshore[i_day] = np.nan
                Theta_inshore[i_day] = np.nan

        return H_inshore, L0, d_inshore, Theta_inshore

def disper(w, h, g):
#DISPER Linear dispersion relation.
    w2 = ((w**2) * h) / g
    q = np.divide(w2, (1 - np.exp(-(w2**(5 / 4))))**(2 / 5))
    #print(w2)
    for j in range(1, 2):
        thq = np.tanh(q)
        thq2 = 1 - thq**2
        a = (1 - q * thq) * thq2
        b = thq + q * thq2
        c = q * thq - w2
        arg = (b**2) - 4 * a * c
        arg = (-b + np.sqrt(arg)) / (2 * a)
        iq = np.argwhere(abs(a * c) < 1.0e-8 * (b**2))
        arg[iq] = - c[iq] / b[iq]
        q += arg

    k = np.sign(w) * q / h
    ik = np.isnan(k)
    k[np.where(ik == True)] = 0
    return k

