class StrOps:
    """Simple implementations for string operations"""
    
    @staticmethod
    def str_reverse(s):
        """Reverse a string"""
        return s[::-1]
    
    @staticmethod
    def palindrome(s):
        """Check if string is a palindrome"""
        s_clean = s.lower().replace(' ', '')
        return s_clean == s_clean[::-1]
