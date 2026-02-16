import matplotlib.pyplot as plt
import numpy as np

# Δεδομένα από τα vmstat samples
samples = np.arange(13)  # 13 δείγματα

# Memory usage (σε MB)
native_free = [262, 262, 262, 186, 138, 107, 84, 84, 84, 84, 82, 81, 81]  # free memory
layered_free = [190, 190, 190, 112, 76, 76, 78, 65, 77, 70, 79, 73, 67]
volume_free = [197, 197, 197, 123, 76, 82, 67, 79, 84, 82, 80, 77, 75]

# I/O Activity (blocks in/out per second)
native_bo = [59870, 0, 0, 3404, 8160, 32388, 35564, 56228, 62576, 86404, 81480, 95416, 92976]  # blocks out
layered_bo = [56155, 0, 0, 2956, 7804, 30076, 35964, 57228, 57608, 82784, 54984, 85440, 79008]
volume_bo = [54564, 0, 72, 2992, 7476, 27472, 38404, 48136, 74516, 68624, 70244, 80760, 87032]

# Context switches per second
native_cs = [19000, 239, 200, 37680, 69868, 56308, 54729, 62495, 70629, 84509, 86735, 84488, 91582]
layered_cs = [5076, 353, 304, 36533, 59656, 49701, 53771, 51486, 72466, 97280, 92591, 65201, 85645]
volume_cs = [1800, 434, 396, 35634, 58770, 48512, 49873, 68821, 77965, 83892, 105252, 86598, 86968]

# CPU utilization (%)
native_cpu_user = [6, 0, 0, 61, 31, 50, 52, 47, 42, 23, 18, 14, 14]
native_cpu_system = [53, 0, 0, 39, 69, 50, 48, 53, 58, 77, 82, 86, 86]
layered_cpu_user = [14, 0, 0, 56, 27, 55, 43, 44, 36, 11, 16, 25, 22]
layered_cpu_system = [53, 0, 0, 43, 73, 45, 57, 56, 64, 89, 84, 75, 78]
volume_cpu_user = [15, 0, 0, 68, 31, 55, 56, 38, 22, 23, 15, 14, 15]
volume_cpu_system = [52, 0, 0, 32, 69, 45, 44, 62, 78, 77, 85, 86, 85]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Free memory timeline
ax1.plot(samples, native_free, label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples, layered_free, label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples, volume_free, label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Free Memory Timeline', fontsize=22, fontweight='bold')
ax1.set_xlabel('Δείγματα',fontsize=20)
ax1.set_ylabel('Free Memory (MB)',fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Average free memory
avg_native_mem = np.mean(native_free[3:])  # Active phase
avg_layered_mem = np.mean(layered_free[3:])
avg_volume_mem = np.mean(volume_free[3:])

scenarios = ['Native', 'Layered', 'Volume']
avg_memory = [avg_native_mem, avg_layered_mem, avg_volume_mem]

bars = ax2.bar(scenarios, avg_memory, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέση Free Memory (Active Phase)', fontsize=22, fontweight='bold')
ax2.set_ylabel('Free Memory (MB)',fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_memory):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{value:.0f}MB', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# I/O throughput timeline (blocks out per second)
ax1.plot(samples[3:], native_bo[3:], label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples[3:], layered_bo[3:], label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples[3:], volume_bo[3:], label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Disk Write Activity (Blocks Out/sec)', fontsize=22, fontweight='bold')
ax1.set_xlabel('Δείγματα',fontsize=20)
ax1.set_ylabel('Blocks Out per Second', fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Average I/O throughput
avg_native_io = np.mean(native_bo[3:])
avg_layered_io = np.mean(layered_bo[3:])
avg_volume_io = np.mean(volume_bo[3:])

avg_io = [avg_native_io, avg_layered_io, avg_volume_io]

bars = ax2.bar(scenarios, avg_io, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέση Disk Write Throughput', fontsize=22, fontweight='bold')
ax2.set_ylabel('Blocks Out per Second', fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_io):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{value/1000:.0f}K', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Context switches timeline
ax1.plot(samples[3:], native_cs[3:], label='Native', color='#2E86AB', linewidth=3, marker='o', markersize=10)
ax1.plot(samples[3:], layered_cs[3:], label='Layered', color='#A23B72', linewidth=3, marker='s', markersize=10)
ax1.plot(samples[3:], volume_cs[3:], label='Volume', color='#F18F01', linewidth=3, marker='^', markersize=10)
ax1.set_title('Context Switches per Second', fontsize=20, fontweight='bold')
ax1.set_xlabel('Δείγματα', fontsize=20)
ax1.set_ylabel('Context Switches/sec', fontsize=20)
ax1.legend(fontsize=20)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=16)

# Average context switches
avg_native_cs = np.mean(native_cs[3:])
avg_layered_cs = np.mean(layered_cs[3:])
avg_volume_cs = np.mean(volume_cs[3:])

avg_context_switches = [avg_native_cs, avg_layered_cs, avg_volume_cs]

bars = ax2.bar(scenarios, avg_context_switches, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Μέσες Context Switches', fontsize=20, fontweight='bold')
ax2.set_ylabel('Context Switches/sec',fontsize=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.tick_params(axis='both', which='major', labelsize=16)

for bar, value in zip(bars, avg_context_switches):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{value/1000:.0f}K', 
            ha='center', va='bottom', fontweight='bold',fontsize=16)

plt.tight_layout()
plt.show()