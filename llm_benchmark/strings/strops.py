class StrOps:
    @staticmethod
    def str_reverse(s):
        """Reverse a string"""
        return s[::-1]
    
    @staticmethod
    def palindrome(s):
        """Check if string is a palindrome"""
        s = s.lower()
        return s == s[::-1]
