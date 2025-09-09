#!/usr/bin/env python3
"""
Micro-benchmark script to measure performance improvements in prime number algorithms.
This script compares the original inefficient O(n) implementation with the optimized O(√n) version.
"""

import time
import statistics
from llm_benchmark.algorithms.primes import Primes

def benchmark_function(func, *args, iterations=5, **kwargs):
    """
    Benchmark a function multiple times and return statistics.
    
    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        iterations: Number of times to run the benchmark
        **kwargs: Keyword arguments to pass to function
    
    Returns:
        dict: Statistics including mean, min, max, and standard deviation
    """
    times = []
    results = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        times.append(end_time - start_time)
        results.append(result)
    
    # Verify all results are the same
    if not all(r == results[0] for r in results):
        raise ValueError("Function results are inconsistent across runs")
    
    return {
        'mean': statistics.mean(times),
        'min': min(times),
        'max': max(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'result': results[0]
    }

def format_time(seconds):
    """Format time in appropriate units"""
    if seconds >= 1:
        return f"{seconds:.4f}s"
    elif seconds >= 0.001:
        return f"{seconds * 1000:.2f}ms"
    elif seconds >= 0.000001:
        return f"{seconds * 1000000:.2f}μs"
    else:
        return f"{seconds * 1000000000:.2f}ns"

def run_benchmark():
    """Run comprehensive benchmarks comparing original vs optimized implementations"""
    
    print("=" * 80)
    print("MICRO-BENCHMARK: Prime Number Algorithm Optimization")
    print("=" * 80)
    print()
    
    # Test cases - various prime and composite numbers
    test_cases = [
        (101, "Small prime"),
        (500, "Medium composite"),
        (997, "Medium prime"),
        (1500, "Large composite"),
        (1699, "Large prime"),
        (1700, "Main bottleneck case (composite)")
    ]
    
    print(f"{'Test Case':<25} {'Type':<15} {'Original (O(n))':<20} {'Optimized (O(√n))':<20} {'Speedup':<10}")
    print("-" * 95)
    
    total_original_time = 0
    total_optimized_time = 0
    
    for n, description in test_cases:
        # Benchmark original inefficient version
        try:
            original_stats = benchmark_function(Primes.is_prime_original_ineff, n)
            original_time = original_stats['mean']
            total_original_time += original_time
        except Exception as e:
            print(f"Error benchmarking original algorithm for {n}: {e}")
            continue
            
        # Benchmark optimized version  
        try:
            optimized_stats = benchmark_function(Primes.is_prime_ineff, n)  # This is now the optimized version
            optimized_time = optimized_stats['mean']
            total_optimized_time += optimized_time
        except Exception as e:
            print(f"Error benchmarking optimized algorithm for {n}: {e}")
            continue
        
        # Calculate speedup
        speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
        
        # Verify results match
        if original_stats['result'] != optimized_stats['result']:
            print(f"WARNING: Results don't match for {n}!")
        
        print(f"{f'{n} ({description})':<25} {'':<15} {format_time(original_time):<20} {format_time(optimized_time):<20} {speedup:.1f}x")
    
    print("-" * 95)
    
    # Overall performance summary
    overall_speedup = total_original_time / total_optimized_time if total_optimized_time > 0 else float('inf')
    print(f"{'TOTAL':<25} {'':<15} {format_time(total_original_time):<20} {format_time(total_optimized_time):<20} {overall_speedup:.1f}x")
    
    print()
    print("ALGORITHM ANALYSIS:")
    print(f"• Original Algorithm: O(n) complexity - checks all odd numbers up to n")
    print(f"• Optimized Algorithm: O(√n) complexity - only checks up to √n")
    print(f"• Memory Usage: No change - both use O(1) space")
    print(f"• Overall Performance Improvement: {overall_speedup:.1f}x speedup")
    
    # Demonstrate the improvement with the main bottleneck case
    print()
    print("BOTTLENECK ANALYSIS:")
    main_case = 1700
    original_stats = benchmark_function(Primes.is_prime_original_ineff, main_case, iterations=10)
    optimized_stats = benchmark_function(Primes.is_prime_ineff, main_case, iterations=10)
    
    print(f"Main bottleneck case: is_prime_ineff({main_case})")
    print(f"• Original: {format_time(original_stats['mean'])} ± {format_time(original_stats['stdev'])}")
    print(f"• Optimized: {format_time(optimized_stats['mean'])} ± {format_time(optimized_stats['stdev'])}")
    print(f"• Speedup: {original_stats['mean'] / optimized_stats['mean']:.1f}x")
    print(f"• Operations reduced: ~{main_case//2} → ~{int(main_case**0.5)} ({(main_case//2) / int(main_case**0.5):.1f}x fewer)")

if __name__ == "__main__":
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
    except Exception as e:
        print(f"Error running benchmark: {e}")
