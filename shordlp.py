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




# finds an r such that g^r = x (mod p)
def solve_dlp(g, x, p):
    
    print (f"Using Shor's to solve {g} ^ r = {x} (mod {p})")

    A = QuantumRegister(p - 1, name="A")
    B = QuantumRegister(p - 1, name="B")
    circuit = QuantumCircuit(A, B)

    # initialize superposition of A and B states for all a,b in Z_p
    for k, qubit in enumerate(A):
        circuit.h(k) # places A in superposition
        circuit.h(p - 1 + k) # places B in superposition

    


    circuit.draw("mpl", fold=-1)
    plt.show()

    # pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    # trans_circuit = pm.run(circuit)
    # sampler = Sampler(mode=backend)
    # job = sampler.run([trans_circuit], shots=1024)
    # result = job.result()[0]
    # counts = result.data.out.get_counts()
    # print (counts)

r = solve_dlp(3, 6, 7)
print (f"{r} = 3?")