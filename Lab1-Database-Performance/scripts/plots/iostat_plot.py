import matplotlib.pyplot as plt
import numpy as np

# Δεδομένα από τα iostat samples (δείγματα 4-11 - peak activity)
samples = np.arange(8)

# Write operations per second (w/s)
native_wps = [732, 1760, 2219, 2234, 2932, 3215, 3854, 3271]  # w/s
layered_wps = [642, 1646, 2029, 2314, 3011, 2951, 3664, 3271]
volume_wps = [650, 1586, 2089, 2311, 2729, 3467, 3271, 3271]

# Write throughput (wkB/s)
native_throughput = [3404, 8160, 32388, 35564, 56224, 62576, 86404, 68624]  # kB/s
layered_throughput = [2956, 7804, 29778, 35964, 57228, 57608, 82780, 68624]
volume_throughput = [2992, 7476, 27472, 38023, 48132, 74508, 68624, 68624]

# Disk utilization (%)
native_util = [56.80, 99.60, 93.20, 87.20, 92.40, 94.40, 100.00, 98.80]
layered_util = [59.20, 98.80, 92.67, 97.20, 94.80, 96.80, 99.60, 98.80]
volume_util = [54.40, 98.40, 91.20, 92.28, 97.20, 98.00, 98.80, 98.80]

# Write latency (w_await - ms)
native_latency = [0.08, 0.06, 0.19, 0.21, 0.29, 0.29, 0.34, 0.32]  # ms
layered_latency = [0.07, 0.06, 0.20, 0.22, 0.30, 0.29, 0.34, 0.32]
volume_latency = [0.06, 0.07, 0.19, 0.24, 0.28, 0.33, 0.32, 0.32]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Disk throughput timeline
ax1.plot(samples, [x/1024 for x in native_throughput], label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples, [x/1024 for x in layered_throughput], label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples, [x/1024 for x in volume_throughput], label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Disk Write Throughput Timeline', fontsize=22, fontweight='bold')
ax1.set_xlabel('Δείγματα',fontsize=20)
ax1.set_ylabel('Throughput (MB/s)',fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Average throughput
avg_native_tp = np.mean(native_throughput) / 1024  # MB/s
avg_layered_tp = np.mean(layered_throughput) / 1024
avg_volume_tp = np.mean(volume_throughput) / 1024

scenarios = ['Native', 'Layered', 'Volume']
avg_throughput = [avg_native_tp, avg_layered_tp, avg_volume_tp]

bars = ax2.bar(scenarios, avg_throughput, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέση Disk Write Throughput', fontsize=22, fontweight='bold')
ax2.set_ylabel('Throughput (MB/s)',fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_throughput):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.1f} MB/s', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Disk utilization timeline
ax1.plot(samples, native_util, label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples, layered_util, label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples, volume_util, label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Disk Utilization Timeline', fontsize=22, fontweight='bold')
ax1.set_xlabel('Δείγματα',fontsize=20)
ax1.set_ylabel('Utilization (%)',fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(50, 105)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Write latency comparison
avg_native_lat = np.mean(native_latency)
avg_layered_lat = np.mean(layered_latency)
avg_volume_lat = np.mean(volume_latency)

avg_latency = [avg_native_lat, avg_layered_lat, avg_volume_lat]

bars = ax2.bar(scenarios, avg_latency, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέση Write Latency', fontsize=22, fontweight='bold')
ax2.set_ylabel('Latency (ms)',fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_latency):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{value:.2f} ms', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Write operations per second
ax1.plot(samples, native_wps, label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples, layered_wps, label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples, volume_wps, label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Write Operations per Second', fontsize=22, fontweight='bold')
ax1.set_xlabel('Δείγματα',fontsize=20)
ax1.set_ylabel('Operations/sec',fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Average operations per second
avg_native_ops = np.mean(native_wps)
avg_layered_ops = np.mean(layered_wps)
avg_volume_ops = np.mean(volume_wps)

avg_operations = [avg_native_ops, avg_layered_ops, avg_volume_ops]

bars = ax2.bar(scenarios, avg_operations, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέσες Write Operations/sec', fontsize=22, fontweight='bold')
ax2.set_ylabel('Operations/sec',fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_operations):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.0f}', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()