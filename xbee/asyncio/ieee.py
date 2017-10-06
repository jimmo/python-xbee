from xbee.asyncio.base import XBeeBase
import xbee.backend as _xbee


class XBee(_xbee.XBee, XBeeBase):
    pass
