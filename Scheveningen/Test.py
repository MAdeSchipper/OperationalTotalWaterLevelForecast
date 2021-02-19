from Formulas import Run_up21, Run_up22
import pandas as pd
test1 = Run_up21(1/30, 0.488, 40.45)
test2 = Run_up22(0.619, 41.265)

print(test1)
print(test2)

print((1.1+0.8)/(425-340))
betaf = [0.05, 0.04, 0.06, 0.03, 0.06, 0.05, 0.04, 0.02, 0.04, 0.04, 0.07]
print(sum(betaf)/len(betaf))


df1 = pd.DataFrame([1, 2, 3, 4, 5], columns= ['hoi'])
df2 = pd.DataFrame([1, 2, 3, 4, 5, 6], columns= ['hoi'])
df3 = df1.append(df2, ignore_index= True)
print(df3)
