#    This fileis part of OpenVideoChat.
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
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
.. moduleauthor:: Casey DeLorme <CalebCoffie@rit.edu>
"""


# External Imports
import logger
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


# Define Logger for Logging
logger = logging.getLogger('ovc-activity')


##############
# VideoOutBin
##############
class VideoOutBin(Gst.Bin):
    def __init__(self):
        super(VideoOutBin, self).__init__(ip)

		# Set IP
        self.ip = ip

        # Add theora Encoder
        video_enc = Gst.ElementFactory.make("theoraenc", None)
        video_enc.set_property("bitrate", 50)
        video_enc.set_property("speed-level", 2)
        self.add(video_enc)

        # Add rtptheorapay
        video_rtp_theora_pay = Gst.ElementFactory.make("rtptheorapay", None)
        self.add(video_rtp_theora_pay)

        # Add udpsink
        udp_sink = Gst.ElementFactory.make("udpsink", None)
        udp_sink.set_property("host", self.ip)
        udp_sink.set_property("port", 5004)
        self.add(udp_sink)

        # Link Elements
        video_tee.link(video_enc)
        video_enc.link(video_rtp_theora_pay)
        video_rtp_theora_pay.link(udp_sink)


##############
# AudioOutBin
##############
class AudioOutBin(Gst.Bin):
    def __init__(self):
        super(AudioOutBin, self).__init__()

        self.ip = None

        # Audio Source
        audio_src = Gst.ElementFactory.make("autoaudiosrc", None)
        self.add(audio_src)

        # Opus Audio Encoding
        audio_enc = Gst.ElementFactory.make("speexenc", None)
        self.add(audio_enc)

        # RTP Opus Pay
        audio_rtp = Gst.ElementFactory.make("rtpspeexpay", None)
        self.add(audio_rtp)

        # Audio UDP Sink
        udp_sink = Gst.ElementFactory.make("udpsink", None)
        udp_sink.set_property("host", self.ip)
        udp_sink.set_property("port", 5005)
        self.add(udp_sink)

        # Link Elements
        audio_src.link(audio_enc)
        audio_enc.link(audio_rtp)
        audio_rtp.link(udp_sink)


#############
# VideoInBin
#############
class VideoInBin(Gst.Bin):
    def __init__(self):
        super(VideoInBin, self).__init__()

        # Video Source
        video_src = Gst.ElementFactory.make("udpsrc", None)
        video_src.set_property("port", 5004)
        self.add(video_src)

        # RTP Theora Depay
        video_rtp_theora_depay = Gst.ElementFactory.make("rtptheoradepay", None)
        self.add(video_rtp_theora_depay)

        # Video decode
        video_decode = Gst.ElementFactory.make("theoradec", None)
        self.add(video_decode)
        video_rtp_theora_depay.link(video_decode)

        # Change colorspace for xvimagesink
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        self.add(video_convert)

        # Send video to xviamgesink
        xvimage_sink = Gst.ElementFactory.make("autovideosink", None)
        self.add(xvimage_sink)

        # Link Elements
        video_src.link(video_rtp_theora_depay)
        video_decode.link(video_convert)
        video_convert.link(xvimage_sink)


#############
# AudioInBin
#############
class AudioInBin(Gst.Bin):
    def __init__(self):
        super(AudioInBin, self).__init__()

        # Audio Source
        audio_src = Gst.ElementFactory.make("udpsrc", None)
        audio_src.set_property("port", 5005)
        self.add(audio_src)

        # RTP Opus Depay
        audio_rtp = Gst.ElementFactory.make("rtpspeexdepay", None)
        self.add(audio_rtp)

        # Opus Audio Decoding
        audio_dec = Gst.ElementFactory.make("speexdec", None)
        self.add(audio_dec)

        # Audio Sink
        audio_sink = Gst.ElementFactory.make("autoaudiosink", None)
        self.add(audio_sink)

        # Link Elements
        audio_src.link(audio_rtp)
        audio_rtp.link(audio_dec)
        audio_dec.link(audio_sink)