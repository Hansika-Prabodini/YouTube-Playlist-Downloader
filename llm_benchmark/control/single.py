class SingleForLoop:
    @staticmethod
    def sum_range(n):
        """Sum numbers from 1 to n using a loop"""
        total = 0
        for i in range(1, n + 1):
            total += i
        return total
    
    @staticmethod
    def max_list(lst):
        """Find maximum element in list using a loop"""
        if not lst:
            return None
        max_val = lst[0]
        for val in lst:
            if val > max_val:
                max_val = val
        return max_val
    
    @staticmethod
    def sum_modulus(limit, mod):
        """Sum all numbers divisible by mod up to limit"""
        total = 0
        for i in range(1, limit + 1):
            if i % mod == 0:
                total += i
        return total
