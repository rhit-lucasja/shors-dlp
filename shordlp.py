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
def FGate(g, x, p):

    # determine the modular exponentiation value
    f_val = f(g, x, p, a, b)
    if f_val == 0:
        print (f"Error: ({g}^{a})({x}^{b}) = 0 (mod {p})")
        return None
    
    n = floor(log(p - 1, 2)) + 1
    U = np.full((2**n, 2**n), 0)
    for a in range(2**n):
        for b in range(2**n):
            pass

# finds an r such that g^r = x (mod p)
def solve_dlp(g, x, p):
    
    print (f"Using Shor's to solve {g} ^ r = {x} (mod {p})")

    num_exp = floor(log(p - 1, 2)) + 1
    num_base = floor(log(p, 2)) + 1

    # registers for the exponents A,B when we try (g^A)(x^B)
    A = QuantumRegister(num_exp, name="A")
    B = QuantumRegister(num_exp, name="B")

    # for (g^A)(x^B)
    F = QuantumRegister(num_base, name="F")

    # create circuit with known registers
    circuit = QuantumCircuit(A, B, F)

    # initialize superposition of A and B for all states
    circuit.h(A)
    circuit.h(B)
    



    circuit.draw("mpl", fold=-1)
    plt.show()

    # pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    # trans_circuit = pm.run(circuit)
    # sampler = Sampler(mode=backend)
    # job = sampler.run([trans_circuit], shots=1024)
    # result = job.result()[0]
    # counts = result.data.out.get_counts()
    # print (counts)

r = solve_dlp(3, 5, 7)
print (f"{r} = 3?")