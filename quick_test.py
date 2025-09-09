import time
from llm_benchmark.algorithms.primes import Primes

# Test the main bottleneck
print("Testing is_prime_ineff(1700)...")
start = time.time()
result = Primes.is_prime_ineff(1700)
end = time.time()
print(f"Result: {result}, Time: {end - start:.4f}s")

# Test smaller numbers for comparison
test_numbers = [100, 500, 1000, 1500, 1700]
for n in test_numbers:
    start = time.time()
    result = Primes.is_prime_ineff(n)
    end = time.time()
    print(f"is_prime_ineff({n}): {result} in {end - start:.6f}s")
