"""Generate Bell-state circuit and measured histogram evidence on A/B coupling maps."""
from pathlib import Path
import csv
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets' / 'bell_state'
OUT.mkdir(parents=True, exist_ok=True)
COUPLINGS = {
 'A': [(0,1),(1,2),(1,3),(3,4)],
 'B': [(0,1),(1,2),(1,6),(2,3),(2,6),(2,5),(3,4),(4,5),(5,6),(6,7),(6,8),(8,0)]
}
shots = 4096
for name, edges in COUPLINGS.items():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    simulator = AerSimulator()
    compiled = transpile(qc, basis_gates=['rz','sx','x','cx'], coupling_map=CouplingMap(couplinglist=edges + [(b,a) for a,b in edges]),
                         initial_layout=[0,1], optimization_level=1, seed_transpiler=42)
    counts = simulator.run(compiled, shots=shots, seed_simulator=42).result().get_counts()
    (OUT / f'processor_{name}_bell_circuit.txt').write_text(str(compiled.draw(output='text', fold=100)), encoding='utf-8')
    with (OUT / f'processor_{name}_bell_counts.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['bitstring','count','probability'])
        for bits in ['00','01','10','11']:
            writer.writerow([bits, counts.get(bits,0), counts.get(bits,0)/shots])
    fig, ax = plt.subplots(figsize=(6,4))
    labels=['00','01','10','11']
    ax.bar(labels,[counts.get(s,0)/shots for s in labels])
    ax.set_ylim(0,1)
    ax.set_ylabel('Measured probability')
    ax.set_xlabel('Bitstring')
    ax.set_title(f'Processor {name}: Bell state, ideal simulation ({shots} shots)')
    fig.tight_layout()
    fig.savefig(OUT / f'processor_{name}_bell_histogram.png', dpi=180)
    plt.close(fig)
    print(f'Processor {name}: {counts}; circuit depth={compiled.depth()}')
print('Saved evidence to:', OUT)
