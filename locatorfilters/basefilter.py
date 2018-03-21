from qgis.core import Qgis, QgsLocatorFilter, QgsMessageLog
from .. import networkaccessmanager


class GeocoderFilter(QgsLocatorFilter):

    # trying out some kind of base class

    ADDRESS = 750
    STREET = 1500
    ZIP = 3000
    PLACE = 30000
    CITY = 120000
    ISLAND = 250000
    COUNTRY = 4000000

    def __init__(self, iface):
        super(QgsLocatorFilter, self).__init__()
        self.nam = networkaccessmanager.NetworkAccessManager()
        self.iface = iface
        #print('constructor GeocoderFilter')

    def name(self):
        #print('Calling name() van {}'.format(self.__class__.__name__))
        return self.__class__.__name__

    def info(self, msg=""):
        QgsMessageLog.logMessage('{}'.format(msg), 'GeocoderFilter', Qgis.Info)

    def set_key(self, key):
        self.info('setting key: {}  self: {}'.format(key, self))

