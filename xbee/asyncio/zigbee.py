from xbee.asyncio.base import XBeeBase
import xbee.backend as _xbee


class ZigBee(_xbee.ZigBee, XBeeBase):
    pass
