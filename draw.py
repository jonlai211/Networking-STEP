import matplotlib.pyplot as plt
import pandas as pd

# user + sys
df_all = pd.DataFrame({
    'x_axis': [1, 64, 128, 256, 512, 768, 1024],
    'y_axis': [24.04, 24.739, 26.93, 33.4, 33.972, 40.1, 44.620]
})

# user
df_user = pd.DataFrame({
    'x_axis': [1, 64, 128, 256, 512, 768, 1024],
    'y_axis': [20.114, 20.201, 22.08, 26.70, 25.971, 30.83, 31.790]
})

# sys
df_sys = pd.DataFrame({
    'x_axis': [1, 64, 128, 256, 512, 768, 1024],
    'y_axis': [3.927, 4.538, 4.85, 6.73, 8.0, 10.17, 12.830]
})

# plot
plt.plot('x_axis', 'y_axis', data=df_all, linestyle='-', marker='o')
plt.plot('x_axis', 'y_axis', data=df_user, linestyle='-', marker='o')
plt.plot('x_axis', 'y_axis', data=df_sys, linestyle='-', marker='o')
plt.xlabel("File size(KB)")
plt.ylabel("Runtime(ms)")
plt.legend(["CPU time", "User time", "Sys time"], loc="upper left")
plt.show()
