"""
"""

from abc import ABC, abstractmethod


class Visitor(ABC):
    """
    """

    @abstractmethod
    def start_visit(self):
        """
        """
        pass

    @abstractmethod
    def act(self, visitable=None):
        """
        visitable argument is optional but it may be useful in top-down recursive trasverse, which means it allows passing the children AST to the visitor.
        """
        pass
