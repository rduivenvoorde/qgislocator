from qgis.core import QgsProject, QgsLocatorResult, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from .basefilter import GeocoderFilter
from ..networkaccessmanager import RequestsException
import json

class NominatimFilter(GeocoderFilter):

    def __init__(self, iface):
        super().__init__(iface)
        #print('constructor NominatimFilter')

    # def name(self):
    #     ##print('Calling name() van NominatimFilter')
    #     return 'NominatimFilter'

    def clone(self):
        return NominatimFilter(self.iface)

    def displayName(self):
        ##print('Calling displayName() van NominatimFilter')
        return 'Nominatim Geocoder (end with space to search)'

    def prefix(self):
        ##print('Calling prefix() van NominatimFilter')
        return 'osm'

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

    def fetchResults(self, search, context, feedback):
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
        ##print('--- NominatimFilter fetchResults called')
        ##print('NominatimFilter search: {}'.format(search))
        ##print('NominatimFilter context: {}'.format(context))
        #print('NominatimFilter context.targetExtent: {}'.format(context.targetExtent))
        #print('NominatimFilter context.targetExtentCrs: {}'.format(context.targetExtentCrs))
        ##print('NominatimFilter feedback: {}'.format(feedback))

        if len(search) < 3:
            #print('NOT searching because length: {}'.format(len(search)))
            return

        if search[-1] != ' ':
            #print('NOT searching because last char: "{}"'.format(search[-1]))
            return

        # stripping the search string here to be able to see two geocoders at once and Nominatim needs a space on the end
        #search = search.strip()
        url = 'http://nominatim.openstreetmap.org/search?format=json&q={}'.format(search)
        print('Nominatim search: {}'.format(url))
        try:
            # TODO: Provide a valid HTTP Referer or User-Agent identifying the application (QGIS geocoder)
            # see https://operations.osmfoundation.org/policies/nominatim/
            (response, content) = self.nam.request(url)
            ##print('xx response: {}'.format(response))
            # TODO: check statuscode etc
            ##print('xx content: {}'.format(content))

            content_string = content.decode('utf-8')
            docs = json.loads(content_string)
            for doc in docs:
                #print(doc)
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = '{} ({})'.format(doc['display_name'], doc['type'])
                result.userData = doc
                self.resultFetched.emit(result)

        except RequestsException:
            # Handle exception
            errno, strerror = RequestsException.args
            #print('!!!!!!!!!!! EXCEPTION !!!!!!!!!!!!!: \n{}\n{}'. format(errno, strerror))


    # /**
    #  * Triggers a filter a result from this filter. This is called when
    #  * one of the results obtained by a call to fetchResults() is triggered
    #  * by a user. The filter subclass must implement logic here
    #  * to perform the desired operation for the search result.
    #  *
    #  * E.g. a file search filter would open file associated with the triggered
    #  * result.
    #  */
    # virtual void triggerResult( const QgsLocatorResult &result ) = 0;
    def triggerResult(self, result):
        ##print('NominatimFilter triggerResult called, result: {}'.format(result))
        doc = result.userData
        extent = doc['boundingbox']
        # ?? "boundingbox": ["52.641015", "52.641115", "5.6737302", "5.6738302"]
        rect = QgsRectangle(float(extent[2]), float(extent[0]), float(extent[3]), float(extent[1]))
        dest_crs = QgsProject.instance().crs()
        results_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId)
        transform = QgsCoordinateTransform(results_crs, dest_crs, QgsProject.instance())
        r = transform.transformBoundingBox(rect)
        self.iface.mapCanvas().setExtent(r, False)
        # map the result types to generic GeocoderLocator types to determine the zoom
        # BUT only if the extent < 100 meter (as for other objects it is probably ok)
        # mmm, some objects return 'type':'province', but extent is point
        scale_denominator = False  # meaning we keep the extent from the result
        #print("doc['type']: {}".format(doc['type']))
        if doc['type'] == 'house':
            scale_denominator = self.ADDRESS
        elif doc['type'] in ['way', 'motorway_junction', 'cycleway']:
            scale_denominator = self.STREET
        elif doc['type'] == 'postcode':
            scale_denominator = self.ZIP
        if scale_denominator:
            self.iface.mapCanvas().zoomScale(scale_denominator)
        self.iface.mapCanvas().refresh()

