"""Tracks active survival effects in Star Trek: Legends.

Attributes:
    BUFFS (dict): {`str`:`int`} Maps names of survival effects to the
        duration of the effect, measured in number of battles.

"""

import json
import ui
import dialogs

BUFFS = {
    'ATTACK UP': 10,
    'ATTACK DOWN': 10,
    'DEFENSE UP': 10,
    'DEFENSE DOWN': 10,
    'CLOAK': 15,
    'TECH UP': 10,
    'TECH DOWN': 10,
    'MORALE UP': 5,
    'MORALE DOWN': 10,
    'CRIT CHANCE UP': 15,
    'RED ALERT': 15,
    'SCAN': 15,
    'SHIELD': 10,
    'HEAL': 1,
    'REGENERATE': 5
}

class BuffList():
    """A wrapper around the dictionary of active survival effects.

    The dictionary is stored in a private attribute as a dictionary
    whose keys match `BUFFS` and whose values are the number of battles
    remaining.

    Attributes:
        buffTracker (BuffTracker): The `BuffTracker` instance associated
            with this buff list.

    """

    def __init__(self, buffTracker):
        """The constructor tries to load the buff list data from
        'bufftracker.json' in the current working directory. If no such
        file exists, the buff list is initialized with an empty
        dictionary.

        """
        self.buffTracker = buffTracker
        try:
            with open('bufftracker.json', encoding='utf-8') as f:
                self._buffList = json.load(f)
        except FileNotFoundError:
            self._buffList = {buff: 0 for buff in BUFFS}
            self.save()

    @property
    def buffList(self):
        """`dict`: {`str`:`int`} The dictionary of buffs that have
        positive duration.
        """
        return {k: v for  k, v in self._buffList.items() if v > 0}    

    @property
    def numRows(self):
        """`int`: The number of active effects."""
        return len(self.buffList)

    def save(self):
        """Saves the buff list data to 'bufftracker.json' in the current
        working directory.

        """
        with open('bufftracker.json', 'w', encoding='utf-8') as f:
            json.dump(self._buffList, f, indent=4)

    def add(self, buff, duration):
        """Adds the given buff with the given duration to the list of
        active effects. Then saves the data.

        Args:
            buff (str): The name of the effect.
            duration (int): The number of remaining battles for the
                effect.

        """
        self._buffList[buff] += duration
        self.save()

    def decrement(self):
        """Decreases each duration by 1, then saves the data.

        """
        for buff in self.buffList:
            self._buffList[buff] -= 1
        self.save()

    # pylint: disable-next=invalid-name, unused-argument
    def tableview_number_of_rows(self, tableview, section):
        """Returns the `numRows` attribute.

        """
        return self.numRows

    # pylint: disable-next=invalid-name, unused-argument
    def tableview_cell_for_row(self, tableview, section, row):
        """Creates and returns a cell for the given row.

        """
        buff, duration = sorted(list(self.buffList.items()))[row]
        cell = ui.TableViewCell()
        cell.text_label.text = f'{buff} ({duration})'
        return cell

    # pylint: disable-next=invalid-name, unused-argument, no-self-use
    def tableview_can_delete(self, tableview, section, row):
        """Enables row deletion."""
        return True

    # pylint: disable-next=invalid-name, unused-argument, no-self-use
    def tableview_title_for_delete_button(self, tableview, section, row):
        """Changes the 'Delete' button to an 'Adjust' button."""
        return 'Adjust'

    # pylint: disable-next=invalid-name, unused-argument
    def tableview_delete(self, tableview, section, row):
        """Prompts the user for an integer between 0 and 15, then sets
        the duration for the given row to that integer. If that integer
        is 0, the row is deleted. Buff list data is then saved and the
        buff tracker view is refreshed.

        """
        duration = dialogs.list_dialog(
            'Battles Remaining', items=list(range(16))
        )
        buff = sorted(list(self.buffList))[row]
        if duration is not None:
            self._buffList[buff] = duration
        self.save()
        self.buffTracker.refresh()

class BuffTracker(ui.View):
    """The Buff Tracker app.

    Attributes:
        buttons (dict): {`str`:`ui.Button`} Maps names of buffs to their
            corresponding button in the UI.
        battleButton (ui.Button): The battle button in the UI.
        table (ui.TableView): The table in the UI.

    """

    def __init__(self): # pylint: disable=super-init-not-called
        """The constructor sets the name and background color of the
        app, creates the buff buttons, battle button, and table, and
        adds them as subviews. An instance of `BuffList` is created and
        the table's data source and delegate are set to this instance.

        """
        self.name = 'Buff Tracker'
        self.background_color = 'blue'
        self._buttonHeight = 60
        self._cellHeight = 44
        self.buttons = {}
        for buff in BUFFS:
            button = ui.Button(
                title=buff, action=self.add,
                font=('<system>', 13), tint_color='white',
                background_color='green', border_color='black', border_width=1
            )
            self.buttons[buff] = button
            self.add_subview(button)
        self.battleButton = ui.Button(
            title='BATTLE', action=self.battle,
            font=('<system-bold>', 25), tint_color='white',
            background_color='red', border_color='black', border_width=1
        )
        self.add_subview(self.battleButton)
        buffList = BuffList(self)
        self.table = ui.TableView(
            allows_selection=False, always_bounce_vertical=False,
            data_source=buffList, delegate=buffList
        )
        self.add_subview(self.table)

    def refresh(self):
        """Reloads the table data and sets the table height to match the
        number of rows, if there is space. Otherwise, sets the table
        height to fill the bottom part of the view.

        """
        self.table.reload_data()
        numRows = self.table.data_source.numRows
        self.table.height = min(
            self._cellHeight * numRows,
            self.height - 6 * self._buttonHeight
        )

    def add(self, sender):
        """Called when a buff button is tapped. Adds a new instance of
        the given buff with duration given by BUFFS. Then refreshes the
        app.

        """
        self.table.data_source.add(sender.title, BUFFS[sender.title])
        self.refresh()

    def battle(self, sender=None): # pylint: disable=unused-argument
        """Calls the data source's `decrement()` method, then refreshes
        the app.

        """
        self.table.data_source.decrement()
        self.refresh()

    def layout(self):
        """Sets the `frame` attribute of every button, sets the table's
        `x`, `y`, and `width` attributes, then refreshes the app.

        """
        for index, button in enumerate(self.buttons.values()):
            row = index % 5
            column = int(index/5)
            button.frame = (
                column * self.width/3,
                row * self._buttonHeight,
                self.width/3,
                self._buttonHeight
            )
        self.battleButton.frame = (
            0, 5 * self._buttonHeight, self.width, self._buttonHeight
        )
        self.table.x = 0
        self.table.y = 6 * self._buttonHeight
        self.table.width = self.width
        self.refresh()

if __name__ == '__main__':
    BuffTracker().present('fullscreen', hide_title_bar=True)
