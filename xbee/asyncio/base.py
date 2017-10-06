"""
base.py

By Jim Mussared, 2017

asyncio XBee superclass module

This class defines data and methods common to all XBee modules.
This class should be subclassed in order to provide
series-specific functionality.
"""
from xbee.frame import APIFrame
from xbee.backend.base import XBeeBase as _XBeeBase
import asyncio
import serial_asyncio
from collections import deque


class XBeeBase(_XBeeBase, asyncio.Protocol):
    """
    Abstract base class providing command generation and response
    parsing methods for XBee modules.

    Constructor arguments:
        ser:    The file-like serial port to use.


        shorthand: boolean flag which determines whether shorthand command
                   calls (i.e. xbee.at(...) instead of xbee.send("at",...)
                   are allowed.

        callback: function which should be called with frame data
                  whenever a frame arrives from the serial port.
                  When this is not None, the wait_for_frame() future can be used.

        escaped: boolean flag which determines whether the library should
                 operate in escaped mode. In this mode, certain data bytes
                 in the output and input streams will be escaped and unescaped
                 in accordance with the XBee API. This setting must match
                 the appropriate api_mode setting of an XBee device; see your
                 XBee device's documentation for more information.

        error_callback: function which should be called with an Exception
                 whenever an exception is raised while waiting for data from
                 the serial port. This will only take affect if the callback
                 argument is also used.
    """

    def __init__(self, ser, loop=None, *args, **kwargs):
        super(XBeeBase, self).__init__(ser, *args, **kwargs)

        if not loop:
            loop = asyncio.get_event_loop()

        self._transport = serial_asyncio.SerialTransport(loop, self, self.serial)

        self._frame = None
        self._data = bytearray()
        self._future = None
        self._queue = deque()

        if self._callback:
            pass

    def halt(self):
        """
        halt: None -> None
        """
        if self._callback:
            pass

    async def wait_read_frame(self):
        """
        wait_read_frame: None -> frame info dictionary
        """
        if self._queue:
            fut = asyncio.Future()
            fut.set_result(self._queue.popleft())
            return await fut
        else:
            self._future = asyncio.Future()
            return await self._future

    def data_received(self, data):
        self._data += data

        if not self._frame:
            for i in range(len(self._data)):
                if self._data[i:i+1] == APIFrame.START_BYTE:
                    self._frame = APIFrame(escaped=self._escaped)
                    self._data = self._data[i:]
                    break

        if not self._frame:
            return

        i = 0
        while i < len(self._data) and self._frame.remaining_bytes() > 0:
            self._frame.fill(self._data[i:i+1])
            i += 1
        self._data = self._data[i:]

        if self._frame.remaining_bytes() == 0:
            try:
                self._frame.parse()
                info = self._split_response(self._frame.data)
                if self._frame.data:
                    if self._callback:
                        self._callback(info)
                    elif self._future:
                        self._future.set_result(info)
                        self._future = None
                    else:
                        self._queue.append(info)
            except ValueError:
                print('Bad frame checksum')
                pass
            self._frame = None

    def connection_lost(self, exc):
        print('port closed')
        self._transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self._transport.get_write_buffer_size())

    def resume_writing(self):
        print(self._transport.get_write_buffer_size())
        print('resume writing')
