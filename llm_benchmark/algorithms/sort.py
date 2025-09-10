class Sort:
    """Simple implementations for sorting operations"""
    
    @staticmethod
    def sort_list(lst):
        """Sort list in place using bubble sort"""
        n = len(lst)
        for i in range(n):
            for j in range(0, n - i - 1):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
    
    @staticmethod
    def dutch_flag_partition(lst, pivot):
        """Dutch flag partition around pivot value"""
        left = 0
        right = len(lst) - 1
        i = 0
        
        while i <= right:
            if lst[i] < pivot:
                lst[i], lst[left] = lst[left], lst[i]
                left += 1
                i += 1
            elif lst[i] > pivot:
                lst[i], lst[right] = lst[right], lst[i]
                right -= 1
            else:
                i += 1
    
    @staticmethod
    def max_n(lst, n):
        """Find the n largest elements"""
        sorted_lst = sorted(lst, reverse=True)
        return sorted_lst[:n]
