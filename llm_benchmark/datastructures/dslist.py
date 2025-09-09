class DsList:
    @staticmethod
    def modify_list(lst):
        """Modify list by doubling all elements"""
        return [x * 2 for x in lst]
    
    @staticmethod
    def search_list(lst, target):
        """Linear search for target in list"""
        for i, val in enumerate(lst):
            if val == target:
                return i
        return -1
    
    @staticmethod
    def sort_list(lst):
        """Sort list using built-in sort"""
        result = lst.copy()
        result.sort()
        return result
    
    @staticmethod
    def reverse_list(lst):
        """Reverse list"""
        return lst[::-1]
    
    @staticmethod
    def rotate_list(lst, k):
        """Rotate list by k positions"""
        if not lst or k == 0:
            return lst.copy()
        k = k % len(lst)
        return lst[k:] + lst[:k]
    
    @staticmethod
    def merge_lists(lst1, lst2):
        """Merge two lists"""
        return lst1 + lst2
