class DsList:
    """Simple implementations for list data structure operations"""
    
    @staticmethod
    def modify_list(lst):
        """Return a modified copy of the list (doubled values)"""
        return [x * 2 for x in lst]
    
    @staticmethod
    def search_list(lst, target):
        """Search for target in list and return index"""
        for i, val in enumerate(lst):
            if val == target:
                return i
        return -1
    
    @staticmethod
    def sort_list(lst):
        """Return a sorted copy of the list"""
        return sorted(lst)
    
    @staticmethod
    def reverse_list(lst):
        """Return a reversed copy of the list"""
        return lst[::-1]
    
    @staticmethod
    def rotate_list(lst, positions):
        """Return a rotated copy of the list"""
        if not lst:
            return lst
        n = len(lst)
        positions = positions % n
        return lst[positions:] + lst[:positions]
    
    @staticmethod
    def merge_lists(lst1, lst2):
        """Return a merged copy of two lists"""
        return lst1 + lst2
