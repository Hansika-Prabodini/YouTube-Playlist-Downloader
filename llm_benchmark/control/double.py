class DoubleForLoop:
    @staticmethod
    def sum_square(n):
        """Sum of squares using nested loops - intentionally inefficient O(n²)"""
        total = 0
        for i in range(1, n + 1):
            # Inefficient: recalculate square using nested loop
            square = 0
            for j in range(i):
                square += i
            total += square
        return total
    
    @staticmethod
    def sum_triangle(n):
        """Sum triangular numbers using nested loops"""
        total = 0
        for i in range(1, n + 1):
            triangular = 0
            for j in range(1, i + 1):
                triangular += j
            total += triangular
        return total
    
    @staticmethod
    def count_pairs(lst):
        """Count pairs in list using nested loops - O(n²)"""
        count = 0
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                count += 1
        return count
    
    @staticmethod
    def count_duplicates(list1, list2):
        """Count duplicates between two lists using nested loops"""
        count = 0
        for item1 in list1:
            for item2 in list2:
                if item1 == item2:
                    count += 1
        return count
    
    @staticmethod
    def sum_matrix(matrix):
        """Sum all elements in 2D matrix"""
        total = 0
        for row in matrix:
            for element in row:
                total += element
        return total
