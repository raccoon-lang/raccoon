"""
Declares a base Visitor class.
"""


class Visitor:
    """
    Base Visitotr class
    """
    def start_visit(self):
        pass

    def act(self, visitable):
        return False
