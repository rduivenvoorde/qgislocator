from qgis.core import Qgis, QgsLocatorFilter, QgsMessageLog, QgsSettings
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
        self.settings = QgsSettings()
        # key to use when a location provider needs an api key (see googlegeocoder for example)
        self.settings_key = 'NOT USED, TO BE SET IN LOCATIONFILTER IMPLEMENTATION'

    # def hasConfigWidget(self):
    #     return False
    #
    # # /**
    # #  * Returns true if the filter should be used when no prefix
    # #  * is entered.
    # #  * \see setUseWithoutPrefix()
    # #  */
    # def useWithoutPrefix(self):
    #     return False

    # emit resultFetched() signal
    #  /**
    #  * Retrieves the filter results for a specified search \a string. The \a context
    #  * argument encapsulates the context relating to the search (such as a map
    #  * extent to prioritize).
    #  *
    #  * Implementations of fetchResults() should emit the resultFetched()
    #  * signal whenever they encounter a matching result.
    #  *
    #  * Subclasses should periodically check the \a feedback object to determine
    #  * whether the query has been canceled. If so, the subclass should return
    #  * this method as soon as possible.
    #  */

    # /**
    #  * Triggers a filter \a result from this filter. This is called when
    #  * one of the results obtained by a call to fetchResults() is triggered
    #  * by a user. The filter subclass must implement logic here
    #  * to perform the desired operation for the search result.
    #  * E.g. a file search filter would open file associated with the triggered
    #  * result.
    #  */
    # virtual void triggerResult( const QgsLocatorResult &result ) = 0;

    # # /**
    # #  * Returns true if the filter should be used when no prefix
    # #  * is entered.
    # #  * \see setUseWithoutPrefix()
    # #  */
    #def useWithoutPrefix(self):
    #    return True

    def name(self):
        #print('Calling name() van {}'.format(self.__class__.__name__))
        return self.__class__.__name__

    def info(self, msg=""):
        QgsMessageLog.logMessage('{} {}'.format(self.__class__.__name__, msg), 'GeocoderFilter', Qgis.Info)

    def set_key(self, key):
        self.info('setting key: {}  self: {}'.format(key, self))
