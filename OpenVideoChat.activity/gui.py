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
import logger
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

# Define Logger for Logging
logger = logging.getLogger('ovc-activity')


# Constants
MAX_MESSAGE_SIZE = 200
MIN_CHAT_HEIGHT = 180


class Gui(Gtk.Grid):
    def __init__(self, activity):
        Gtk.Grid.__init__(self)

        # Set Activity
        self.activity = activity

        # Set Activity Title
        self.activity.set_title(_("OpenVideoChat"))

        # Add Video & Chat Containers
        self.add(self.build_video())
        self.attach(self.build_chat(), 0, 1, 1, 1)

        # Append Toolbar
        self.activity.set_toolbar_box(self.build_toolbar())

        # Display GUI
        self.show()

    def build_video(self):
        # Prepare Video Display
        self.movie_window_preview = Gtk.DrawingArea()
        self.movie_window = Gtk.DrawingArea()

        # Use Fixed to append overlays to an overlay
        video_fixed = Gtk.Fixed()
        video_fixed.put(self.movie_window, 0, 0)
        video_fixed.put(self.movie_window_preview, 0, 0)
        video_fixed.set_halign(Gtk.Align.START)
        video_fixed.set_valign(Gtk.Align.START)

        # Use event box for background coloring
        video_eventbox = Gtk.EventBox()
        video_eventbox.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01,.01,.01,.8))
        video_eventbox.set_hexpand(True)
        video_eventbox.set_vexpand(True)
        video_eventbox.add(video_fixed)
        video_eventbox.show_all()

        # Return Overlay Container
        return video_eventbox

    def build_chat(self):
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

        # Display all chat components
        chat_expander.show_all()

        # Return entire expander
        return chat_expander

    def build_toolbar(self):
        # Prepare Primary Toolbar Container
        toolbar_box = ToolbarBox();

        # Create activity button
        toolbar_box.toolbar.insert(ActivityButton(self.activity), -1)

        # Storage for Toggle Buttons
        self.settings_buttons = {}

        # Video Toggle
        self.settings_buttons["toggle_video"] = ToolButton()
        self.settings_buttons["toggle_video"].connect("clicked", self.toggle_video)
        toolbar_box.toolbar.insert(self.settings_buttons["toggle_video"], -1)

        # Audio Toggle
        self.settings_buttons["toggle_audio"] = ToolButton()
        self.settings_buttons["toggle_audio"].connect("clicked", self.toggle_audio)
        toolbar_box.toolbar.insert(self.settings_buttons["toggle_audio"], -1)

        # Forced Refresh
        reload_video = ToolButton("view-refresh")
        reload_video.set_tooltip_text(_("Reload Video"))
        reload_video.connect("clicked", self.force_redraw)
        toolbar_box.toolbar.insert(reload_video, -1)

        # Push stop button to far right
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)

        # Create stop button
        toolbar_box.toolbar.insert(StopButton(self.activity), -1)

        # Run Toggles
        self.run_toggles()

        # Display all components & Return
        toolbar_box.show_all()
        return toolbar_box

    def run_toggles(self):
        self.toggle_video(None)
        self.toggle_audio(None)

    def toggle_video(self, trigger):
        if self.activity.get_stream():
            self.settings_buttons["toggle_video"].set_sensitive(True)
            if self.settings_buttons["toggle_video"].get_icon_name() == "activity-stop":
                self.movie_window.hide()
                self.movie_window_preview_width, self.movie_window_preview_height = False, False
                self.settings_buttons["toggle_video"].set_icon_name("activity-start")
                self.settings_buttons["toggle_video"].set_tooltip_text("Start Video")
                # Call to GStreamer to restart video
            else:
                self.movie_window.show()
                self.movie_window_preview_width, self.movie_window_preview_height = 320, 240
                self.settings_buttons["toggle_video"].set_icon_name("activity-stop")
                self.settings_buttons["toggle_video"].set_tooltip_text("Stop Video")
                # Call to GStreamer to end video
        else:
            self.settings_buttons["toggle_video"].set_sensitive(False)
            self.settings_buttons["toggle_video"].set_icon_name("activity-start")
            self.settings_buttons["toggle_video"].set_tooltip_text("Start Video")
            self.movie_window.hide()

    def toggle_audio(self, trigger):
        if self.activity.get_stream():
            self.settings_buttons["toggle_audio"].set_sensitive(True)
            if self.settings_buttons["toggle_audio"].get_icon_name() == "speaker-000":
                self.settings_buttons["toggle_audio"].set_icon_name("speaker-100")
                self.settings_buttons["toggle_audio"].set_tooltip_text("Turn on Sound")
                # Call to GStreamer to restart audio
            else:
                self.settings_buttons["toggle_audio"].set_icon_name("speaker-000")
                self.settings_buttons["toggle_audio"].set_tooltip_text("Mute Sound")
                # Call to GStreamer to end audio
        else:
            self.settings_buttons["toggle_audio"].set_sensitive(False)
            self.settings_buttons["toggle_audio"].set_icon_name("speaker-100")
            self.settings_buttons["toggle_audio"].set_tooltip_text("Turn on Sound")

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
        # With fixed for overlay order of show() matters
        self.movie_window.hide()
        self.movie_window_preview.hide()
        self.movie_window_preview.show()
        if self.activity.get_stream():
            self.movie_window.show()

    def render_preview(self, source):
        if self.movie_window_preview_height:
            self.movie_window_preview.set_size_request(
                    self.movie_window_preview.get_parent().get_parent().get_allocation().width,
                    self.movie_window_preview.get_parent().get_parent().get_allocation().height)
        else:
            self.movie_window_preview.set_size_request(
                    self.movie_window_preview_width,
                    self.movie_window_preview_height)
        source.set_xwindow_id(self.movie_window_preview.get_property('window').get_xid())

    def render_incoming(self, source):
        self.movie_window.set_size_request(
                self.movie_window.get_parent().get_parent().get_allocation().width,
                self.movie_window.get_parent().get_parent().get_allocation().height)
        source.set_xwindow_id(self.movie_window.get_property('window').get_xid())
