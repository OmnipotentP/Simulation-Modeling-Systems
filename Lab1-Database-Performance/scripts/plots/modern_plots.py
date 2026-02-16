import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# ΡΥΘΜΙΣΕΙΣ ΜΟΝΤΕΡΝΟΥ ΣΤΥΛ
plt.style.use('seaborn')  # Χρησιμοποιούμε το classic seaborn

# 1. Φόρτωση των δεδομένων
try:
    df = pd.read_csv('/home/user/ycsb_results/final_results.csv')
except FileNotFoundError:
    print("Σφάλμα: Δεν βρέθηκε το αρχείο final_results.csv!")
    exit()

# Καθαρισμός: Μετατροπή του Relative Error από string "X%" σε αριθμό
if df['Relative_Error'].dtype == object:
    df['Relative_Error'] = df['Relative_Error'].str.rstrip('%').astype('float') / 100.0

# 2. Προετοιμασία φακέλου εξόδου
output_dir = '/home/user/plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 3. ΜΟΝΤΕΡΝΕΣ ΡΥΘΜΙΣΕΙΣ ΕΜΦΑΝΙΣΗΣ
workloads = ['workloada', 'workloadb', 'workloadc']

# Μοντέρνο color palette (professional)
modern_colors = {
    'native': '#2E86AB',   # Sophisticated blue
    'layered': '#A23B72',  # Elegant purple
    'volume': '#F18F01'    # Warm orange
}

# Professional markers and styles
modern_styles = {
    'native':  {'color': '#2E86AB', 'marker': 'o', 'linestyle': '-', 'linewidth': 2.5, 'markersize': 8, 'label': 'Native'},
    'layered': {'color': '#A23B72', 'marker': 's', 'linestyle': '--', 'linewidth': 2.5, 'markersize': 8, 'label': 'Layered'},
    'volume':  {'color': '#F18F01', 'marker': 'D', 'linestyle': '-.', 'linewidth': 2.5, 'markersize': 8, 'label': 'Volume'}
}

# Workload colors for bar plots
workload_colors_modern = {
    'workloada': '#1B9E77',  # Mountain Meadow
    'workloadb': '#D95F02',  # Bamboo
    'workloadc': '#7570B3'   # Deluge
}

workload_labels = {
    'workloada': 'Workload A',
    'workloadb': 'Workload B', 
    'workloadc': 'Workload C'
}

print("Δημιουργία μοντέρνων γραφημάτων...")

# 4. ΜΟΝΤΕΡΝΑ LINE PLOTS
for workload in workloads:
    # Create figure with modern proportions
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    # Φιλτράρουμε τα δεδομένα μόνο για το τρέχον workload
    df_w = df[df['Workload'] == workload]
    
    # Σχεδιάζουμε μία γραμμή για κάθε σενάριο
    for scenario in ['native', 'layered', 'volume']:
        data = df_w[df_w['Scenario'] == scenario].sort_values('Threads')
        
        if not data.empty:
            # Modern errorbar with subtle styling
            ax.errorbar(
                data['Threads'], 
                data['Mean_Throughput'], 
                yerr=data['CI_Half_Width'],
                label=modern_styles[scenario]['label'],
                color=modern_styles[scenario]['color'],
                marker=modern_styles[scenario]['marker'],
                linestyle=modern_styles[scenario]['linestyle'],
                linewidth=modern_styles[scenario]['linewidth'],
                markersize=modern_styles[scenario]['markersize'],
                capsize=4,
		capthick=1.5,
                elinewidth=1.5,  
                alpha=0.9
            )

    # ΜΟΝΤΕΡΝΗ ΜΟΡΦΟΠΟΙΗΣΗ
    ax.set_title(f'Throughput vs Thread Count - {workload.upper()}', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Number of Threads', fontsize=12, fontweight='medium')
    ax.set_ylabel('Throughput (ops/sec)', fontsize=12, fontweight='medium')
    
    # Clean grid
    ax.grid(True, linestyle='-', alpha=0.1, color='gray')
    ax.set_axisbelow(True)
    
    # Modern legend
    ax.legend(fontsize=11, frameon=True, fancybox=True, 
              shadow=True, framealpha=0.9, loc='best')
    
    # Clean x-axis
    ax.set_xticks([1, 4, 8])
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Remove spines for modern look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add subtle background
    ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    
    # Αποθήκευση σε high-quality PNG
    filename = f'{output_dir}/modern_{workload}_throughput.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Αποθηκεύτηκε: {filename}")
    plt.close()

# 5. ΜΟΝΤΕΡΝΑ BAR PLOTS
print("Δημιουργία μοντέρνων bar plots...")

for scenario in ['native', 'layered', 'volume']:
    # Create modern subplot layout
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle(f'Throughput Analysis - {modern_styles[scenario]["label"]} Deployment', 
                fontsize=18, fontweight='bold', y=1.02)
    
    # Set background color
    fig.patch.set_facecolor('white')
    
    for thread_idx, thread_count in enumerate([1, 4, 8]):
        ax = axes[thread_idx]
        
        # Φιλτράρουμε τα δεδομένα
        data = df[(df['Scenario'] == scenario) & (df['Threads'] == thread_count)]
        
        # Προετοιμασία δεδομένων
        workloads_plot = []
        throughputs = []
        errors = []
        
        for workload in workloads:
            workload_data = data[data['Workload'] == workload]
            if not workload_data.empty:
                workloads_plot.append(workload)
                throughputs.append(workload_data['Mean_Throughput'].values[0])
                errors.append(workload_data['CI_Half_Width'].values[0])
        
        # ΜΟΝΤΕΡΝΕΣ ΜΠΑΡΕΣ 
        bars = ax.bar([workload_labels[w] for w in workloads_plot], 
                     throughputs, 
                     color=[workload_colors_modern[w] for w in workloads_plot],
                     yerr=errors, 
                     capsize=6, 
                     error_kw={'capthick': 1.5},  
                     alpha=0.85,
                     edgecolor='white',
                     linewidth=1.5)
        
        # Μορφοποίηση subplot
        ax.set_title(f'{thread_count} Threads', fontsize=13, fontweight='semibold', pad=15)
        ax.set_ylabel('Throughput (ops/sec)', fontsize=11, fontweight='medium')
        
        # Clean grid
        ax.grid(True, linestyle='-', alpha=0.1, axis='y', color='gray')
        ax.set_axisbelow(True)
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Set background
        ax.set_facecolor('#f8f9fa')
        
        # Προσθήκη τιμών πάνω από τις μπάρες με μοντέρνο στυλ
        for bar, throughput, error in zip(bars, throughputs, errors):
            ax.text(bar.get_x() + bar.get_width()/2, 
                   bar.get_height() + error + (max(throughputs) * 0.02),
                   f'{throughput:.0f}', 
                   ha='center', va='bottom', 
                   fontsize=10, fontweight='medium',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                           edgecolor='gray', alpha=0.8))
        
        # Rotate x-labels if needed
        ax.tick_params(axis='x', rotation=0, labelsize=10)
        ax.tick_params(axis='y', labelsize=9)
    
    plt.tight_layout()
    
    # Αποθήκευση
    filename = f'{output_dir}/modern_bar_plot_{scenario}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Αποθηκεύτηκε: {filename}")
    plt.close()

# 6. ΕΠΙΠΛΕΟΝ: COMPARISON HEATMAP (ΠΟΛΥ ΜΟΝΤΕΡΝΟ)
print("Δημιουργία heatmap comparison...")

# Create a pivot table for the heatmap
pivot_data = df.pivot_table(values='Mean_Throughput', 
                           index=['Scenario', 'Threads'], 
                           columns='Workload')

fig, ax = plt.subplots(figsize=(14, 8))

# Create heatmap data
heatmap_data = []
scenario_labels = []
for scenario in ['native', 'layered', 'volume']:
    for threads in [1, 4, 8]:
        row = []
        for workload in workloads:
            try:
                value = pivot_data.loc[(scenario, threads), workload]
                row.append(value)
            except KeyError:
                row.append(0)  # Default value if data missing
        heatmap_data.append(row)
        scenario_labels.append(f"{scenario}\n{threads}t")

heatmap_data = np.array(heatmap_data)

# Χρησιμοποιούμε πιο contrast colormap
im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')  # Αλλαγή σε viridis για καλύτερο contrast

# Set labels με μεγαλύτερα fonts
ax.set_xticks(np.arange(len(workloads)))
ax.set_xticklabels([workload_labels[w] for w in workloads], fontsize=12, fontweight='bold')
ax.set_yticks(np.arange(len(scenario_labels)))
ax.set_yticklabels(scenario_labels, fontsize=11, fontweight='medium')

# ΑΦΑΙΡΕΣΑΜΕ ΤΟ GRID ΓΙΑ ΝΑ ΜΗΝ ΕΠΗΡΕΑΖΕΙ ΤΑ ΝΟΥΜΕΡΑ
ax.grid(False)

# Add values in cells με καλύτερο styling
for i in range(len(scenario_labels)):
    for j in range(len(workloads)):
        if heatmap_data[i, j] > 0:
            # Πιο έξυπνη επιλογή χρώματος κειμένου βάσει φωτεινότητας
            cell_value = heatmap_data[i, j]
            max_value = np.max(heatmap_data)
            
            # Αν το κελί είναι πολύ φωτεινό, βάλε σκούρο κείμενο, αλλιώς άσπρο
            text_color = "black" if cell_value < max_value * 0.6 else "white"
            
            # Προσθήκη background στο κείμενο για καλύτερη ανάγνωση
            ax.text(j, i, f'{cell_value:.0f}',
                   ha="center", va="center", 
                   color=text_color,
                   fontweight='bold', 
                   fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.4", 
                           facecolor='white' if text_color == 'black' else 'black',
                           edgecolor='none',
                           alpha=0.0))

ax.set_title("Performance Heatmap: Throughput Comparison (ops/sec)\nAcross All Configurations", 
            fontsize=18, fontweight='bold', pad=25)

# Add colorbar με καλύτερη ετικέτα
cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.ax.set_ylabel('Throughput (ops/sec)', rotation=-90, va="bottom", fontsize=12, fontweight='medium')

# Βελτίωση layout
plt.tight_layout()

filename = f'{output_dir}/modern_heatmap_comparison.png'
plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
print(f"  Αποθηκεύτηκε: {filename}")
plt.close()

print(f"\n ΟΛΟΚΛΗΡΩΘΗΚΕ! Τα μοντέρνα γραφήματα βρίσκονται στον φάκελο {output_dir}")
print(" Δημιουργήθηκαν:")
print("   • 3 μοντέρνα line plots (ένα για κάθε workload)")
print("   • 3 μοντέρνα bar plots (ένα για κάθε deployment)")
print("   • 1 performance heatmap (συνολική σύγκριση)")