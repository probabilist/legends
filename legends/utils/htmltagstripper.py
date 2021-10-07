"""The `legends.utils.htmltagstripper.HTMLTagStripper` class.

"""

from html.parser import HTMLParser

__all__ = ['HTMLTagStripper']

# pylint: disable-next=abstract-method, too-few-public-methods
class HTMLTagStripper(HTMLParser):
    """An HTML parser that removes start and end tags.

    Attributes:
        text (str): The parsed HTML.

    """
    def __init__(self, data=None):
        """The constructor creates a new parser and parses the given
        data.

        Args:
            data (str): The HTML to parse.

        """
        HTMLParser.__init__(self)
        self.text = ''
        if data is not None:
            self.feed(data)

    def handle_data(self, data): # pylint: disable=invalid-name
        """Copy data verbatim.

        """
        self.text += data
