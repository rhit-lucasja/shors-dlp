import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fractions import Fraction
from math import floor, gcd, log

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, UnitaryGate
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.visualization import plot_histogram

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2 as Sampler

backend = AerSimulator()

def M2mod15():
    # M2 (mod 15)
    b = 2
    U = QuantumCircuit(4)

    U.swap(2, 3)
    U.swap(1, 2)
    U.swap(0, 1)

    U = U.to_gate()
    U.name = f"M_{b}"

    return U
def draw_M2mod15():
    # get the M2 operator
    M2 = M2mod15()
    # attach operator to circuit and display
    circ = QuantumCircuit(4)
    circ.compose(M2, inplace=True)
    circ.decompose(reps=2).draw(output="mpl", fold=-1)
    plt.show()

def controlled_M2mod15():
    # controlled M2 operator mod 15
    b = 2
    U = QuantumCircuit(4)

    U.swap(2, 3)
    U.swap(1, 2)
    U.swap(0, 1)

    U = U.to_gate()
    U.name = f"M_{b}"
    c_U = U.control()

    return c_U
def draw_cM2mod15():
    # get the cM2 operator
    controlled_M2 = controlled_M2mod15()
    # add to the circuit and plot
    circ = QuantumCircuit(5)
    circ.compose(controlled_M2, inplace=True)
    circ.decompose(reps=1).draw(output="mpl", fold=-1)
    plt.show()

def M4mod15():
    # M4 (mod 15)
    b = 4
    U = QuantumCircuit(4)

    U.swap(1, 3)
    U.swap(0, 2)

    U = U.to_gate()
    U.name = f"M_{b}"

    return U
def draw_M4mod15():
    # Get the M4 operator
    M4 = M4mod15()
    # Add it to a circuit and plot
    circ = QuantumCircuit(4)
    circ.compose(M4, inplace=True)
    circ.decompose(reps=2).draw(output="mpl", fold=-1)
    plt.show()

def controlled_M4mod15():
    b = 4
    U = QuantumCircuit(4)

    U.swap(1, 3)
    U.swap(0, 2)

    U = U.to_gate()
    U.name = f"M_{b}"
    c_U = U.control()

    return c_U
def draw_cM4mod15():
    # Get the controlled-M4 operator
    controlled_M4 = controlled_M4mod15()
    # Add it to a circuit and plot
    circ = QuantumCircuit(5)
    circ.compose(controlled_M4, inplace=True)
    circ.decompose(reps=1).draw(output="mpl", fold=-1)
    plt.show()

def mod_mult_gate(g, N):
    # Modular multiplication using permutation matrix gate
    if gcd(g, N) > 1:
        print(f"Error: gcd({g},{N}) > 1")
    else:
        n = floor(log(N - 1, 2)) + 1
        U = np.full((2**n, 2**n), 0)
        for x in range(N):
            U[g * x % N][x] = 1
        for x in range(N, 2**n):
            U[x][x] = 1
        G = UnitaryGate(U)
        G.name = f"M_{g}"
        return G
def draw_mod_mult_gate(g, N):
    M = mod_mult_gate(g, N)
    # Add it to a circuit
    circ = QuantumCircuit(4)
    circ.compose(M, inplace=True)
    # circ.decompose(reps=9).draw(output="mpl", fold=-1)
    circ = circ.decompose()
    # Transpile the circuit and get the depth
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled_circ = pm.run(circ)

    # stats about the depth of the transpiled circuit
    print(f"qubits: {circ.num_qubits}")
    print(
        f"2q-depth: {transpiled_circ.depth(lambda x: x.operation.num_qubits==2)}"
    )
    print(f"2q-size: {transpiled_circ.size(lambda x: x.operation.num_qubits==2)}")
    print(f"Operator counts: {transpiled_circ.count_ops()}")
    transpiled_circ.decompose().draw(output="mpl", fold=-1, style="clifford", idle_wires=False)

    # display the transpiled circuit
    plt.show()

# Order finding problem for N = 15 with a = 2
N = 15
a = 2

# Number of qubits
num_target = floor(log(N - 1, 2)) + 1  # for modular exponentiation operators
num_control = 2 * num_target  # for enough precision of estimation

# List of M_b operators in order
def a2kmodN(a, k, N):
    """Compute a^{2^k} (mod N) by repeated squaring"""
    for i in range(k):
        a = int(np.mod(a**2, N))
    return a
k_list = range(num_control)
b_list = [a2kmodN(2, k, 15) for k in k_list]

# Initialize the circuit
control = QuantumRegister(num_control, name="C")
target = QuantumRegister(num_target, name="T")
output = ClassicalRegister(num_control, name="out")
circuit = QuantumCircuit(control, target, output)

# Initialize the target register to the state |1>
circuit.x(num_control)

# Add the Hadamard gates and controlled versions of the
# multiplication gates
for k, qubit in enumerate(control):
    circuit.h(k)
    b = b_list[k]
    if b == 2:
        circuit.compose(
            M2mod15().control(), qubits=[qubit] + list(target), inplace=True
        )
    elif b == 4:
        circuit.compose(
            M4mod15().control(), qubits=[qubit] + list(target), inplace=True
        )
    else:
        continue  # M1 is the identity operator

# Apply the inverse QFT to the control register
circuit.compose(QFT(num_control, inverse=True), qubits=control, inplace=True)

# Measure the control register
circuit.measure(control, output)

circuit.draw("mpl", fold=-1)
plt.show()

# actually running the circuit
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
trans_circuit = pm.run(circuit)
sampler = Sampler(mode=backend)
job = sampler.run([trans_circuit], shots=1024)
result = job.result()[0]
counts = result.data.out.get_counts()
print (counts)

# Rows to be displayed in table
rows = []
# Corresponding phase of each bitstring
measured_phases = []

for output in counts:
    decimal = int(output, 2)  # Convert bitstring to decimal
    phase = decimal / (2**num_control)  # Find corresponding eigenvalue
    measured_phases.append(phase)
    # Add these values to the rows in our table:
    rows.append(
        [
            f"{output}(bin) = {decimal:>3}(dec)",
            f"{decimal}/{2 ** num_control} = {phase:.2f}",
        ]
    )

# Print the rows in a table
headers = ["Register Output", "Phase"]
df = pd.DataFrame(rows, columns=headers)
print(df)

# using contnued fractions with limited denom to guess at r
# Rows to be displayed in a table
rows = []

for phase in measured_phases:
    frac = Fraction(phase).limit_denominator(15)
    rows.append(
        [phase, f"{frac.numerator}/{frac.denominator}", frac.denominator]
    )

# Print the rows in a table
headers = ["Phase", "Fraction", "Guess for r"]
df = pd.DataFrame(rows, columns=headers)
print(df)

# actually factoring N using the order guesses r
a = 2
N = 15

FACTOR_FOUND = False
num_attempt = 0

while not FACTOR_FOUND:
    print(f"\nATTEMPT {num_attempt+1}:")
    # Here, we get the bitstring by iterating over outcomes
    # of a previous hardware run with multiple shots.
    # Instead, we can also perform a single-shot measurement
    # here in the loop.
    bitstring = list(counts.keys())[num_attempt]
    num_attempt += 1
    # Find the phase from measurement
    decimal = int(bitstring, 2)
    phase = decimal / (2**num_control)  # phase = k / r
    print(f"Phase: theta = {phase}")

    # Guess the order from phase
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator  # order = r
    print(f"Order of {a} modulo {N} estimated as: r = {r}")

    if phase != 0:
        # Guesses for factors are gcd(a^{r / 2} ± 1, 15)
        if r % 2 == 0:
            x = pow(a, r // 2, N) - 1
            d = gcd(x, N)
            if d > 1:
                FACTOR_FOUND = True
                print(f"*** Non-trivial factor found: {x} ***")