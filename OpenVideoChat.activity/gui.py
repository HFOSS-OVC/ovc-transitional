#    This file is part of OpenVideoChat.
#
#    OpenVideoChat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenVideoChat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenVideoChat.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod: `OpenVideoChat/OpenVideoChat.activity/gui` -- Open Video Chat Gui
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthor:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# External Imports
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.graphics.toolbarbox import ToolbarButton
# from sugar.activity.activity import ActivityToolbox
# from sugar.graphics.toolbutton import ToolButton

# Constants
MAX_MESSAGE_SIZE = 200
MIN_CHAT_HEIGHT = 180


class Gui(Gtk.Grid):
    def __init__(self, activity):
        Gtk.Grid.__init__(self)

        # Set Activity
        self.activity = activity

        # Add Video & Chat Containers
        self.add(self.build_videogrid())
        self.attach(self.build_chatgrid(), 0, 1, 1, 1)

        # Append Toolbar
        self.activity.set_toolbar_box(self.build_toolbar())

        # Display GUI
        self.show()

    def build_videogrid(self):
        # Prepare Video Display
        self.movie_window_preview = Gtk.DrawingArea()
        self.movie_window = Gtk.DrawingArea()
        self.movie_window_preview.set_hexpand(True)
        self.movie_window_preview.set_vexpand(True)
        self.movie_window.set_hexpand(True)
        self.movie_window.set_vexpand(True)

        # Create Grid Container
        video_grid = Gtk.Grid()
        video_grid.set_column_spacing(6)
        video_grid.add(self.movie_window_preview)
        video_grid.attach_next_to(self.movie_window, self.movie_window, Gtk.PositionType.RIGHT, 1, 1)

        # Add a name & apply complex CSS based theming
        provider = Gtk.CssProvider()
        provider.load_from_data("GtkDrawingArea { background: #000000; }")
        # provider.load_from_data(".background { background: #000 }")# Apply to whole window
        styler = video_grid.get_style_context()
        styler.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        video_grid.show_all()

        # Return Main Container
        return video_grid

    def build_chatgrid(self):
        # Prepare Chat Text Container
        self.chat_text = Gtk.TextBuffer()
        self.text_view = Gtk.TextView()
        self.text_view.set_buffer(self.chat_text)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Prepare Scrollable History
        chat_history = Gtk.ScrolledWindow()
        chat_history.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        chat_history.set_min_content_height(MIN_CHAT_HEIGHT)
        chat_history.add(self.text_view)
        chat_history.set_hexpand(True)

        # Send button to complete feel of a chat program
        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_max_length(MAX_MESSAGE_SIZE)
        self.chat_entry.connect("activate", self.send_message)
        self.chat_entry.set_hexpand(True)
        send_button = Gtk.Button(_("Send"))
        send_button.connect("clicked", self.send_message)

        # Wrap expanded Entry and normal-sized Send buttons into Grid Row
        chat_grid = Gtk.Grid()
        chat_grid.attach(chat_history, 0, 0, 2, 1)
        chat_grid.attach(self.chat_entry, 0, 1, 1, 1)
        chat_grid.attach(send_button, 1, 1, 1, 1)

        # Chat expander allows visibly toggle-able container for all chat components
        chat_expander = Gtk.Expander()
        chat_expander.set_label(_("Chat"))
        chat_expander.set_expanded(True)
        chat_expander.add(chat_grid)

        chat_expander.show_all()

        # Return entire expander
        return chat_expander

    def build_toolbar(self):
        # Prepare Primary Toolbar Container
        toolbar_box = ToolbarBox();

        # Create activity button
        toolbar_box.toolbar.insert(ActivityButton(self.activity), -1)

        # Create Settings Drop-Down
        settings_toolbar = self.build_settings_toolbar()
        settings_toolbar_button = ToolbarButton(
                page=settings_toolbar,
                icon_name="preferences-system")
                # icon_name="view-source")
        toolbar_box.toolbar.insert(settings_toolbar_button, -1)

        # Push stop button to far right
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)

        # Create stop button
        toolbar_box.toolbar.insert(StopButton(self.activity), -1)

        # Display all components & Return
        toolbar_box.show_all()
        return toolbar_box

    def build_settings_toolbar(self):
        # Storage for Settings Buttons
        self.settings_buttons = {}

        # Add Hacky-Reload Button (For now)
        self.settings_buttons["reload_video"] = ToolButton("view-refresh")
        self.settings_buttons["reload_video"].set_tooltip_text(_("Reload Video"))
        self.settings_buttons["reload_video"].connect("clicked", self.force_redraw)

        # Video Toggle Button
        self.settings_buttons["toggle_video"] = ToolButton()
        self.settings_buttons["toggle_video"].connect("clicked", self.toggle_video)
        self.toggle_video(None)

        # Audio Toggle Button
        self.settings_buttons["toggle_audio"] = ToolButton()
        self.settings_buttons["toggle_audio"].connect("clicked", self.toggle_audio)
        self.toggle_audio(None)

        # Create Settings Menu
        settings_toolbar = Gtk.Toolbar()
        settings_toolbar.insert(self.settings_buttons["reload_video"], -1)
        settings_toolbar.insert(self.settings_buttons["toggle_video"], -1)
        settings_toolbar.insert(self.settings_buttons["toggle_audio"], -1)

        # Display & Return Settings Menu
        settings_toolbar.show_all()
        return settings_toolbar

    def toggle_video(self, trigger):
        if self.activity.get_stream() and self.settings_buttons["toggle_video"].get_icon_name() == "activity-start":
            self.movie_window.show()
            # Call to gstreamer here
            self.settings_buttons["toggle_video"].set_icon_name("activity-stop")
            self.settings_buttons["toggle_video"].set_tooltip_text(_("Stop Video"))
        else:
            self.movie_window.hide()
            # Call to gstreamer here
            self.settings_buttons["toggle_video"].set_icon_name("activity-start")
            self.settings_buttons["toggle_video"].set_tooltip_text(_("Start Video"))

    def toggle_audio(self, trigger):
        if self.activity.get_stream() and self.settings_buttons["toggle_video"].get_icon_name() == "speaker-100":
            # Call to gstreamer here
            self.settings_buttons["toggle_audio"].set_icon_name("speaker-100")
            self.settings_buttons["toggle_audio"].set_tooltip_text(_("Mute Audio"))
        else:
            # Call to gstreamer here
            self.settings_buttons["toggle_audio"].set_icon_name("speaker-000")
            self.settings_buttons["toggle_audio"].set_tooltip_text(_("Turn Audio On"))

    def receive_stream(self):
        self.toggle_video(None)
        self.toggle_audio(None)

    def get_history(self):
        return self.chat_text.get_text(
                self.chat_text.get_start_iter(),
                self.chat_text.get_end_iter(),
                True)

    def receive_message(self, message):
        self.chat_text.insert(self.chat_text.get_end_iter(), "%s\n" % message, -1)
        self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1, False, 0.0, 0.0)

    def send_message(self, trigger):
        if (self.chat_entry.get_text() != ""):
            self.receive_message(self.chat_entry.get_text())# Temporary for Testing Non-Networked
            # self.activity.send_message(self.chat_entry.get_text())
            self.chat_entry.set_text("")

    def force_redraw(self, trigger):
        # Fixme: This should not be required, this is a hack for now until
        # a better solution that works is found
        self.movie_window_preview.hide()
        self.movie_window_preview.show()
        self.movie_window.hide()
        if self.activity.get_stream():
            self.movie_window.show()

    def render_preview(self, source):
        source.set_xwindow_id(self.movie_window_preview.get_property('window').get_xid())

    def render_incoming(self, source):
        source.set_xwindow_id(self.movie_window.get_property('window').get_xid())
