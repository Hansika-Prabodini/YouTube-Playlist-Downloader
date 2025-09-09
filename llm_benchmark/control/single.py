class SingleForLoop:
    """Simple implementations for single for loop operations"""
    
    @staticmethod
    def sum_range(n):
        """Sum numbers from 1 to n"""
        return sum(range(1, n + 1))
    
    @staticmethod
    def max_list(lst):
        """Find maximum value in a list"""
        if not lst:
            return None
        max_val = lst[0]
        for val in lst:
            if val > max_val:
                max_val = val
        return max_val
    
    @staticmethod
    def sum_modulus(n, mod):
        """Sum all numbers from 1 to n that are divisible by mod"""
        total = 0
        for i in range(1, n + 1):
            if i % mod == 0:
                total += i
        return total
