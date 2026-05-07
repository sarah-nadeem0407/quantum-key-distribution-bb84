# Quantum Key Distribution (BB84 Simulation)

## Overview
This project simulates the BB84 Quantum Key Distribution protocol to demonstrate secure key exchange under noisy conditions.

## Features
- Simulates quantum bit transmission between sender and receiver
- Implements BB84 protocol for secure key generation
- Applies error correction (LDPC + Cascade)
- Uses privacy amplification to reduce information leakage

## Technologies Used
- Python
- NumPy
- Qiskit

## How It Works
1. Random quantum bits are generated and encoded
2. Transmission occurs over a simulated noisy channel
3. Receiver measures qubits using random bases
4. Matching bases are used to form a shared key
5. Error correction and privacy amplification improve key security

## Output
- Final shared key between sender and receiver
- Error rates before and after correction

## Security Relevance
Demonstrates principles of secure communication and key exchange, relevant to cryptographic systems and future quantum-safe security models.

## How to Run
1. Install dependencies:
   pip install -r requirements.txt

2. Run:
   python main.py
