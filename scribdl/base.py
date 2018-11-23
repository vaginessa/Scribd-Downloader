from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class ScribdBase:
    """
    An Abstract Base Class for Scribd books and documents.
    """

    @abstractmethod
    def get_content(self):
        """
        An abstract method for fetching content off Scribd book or document.
        """
        pass
