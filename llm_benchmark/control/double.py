class DoubleForLoop:
    """Simple implementations for double for loop operations"""
    
    @staticmethod
    def sum_square(n):
        """Sum of squares from 1 to n"""
        total = 0
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                total += j * j
        return total
    
    @staticmethod
    def sum_triangle(n):
        """Sum triangular numbers"""
        total = 0
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                total += j
        return total
    
    @staticmethod
    def count_pairs(lst):
        """Count pairs in a list"""
        count = 0
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                count += 1
        return count
    
    @staticmethod
    def count_duplicates(lst1, lst2):
        """Count duplicates between two lists"""
        count = 0
        for item1 in lst1:
            for item2 in lst2:
                if item1 == item2:
                    count += 1
        return count
    
    @staticmethod
    def sum_matrix(matrix):
        """Sum all elements in a matrix"""
        total = 0
        for row in matrix:
            for val in row:
                total += val
        return total
