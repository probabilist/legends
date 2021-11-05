"""Tools for basic event handling.

"""

from legends.utils.functions import formatDict, objDict

__all__ = ['Event', 'EventHandler']

class Event(): # pylint: disable=too-few-public-methods
    """A simple event class meant to be subclassed.

    """

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, formatDict(objDict(self))
        )

class EventHandler():
    """A simple event handler.

    """

    def __init__(self):
        self._subscribers = []  # the list of subscribers

    def subscribe(self, callback):
        """Used to subscribe to the event handler.

        Args:
            callback (callable): The callable object to add to the list
                of subscribers. Must take one argument.

        """
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Used to unsubscribe from the event handler.

        Args:
            callback (callable): The callable object to remove from the
                list of subscribers. Must take one argument.

        """
        self._subscribers.remove(callback)

    def notify(self, event):
        """Notifies the subscribers of an event. More specifically, each
        callable in the list of subscribers is called with the given
        event object as the argument.

        Args:
            event (obj): The object to pass to the subscribing
                callables.

        """
        for func in self._subscribers:
            func(event)
