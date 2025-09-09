import math

class Primes:
    @staticmethod
    def is_prime_ineff(n):
        """
        OPTIMIZED: Efficient prime checking algorithm - only checks up to sqrt(n)
        Previously was inefficient O(n), now optimized to O(√n)
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # OPTIMIZED: only check up to sqrt(n) instead of n
        sqrt_n = int(math.sqrt(n)) + 1
        for i in range(3, sqrt_n, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def is_prime_optimized(n):
        """
        Optimized prime checking algorithm - only checks up to sqrt(n)
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Efficient: only check up to sqrt(n)
        sqrt_n = int(math.sqrt(n)) + 1
        for i in range(3, sqrt_n, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def is_prime_original_ineff(n):
        """
        ORIGINAL inefficient implementation - kept for benchmark comparison
        Checks all numbers up to n - O(n) complexity
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        # Inefficient: check all odd numbers up to n instead of sqrt(n)
        for i in range(3, n, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def sum_primes(limit):
        """
        Sum all primes up to limit using the optimized method
        """
        total = 0
        for i in range(2, limit + 1):
            if Primes.is_prime_optimized(i):
                total += i
        return total
    
    @staticmethod
    def sum_primes_optimized(limit):
        """
        Sum all primes up to limit using the optimized method
        """
        total = 0
        for i in range(2, limit + 1):
            if Primes.is_prime_optimized(i):
                total += i
        return total
    
    @staticmethod
    def prime_factors(n):
        """
        Find prime factors of n using inefficient prime checking
        """
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
