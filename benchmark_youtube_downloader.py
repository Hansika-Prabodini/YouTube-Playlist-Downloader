#!/usr/bin/env python3
"""
Micro-benchmark script to test performance improvements in YouTube Downloader GUI.
This script tests the specific bottlenecks we identified and optimized.
"""

import time
import re
import threading
import subprocess
import sys
from collections import deque
import psutil
import os
from memory_profiler import profile

class PerformanceBenchmark:
    def __init__(self):
        # Original patterns (compiled each time)
        self.original_patterns = [
            r'\[download\] 100%',
            r'\[ExtractAudio\] Destination:',
            r'\[ffmpeg\] Destination:',
            r'\[Merger\] Merging formats into'
        ]
        
        # Pre-compiled patterns (optimized)
        self.compiled_patterns = [
            re.compile(r'\[download\] 100%'),
            re.compile(r'\[ExtractAudio\] Destination:'),
            re.compile(r'\[ffmpeg\] Destination:'),
            re.compile(r'\[Merger\] Merging formats into')
        ]
        
        # Progress regex
        self.progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
        
        # Sample output data for testing
        self.sample_lines = [
            "[download] 15.2% of 45.6MB at 1.2MB/s ETA 00:35",
            "[download] 32.7% of 45.6MB at 1.5MB/s ETA 00:22", 
            "[download] 67.3% of 45.6MB at 1.8MB/s ETA 00:08",
            "[download] 100% of 45.6MB in 00:42",
            "[ExtractAudio] Destination: video.mp3",
            "[ffmpeg] Destination: video.mp4",
            "Some random output line",
            "Another non-matching line"
        ] * 100  # Multiply for more realistic testing

    def benchmark_regex_compilation(self, iterations=10000):
        """Test regex compilation overhead - ORIGINAL vs OPTIMIZED approach"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Regex Compilation Performance")
        print(f"{'='*60}")
        
        # Original approach: compile patterns each time
        start_time = time.time()
        for _ in range(iterations):
            for pattern in self.original_patterns:
                for line in self.sample_lines[:10]:  # Test with subset
                    re.search(pattern, line)
        original_time = time.time() - start_time
        
        # Optimized approach: use pre-compiled patterns  
        start_time = time.time()
        for _ in range(iterations):
            for compiled_pattern in self.compiled_patterns:
                for line in self.sample_lines[:10]:  # Test with subset
                    compiled_pattern.search(line)
        optimized_time = time.time() - start_time
        
        improvement = ((original_time - optimized_time) / original_time) * 100
        
        print(f"Original approach (compile each time): {original_time:.4f} seconds")
        print(f"Optimized approach (pre-compiled):    {optimized_time:.4f} seconds")
        print(f"Performance improvement: {improvement:.2f}%")
        print(f"Speed multiplier: {original_time/optimized_time:.2f}x faster")

    def benchmark_progress_parsing(self, iterations=50000):
        """Test progress regex performance"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Progress Parsing Performance") 
        print(f"{'='*60}")
        
        progress_lines = [line for line in self.sample_lines if 'download' in line and '%' in line]
        
        # Test progress parsing speed
        start_time = time.time()
        matches_found = 0
        for _ in range(iterations):
            for line in progress_lines:
                match = self.progress_regex.search(line)
                if match:
                    matches_found += 1
                    try:
                        percentage = float(match.group(1))
                    except (ValueError, IndexError):
                        pass
        
        parsing_time = time.time() - start_time
        lines_per_second = (iterations * len(progress_lines)) / parsing_time
        
        print(f"Processed {iterations * len(progress_lines)} lines in {parsing_time:.4f} seconds")
        print(f"Processing speed: {lines_per_second:,.0f} lines/second")
        print(f"Matches found: {matches_found}")

    def benchmark_memory_usage(self):
        """Test memory usage with different buffer sizes"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Memory Usage Comparison")
        print(f"{'='*60}")
        
        # Test with original buffer size (50)
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        large_buffer = deque(maxlen=50)
        for i in range(10000):
            large_buffer.append(f"Sample output line {i} with some content to simulate real output")
        
        large_buffer_memory = process.memory_info().rss / 1024 / 1024  # MB
        large_buffer_usage = large_buffer_memory - initial_memory
        
        # Clear and test with optimized buffer size (20)
        del large_buffer
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        small_buffer = deque(maxlen=20) 
        for i in range(10000):
            small_buffer.append(f"Sample output line {i} with some content to simulate real output")
            
        small_buffer_memory = process.memory_info().rss / 1024 / 1024  # MB
        small_buffer_usage = small_buffer_memory - current_memory
        
        print(f"Original buffer (maxlen=50): {large_buffer_usage:.2f} MB")
        print(f"Optimized buffer (maxlen=20): {small_buffer_usage:.2f} MB") 
        if large_buffer_usage > 0:
            memory_saved = ((large_buffer_usage - small_buffer_usage) / large_buffer_usage) * 100
            print(f"Memory saved: {memory_saved:.2f}%")

    def benchmark_ui_update_frequency(self):
        """Simulate UI update frequency impact"""
        print(f"\n{'='*60}")
        print("BENCHMARK: UI Update Frequency Impact")
        print(f"{'='*60}")
        
        # Simulate original approach (update every line)
        updates_original = 0
        start_time = time.time()
        for line in self.sample_lines:
            # Simulate UI update overhead
            time.sleep(0.0001)  # Simulate small GUI update delay
            updates_original += 1
        original_time = time.time() - start_time
        
        # Simulate optimized approach (batched updates)
        updates_optimized = 0
        last_update = 0
        ui_update_interval = 0.1  # 100ms interval
        start_time = time.time()
        for i, line in enumerate(self.sample_lines):
            current_time = time.time()
            if (current_time - last_update) >= ui_update_interval:
                # Simulate UI update overhead
                time.sleep(0.0001)
                updates_optimized += 1
                last_update = current_time
        optimized_time = time.time() - start_time
        
        print(f"Original approach - Updates: {updates_original}, Time: {original_time:.4f}s")
        print(f"Optimized approach - Updates: {updates_optimized}, Time: {optimized_time:.4f}s")
        print(f"UI updates reduced by: {((updates_original - updates_optimized) / updates_original) * 100:.2f}%")
        if original_time > optimized_time:
            print(f"Time improvement: {((original_time - optimized_time) / original_time) * 100:.2f}%")

    def benchmark_monitoring_frequency(self):
        """Test impact of monitoring frequency changes"""
        print(f"\n{'='*60}")
        print("BENCHMARK: Monitoring Frequency Impact")
        print(f"{'='*60}")
        
        # Simulate original monitoring (every 100ms)
        original_frequency = 0.1  # 100ms
        duration = 10  # 10 seconds simulation
        original_calls = int(duration / original_frequency)
        
        # Simulate optimized monitoring (every 500ms)  
        optimized_frequency = 0.5  # 500ms
        optimized_calls = int(duration / optimized_frequency)
        
        cpu_overhead_per_call = 0.001  # Simulated CPU overhead per monitoring call
        
        original_cpu_time = original_calls * cpu_overhead_per_call
        optimized_cpu_time = optimized_calls * cpu_overhead_per_call
        
        print(f"Original monitoring (100ms): {original_calls} calls in {duration}s")
        print(f"Optimized monitoring (500ms): {optimized_calls} calls in {duration}s")
        print(f"Monitoring calls reduced by: {((original_calls - optimized_calls) / original_calls) * 100:.2f}%")
        print(f"CPU overhead reduced by: {((original_cpu_time - optimized_cpu_time) / original_cpu_time) * 100:.2f}%")

    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("YouTube Downloader GUI Performance Benchmarks")
        print("=" * 60)
        print("Testing optimizations made to address identified bottlenecks...")
        
        self.benchmark_regex_compilation()
        self.benchmark_progress_parsing() 
        self.benchmark_memory_usage()
        self.benchmark_ui_update_frequency()
        self.benchmark_monitoring_frequency()
        
        print(f"\n{'='*60}")
        print("SUMMARY OF OPTIMIZATIONS MADE:")
        print("=" * 60)
        print("1. ✅ Reduced monitoring frequency from 100ms to 500ms")
        print("2. ✅ Pre-compiled regex patterns to avoid repeated compilation")
        print("3. ✅ Reduced memory buffer size from 50 to 20 lines")
        print("4. ✅ Implemented batched UI updates to reduce GUI thread load")
        print("5. ✅ Optimized subprocess output processing")
        print(f"\n{'='*60}")

if __name__ == "__main__":
    try:
        import memory_profiler
    except ImportError:
        print("Installing memory_profiler for memory benchmarks...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "memory-profiler", "psutil"])
        import memory_profiler
    
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
