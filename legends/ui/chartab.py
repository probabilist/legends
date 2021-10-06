"""The `legends.ui.chartab.CharTab` class and related objects.

"""

import tkinter as tk

__all__ = ['CharTab']

class CharTab(tk.Frame):
    """Displays details about a character.

    """
    def __init__(self, session, **options):
        """The constructor creates an instance as a child of the given
        session.

        Args:
            session (legends.ui.session.Session): The session to assign
                as the instance's parent.

        """
        tk.Frame.__init__(self, session, **options)
        self.actionBar().pack(fill=tk.X)

    def actionBar(self):
        """Builds and returns an action bar that allows the user to
        interact with the `CharTab`.

        """
        bar = tk.Frame(self)
        tk.Button(
            bar,
            text='back to roster',
            command=self.master.rosterTab
        ).pack(side=tk.LEFT)
        return bar
