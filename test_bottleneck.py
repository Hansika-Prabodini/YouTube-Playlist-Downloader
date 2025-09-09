import time
from llm_benchmark.algorithms.primes import Primes
from llm_benchmark.control.double import DoubleForLoop
from llm_benchmark.generator.gen_list import GenList

def benchmark_function(func, *args, **kwargs):
    """Benchmark a function and return execution time"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time, result

def test_bottlenecks():
    """Test various functions to identify bottlenecks"""
    print("Testing potential bottlenecks...")
    print("=" * 50)
    
    # Test prime operations
    print("Testing prime operations:")
    time_taken, result = benchmark_function(Primes.is_prime_ineff, 1700)
    print(f"is_prime_ineff(1700): {time_taken:.4f}s -> {result}")
    
    time_taken, result = benchmark_function(Primes.sum_primes, 100)
    print(f"sum_primes(100): {time_taken:.4f}s -> {result}")
    
    # Test double loop operations
    print("\nTesting double loop operations:")
    time_taken, result = benchmark_function(DoubleForLoop.sum_square, 1000)
    print(f"sum_square(1000): {time_taken:.4f}s -> {result}")
    
    time_taken, result = benchmark_function(DoubleForLoop.sum_triangle, 500)
    print(f"sum_triangle(500): {time_taken:.4f}s -> {result}")
    
    # Test with larger data
    large_list = GenList.random_list(1000, 100)
    time_taken, result = benchmark_function(DoubleForLoop.count_pairs, large_list)
    print(f"count_pairs(1000 items): {time_taken:.4f}s -> {result}")

if __name__ == "__main__":
    test_bottlenecks()
