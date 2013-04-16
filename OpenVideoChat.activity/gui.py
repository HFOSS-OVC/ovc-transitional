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
import gi
from gi.repository import Gtk
from gettext import gettext as _#For Translations
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
<<<<<<< HEAD
from gi.repository import Gtk
print "gui 3"
from gi.repository import Gtk
=======

# from sugar.activity.activity import ActivityToolbox
# from sugar.graphics.toolbutton import ToolButton
>>>>>>> 77cc2b7... Adding bugfixes by CDeLorme



class Gui(Gtk.Box):
    def __init__(self, activity):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        # Set Activity
        self.activity = activity

        # Prepare Movie Container
        mov_box = Gtk.Box(True, 8)
        mov_box.set_orientation(Gtk.Orientation.VERTICAL)

        #Add movie window
        self.movie_window = Gtk.DrawingArea()
        self.movie_window_preview = Gtk.DrawingArea()
        mov_box.pack_start(self.movie_window, True, True, 0)
        mov_box.pack_start(self.movie_window_preview, True, True, 0)

        # Add the mov_box
        self.pack_start(mov_box, True, True, 0)

        # Add Chat section
        ##################

        # Chat expander allows chat to be hidden/shown
        chat_expander = Gtk.Expander()
        chat_expander.set_label(_("Chat"))
        chat_expander.set_expanded(True)
        self.pack_start(chat_expander, False, True, 0)

        # Create Chat Container
        chat_holder = Gtk.Box()
        chat_holder.set_orientation(Gtk.Orientation.VERTICAL)
        chat_expander.add(chat_holder)

        # Prepare History Storage
        chat_history = Gtk.ScrolledWindow()
        chat_history.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Prepare Chat Entry Area
        self.chat_text = Gtk.TextBuffer()
        self.text_view = Gtk.TextView()
        self.text_view.set_buffer(self.chat_text)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_size_request(-1, 200)
        chat_history.add(self.text_view)

        # Send button to complete feel of a chat program
        self.chat_entry = Gtk.Entry()
        self.chat_entry.connect("activate", self.send_chat)
        send_but = Gtk.Button(_("Send"))
        send_but.connect("clicked", self.send_chat)

       # Wrap button and entry in hbox so they are on the same line
        chat_entry_hbox = Gtk.Box(True, 8)
        chat_entry_hbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        chat_entry_hbox.pack_start(self.chat_entry, True, True, 0)
        chat_entry_hbox.pack_end(send_but, False, True, 0)

        # Add chat history and entry to expander
        chat_holder.pack_start(chat_history, True, True, 0)
        chat_holder.pack_start(chat_entry_hbox, False, True, 0)

        # Show gui
        self.build_toolbars()
        self.show_all()

        print "Done Creating Toolbars"

        # Below causing errors, maybe requires toolbars code to finish execution?
        #scroll to bottom
        self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1)

    def get_history(self):
        return self.chat_text.get_text(self.chat_text.get_start_iter(),
                                        self.chat_text.get_end_iter())

    def add_chat_text(self, text):
        self.chat_text.insert(self.chat_text.get_end_iter(), "%s\n" % text)
        self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1)

    def send_chat(self, w):
        if self.chat_entry.get_text != "":
            self.activity.send_chat_text(self.chat_entry.get_text())
            self.chat_entry.set_text("")

    def build_toolbars(self):
        self.settings_bar = Gtk.Toolbar()
        self.settings_buttons = {}

        print "Create Tooltips Storage"
        tips = Gtk.Tooltips()

        print "Create Toolbars"

        # Generate array of menu items
        self.settings_buttons['reload_video'] = Gtk.ToolButton('view-spiral')

        # self.settings_buttons['reload_video'].set_tooltip(_("Reload Screen"))

        self.settings_buttons['reload_video'].connect(
                "clicked",
                self.force_redraw,
                None)
        self.settings_bar.insert(
                self.settings_buttons['reload_video'],
                -1)

        print "Done with Reload Video"

        self.toolbox = ToolbarBox(self.activity)
        self.toolbox.add_toolbar(
                _("Settings"),
                self.settings_bar)

        self.activity.set_toolbar_box(self.toolbox)
        self.toolbox.show_all()

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
