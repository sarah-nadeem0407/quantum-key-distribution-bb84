# Quantum Key Distribution (BB84 Simulation)

## Overview
This project simulates the BB84 Quantum Key Distribution protocol to demonstrate secure key exchange under noisy conditions.

---

## Key Components
- BB84 Protocol Simulation
- LDPC + Cascade Error Correction
- Privacy Amplification
- Secure Key Expansion

---

## Architecture

![Flow Diagram](flow-diagram.png)

![Detailed Flow](detailed-flow.png)

---

## Features
- Simulates quantum bit transmission between sender and receiver  
- Implements BB84 protocol for secure key generation  
- Applies error correction (LDPC + Cascade)  
- Uses privacy amplification to reduce information leakage  

---

## Technologies Used
- Python  
- NumPy  
- Qiskit  
- Cryptography  

---

## How It Works
1. Random quantum bits are generated and encoded  
2. Transmission occurs over a simulated noisy channel  
3. Receiver measures qubits using random bases  
4. Matching bases are used to form a shared key  
5. Error correction and privacy amplification improve key security  

---

## Performance Graphs

<p align="center">
  <img src="graph-128.png" width="300"/>
  <img src="graph-256.png" width="300"/>
</p>

---

## Sample Output

![Output](output-1.png)

---

## Output
- Final shared key between sender and receiver  
- Error rates before and after correction  

---

## Security Relevance
Demonstrates principles of secure communication and key exchange, relevant to cryptographic systems and future quantum-safe security models.

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
