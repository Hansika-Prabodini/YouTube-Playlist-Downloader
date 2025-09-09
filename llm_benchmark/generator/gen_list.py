import random

class GenList:
    @staticmethod
    def random_list(size, max_val):
        """Generate a random list of specified size with values up to max_val"""
        return [random.randint(1, max_val) for _ in range(size)]
    
    @staticmethod
    def random_matrix(rows, cols):
        """Generate a random matrix of specified dimensions"""
        return [[random.randint(1, 100) for _ in range(cols)] for _ in range(rows)]
