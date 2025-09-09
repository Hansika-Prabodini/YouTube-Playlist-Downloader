#!/usr/bin/env python3
"""
Quick test to verify the optimization is working
"""

import time
from llm_benchmark.algorithms.primes import Primes

def test_prime_optimization():
    """Test that the optimization is working correctly"""
    
    test_number = 1700
    
    print("Testing Prime Number Optimization")
    print("=" * 40)
    
    # Test the original inefficient version
    print("Testing original inefficient algorithm...")
    start = time.perf_counter()
    result_orig = Primes.is_prime_original_ineff(test_number)
    time_orig = time.perf_counter() - start
    
    # Test the current (optimized) version
    print("Testing optimized algorithm...")
    start = time.perf_counter()
    result_opt = Primes.is_prime_ineff(test_number)  # This is now optimized
    time_opt = time.perf_counter() - start
    
    print(f"\nResults for is_prime({test_number}):")
    print(f"Original algorithm: {result_orig} in {time_orig:.6f}s")
    print(f"Optimized algorithm: {result_opt} in {time_opt:.6f}s")
    print(f"Speedup: {time_orig/time_opt:.1f}x faster")
    print(f"Results match: {result_orig == result_opt}")
    
    # Test that main.py will now run much faster
    print(f"\nThe main.py bottleneck is_prime_ineff(1700) is now optimized!")
    print(f"Expected runtime reduction: ~{time_orig/time_opt:.1f}x faster")

if __name__ == "__main__":
    test_prime_optimization()
