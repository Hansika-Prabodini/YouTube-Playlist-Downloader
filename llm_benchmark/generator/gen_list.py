import random

class GenList:
    """Simple implementations for list generation"""
    
    @staticmethod
    def random_list(size, max_val):
        """Generate a random list of given size with values up to max_val"""
        return [random.randint(1, max_val) for _ in range(size)]
    
    @staticmethod
    def random_matrix(rows, cols):
        """Generate a random matrix of given dimensions"""
        return [[random.randint(1, 10) for _ in range(cols)] for _ in range(rows)]
