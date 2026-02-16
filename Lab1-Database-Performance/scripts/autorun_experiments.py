import subprocess
import os
import time
import re # Για να διαβάζουμε τα αποτελέσματα του YCSB
import numpy as np # Για στατιστικούς υπολογισμούς (mean, std)
import scipy.stats as st # Για τον υπολογισμό του t-value
import signal

# --- 1. ΟΡΙΣΜΟΣ ΠΑΡΑΓΟΝΤΩΝ ΚΑΙ ΕΠΙΠΕΔΩΝ ---
DB_SCENARIOS = ["native", "layered", "volume"]
WORKLOADS = ["workloada", "workloadb", "workloadc"]
THREADS = [1, 4, 8]

# --- 2. ΡΥΘΜΙΣΕΙΣ ΓΙΑ ΤΟ CI ---
MIN_RUNS = 3 # Ελάχιστες επαναλήψεις
ALPHA = 0.05 # Για 95% διάστημα εμπιστοσύνης
CI_THRESHOLD = 0.05 # Σταματάμε αν το (CI / mean) < 5%
MAX_RUN_ATTEMPTS = 8

# --- 2. ΒΑΣΙΚΟΙ ΦΑΚΕΛΟΙ ---
YCSB_HOME = "/home/user/Benchmarks/ycsb-0.17.0"
SCRIPTS_HOME = "/home/user/Scripts"
RESULTS_DIR = "/home/user/ycsb_results"
MONITORING_DIR = f"{RESULTS_DIR}/monitoring"

# --- 3. ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ---

def run_command(command, cwd=None, suppress_errors=False, capture_output=False):
    """Εκτέλεση εντολών"""
    effective_cwd = cwd or os.getcwd()
    
    if not suppress_errors:
        print(f"--- EXEC: {command}")
    
    try:
        if command.strip().endswith("&"):
            """Χρειαζόμαστε shell=True για εντολές όπως 'echo 3 > ...' και pkill"""
            subprocess.Popen(command, shell=True, cwd=effective_cwd, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            return None
        elif capture_output:
            return subprocess.run(command, shell=True, cwd=effective_cwd, 
                               capture_output=True, text=True, timeout=300)
        else:
            subprocess.run(command, shell=True, check=True, cwd=effective_cwd, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        if not suppress_errors:
            print(f"!!! ERROR: {command}")
    except Exception as e:
        if not suppress_errors:
            print(f"!!! GENERAL ERROR: {command}")
    
    return None

def start_monitoring(run_id, scenario, workload, threads):
    """Ξεκινάει το monitoring των πόρων συστήματος"""
    print("--- STARTING SYSTEM MONITORING ---")
    
    run_command(f"mkdir -p {MONITORING_DIR}", suppress_errors=True)
    
    base_filename = f"{MONITORING_DIR}/monitor_{scenario}_{workload}_{threads}th_run{run_id}"
    run_command(f"rm -f {base_filename}.*", suppress_errors=True)
    
    # Εκκίνηση monitoring tools
    tools = {
        'mpstat': f"mpstat 1 > {base_filename}.mpstat",
        'vmstat': f"vmstat 1 > {base_filename}.vmstat", 
        'iostat': f"iostat -dx 1 > {base_filename}.iostat"
    }
    
    monitoring_pids = {}
    for tool, cmd in tools.items():
        proc = subprocess.Popen(f"{cmd} &", shell=True, 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        monitoring_pids[tool] = proc.pid
    
    time.sleep(2)
    return monitoring_pids, base_filename

def stop_monitoring(monitoring_pids):
    """Τερματίζει όλα τα monitoring processes"""
    print("--- STOPPING SYSTEM MONITORING ---")
    
    for tool, pid in monitoring_pids.items():
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
                print(f"--- Killed {tool} process (PID: {pid})")
            except OSError:
                pass  # Process already terminated
        except (OSError, ProcessLookupError):
            pass  # Process already gone
    
    # Επιπλέον καθαρισμός
    for tool in ['mpstat', 'vmstat', 'iostat']:
        run_command(f"pkill -f '{tool} 1'", suppress_errors=True)
    
    time.sleep(2)

def aggressive_cleanup():
    """Επιθετικός καθαρισμός - ΔΙΑΤΗΡΗΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ"""
    print("--- SMART CLEANUP ---")
    
    # Διατήρηση αποτελεσμάτων, διαγραφή προσωρινών
    run_command("find /home/user/ycsb_results/ -type f ! -name '*.csv' ! -name 'monitoring' ! -path '*/monitoring/*' -delete", 
                suppress_errors=True)
    
    # Καθαρισμός Docker και system
    run_command("docker system prune -a -f --volumes", suppress_errors=True)
    run_command("sudo apt clean", suppress_errors=True)
    run_command("sudo rm -rf /tmp/* /var/tmp/*", suppress_errors=True)
    
    # Τερματισμός monitoring processes
    for tool in ['mpstat', 'vmstat', 'iostat']:
        run_command(f"pkill -f '{tool} 1'", suppress_errors=True)
    
    # Backup αποτελεσμάτων
    run_command(f"cp {RESULTS_DIR}/final_results.csv /home/user/final_results_backup.csv 2>/dev/null", 
                suppress_errors=True)
    
    # Έλεγχος χώρου
    result = run_command("df -h / | tail -1", capture_output=True)
    if result and result.stdout:
        print(f"--- DISK SPACE: {result.stdout.strip()}")

def parse_ycsb_output(output_text):
    """Εξαγωγή throughput από YCSB output"""
    for line in output_text.split('\n'):
        if "[OVERALL], Throughput(ops/sec)," in line:
            return float(line.split(",")[2].strip())
    return 0.0

def calculate_ci(data):
    """
    Υπολογίζει το 95% CI για μια λίστα δεδομένων.
    Επιστρέφει (mean, half_width, relative_error)
    """
    if len(data) < 2:
        return 0, 0, 1.0

    n = len(data)
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)

    if std_dev == 0.0 or mean == 0.0:
        return mean, 0.0, 1.0 # Επιστρέφουμε 1.0 (100% σφάλμα) για να συνεχίσει

    std_err = std_dev / np.sqrt(n)
    # Βρίσκουμε το t-value από τον πίνακα t (Παράρτημα 2)
    # για (n-1) βαθμούς ελευθερίας (df) και 95% CI
    # Η scipy το κάνει αυτόματα:
    t_value = st.t.ppf(1 - ALPHA / 2, df=n - 1)
    ci_half_width = t_value * std_err
    relative_error = ci_half_width / mean

    return mean, ci_half_width, relative_error

def update_workload_files():
    """
    Ενημέρωση workload files με 500,000 records
    Το προσθέσαμε για να μπορούμε να μπορούμε να κάνουμε
    αλλαγή πιο εύκολα μέσα από τον κώδικα. 
    """
    for workload in ["workloada", "workloadb", "workloadc"]:
        file_path = f"{YCSB_HOME}/workloads/{workload}"
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Αντικατάσταση recordcount και operationcount
        content = re.sub(r'recordcount=.*', 'recordcount=500000', content)
        content = re.sub(r'operationcount=.*', 'operationcount=500000', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    print("--- Workload files updated to 500,000 records")

def get_scenario_params(scenario):
    """Επιστρέφει τις παραμέτρους για κάθε scenario"""
    params = {
        "native": {
            "init": "create-native",
            "delete": "delete-native", 
            "start": "start-native",
            "stop": "stop-native",
            "properties": "jdbc-binding/conf/db.properties"
        },
        "layered": {
            "init": "create-layered",
            "delete": "delete-layered",
            "start": "start-layered", 
            "stop": "stop-layered",
            "properties": "jdbc-binding/conf/db.container.properties"
        },
        "volume": {
            "init": "create-volume",
            "delete": "delete-volume",
            "start": "start-volume",
            "stop": "stop-volume",
            "properties": "jdbc-binding/conf/db.container.properties"
        }
    }
    return params[scenario]

# --- 4. ΚΥΡΙΟΣ ΒΡΟΧΟΣ ΠΕΙΡΑΜΑΤΩΝ ---

def main():
    """Κύρια λειτουργία του πειράματος"""
    # Αρχικός καθαρισμός και προετοιμασία
    aggressive_cleanup()
    update_workload_files()
    
    run_command(f"mkdir -p {RESULTS_DIR} {MONITORING_DIR}", suppress_errors=True)
    
    # Προετοιμασία αρχείου αποτελεσμάτων
    file_path = f"{RESULTS_DIR}/final_results.csv"
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w") as f:
            f.write("Scenario,Workload,Threads,Runs,Mean_Throughput,CI_Half_Width,Relative_Error\n")
    
    results_log = open(file_path, "a")
    experiment_count = 0
    
    # Κύριος βρόχος πειραμάτων
    for scenario in DB_SCENARIOS:
        params = get_scenario_params(scenario)
        
        # Επανάληψη για κάθε workload (A, B, C)
        for workload_file in WORKLOADS:

            # Επανάληψη για κάθε αριθμό νημάτων (1, 4, 8)
            for thread_count in THREADS:
                experiment_count += 1
                
                # Περιοδικός καθαρισμός
                if experiment_count % 2 == 0:
                    aggressive_cleanup()
                
                print(f"\n*** EXPERIMENT {experiment_count}: {scenario}, {workload_file}, {thread_count} threads ***")
                run_experiment(scenario, workload_file, thread_count, params, results_log)
    
    # Τελικές λειτουργίες
    print("\n*** SAVING FINAL RESULTS ***")
    run_command(f"cp {RESULTS_DIR}/final_results.csv /home/user/final_results_backup.csv")
    run_command(f"ls -la {RESULTS_DIR}/ {MONITORING_DIR}/")
    
    aggressive_cleanup()
    results_log.close()
    
    print(f"\n*** ALL EXPERIMENTS COMPLETED ***")
    print(f"Results: {RESULTS_DIR}/final_results.csv")
    print(f"Monitoring Data: {MONITORING_DIR}/")
    print(f"Backup: /home/user/final_results_backup.csv")

def run_experiment(scenario, workload_file, thread_count, params, results_log):
    """Εκτελεί ένα πείραμα με όλες τις επαναλήψεις"""
    ycsb_workload_path = f"workloads/{workload_file}"
    
    # Database setup
    print("--- Setting up database...")
    run_command(f"{SCRIPTS_HOME}/mariadb.sh {params['init']}", cwd=YCSB_HOME)
    
    wait_time = 60 if scenario == "layered" else 40
    print(f"Waiting {wait_time}s for DB...")
    time.sleep(wait_time)
    
    # YCSB Load
    print("--- Loading data...")
    run_command(f"./bin/ycsb.sh load jdbc -P {ycsb_workload_path} -P {params['properties']} -s", 
               cwd=YCSB_HOME)
    
    # Εκτέλεση επαναλήψεων
    throughput_results = [] # Λίστα για αποθήκευση ρυθμαπόδοσης
    total_attempts = 0
    need_more_runs = True
    
    while need_more_runs and total_attempts < MAX_RUN_ATTEMPTS:
        total_attempts += 1
        throughput = run_single_iteration(scenario, workload_file, thread_count, params, total_attempts)
        
        if throughput > 0:
            throughput_results.append(throughput)
            print(f"--- Throughput: {throughput:.2f} ops/sec")
            
            if len(throughput_results) >= MIN_RUNS:
                mean_throughput, ci_width, rel_err = calculate_ci(throughput_results)
                print(f"--- STATS: Mean={mean_throughput:.2f}, CI±{ci_width:.2f}, Error={rel_err:.2%}")
                
                if rel_err < CI_THRESHOLD:
                    need_more_runs = False
                    results_log.write(f"{scenario},{workload_file},{thread_count},{len(throughput_results)},{mean_throughput:.2f},{ci_width:.2f},{rel_err:.2%}\n")
                    results_log.flush()
                    break
    
    # Cleanup μετά από κάθε experiment
    print("--- Cleaning up...")
    run_command(f"{SCRIPTS_HOME}/mariadb.sh {params['delete']}", cwd=YCSB_HOME)
    
    if scenario in ["layered", "volume"]:
        run_command("docker system prune -f", suppress_errors=True)

def run_single_iteration(scenario, workload_file, thread_count, params, run_id):
    """Εκτελεί μία επανάληψη του πειράματος"""
    # Database restart
    run_command(f"{SCRIPTS_HOME}/mariadb.sh {params['stop']}", cwd=YCSB_HOME)
    time.sleep(3)
    run_command(f"{SCRIPTS_HOME}/mariadb.sh {params['start']}", cwd=YCSB_HOME)
    time.sleep(15)
    
    # Clean caches
    run_command("echo 3 > /proc/sys/vm/drop_caches", suppress_errors=True)
    
    # Monitoring
    monitoring_pids, _ = start_monitoring(run_id, scenario, workload_file, thread_count)
    
    # YCSB Run
    ycsb_command = f"./bin/ycsb.sh run jdbc -P workloads/{workload_file} -P {params['properties']} -threads {thread_count} -s"
    result = run_command(ycsb_command, cwd=YCSB_HOME, capture_output=True)
    
    stop_monitoring(monitoring_pids)
    
    if result and result.returncode == 0:
        return parse_ycsb_output(result.stdout)
    
    return 0.0

if __name__ == "__main__":
    main()