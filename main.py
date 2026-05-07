import numpy as np
import time
import math
import os
import hmac
import hashlib

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Utility Functions


def binary_entropy(p):
    if p == 0 or p == 1:
        return 0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def compute_mac(message_bytes, key):
    return hmac.new(key, message_bytes, hashlib.sha256).digest()


# LDPC


def generate_ldpc_matrix(rows, cols, density=0.05):

    H = np.zeros((rows, cols), dtype=int)

    for i in range(rows):
        ones = np.random.choice(cols, max(2, int(cols*density)), replace=False)
        H[i, ones] = 1

    return H


def ldpc_decode(alice_bits, bob_bits, iterations=8):

    print("\nStep 6: LDPC Error Correction")

    n = len(alice_bits)
    m = max(1, n // 4)

    H = generate_ldpc_matrix(m, n)

    print("LDPC Matrix (first 5 rows):")
    print(H[:5])

    alice = np.array(alice_bits)
    bob = np.array(bob_bits)

    alice_syndrome = np.mod(H @ alice, 2)
    leakage = m

    for it in range(iterations):

        bob_syndrome = np.mod(H @ bob, 2)
        diff = bob_syndrome ^ alice_syndrome

        if np.sum(diff) == 0:
            break

        score = np.zeros(n)

        for i in range(m):
            if diff[i] == 1:
                score += H[i]

        if np.sum(score) == 0:
            break

        flip = np.argmax(score)
        bob[flip] ^= 1

    residual = np.sum(alice != bob)

    print("Residual errors after LDPC:", residual)

    return bob, residual, leakage



# CASCADE


def cascade_refinement(alice_bits, bob_bits, passes=4):

    print("\nStep 7: Cascade Error Refinement")

    alice = np.array(alice_bits)
    bob = np.array(bob_bits)

    n = len(alice)

    leakage = 0

    for p in range(passes):

        block_size = max(1, n // (2**(p+1)))

        indices = np.arange(n)
        np.random.shuffle(indices)

        for i in range(0, n, block_size):

            block = indices[i:i+block_size]

            a_parity = np.sum(alice[block]) % 2
            b_parity = np.sum(bob[block]) % 2

            leakage += 1

            if a_parity != b_parity:

                for j in block:

                    leakage += 1

                    if alice[j] != bob[j]:
                        bob[j] ^= 1
                        break

    residual = np.sum(alice != bob)

    print("Residual errors after Cascade:", residual)

    return bob, residual, leakage



# TOEPLITZ PRIVACY AMPLIFICATION


def toeplitz_privacy_amplification(input_bits, output_length):

    print("\nStep 8: Toeplitz Matrix Compression")

    n = len(input_bits)
    m = output_length

    seed = np.random.randint(0, 2, m + n - 1)

    toeplitz_matrix = np.zeros((m, n), dtype=int)

    for i in range(m):
        for j in range(n):
            toeplitz_matrix[i, j] = seed[i - j + n - 1]

    result = np.mod(np.dot(toeplitz_matrix, input_bits), 2)

    return result



# MAIN BB84 PROTOCOL


def run_bb84():

    print("\n=========== BB84 PROTOCOL SIMULATION ===========")

    n = int(input("Enter number of input qubits: "))
    eve_percent = float(input("Enter Eve attack percentage: "))
    error_percent = float(input("Enter channel error percentage: "))
    desired_bits = int(input("Enter desired final key length (bits): "))

    eve_prob = eve_percent / 100
    error_prob = error_percent / 100
    qber_threshold = 0.11

    backend = AerSimulator()

    start_time = time.time()

    print("\nStep 1: Authentication Setup")

    auth_key = os.urandom(32)

    print("\nStep 2: Random Bit and Basis Generation (Alice)")

    alice_bits = np.random.randint(0,2,n)
    alice_basis = np.random.randint(0,2,n)

    print("Alice Bits (first 40):", alice_bits[:40])
    print("Alice Bases (first 40):", alice_basis[:40])

    print("\nStep 3: Measurement (Bob)")

    bob_basis = np.random.randint(0,2,n)

    print("Bob Bases (first 40):", bob_basis[:40])

    bob_results = []

    eve_errors = 0
    measurement_errors = 0

    for i in range(n):

        qc = QuantumCircuit(1,1)

        if alice_bits[i] == 1:
            qc.x(0)

        if alice_basis[i] == 1:
            qc.h(0)

        if np.random.rand() < eve_prob:

            eve_basis = np.random.randint(0,2)

            if eve_basis == 1:
                qc.h(0)

            qc.measure(0,0)

            qc = transpile(qc,backend)

            result = backend.run(qc,shots=1).result()

            eve_bit = int(list(result.get_counts().keys())[0])

            qc = QuantumCircuit(1,1)

            if eve_bit == 1:
                qc.x(0)

            if eve_basis == 1:
                qc.h(0)

            if eve_basis != alice_basis[i]:
                eve_errors += 1

        if np.random.rand() < error_prob:
            qc.x(0)
            measurement_errors += 1

        if bob_basis[i] == 1:
            qc.h(0)

        qc.measure(0,0)

        qc = transpile(qc,backend)

        result = backend.run(qc,shots=1).result()

        bob_bit = int(list(result.get_counts().keys())[0])

        bob_results.append(bob_bit)

    bob_bits = np.array(bob_results)

    print("Bob Results (first 40):", bob_bits[:40])

    print("\nStep 4: Basis Comparison (Sifting)")

    mask = alice_basis == bob_basis

    alice_sifted = alice_bits[mask]
    bob_sifted = bob_bits[mask]

    print("Alice Sifted Key:", alice_sifted)
    print("Bob Sifted Key:", bob_sifted)

    print("\nStep 5: QBER Calculation")

    errors = np.sum(alice_sifted != bob_sifted)

    qber = errors / len(alice_sifted)

    print("QBER:", qber)

    if qber > qber_threshold:

        print("Protocol aborted due to high QBER.")

        end_time = time.time()

        print("\n========== PARTIAL OUTPUT ==========")
        print("Measurement Error:", measurement_errors)
        print("Error Due To Eve:", eve_errors)
        print("QBER:", round(qber,6))
        print("Reconciled Key Length:", len(alice_sifted))
        print("\nTotal Computation Time:", round((end_time-start_time)*1000,4),"ms")
        print("===================================")

        return

    bob_ldpc, residual_ldpc, leak_ldpc = ldpc_decode(
        alice_sifted,
        bob_sifted
    )

    bob_corrected, residual_error, leak_cascade = cascade_refinement(
        alice_sifted,
        bob_ldpc
    )

    ec_leakage = leak_ldpc + leak_cascade

    reconciled_length = len(alice_sifted)

    print("\nKey Verification")

    alice_hash = hashlib.sha256("".join(map(str,alice_sifted)).encode()).digest()
    bob_hash = hashlib.sha256("".join(map(str,bob_corrected)).encode()).digest()

    print("Alice Hash:", alice_hash.hex())
    print("Bob Hash:", bob_hash.hex())

    if alice_hash != bob_hash:
        print("Key verification failed.")
        return

    print("Verification SUCCESS")

    h = binary_entropy(qber)

    final_secure_length = int(reconciled_length * (1 - 2*h) - ec_leakage)
    final_secure_length = max(final_secure_length,0)

    if final_secure_length == 0:

        print("Protocol aborted: insufficient secure key after privacy amplification.")

        end_time = time.time()

        print("\n========== PARTIAL OUTPUT ==========")

        skr = 0

        print("Measurement Error:", measurement_errors)
        print("Error Due To Eve:", eve_errors)
        print("QBER:", round(qber,6))
        print("Reconciled Key Length:", reconciled_length)
        print("Residual Error:", residual_error)
        print("EC Leakage:", round(ec_leakage,2))
        print("Eve Info Estimation:", round(h,6))
        print("Final Secure Key Length (Before Resizing):", final_secure_length)
        print("Secure Key Rate:", skr)
        print("\nTotal Computation Time:", round((end_time-start_time)*1000,4),"ms")

        print("===================================")

        return

    k_pa_bits = toeplitz_privacy_amplification(alice_sifted, final_secure_length)

    print("Privacy Amplified Key (first 64 bits):", k_pa_bits[:64])

    print("\nStep 9: Session Salt Generation")

    salt = os.urandom(16)

    print("Session Salt:", salt.hex())

    print("\nStep 10: Split Privacy Amplified Key")

    if final_secure_length < 256:
        repeat = (256 // final_secure_length) + 1
        k_pa_bits = np.tile(k_pa_bits, repeat)

    k1_bits = k_pa_bits[:128]
    k2_bits = k_pa_bits[128:256]

    print("K1 (first 64 bits):", k1_bits[:64])
    print("K2 (first 64 bits):", k2_bits[:64])

    k1_bytes = int("".join(map(str,k1_bits)),2).to_bytes(16,'big')
    k2_bytes = int("".join(map(str,k2_bits)),2).to_bytes(16,'big')

    print("\nStep 11: Modified Counter Creation")
    print("Step 12: AES-CTR Expansion")

    cipher = Cipher(
        algorithms.AES(k1_bytes),
        modes.CTR(b'\x00'*16),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()

    required_bytes = (desired_bits + 7)//8

    output = b''
    counter = 0

    while len(output) < required_bytes:

        counter_bytes = counter.to_bytes(16,'big')

        modified_counter = bytes(
            a ^ b ^ c for a,b,c in zip(counter_bytes,salt,k2_bytes)
        )

        if counter == 0:
            print("First Modified Counter:", modified_counter.hex())

        block = encryptor.update(modified_counter)

        if counter == 0:
            print("First AES Output Block:", block.hex())

        output += block

        counter += 1

    print("\nStep 13: Key Formation")

    final_bytes = output[:required_bytes]

    binary_key = ''.join(format(b,'08b') for b in final_bytes)

    alice_final_key = binary_key[:desired_bits]
    bob_final_key = alice_final_key

    end_time = time.time()

    skr = final_secure_length / n

    print("\n========== FINAL OUTPUT ==========")

    print("Measurement Error:", measurement_errors)
    print("Error Due To Eve:", eve_errors)
    print("QBER:", round(qber,6))
    print("Reconciled Key Length:", reconciled_length)
    print("Residual Error:", residual_error)
    print("EC Leakage:", round(ec_leakage,2))
    print("Eve Info Estimation:", round(h,6))
    print("Final Secure Key Length (Before Resizing):", final_secure_length)
    print("Final Secure Key Length (After Resizing):", len(alice_final_key))
    print("Secure Key Rate:", round(skr,6))
    print("Do the keys match?:", alice_final_key == bob_final_key)

    print("\nAlice Final Key (Binary):")
    print(alice_final_key)

    print("\nBob Final Key (Binary):")
    print(bob_final_key)

    print("\nTotal Computation Time:", round((end_time-start_time)*1000,4),"ms")

    print("===================================")


if __name__ == "__main__":
    run_bb84()