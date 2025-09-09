class Sort:
    @staticmethod
    def sort_list(lst):
        """Simple bubble sort - inefficient O(n²) algorithm"""
        n = len(lst)
        for i in range(n):
            for j in range(0, n - i - 1):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
    
    @staticmethod
    def dutch_flag_partition(lst, pivot):
        """Dutch flag partitioning around pivot value"""
        low = 0
        mid = 0  
        high = len(lst) - 1
        
        while mid <= high:
            if lst[mid] < pivot:
                lst[low], lst[mid] = lst[mid], lst[low]
                low += 1
                mid += 1
            elif lst[mid] == pivot:
                mid += 1
            else:
                lst[mid], lst[high] = lst[high], lst[mid]
                high -= 1
    
    @staticmethod
    def max_n(lst, n):
        """Return the n largest elements using inefficient approach"""
        sorted_list = lst.copy()
        Sort.sort_list(sorted_list)  # Use our inefficient bubble sort
        return sorted_list[-n:] if n <= len(sorted_list) else sorted_list
