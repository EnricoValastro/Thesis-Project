# To use on jupyter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

number = np.arange(1,34)

total_time = [
    #To fill with data
]

downtime = [
    #To fill with data
]

data_time = [
    #To fill with data
]

plt.title("Partial Post-copy Migration")
plt.xlabel("Iterazione n.")
plt.ylabel("Tempo medio (s)")
plt.plot(number, total_time, marker='o', label="Total Time")
plt.plot(number, downtime, marker='o', color="green", label="Downtime")
plt.plot(number, data_time, marker='o', color="orange", label="Data Migration")
plt.ylim(0, 7.5)
plt.legend(loc="upper right")