import ciw
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- ΡΥΘΜΙΣΕΙΣ ---
SIM_REPLICATIONS = 30     # Πλήθος επαναλήψεων
CUSTOMERS_TO_SIMULATE = 15000  # Πόσους πελάτες θα προσομοιώσουμε (όχι χρόνο, αλλά πλήθος)
MOVING_AVG_WINDOW = 500   # Παράθυρο εξομάλυνσης (για το γράφημα)
D_PARAMETER = 0           # Θα χρησιμοποιήσουμε το βέλτιστο σενάριο (Algo 2, d=0)

# --- ΟΡΙΣΜΟΣ ΔΙΚΤΥΟΥ (Όπως πριν) ---
def get_network_params():
    params = {
        'arrival_distributions': {
            'Class 0': [
                ciw.dists.Exponential(rate=1.0),      # Node 1: Dispatcher
                None, None, None, None, None, None, None, None, None, None, None
            ]
        },
        'service_distributions': {
            'Class 0': [
                ciw.dists.Deterministic(value=0.0),     
                ciw.dists.Exponential(rate=0.08333333), # Nodes 2-6 (Slow)
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.125),      # Nodes 7-9 (Medium)
                ciw.dists.Exponential(rate=0.125),
                ciw.dists.Exponential(rate=0.125),
                ciw.dists.Exponential(rate=0.25),       # Nodes 10-12 (Fast)
                ciw.dists.Exponential(rate=0.25),
                ciw.dists.Exponential(rate=0.25)
            ]
        },
        'routing': {'Class 0': [[0.0]*12 for _ in range(12)]},
        'number_of_servers': [1] * 12,
        'queue_capacities': [float('inf')] * 12
    }
    return params

class RoutingDecision2(ciw.Node):
    def next_node(self, ind):
        workers = [self.simulation.nodes[i] for i in range(2, 13)]
        sorted_workers = sorted(workers, key=lambda x: x.number_of_individuals)
        best_node = sorted_workers[0]
        
        best_node_idx = self.simulation.nodes.index(best_node)
        
        if best_node_idx >= 10: 
            return best_node
        else:
            for node in sorted_workers:
                idx = self.simulation.nodes.index(node)
                if idx >= 10: 
                    if node.number_of_individuals <= best_node.number_of_individuals + D_PARAMETER:
                        return node
                    else:
                        break 
            return best_node

# --- ΕΚΤΕΛΕΣΗ ΠΕΙΡΑΜΑΤΟΣ ---
print(f"--- Running Transient Analysis (Bonus) ---")
print(f"Algorithm 2 (d=0), Replications: {SIM_REPLICATIONS}, Customers: {CUSTOMERS_TO_SIMULATE}")

# Λεξικό για να μαζέψουμε τους χρόνους αναμονής ανά Customer ID
# customer_waits[1] = [wait_rep1, wait_rep2, ...]
customer_waits = {i: [] for i in range(1, CUSTOMERS_TO_SIMULATE + 1)}

# Λίστα για να κρατήσουμε όλα τα records για τον τελικό υπολογισμό
all_records_combined = []

for rep in range(SIM_REPLICATIONS):
    print(f"Running replication {rep+1}/{SIM_REPLICATIONS}...", end='\r')
    ciw.seed(rep)
    
    N = ciw.create_network(**get_network_params())
    Q = ciw.Simulation(N, node_class=[RoutingDecision2] + [ciw.Node]*11)
    
    # Τρέχουμε μέχρι να εξυπηρετηθεί ο συγκεκριμένος αριθμός πελατών
    # Χρησιμοποιούμε simulate_until_max_customers (είναι πιο κατάλληλο εδώ)
    Q.simulate_until_max_customers(CUSTOMERS_TO_SIMULATE, method='Finish')
    
    recs = Q.get_all_records()
    all_records_combined.append(recs)
    
    for r in recs:
        if r.node > 1 and r.id_number <= CUSTOMERS_TO_SIMULATE:
            customer_waits[r.id_number].append(r.waiting_time)

print("\nProcessing data...")

# Υπολογισμός Μέσου Όρου ανά ID
ids = sorted(customer_waits.keys())
mean_waits = [np.mean(customer_waits[i]) if customer_waits[i] else 0 for i in ids]

# Εφαρμογή Κυλιόμενου Μέσου για εξομάλυνση
series = pd.Series(mean_waits)
smooth_waits = series.rolling(window=MOVING_AVG_WINDOW, min_periods=1).mean()

# --- ΕΥΡΕΣΗ ΣΗΜΕΙΟΥ ΤΟΜΗΣ  ---
# Θεωρούμε ότι σταθεροποιείται όταν η αλλαγή στον κυλιόμενο μέσο είναι πολύ μικρή
# Θα χρησιμοποιήσουμε μια ασφαλή τιμή βάσει της καμπύλης ή έναν αλγόριθμο.
# Αλγόριθμος: Όταν το σχετικό σφάλμα του moving average σε σχέση με τον τελικό μέσο είναι < 10%
final_avg = smooth_waits.iloc[-1]
cutoff_customer = 0

for i in range(MOVING_AVG_WINDOW, len(smooth_waits)):
    val = smooth_waits.iloc[i]
    if abs(val - final_avg) / final_avg < 0.05: # 5% tolerance
        cutoff_customer = i
        break

if cutoff_customer == 0: cutoff_customer = 2000 # Fallback

print(f"\n--- ΑΠΟΤΕΛΕΣΜΑΤΑ BONUS ---")
print(f"Εντοπίστηκε σταθεροποίηση μετά τον πελάτη: {cutoff_customer}")
print(f"(Αυτό είναι το μήκος της μεταβατικής κατάστασης σε πλήθος πελατών)")

# --- ΓΡΑΦΗΜΑ ---
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Χρώματα
COLOR_RAW = '#95A5A6'     
COLOR_SMOOTH = '#2980B9'  
COLOR_CUTOFF = '#E74C3C'  
COLOR_TRANSIENT = '#E74C3C' 
COLOR_STEADY = '#27AE60'    

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

# 1. Raw Data 
ax.plot(ids, mean_waits, color=COLOR_RAW, alpha=0.3, linewidth=0.8, label='Raw Data (Ensemble)', zorder=1)

# 2. Moving Average
ax.plot(ids, smooth_waits, color=COLOR_SMOOTH, linewidth=2.5, label=f'Moving Average (w={MOVING_AVG_WINDOW})', zorder=5)

# 3. Cutoff Line
ax.axvline(x=cutoff_customer, color=COLOR_CUTOFF, linestyle='--', linewidth=2, zorder=6)

# 4. Ζώνες (Shaded Regions)
raw_max_98 = np.percentile(mean_waits, 98)
smooth_max = max(smooth_waits)
y_limit = max(raw_max_98, smooth_max) * 1.2

ax.axvspan(0, cutoff_customer, color=COLOR_TRANSIENT, alpha=0.08, zorder=0)
ax.axvspan(cutoff_customer, max(ids), color=COLOR_STEADY, alpha=0.08, zorder=0)

# 5. Annotations
# Cutoff Label
ax.annotate(f'Cutoff Point\n(n={cutoff_customer})', 
            xy=(cutoff_customer, smooth_waits.iloc[cutoff_customer]), 
            xytext=(cutoff_customer + 2000, smooth_waits.iloc[cutoff_customer] + (y_limit * 0.1)),
            arrowprops=dict(facecolor='black', arrowstyle='->', shrinkB=5),
            fontweight='bold', ha='left', zorder=10)

# Zone Labels
ax.text(cutoff_customer/2, y_limit * 1.95, 'TRANSIENT PHASE\n(Unstable)', 
        ha='center', va='top', color=COLOR_CUTOFF, fontweight='bold', fontsize=10, alpha=0.7)

center_steady = cutoff_customer + (max(ids) - cutoff_customer)/2
ax.text(center_steady, y_limit * 1.95, 'STEADY STATE\n(Balanced)', 
        ha='center', va='top', color=COLOR_STEADY, fontweight='bold', fontsize=10, alpha=0.7)

# Τίτλοι και Όρια
ax.set_title('Bonus Analysis: Determination of Warm-up Period')
ax.set_xlabel('Customer ID (Arrival Sequence)')
ax.set_ylabel('Mean Waiting Time (sec)')
ax.set_xlim(0, max(ids))

ax.legend(loc='upper right', frameon=True, framealpha=0.9)

plt.tight_layout()
plt.savefig('bonus_analysis_plot.png')
print("Γράφημα αποθηκεύτηκε: bonus_analysis_plot.png")

# --- ΥΠΟΛΟΓΙΣΜΟΣ ΤΕΛΙΚΩΝ ΣΤΑΤΙΣΤΙΚΩΝ ΜΕ ΔΙΑΓΡΑΦΗ ---
# Τώρα υπολογίζουμε τα metrics χρησιμοποιώντας τα δεδομένα ΜΕΤΑ το cutoff
print("\nRecalculating statistics excluding initial data...")

valid_waits = []
node_busy_time = {i: 0.0 for i in range(2, 13)}
total_sim_time_sum = 0
completed_jobs_sum = 0

for recs in all_records_combined:
    # Βρίσκουμε τον χρόνο άφιξης του πελάτη 'cutoff_customer' για να κόψουμε βάσει χρόνου σε κάθε run
    # ή απλά κόβουμε βάσει ID. Η εκφώνηση λέει "διαγραφή αρχικών αποτελεσμάτων".
    # Συνήθως κόβουμε τα records με id <= cutoff
    
    filtered_recs = [r for r in recs if r.id_number > cutoff_customer]
    
    if not filtered_recs: continue
    
    # Wait Time
    for r in filtered_recs:
        if r.node > 1:
            valid_waits.append(r.waiting_time)
            
    # Throughput & Utilization
    # Πρέπει να βρούμε το χρονικό παράθυρο.
    # Start: Άφιξη του cutoff_customer. End: Τέλος προσομοίωσης.
    
    # Βρες το record του cutoff customer για να δεις πότε μπήκε
    cutoff_rec = next((r for r in recs if r.id_number == cutoff_customer), None)
    if cutoff_rec:
        start_time = cutoff_rec.arrival_date
    else:
        start_time = 0
        
    end_time = max(r.service_end_date for r in recs)
    duration = end_time - start_time
    
    if duration <= 0: continue
    
    total_sim_time_sum += duration
    completed_jobs_sum += len([r for r in filtered_recs if r.service_end_date > start_time])
    
    # Util per node
    for r in filtered_recs:
        if r.node == 1: continue
        # Επικάλυψη με το παράθυρο [start_time, end_time]
        eff_start = max(r.service_start_date, start_time)
        eff_end = min(r.service_end_date, end_time)
        if eff_end > eff_start:
            node_busy_time[r.node] += (eff_end - eff_start)

# Final Stats
final_wait = sum(valid_waits) / len(valid_waits)
final_throughput = completed_jobs_sum / total_sim_time_sum
node_utils = {i: (node_busy_time[i] / total_sim_time_sum) for i in range(2, 13)}
total_util = sum(node_utils.values()) / 11

print(f"\n--- ΤΕΛΙΚΑ ΣΤΑΤΙΣΤΙΚΑ (STEADY STATE) ---")
print(f"Μέσος Χρόνος Αναμονής: {final_wait:.6f} sec")
print(f"Throughput: {final_throughput:.6f} jobs/sec")
print(f"Μέση Συνολική Χρησιμοποίηση: {total_util:.4f}")
print("Done.")