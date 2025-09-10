class Primes:
    """Simple implementations for prime number operations"""
    
    @staticmethod
    def is_prime_ineff(n):
        """Inefficient prime check"""
        if n < 2:
            return False
        for i in range(2, n):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def sum_primes(n):
        """Sum all primes up to n"""
        total = 0
        for i in range(2, n + 1):
            if Primes.is_prime_ineff(i):
                total += i
        return total
    
    @staticmethod
    def prime_factors(n):
        """Find prime factors of n"""
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
