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
    def act(self, visitable):
        """
        """
        pass
