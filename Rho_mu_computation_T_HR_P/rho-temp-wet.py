import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

""" Computation of the dynamic viscosity"""

# According to https://www.researchgate.net/publication/334710761_Humidification_Effect_on_Humid_air_viscosity
def PS(T):
    # T is in celcius, this formula is valid between -50 and 200 C
    return np.exp(46.784 - (6435)/(T+273.15) - 3.868*np.log2(T+273.15))

def mu_v(T):
    return (3.01472*10**-6)/(1 + (673/(T+273.15)))*np.sqrt((T+273.15)/273.15)

def mu_a(T):
    return 10**-5*(0.0046*T+1.7176)

def mu(T, HR, PT):
    mua = mu_a(T)
    muv = mu_v(T)
    ps = PS(T)
    return (9.81*10**5)/((HR*ps)/muv + (PT-HR*ps)/mua)

def rho_gp(T, PT):
    return PT/(287.05*(T+273.15))

"""Computation of the density"""
# According to https://fr.wikipedia.org/wiki/Masse_volumique_de_l%27air

Rs = 287.06 
Rv = 461
def rho(HR, T, PT):
    return 1/(Rs*(T + 273.15))*(PT-230.617*HR*np.exp((17.5043*T)/(241.2+T)))
# According to https://www.meteoblue.com/en/weather/archive/export?daterange=2024-01-01%20-%202025-06-09&locations%5B%5D=basel_switzerland_2661604&domain=ERA5T&params%5B%5D=&params%5B%5D=temp2m&params%5B%5D=&params%5B%5D=relhum2m&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&utc_offset=%2B00%3A00&timeResolution=hourly&temperatureunit=CELSIUS&velocityunit=KILOMETER_PER_HOUR&energyunit=watts&lengthunit=metric&degree_day_type=10%3B30&gddBase=10&gddLimit=30
# we can find HR_inf and HR_sup
HR_inf = 0.475 # 06/04/2025
HR_sup = 0.963 # 11/02/2025
HR = np.linspace(HR_inf, HR_sup, 20)
T_inf = -5
T_sup = 35
T = np.linspace(T_inf, T_sup, 20)

# According to https://www.meteoblue.com/en/weather/archive/export?daterange=2024-01-01%20-%202025-06-09&locations%5B%5D=basel_switzerland_2661604&domain=ERA5T&params%5B%5D=&params%5B%5D=temp2m&params%5B%5D=&params%5B%5D=relhum2m&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&params%5B%5D=&utc_offset=%2B00%3A00&timeResolution=hourly&temperatureunit=CELSIUS&velocityunit=KILOMETER_PER_HOUR&energyunit=watts&lengthunit=metric&degree_day_type=10%3B30&gddBase=10&gddLimit=30
# we can find HR_inf and HR_sup
p_inf = 98750 # value of 10/02/2024
p_sup = 103910 # value of 13/01/2025
p = np.linspace(p_inf, p_sup, 20)
plt.plot(T, rho(0, T, 101325), label="rho dry air, p=101325 Pa")
plt.plot(T, rho(0, T, 98750), label="rho dry air, p=98750 Pa extreme value of the 10/02/2024")
plt.plot(T, rho(0, T, 103910), label="rho dry air, p=103910 Pa extreme value of the 13/01/2025")
plt.xlabel("Temperature (C)")
plt.ylabel("Density (kg/m3)")
plt.title("Density of dry air as a function of temperature for different pressures")
plt.legend()
plt.show()

plt.plot(T, rho(0.5, T, 101325), label="rho humid air, p=101325 Pa")
plt.plot(T, rho(0.5, T, 98750), label="rho humid air, p=98750 Pa extreme value of the 10/02/2024")
plt.plot(T, rho(0.5, T, 103910), label="rho humid air, p=103910 Pa extreme value of the 13/01/2025")
plt.xlabel("Temperature (C)")
plt.ylabel("Density (kg/m3)")
plt.title("Density of humid air (HR=0.5) as a function of temperature for different pressures")
plt.legend()
plt.show()

plt.plot(T, rho(1, T, 101325), label="rho humid air, p=101325 Pa")
plt.plot(T, rho(1, T, 98750), label="rho humid air, p=98750 Pa extreme value of the 10/02/2024")
plt.plot(T, rho(1, T, 103910), label="rho humid air, p=103910 Pa extreme value of the 13/01/2025")
plt.xlabel("Temperature (C)")
plt.ylabel("Density (kg/m3)")
plt.title("Density of humid air (HR=1) as a function of temperature for different pressures")
plt.legend()
plt.show()


def factRe(rho, nu):
    """Computation of the Reynolds factor"""
    return rho/nu

ordo = np.zeros((20, 20, 20))
def compute(ordo):

    for i in range(len(p)):
        for j in range(len(T)):
            for k in range(len(HR)):
                if(factRe(rho(HR[k], T[j], p[i]), mu(T[j], HR[k], p[i])) < 0):
                    print(f"T = {T[j]}, p = {p[i]}, HR = {HR[k]} \n")
                    print(f"rho = {rho(HR[k], T[j], p[i])} \n")
                    return 0
                ordo[i, j, k] = factRe(rho(HR[k], T[j], p[i]), mu(T[j], HR[k], p[i]))


compute(ordo)
indiceM = np.unravel_index(np.argmax(ordo, axis=None), ordo.shape)
maxvalue = np.max(ordo)
print(f"p = {indiceM[0]*(p_sup-p_inf)/20 + p_inf}, T = {indiceM[1]*(T_sup-T_inf)/20 + T_inf}, HR = {indiceM[2]*(HR_sup - HR_inf)/20 + HR_inf}")
print(f"argmax {np.unravel_index(np.argmax(ordo, axis=None), ordo.shape)}, value = {maxvalue} \n")
print("############## \n")
indicem = np.unravel_index(np.argmin(ordo, axis=None), ordo.shape)
minvalue = np.min(ordo)
print(f"p = {indicem[0]*(p_sup-p_inf)/20 + p_inf}, T = {indicem[1]*(T_sup-T_inf)/20 + T_inf}, HR = {indicem[2]*(HR_sup - HR_inf)/20 + HR_inf}")
print(f"argmin {np.unravel_index(np.argmin(ordo, axis=None), ordo.shape)}, value = {minvalue} \n")
print("############## \n")
print(f"theo factor factor = {np.max(ordo)/np.min(ordo)}")

"""we can see that the pressure seems to be the main factor so lets compare the value of the factor between the 10/02/2024 and 13/01/2025"""

print(f"ratio between  10/02/2024 and 13/01/2025 = {factRe(rho(0.797, -2.2, 103910), mu(-2.2, 0.797, 103910))/factRe(rho(0.937, 9.4, 98750), mu(9.4, 0.937, 98750))}")


"""Let s compute the evolution of the factor during the last year in ferrol"""


# Path to the CSV file
file_path = "dataexport_20250609T110413.csv"

# Read the CSV file, skipping the first 5 rows
df = pd.read_csv(file_path, skiprows=5)

# Rename columns for clarity
df.columns = ['datetime', 'temperature', 'humidity', 'pressure']

# Convert columns to the correct format
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
df['pressure'] = pd.to_numeric(df['pressure'], errors='coerce')

# Supprimer les lignes avec des valeurs manquantes
df = df.dropna()

# Extract data in np array
dates = np.array(df['datetime'].tolist())
temperatures = np.array(df['temperature'].tolist())
humidity = np.array(df['humidity'].tolist())*10**-2 #to have the humidity between 0 and 1
presure = np.array(df['pressure'].tolist())*10**2 #to have pressure in pascal

print(humidity[3:])

history_factor = np.zeros_like(dates)
#compute factor

history_factor = factRe(rho(humidity, temperatures, presure), mu(temperatures, humidity, presure))
history_factor_min = np.min(history_factor)
dimless_fact = history_factor / history_factor_min

#compute factor withou humidity
meam_humidity = np.mean(humidity)
history_factor_without_h = np.zeros_like(dates)
history_factor_without_h = factRe(rho(meam_humidity, temperatures, presure), mu(temperatures, meam_humidity, presure))
dimless_fact_wh = history_factor_without_h / history_factor_min
print("############## \n")
print(f"Mean HR = {meam_humidity}\n")
#compute factor withou humidity and temperature
mean_temp = np.mean(temperatures)
history_factor_without_h_t = np.zeros_like(dates)
history_factor_without_h_t = factRe(rho(meam_humidity, mean_temp, presure), mu(mean_temp, meam_humidity, presure))

dimless_fact_wht = history_factor_without_h_t / history_factor_min
#compute factor with ideal gas law
factor_gp = factRe(rho_gp(temperatures, presure), mu(temperatures, meam_humidity, presure))
dimless_fact_gp = factor_gp / history_factor_min
# plot
plt.plot(dates, dimless_fact, label="Full model")
plt.plot(dates, dimless_fact_wh, label="history without humidity")
plt.plot(dates, dimless_fact_wht, label="history without humidity and temp")
#plt.plot(dates, dimless_fact_gp, label="ideal gas model")
plt.title("Evolution of the rho/mu factor in ferrol between the 01/01/2024 and 06/09/2025")
plt.xlabel("date")
plt.ylabel("dimesionless rho/mu")
plt.legend()
plt.show()

# plot humidity error 
plt.plot(dates, (history_factor - history_factor_without_h)/history_factor*100, label="error")
plt.title("Estmation error of the factor rho/mu with and without humidity")
plt.ylabel("Error in %")
plt.xlabel("Date")
plt.show()

# plot gp error
plt.plot(dates, (history_factor - factor_gp)/history_factor*100, label="error")
plt.title("Estmation error of the factor rho/mu with full model and ideal gas law")
plt.ylabel("Error in %")
plt.xlabel("Date")
plt.show()
