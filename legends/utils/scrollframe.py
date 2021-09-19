"""The `legends.utils.scrollframe.ScrollFrame` class.

"""

import tkinter as tk
from tkinter import LEFT, RIGHT, Y, YES, BOTH, NW

__all__ = ['ScrollFrame']

class ScrollFrame(tk.Frame):
    """A simple scrollable frame.

    A ScrollFrame object is a Frame with a Canvas and a Scrollbar
    embedded in it. Attached to the canvas is another frame, which is
    accessed via the `content` attribute. This frame is meant to hold
    other widgets, so widgets should be added to `content`, not to the
    ScrollFrame object itself.

    A ScrollFrame only has a vertical scrollbar. When the size of the
    `content` frame changes, the width of the embedded canvas also
    changes to match it. Parent objects can set the 'height' option of
    the `canvas` attribute to give the scrollable frame any desired
    initial height.

    Attributes:
        canvas (Canvas): The embedded canvas.
        scrollbar (Scrollbar): The embedded scrollbar.
        content (Frame): The inner frame, attached to the embedded
            canvas. Widgets should be attached to this.

    """

    def __init__(self, parent=None, **options):
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
        self.content.bind('<Configure>', self.onContentConfig)

    def onMouseWheel(self, event):
        """Allows the user to use the mouse wheel/trackpad to scroll the
        canvas.

        """
        self.canvas.yview_scroll(-1 * event.delta, 'units')

    def onContentConfig(self, event): # pylint: disable=unused-argument
        """When the content area changes, the canvas adjusts its width
        and scrollable region to match it.

        """
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"),
            width=self.canvas.bbox('all')[2] - self.canvas.bbox('all')[0]
        )
