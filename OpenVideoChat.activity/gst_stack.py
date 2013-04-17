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
:mod: `OpenVideoChat/OpenVideoChat.activity/gst_stack` --
        Open Video Chat GStreamer Stack
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthro:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
"""

#External Imports
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

#Internal Imports

#Define the limitations of the device
CAPS = "video/x-raw,width=320,height=240,framerate=15/1"


class GSTStack:

    def __init__(self, link_function):
        Gst.init(None)
        self._out_pipeline = None
        self._in_pipeline = None

    
    #Outgoing Pipeline
    def build_outgoing_pipeline(self, ip):
        #Checks if there is outgoing pipeline already
        if self._out_pipeline != None:
            print "WARNING: outgoing pipeline exists"
            return

        print "Building outgoing pipeline UDP to %s" % ip

        # Pipeline:
        # v4l2src -> videorate -> (CAPS) -> tee -> theoraenc -> rtptheorapay -> udpsink
        #                                     \
        #                     -> queue -> ffmpegcolorspace -> ximagesink
        self._out_pipeline = Gst.Pipeline()


        #Video Bin
        video_out_bin = Gst.Bin.new
           
        # Video Source
        video_src = Gst.ElementFactory.make("autovideosrc", None)
        video_out_bin.add(video_src)

        # Video Rate element to allow setting max framerate
        video_rate = Gst.ElementFactory.make("videorate", None)
        video_out_bin.add(video_rate)
        video_src.link(video_rate)

        # Add caps to limit rate and size
        video_caps = Gst.ElementFactory.make("capsfilter", None)
        video_caps.set_property("caps", Gst.caps_from_string(CAPS))
        video_out_bin.add(video_caps)
        video_rate.link(video_caps)

        #Add tee element
        video_tee = Gst.ElementFactory.make("tee", None)
        video_out_bin.add(video_tee)
        video_caps.link(video_tee)

        # Add theora Encoder
        video_enc = Gst.ElementFactory.make("theoraenc", None)
        video_enc.set_property("bitrate", 50)
        video_enc.set_property("speed-level", 2)
        video_out_bin.add(video_enc)
        video_tee.link(video_enc)

        #Add rtptheorapay
        video_rtp_theora_pay = Gst.ElementFactory.make("rtptheorapay", None)
        video_out_bin.add(video_rtp_theora_pay)
        video_enc.link(video_rtp_theora_pay)

        #Add udpsink
        udp_sink = Gst.ElementFactory.make("udpsink", None)
        udp_sink.set_property("host", ip)
        udp_sink.set_property("port", 5004)
        video_out_bin.add(udp_sink)
        video_rtp_theora_pay.link(udp_sink)


        ## On other side of pipeline. connect tee to ximagesink
        # Queue element to receive video from tee
        video_queue = Gst.ElementFactory.make("queue", None)
        video_out_bin.add(video_queue)
        video_tee.link(video_queue)

        # Change colorspace for ximagesink
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        video_out_bin.add(video_convert)
        video_queue.link(video_convert)

        # Send to ximagesink
        ximage_sink = Gst.ElementFactory.make("ximagesink", None)
        video_out_bin.add(ximage_sink)
        video_convert.link(ximage_sink)





        # Audio Bin
        audio_out_bin = Gst.Bin.new
            
        # Audio Source
        audio_src = Gst.ElementFactory.make("autoaudiosrc", None)
        audio_out_bin.add(audio_src)

        # Opus Audio Encoding
        audio_enc = Gst.ElementFactory.make("opusenc", None)
        audio_out_bin.add(audio_enc)
        audio_src.link(audio_enc)

        # RTP Opus Pay
        audio_rtp = Gst.ElementFactory.make("rtpopuspay", None)
        audio_out_bin.add(audio_rtp)
        audio_enc.link(audio_rtp)

        # Audio UDP Sink
        udp_sink = Gst.ElementFactory.make("udpsink", None)
        udp_sink.set_property("host", ip)
        udp_sink.set_property("port", 5005)
        audio_out_bin.add(udp_sink)
        audio_rtp.link(udp_sink)


        self._out_pipeline.add(video_out_bin)
        self._out_pipeline.add(audio_out_bin)


        # Connect to pipeline bus for signals.
        bus = self._out_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        def on_message(bus, message):
            """
            This method handles errors on the video bus and then stops
            the pipeline.
            """
            t = message.type
            if t == Gst.MessageType.EOS:
                self._out_pipeline.set_state(Gst.State.NULL)
            elif t == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._out_pipeline.set_state(Gst.State.NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-xwindow-id":
                # Assign the viewport
                self.link_function(message.src, 'PREVIEW')

        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)

    

    #Incoming Pipeline
    def build_incoming_pipeline(self):
        if self._in_pipeline != None:
            print "WARNING: incoming pipeline exists"
            return

        # Set up the gstreamer pipeline
        print "Building Incoming Video Pipeline"

        # Pipeline:
        # udpsrc -> rtptheoradepay -> theoradec -> ffmpegcolorspace -> xvimagesink
        self._in_pipeline = Gst.Pipeline()


        #Video Bin
        video_in_bin = Gst.Bin.new
           
        # Video Source
        video_src = Gst.ElementFactory.make("udpsrc", None)
        video_src.set_property("port", 5004)
        video_in_bin.add(video_src)

        # RTP Theora Depay
        video_rtp_theora_depay = Gst.ElementFactory.make("rtptheoradepay", None)
        self._in_pipeline.add(video_rtp_theora_depay)
        video_in_bin.add(video_rtp_theora_depay)
        video_src.link(video_rtp_theora_depay)

        # Video decode
        video_decode = Gst.ElementFactory.make("theoradec", None)
        video_in_bin.add(video_decode)
        video_rtp_theora_depay.link(video_decode)

        # Change colorspace for xvimagesink
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        video_in_bin.add(video_convert)
        video_decode.link(video_convert)

        # Send video to xviamgesink
        xvimage_sink = Gst.ElementFactory.make("autovideosink", None)
        xvimage_sink.set_property("force-aspect-ratio", True)
        self._in_pipeline.add(xvimage_sink)
        video_convert.link(xvimage_sink)


        # Audio Bin
        audio_out_bin = Gst.Bin.new

        # Audio Source
        audio_src = Gst.ElementFactory.make("udpsrc", None)
        audio_src.set_property("port", 5005)
        audio_in_bin.add(audio_src)

        # RTP Opus Depay
        audio_rtp = Gst.ElementFactory.make("rtpopusdepay", None)
        audio_in_bin.add(audio_rtp)
        audio_src.link(audio_rtp)

        # Opus Audio Decoding
        audio_dec = Gst.ElementFactory.make("opusdec", None)
        audio_in_bin.add(audio_enc)
        audio_rtp.link(audio_enc)

        # Audio Sink
        audio_sink = Gst.ElementFactory.make("autoaudiosink", None)
        audio_in_bin.add(audio_sink)
        audio_dec.link(audio_sink)


        self._in_pipeline.add(video_in_bin)
        self._in_pipeline.add(audio_in_bin)

        # Connect to pipeline bus for signals.
        bus = self._in_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        def on_message(bus, message):
            """
            This method handles errors on the video bus and then stops
            the pipeline.
            """
            t = message.type
            if t == Gst.MessageType.EOS:
                self._in_pipeline.set_state(Gst.State.NULL)
            elif t == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._in_pipeline.set_state(Gst.State.NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-xwindow-id":
                # Assign the viewport
                self.link_function(message.src, 'MAIN')

        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)

    def start_stop_outgoing_pipeline(self, start=True):
        if self._out_pipeline != None:
            if start:
                print "Setting Outgoing Pipeline state: STATE_PLAYING"
                self._out_pipeline.set_state(Gst.State.PLAYING)
            else:
                print "Setting Outgoing Pipeline state: STATE_NULL"
                self._out_pipeline.set_state(Gst.State.NULL)

    def start_stop_incoming_pipeline(self, start=True):
        if self._in_pipeline != None:
            if start:
                print "Setting Incoming Pipeline state: STATE_PLAYING"
                self._in_pipeline.set_state(Gst.State.PLAYING)
            else:
                print "Setting Incoming Pipeline state: STATE_NULL"
                self._in_pipeline.set_state(Gst.State.NULL)
