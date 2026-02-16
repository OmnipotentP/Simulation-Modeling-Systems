import os
import re

# Ρυθμίσεις
SIM_TIME = 86400  # 24 ώρες
PYTHON_CMD = "python" 

# Λίστα πειραμάτων: (Αλγόριθμος, d)
experiments = [
    (1, 0),       # Αλγόριθμος 1
    (2, 0),       # Αλγόριθμος 2 με d=0
    (2, 1),       # Αλγόριθμος 2 με d=1
    (2, 2),       # Αλγόριθμος 2 με d=2
    (2, 3),       # Αλγόριθμος 2 με d=3
    (2, 4),       # Αλγόριθμος 2 με d=4
    (2, 5)        # Αλγόριθμος 2 με d=5
]

def parse_results(filename):
    """Διαβάζει το αρχείο αποτελεσμάτων και εξάγει τα βασικά νούμερα."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Αναζήτηση με Regular Expressions
        wait_match = re.search(r"Μέσος Χρόνος Αναμονής:\s+([0-9.]+)", content)
        util_match = re.search(r"Μέση Συνολική Χρησιμοποίηση.*:\s+([0-9.]+)", content)
        
        mean_wait = float(wait_match.group(1)) if wait_match else 0.0
        total_util = float(util_match.group(1)) if util_match else 0.0
        
        return mean_wait, total_util
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return 0.0, 0.0

print("==================================================")
print(f"   STARTING AUTOMATED EXPERIMENTS (Time: {SIM_TIME}s)")
print("==================================================")

results_summary = []

for algo, d in experiments:
    print(f"\n---> Running Algorithm {algo} with d={d}...")
    
    # Εκτέλεση του simulation.py
    cmd = f"{PYTHON_CMD} simulation.py {SIM_TIME} {algo} {d}"
    exit_code = os.system(cmd)
    
    if exit_code != 0:
        print(f"!!! Error running simulation for Algo {algo}, d={d}")
        continue
        
    # Ανάγνωση αποτελεσμάτων
    filename = f"results_algo{algo}_d{d}.txt"
    if os.path.exists(filename):
        wait, util = parse_results(filename)
        results_summary.append({
            'algo': algo,
            'd': d,
            'wait': wait,
            'util': util
        })
    else:
        print(f"Warning: Output file {filename} not found.")

# --- ΕΚΤΥΠΩΣΗ ΤΕΛΙΚΟΥ ΠΙΝΑΚΑ ---
print("\n\n")
print("=============================================================")
print("               FINAL SUMMARY REPORT                          ")
print("=============================================================")
print(f"{'Algo':<6} | {'d':<3} | {'Mean Wait (sec)':<18} | {'Avg Utilization':<18}")
print("-" * 60)

for res in results_summary:
    print(f"{res['algo']:<6} | {res['d']:<3} | {res['wait']:<18.4f} | {res['util']:<18.4f}")

print("=============================================================")
print("Done! Use these numbers for your report graphs.")