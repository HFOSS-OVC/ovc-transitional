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
from gettext import gettext as _
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.graphics.toolbarbox import ToolbarButton
# from sugar.activity.activity import ActivityToolbox
# from sugar.graphics.toolbutton import ToolButton

class Gui(Gtk.Box):
    def __init__(self, activity):
        Gtk.Box.__init__(self)

        # Set Orientation
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # Set Activity
        self.activity = activity

        # Add Video & Chatbox Containers
        self.pack_start(self.build_videobox(), True, True, 0)
        self.pack_start(self.build_chatbox(), True, True, 0)

        # Append Toolbar
        self.activity.set_toolbar_box(self.build_toolbar())

        # Display GUI
        self.show_all()

        # Fix scroll_to_iter & placement of this code
        # Scroll to bottom
        # self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0, False, 0.5, 0.5)

    def build_videobox(self):
        # Prepare Video Display
        self.movie_window = Gtk.DrawingArea()
        self.movie_window_preview = Gtk.DrawingArea()

        # Prepare Video Container
        mov_box = Gtk.Box(True, 8)
        mov_box.set_orientation(Gtk.Orientation.VERTICAL)
        mov_box.pack_start(self.movie_window, True, True, 0)
        mov_box.pack_start(self.movie_window_preview, True, True, 0)

        return mov_box

    def build_chatbox(self):
        # Prepare Chat Entry Area
        self.chat_text = Gtk.TextBuffer()
        self.text_view = Gtk.TextView()
        self.text_view.set_buffer(self.chat_text)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)

        # Not sure about sizing
        # self.text_view.set_size_request(-1, 180)

        # Prepare History Storage
        chat_history = Gtk.ScrolledWindow()
        chat_history.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        chat_history.add(self.text_view)

        # Send button to complete feel of a chat program
        self.chat_entry = Gtk.Entry()
        self.chat_entry.connect("activate", self.send_chat)
        send_button = Gtk.Button(_("Send"))
        send_button.connect("clicked", self.send_chat)

        # Still not sure about sizing (but the send button should be small)
        # send_button.set_size_request(40, -1)

       # Wrap button and entry in horizontal oriented box so they are on the same line
        chat_entry_box = Gtk.Box(True, 8)
        chat_entry_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        chat_entry_box.pack_start(self.chat_entry, True, True, 0)
        chat_entry_box.pack_end(send_button, False, True, 0)

        # Create box for all chat components & add history & input
        chat_holder = Gtk.Box()
        chat_holder.set_orientation(Gtk.Orientation.VERTICAL)
        chat_holder.pack_start(chat_history, True, True, 0)
        chat_holder.pack_start(chat_entry_box, False, True, 0)

        # Chat expander allows visibly toggle-able container for all chat components
        chat_expander = Gtk.Expander()
        chat_expander.set_label(_("Chat"))
        chat_expander.set_expanded(True)
        chat_expander.add(chat_holder)

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
                icon_name="view-source")
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
        # Create Settings Menu
        settings_toolbar = Gtk.Toolbar()

        # Add Hacky-Reload Button (For now)
        reload_video = ToolButton("view-refresh")
        reload_video.set_tooltip_text(_("Reload Screen"))
        reload_video.connect("clicked", self.force_redraw, None)
        settings_toolbar.insert(reload_video, -1)

        # Display & Return Settings Menu
        settings_toolbar.show_all()
        return settings_toolbar

    def get_history(self):
        return self.chat_text.get_text(
                self.chat_text.get_start_iter(),
                self.chat_text.get_end_iter())

    def add_chat_text(self, text):
        self.chat_text.insert(self.chat_text.get_end_iter(), "%s\n" % text)
        self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1)

    def send_chat(self, w):
        if self.chat_entry.get_text != "":
            self.activity.send_chat_text(self.chat_entry.get_text())
            self.chat_entry.set_text("")

    def force_redraw(self, widget, value=None):
        # Fixme: This should not be required, this is a hack for now until
        # a better solution that works is found
        self.movie_window.hide()
        self.movie_window_preview.hide()
        self.movie_window.show()
        self.movie_window_preview.show()

    def send_video_to_screen(self, source, screen):
        if screen == 'MAIN':
            source.set_xwindow_id(self.movie_window.get_property('window').get_xid())
        elif screen == 'PREVIEW':
            source.set_xwindow_id(self.movie_window_preview.get_property('window').get_xid())
