import matplotlib.pyplot as plt
import numpy as np

# Δεδομένα από τα mpstat samples
timestamps = np.arange(14)  # 14 δείγματα (11:37:10-11:37:24)

# Native CPU utilization
native_user = [0, 0, 61.22, 30.69, 49.0, 53.0, 47.0, 42.42, 23.0, 17.82, 14.0, 14.14, 22.0, 17.82]
native_system = [0, 0, 38.78, 69.31, 49.0, 47.0, 53.0, 56.57, 74.0, 79.21, 84.0, 85.86, 78.0, 81.19]
native_softirq = [0, 0, 0, 0, 2.0, 0, 0, 1.01, 3.0, 2.97, 2.0, 0, 0, 0.99]

# Layered CPU utilization  
layered_user = [0, 0, 55.56, 26.73, 56.0, 43.0, 44.0, 36.0, 11.0, 16.0, 25.0, 21.78, 24.24, 25.0]
layered_system = [0, 0, 43.43, 72.28, 44.0, 56.0, 56.0, 61.0, 87.0, 83.0, 73.0, 76.24, 73.74, 74.0]
layered_softirq = [0, 0, 0, 0.99, 0, 1.0, 0, 3.0, 2.0, 1.0, 2.0, 1.98, 2.02, 1.0]

# Volume CPU utilization
volume_user = [0, 0, 67.68, 31.0, 54.0, 56.44, 38.0, 22.0, 23.0, 15.0, 14.0, 15.0, 19.0, 15.0]
volume_system = [0, 0, 32.32, 68.0, 46.0, 43.56, 61.0, 77.0, 74.0, 85.0, 85.0, 82.0, 79.0, 85.0]
volume_softirq = [0, 0, 0, 1.0, 0, 0, 1.0, 1.0, 3.0, 0, 1.0, 3.0, 2.0, 0]

# Υπολογισμός μέσων όρων
avg_native_user = np.mean(native_user[2:])  # Αγνοούμε τα πρώτα 2 idle samples
avg_native_system = np.mean(native_system[2:])
avg_layered_user = np.mean(layered_user[2:])
avg_layered_system = np.mean(layered_system[2:])
avg_volume_user = np.mean(volume_user[2:])
avg_volume_system = np.mean(volume_system[2:])

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

# Native
ax1.plot(timestamps, native_user, label='% User', color='#2E86AB', linewidth=3, marker='o', markersize=12)
ax1.plot(timestamps, native_system, label='% System', color='#A23B72', linewidth=3, marker='s', markersize=12)
ax1.plot(timestamps, native_softirq, label='% SoftIRQ', color='#F18F01', linewidth=3, marker='^', markersize=12)
ax1.set_title('Native Deployment - CPU Utilization', fontsize=22, fontweight='bold')
ax1.set_ylabel('CPU %', fontsize=18, fontweight='bold')
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 100)
ax1.tick_params(axis='both', which='major', labelsize=14)

# Layered
ax2.plot(timestamps, layered_user, label='% User', color='#2E86AB', linewidth=3, marker='o', markersize=12)
ax2.plot(timestamps, layered_system, label='% System', color='#A23B72', linewidth=3, marker='s', markersize=12)
ax2.plot(timestamps, layered_softirq, label='% SoftIRQ', color='#F18F01', linewidth=3, marker='^', markersize=12)
ax2.set_title('Layered Deployment - CPU Utilization', fontsize=22, fontweight='bold')
ax2.set_ylabel('CPU %', fontsize=18, fontweight='bold')
ax2.legend(fontsize=20)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 100)
ax2.tick_params(axis='both', which='major', labelsize=14)

# Volume
ax3.plot(timestamps, volume_user, label='% User', color='#2E86AB', linewidth=3, marker='o', markersize=12)
ax3.plot(timestamps, volume_system, label='% System', color='#A23B72', linewidth=3, marker='s', markersize=12)
ax3.plot(timestamps, volume_softirq, label='% SoftIRQ', color='#F18F01', linewidth=3, marker='^', markersize=12)
ax3.set_title('Volume Deployment - CPU Utilization', fontsize=22, fontweight='bold')
ax3.set_xlabel('Δείγματα (δευτερόλεπτα)', fontsize=18)
ax3.set_ylabel('CPU %', fontsize=18, fontweight='bold')
ax3.legend(fontsize=20)
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, 100)
ax3.tick_params(axis='both', which='major', labelsize=16)

plt.tight_layout()
plt.show()

# Μέσες τιμές CPU utilization
scenarios = ['Native', 'Layered', 'Volume']
user_means = [avg_native_user, avg_layered_user, avg_volume_user]
system_means = [avg_native_system, avg_layered_system, avg_volume_system]

x = np.arange(len(scenarios))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, user_means, width, label='% User', color='#2E86AB', alpha=0.8)
bars2 = ax.bar(x + width/2, system_means, width, label='% System', color='#A23B72', alpha=0.8)

ax.set_xlabel('Σενάρια Ανάπτυξης', fontsize=22, fontweight='bold')
ax.set_ylabel('Μέση CPU Utilization (%)', fontsize=22, fontweight='bold')
ax.set_title('Σύγκριση Μέσης CPU Utilization', fontsize=24, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=20)
ax.legend(fontsize=20)
ax.grid(True, alpha=0.3, axis='y')
ax.tick_params(axis='both', which='major', labelsize=20)

# Προσθήκη τιμών
for bar, value in zip(bars1, user_means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', 
            ha='center', va='bottom', fontweight='bold',fontsize=20)

for bar, value in zip(bars2, system_means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', 
            ha='center', va='bottom', fontweight='bold',fontsize=20)

plt.tight_layout()
plt.show()

# Υπολογισμός user/system ratio
user_system_ratio = [u/s for u, s in zip(user_means, system_means)]

fig, ax = plt.subplots(figsize=(8, 6))

bars = ax.bar(scenarios, user_system_ratio, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)

ax.set_xlabel('Σενάρια Ανάπτυξης', fontsize=22, fontweight='bold')
ax.set_ylabel('User/System Ratio', fontsize=22, fontweight='bold')
ax.set_title('Αναλογία User vs System CPU Time', fontsize=24, fontweight='bold')
ax.set_xticklabels(scenarios, fontsize=20)
ax.grid(True, alpha=0.3, axis='y')
ax.tick_params(axis='both', which='major', labelsize=20)

# Προσθήκη τιμών
for bar, value in zip(bars, user_system_ratio):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.2f}', 
            ha='center', va='bottom', fontweight='bold', fontsize=20)

plt.tight_layout()
plt.show()