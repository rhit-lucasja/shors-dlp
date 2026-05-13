print ("Importing libraries...")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fractions import Fraction
from math import floor, gcd, log

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT, UnitaryGate
from qiskit.transpiler import generate_preset_pass_manager

from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import SamplerV2 as Sampler
print ("Finished importing.")

backend = AerSimulator()

# f(a, b) = (g^a)(x^b)
def f(g, x, p, a, b):
    return (pow(g, a, p) * pow(x, b, p)) % p

# generate unitary gate / permutation matrix for f(a, b)
def FGate(g, x, p, num_exp, num_base):
    
    sz = 2 ** (2 * num_exp + num_base)
    U = np.full((sz, sz), 0, dtype=complex) # permutation matrix

    for a in range(2**num_exp):
        for b in range(2**num_exp):
            # coerce exponents to mod p-1
            aa = a % (p - 1)
            bb = b % (p - 1)
            # figure out modular exponentiation result
            f_val = f(g, x, p, aa, bb)

            # need a third dimension to create true permutation matrix
            #   since (a,b) alone do not give unique outputs f(a,b)
            #   but y XOR f(a, b) would be reversible and unique
            #   and in practice we'll just use y=0 always to store f(a,b)
            for y in range(2**num_base):
                # original state |A>|B>|Y>
                old = (a << (num_exp + num_base)) | (b << num_base) | y

                # new state |A>|B>|Y XOR F>
                new = (a << (num_exp + num_base)) | (b << num_base) | (y ^ f_val)

                # set result in unitary matrix
                U[new][old] = 1

    # after looping, should have unitary matrix
    # convert into a gate to be used in circuit
    G = UnitaryGate(U)
    G.name = f"FGate"
    return G

# finds an r such that g^r = x (mod p)
def solve_dlp(g, x, p, draw=False):
    
    print (f"Using Shor's to solve {g} ^ r = {x} (mod {p})")

    num_exp = floor(log(p - 1, 2)) + 1
    num_base = floor(log(p, 2)) + 1

    # registers for the exponents A,B when we try (g^A)(x^B)
    A = QuantumRegister(num_exp, name="A")
    B = QuantumRegister(num_exp, name="B")

    # for (g^A)(x^B) entanglement
    F = QuantumRegister(num_base, name="F")

    # for measurements
    G = ClassicalRegister(num_base, name="G")
    out = ClassicalRegister(2 * num_exp, name="out")

    # create circuit with known registers
    circuit = QuantumCircuit(A, B, F, G, out)

    # initialize superposition of A and B for all states
    amps = np.zeros(2 ** num_exp, dtype=complex)
    for i in range(p - 1):
        amps[i] = 1 / np.sqrt(p - 1) # thus equal prob. to the p-1 valid states for A and B
    circuit.initialize(amps, A)
    circuit.initialize(amps, B)
    
    # create the gate that sets F into f(a, b)
    FG = FGate(g, x, p, num_exp, num_base)

    # apply the gate to the circuit that we have
    circuit.compose(
        FG, qubits=list(A) + list(B) + list(F), inplace=True
    )

    # measure the F register to narrow down A, B pairs
    circuit.measure(F, G)

    # apply inverse QFT to the A and B registers
    circuit.compose(QFT(num_exp, inverse=True), qubits=A, inplace=True)
    circuit.compose(QFT(num_exp, inverse=True), qubits=B, inplace=True)

    # measure the A and B registers
    circuit.measure(A[:] + B[:], out)

    # display the circuit in new window before simulation
    if draw:
        circuit.draw("mpl", fold=-1)
        plt.show()

    # run the circuit and determine counts for a and b
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    trans_circuit = pm.run(circuit)
    sampler = Sampler(mode=backend)
    job = sampler.run([trans_circuit], shots=1024)
    result = job.result()[0]
    counts = result.data.out.get_counts()

    # convert outputs in counts to decimal a and b values
    guesses = []
    for output in counts:
        # convert bitstring to decimal
        decA = int(output[:3], 2)
        decB = int(output[3:], 2)
        guesses.append((decA, decB, counts[output]))

    # now actually sort based on most common outputs first
    guesses.sort(key=lambda x: x[2], reverse=True)
    print (guesses)

    # iterate thru most common guesses and solve for r
    #   QFT gave us a + rb = 0 (mod p-1)
    #     so r = -a * b^-1 (mod p-1)
    #       this does mean b must have an inverse mod p-1
    for i in range(len(guesses)):
        # extract guess information
        (a, b, freq) = guesses[i]
        # determine if a,b input is even valid
        if gcd(b, p-1) != 1 or a == 0:
            continue
        # solve for r
        na = (-a) % (p-1)
        binv = pow(b, -1, p-1)
        r = (na * binv) % (p-1)
        if pow(g, r, p) == x:
            return r

results = []
for i in range(1, 7):
    x = pow(3, i, 7)
    r = solve_dlp(3, x, 7)
    results.append(r)
print (results)