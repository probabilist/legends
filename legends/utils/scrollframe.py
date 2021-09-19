"""The `legends.utils.scrollframe.ScrollFrame` class.

"""

import tkinter as tk
from tkinter import LEFT, RIGHT, Y, YES, BOTH, NW

__all__ = ['ScrollFrame']

class ScrollFrame(tk.Frame):
    """A simple scrollable frame.

    A `ScrollFrame` object is a `tk.Frame` with a `tk.Canvas` and a
    `tk.Scrollbar` embedded in it. Attached to the canvas is another
    frame, which is accessed via the `content` attribute. This frame is
    meant to hold other widgets, so widgets should be added to
    `content`, not to the `ScrollFrame` object itself.

    A `ScrollFrame` only has a vertical scrollbar. When the size of the
    `content` frame changes, the width of the embedded canvas also
    changes to match it. Parent objects can set the 'height' option of
    the `canvas` attribute to give the scrollable frame any desired
    initial height.

    Attributes:
        canvas (tk.Canvas): The embedded canvas.
        scrollbar (tk.Scrollbar): The embedded scrollbar.
        content (tk.Frame): The inner frame, attached to the embedded
            canvas. Widgets should be attached to this.

    """

    def __init__(self, parent=None, **options):
        """The constructor passes its arguments to the `tk.Frame`
        superclass.

        """
        tk.Frame.__init__(self, parent, **options)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Enter>', lambda event: (
            self.canvas.bind_all('<MouseWheel>', self.onMouseWheel)
        ))
        self.canvas.bind('<Leave>', lambda event: (
            self.canvas.unbind_all('<MouseWheel>')
        ))
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)
        self.content = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.content, anchor=NW)
        self.content.bind('<Configure>', lambda event:self.onContentConfig())

    def onMouseWheel(self, event):
        """Allows the user to use the mouse wheel/trackpad to scroll the
        canvas.

        Args:
            event (tk.Event): The `tk.Event` passed by the
                '<Mousewheel>' event.

        """
        self.canvas.yview_scroll(-1 * event.delta, 'units')

    def onContentConfig(self):
        """When the content area changes, the canvas adjusts its width
        and scrollable region to match it.

        """
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"),
            width=self.canvas.bbox('all')[2] - self.canvas.bbox('all')[0]
        )
