import matplotlib.pyplot as plt
import numpy as np

# Δεδομένα από τα perf stat
scenarios = ['Native', 'Layered', 'Volume']

# Βασικά metrics
execution_time = [78.79, 82.58, 82.93]  # seconds
throughput_ops = [7898.48, 7465.27, 7487.22]  # από το CSV

# CPU Utilization
task_clock = [18165.01, 19086.66, 18395.99]  # msec
context_switches = [509492, 509255, 508891]  # count

# CPU Efficiency
instructions = [44261814520, 47872255346, 43681657845]  # count
cycles = [61525628961, 65221913466, 63172401809]  # count
ipc = [0.72, 0.73, 0.69]  # instructions per cycle

# Cache Performance
l1_dcache_load_misses = [1478111654, 1586097629, 1450351994]  # count
l1_dcache_loads = [20851096772, 23347424155, 21509973072]  # count
l1_miss_rate = [7.09, 6.79, 6.74]  # percentage

# TLB Performance
dtlb_miss_rate = [25.98, 24.75, 24.31]  # percentage

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Χρόνος εκτέλεσης
bars1 = ax1.bar(scenarios, execution_time, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax1.set_title('Χρόνος Εκτέλεσης', fontsize=14, fontweight='bold')
ax1.set_ylabel('Δευτερόλεπτα', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')

# Throughput
bars2 = ax2.bar(scenarios, throughput_ops, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('Throughput (ops/sec)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Operations/sec', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

# Προσθήκη τιμών
for bar, value in zip(bars1, execution_time):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{value:.2f}s', 
             ha='center', va='bottom', fontweight='bold')

for bar, value in zip(bars2, throughput_ops):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f'{value:.0f}', 
             ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Instructions per Cycle (IPC)
ax1.bar(scenarios, ipc, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax1.set_title('Instructions per Cycle (IPC)', fontsize=14, fontweight='bold')
ax1.set_ylabel('IPC', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')

# L1 Data Cache Miss Rate
ax2.bar(scenarios, l1_miss_rate, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax2.set_title('L1 Data Cache Miss Rate', fontsize=14, fontweight='bold')
ax2.set_ylabel('Miss Rate (%)', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

# D-TLB Miss Rate
ax3.bar(scenarios, dtlb_miss_rate, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax3.set_title('D-TLB Miss Rate', fontsize=14, fontweight='bold')
ax3.set_ylabel('Miss Rate (%)', fontsize=12)
ax3.grid(True, alpha=0.3, axis='y')

# Total Instructions Executed (σε δισεκατομμύρια)
instructions_billions = [i/1e9 for i in instructions]
ax4.bar(scenarios, instructions_billions, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
ax4.set_title('Σύνολο Εντολών', fontsize=14, fontweight='bold')
ax4.set_ylabel('Δισεκατομμύρια Εντολές', fontsize=12)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()