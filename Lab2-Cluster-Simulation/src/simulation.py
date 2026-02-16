import ciw
import sys
import math

# --- ΠΑΡΑΜΕΤΡΟΙ ---
D_PARAMETER = 0
WARMUP_TIME = 3600  # 1 ώρα Warm-up
CONFIDENCE_LEVEL = 0.95
DESIRED_REL_ERROR = 0.05

# Πίνακας t-distribution (από Παράρτημα 1 εκφώνησης, στήλη two-tails 0.05)
T_TABLE = {
    1: 12.71, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
    40: 2.021, 60: 2.000, 80: 1.990, 100: 1.984, 1000: 1.962
}

def get_t_value(df):
    if df in T_TABLE: return T_TABLE[df]
    keys = sorted(T_TABLE.keys())
    for k in reversed(keys):
        if df >= k: return T_TABLE[k]
    return 1.96

def get_network_params():
    """ Ορισμός παραμέτρων δικτύου """
    params = {
        'arrival_distributions': {
            'Class 0': [
                ciw.dists.Exponential(rate=1.0),      # Node 1: Dispatcher
                None, None, None, None, None, None, None, None, None, None, None
            ]
        },
        'service_distributions': {
            'Class 0': [
                ciw.dists.Deterministic(value=0.0),     # Node 1: Dispatcher (Instant)
                ciw.dists.Exponential(rate=0.08333333), # Nodes 2-6 (Slow, 1/12)
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.08333333),
                ciw.dists.Exponential(rate=0.125),      # Nodes 7-9 (Medium, 1/8)
                ciw.dists.Exponential(rate=0.125),
                ciw.dists.Exponential(rate=0.125),
                ciw.dists.Exponential(rate=0.25),       # Nodes 10-12 (Fast, 1/4)
                ciw.dists.Exponential(rate=0.25),
                ciw.dists.Exponential(rate=0.25)
            ]
        },
        'routing': {'Class 0': [[0.0]*12 for _ in range(12)]},
        'number_of_servers': [1] * 12,
        'queue_capacities': [float('inf')] * 12
    }
    return params

# --- ΚΛΑΣΕΙΣ ΔΡΟΜΟΛΟΓΗΣΗΣ ---
class RoutingDecision1(ciw.Node):
    def next_node(self, ind):
        # Οι Workers είναι από το index 2 έως 12 (Nodes 2-12)
        # Το index 0 είναι ArrivalNode, το index 1 είναι Dispatcher (Self)
        workers = [self.simulation.nodes[i] for i in range(2, 13)]
        
        # Επιλογή του worker με τους λιγότερους πελάτες
        best_worker = min(workers, key=lambda x: x.number_of_individuals)
        return best_worker

class RoutingDecision2(ciw.Node):
    def next_node(self, ind):
        # Εύρος 2 έως 13 για να πιάσουμε τους Workers (Nodes 2-12)
        workers = [self.simulation.nodes[i] for i in range(2, 13)]
        
        # Ταξινόμηση με βάση το πλήθος πελατών
        sorted_workers = sorted(workers, key=lambda x: x.number_of_individuals)
        best_node = sorted_workers[0]
        
        # Το Node ID στην Ciw είναι το index στη λίστα nodes.
        # Nodes 10, 11, 12 (Fast) αντιστοιχούν στα indices 10, 11, 12.
        best_node_idx = self.simulation.nodes.index(best_node)
        
        # Αν ο καλύτερος είναι ήδη Fast (Indices 10-12), τον επιλέγουμε
        if best_node_idx >= 10: 
            return best_node
        else:
            # Ψάχνουμε στη λίστα για Fast κόμβο που να ικανοποιεί τη συνθήκη
            for node in sorted_workers:
                idx = self.simulation.nodes.index(node)
                if idx >= 10: # Είναι Fast (Nodes 10-12)
                    # Συνθήκη: load <= min_load + d
                    if node.number_of_individuals <= best_node.number_of_individuals + D_PARAMETER:
                        return node
                    else:
                        break 
            return best_node

# --- ΕΚΤΕΛΕΣΗ ΜΙΑΣ ΠΡΟΣΟΜΟΙΩΣΗΣ ---
def run_single_replication(sim_duration, algorithm, seed):
    print(f"   -> Running replication {seed}...", end='\r', flush=True)
    ciw.seed(seed)
    
    node_classes = [ciw.Node] * 12
    if algorithm == 1:
        node_classes[0] = RoutingDecision1
    elif algorithm == 2:
        node_classes[0] = RoutingDecision2
    
    params = get_network_params()
    N = ciw.create_network(**params)
    Q = ciw.Simulation(N, node_class=node_classes)
    
    Q.simulate_until_max_time(WARMUP_TIME + sim_duration)
    
    records = Q.get_all_records()
    
    # --- ΥΠΟΛΟΓΙΣΜΟΣ ΣΤΑΤΙΣΤΙΚΩΝ ---
    valid_records = [r for r in records if r.arrival_date > WARMUP_TIME]
    
    # 1. Μέσος Χρόνος Αναμονής
    # Node 1 is Dispatcher, ignore wait time there (should be 0 anyway)
    waiting_times = [r.waiting_time for r in valid_records if r.node > 1]
    mean_wait = sum(waiting_times) / len(waiting_times) if waiting_times else 0.0
    
    # 2. Χρησιμοποίηση ανά κόμβο
    node_busy_time = {i: 0.0 for i in range(2, 13)}
    
    for r in records: 
        if r.node == 1: continue 
        
        start = r.service_start_date
        end = r.service_end_date
        
        effective_start = max(start, WARMUP_TIME)
        effective_end = min(end, WARMUP_TIME + sim_duration)
        
        if effective_end > effective_start:
            node_busy_time[r.node] += (effective_end - effective_start)

    utilizations = {i: node_busy_time[i] / sim_duration for i in range(2, 13)}

    # 3. Ρυθμός εξυπηρέτησης
    completed_in_window = [r for r in records if r.service_end_date > WARMUP_TIME and r.service_end_date <= WARMUP_TIME + sim_duration]
    throughput = len(completed_in_window) / sim_duration

    return mean_wait, utilizations, throughput

# --- MAIN ---
def main():
    if len(sys.argv) < 4:
        print("Usage: python simulation.py <sim_time> <algo> <d>")
        sys.exit(1)
        
    sim_time = float(sys.argv[1])
    algo = int(sys.argv[2])
    d_val = int(sys.argv[3])
    
    global D_PARAMETER
    D_PARAMETER = d_val
    
    print(f"--- Starting Simulation (Algo: {algo}, d: {d_val}, Time: {sim_time}) ---")
    
    # Γρήγορο διαγνωστικό check
    print("Running diagnostic check...", end=' ', flush=True)
    try:
        run_single_replication(100, algo, 999)
        print("OK!")
    except Exception as e:
        print(f"\nERROR in Diagnostic: {e}")
        sys.exit(1)

    replications = 0
    mean_waits = []
    all_utilizations = {i: [] for i in range(2, 13)}
    all_throughputs = []
    
    min_reps = 10
    max_reps = 50 
    
    while replications < max_reps:
        replications += 1
        mw, utils, th = run_single_replication(sim_time, algo, replications)
        
        mean_waits.append(mw)
        for i in utils: all_utilizations[i].append(utils[i])
        all_throughputs.append(th)
        
        if replications >= min_reps:
            mean_X = sum(mean_waits) / replications
            variance = sum([(x - mean_X)**2 for x in mean_waits]) / (replications - 1)
            S = math.sqrt(variance)
            t_crit = get_t_value(replications - 1)
            hw = t_crit * (S / math.sqrt(replications))
            
            rel_error = (hw / mean_X) if mean_X > 0 else 1.0
            
            # Καθαρίζουμε την γραμμή προόδου και τυπώνουμε το αποτέλεσμα
            print(f"\rRep {replications}: Mean Wait = {mean_X:.4f} s, Rel Error = {rel_error:.4f}   ")
            
            if rel_error <= DESIRED_REL_ERROR:
                print("--> Precision Met!")
                break
    
    final_mean_wait = sum(mean_waits) / replications
    
    # Υπολογισμός διασποράς και διαστήματος εμπιστοσύνης
    if replications > 1:
        variance = sum([(x - final_mean_wait)**2 for x in mean_waits]) / (replications - 1)
        S = math.sqrt(variance)
        t_crit = get_t_value(replications - 1)
        hw = t_crit * (S / math.sqrt(replications))
        rel_error = (hw / final_mean_wait) if final_mean_wait > 0 else 1.0
    else:
        hw = 0.0
        rel_error = 0.0

    final_throughput = sum(all_throughputs) / replications
    avg_node_util = {i: sum(all_utilizations[i])/replications for i in range(2, 13)}
    final_total_util = sum(avg_node_util.values()) / 11
    
    # --- ΕΓΓΡΑΦΗ ΣΕ ΑΡΧΕΙΟ ---
    filename = f"results_algo{algo}_d{d_val}.txt"
    with open(filename, "w", encoding='utf-8') as f:
        f.write("--- ΑΠΟΤΕΛΕΣΜΑΤΑ ΠΡΟΣΟΜΟΙΩΣΗΣ ---\n")
        f.write(f"Αλγόριθμος: {algo}, D: {d_val}\n")
        f.write(f"Χρόνος Προσομοίωσης: {sim_time} sec (+{WARMUP_TIME} warmup)\n")
        f.write(f"Επαναλήψεις: {replications}\n\n")
        f.write(f"Μέσος Χρόνος Αναμονής: {final_mean_wait:.6f} sec\n")
        f.write(f"(95% CI Half-width: {hw:.6f}, Rel. Error: {rel_error:.4f})\n")
        f.write(f"Μέσος Ρυθμός Εξυπηρέτησης: {final_throughput:.6f} jobs/sec\n")
        f.write(f"Μέση Συνολική Χρησιμοποίηση: {final_total_util:.4f}\n")
        f.write("Μέση Χρησιμοποίηση ανά Κόμβο:\n")
        for i in range(2, 13):
            desc = "Slow" if i <= 6 else ("Medium" if i <= 9 else "Fast")
            f.write(f"  Node {i} ({desc}): {avg_node_util[i]:.4f}\n")

    print(f"\nResults written to {filename}")

if __name__ == "__main__":
    main()