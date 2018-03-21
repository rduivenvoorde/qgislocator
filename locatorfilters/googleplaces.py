import json
from qgis.core import QgsProject, QgsLocatorResult, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from .basefilter import GeocoderFilter
from ..networkaccessmanager import RequestsException


class GooglePlacesFilter(GeocoderFilter):

    def __init__(self, iface):
        super().__init__(iface)
        # TODO come from UI
        self.key = None
        #self.google_config = GoogleLocatorConfig(self.iface.mainWindow())
        self.google_config = None #GoogleLocatorConfig()

    def clone(self):
        return GooglePlacesFilter(self.iface)

    def displayName(self):
        if self.key is None:
            return 'Google Places Api needs a KEY first, see Configure'
        else:
            return 'Google Places Api (end with space to search)'

    def prefix(self):
        return 'gapi'

    def hasConfigWidget(self):
        return True

    def openConfigWidget(self, parent=None):
        print('WIDGET WIDGET')
        self.google_config.show()

    # # /**
    # #  * Returns true if the filter should be used when no prefix
    # #  * is entered.
    # #  * \see setUseWithoutPrefix()
    # #  */
    #def useWithoutPrefix(self):
    #    return True

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


        if self.key is None:
            return

        if len(search) < 3:
            return

        search = search.strip()

        # Google geocoding api
        # https://developers.google.com/maps/documentation/geocoding/get-api-key
        # https://developers.google.com/maps/documentation/geocoding/usage-limits  # 2500 requests per day
#        url = 'https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}'.format(self.key, search)
        # https://maps.googleapis.com/maps/api/geocode/json?types=geocode&key=AIzaSyCSnHVDNVTboIagNdfbQLt2howajtzx8wM&address=2022zj

        # https://developers.google.com/places/web-service/query

        # Google places api
        # https://developers.google.com/places/web-service/usage  # 1000 requests per day
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?types=geocode&key={}&input={}'.format(self.key, search)
        #url = 'https://maps.googleapis.com/maps/api/place/queryautocomplete/json?types=geocode&key={}&input={}'.format(self.key, search)
        # https://maps.googleapis.com/maps/api/place/autocomplete/json?types=geocode&key=AIzaSyCSnHVDNVTboIagNdfbQLt2howajtzx8wM&input=2022zj


        try:
            print('url: {}'.format(url))
            (response, content) = self.nam.request(url)
            ##print('response: {}'.format(response))
            # TODO: check statuscode etc
            print('content: {}'.format(content))

            content_string = content.decode('utf-8')
            obj = json.loads(content_string)

            docs = obj['predictions']
            for doc in docs:
                ##print(doc)
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = '{} ({})'.format(doc['description'], doc['types'])
                result.userData = doc
                self.resultFetched.emit(result)

        except RequestsException:
            # Handle exception
            print('!!!!!!!!!!! EXCEPTION !!!!!!!!!!!!!: \n{}'. format(RequestsException.args))


    # /**
    #  * Triggers a filter \a result from this filter. This is called when
    #  * one of the results obtained by a call to fetchResults() is triggered
    #  * by a user. The filter subclass must implement logic here
    #  * to perform the desired operation for the search result.
    #  * E.g. a file search filter would open file associated with the triggered
    #  * result.
    #  */
    # virtual void triggerResult( const QgsLocatorResult &result ) = 0;
    def triggerResult(self, result):

        # now try to use Google geocoding service to retrieve more/spatial information
        doc = result.userData
        search = doc[0][description]
        types = doc[0][description]

        # TODO

        # https://maps.googleapis.com/maps/api/place/autocomplete/json?types=geocode&key=AIzaSyCSnHVDNVTboIagNdfbQLt2howajtzx8wM&input=2022zj
        # {
        #     "predictions": [
        #         {
        #             "description": "2022 ZJ Haarlem, Netherlands",
        #             "id": "908d63bc498e015b8a36f36dc44fbdcb0315246f",
        #             "matched_substrings": [
        #                 {
        #                     "length": 7,
        #                     "offset": 0
        #                 }
        #             ],
        #             "place_id": "ChIJ80KL8HfvxUcRUot4fROycn4",
        #             "reference": "CkQ0AAAA1W26wZvvQSljCdmcKzIqIEaAQTBOsOPWJLOs4T11dHDmWKVM51Jeav-LQ1eFDgxbMesV8xZs9dPDQJ1HfmNKkhIQOdQHqNz87HfHhULhnC6GIxoUqjLPw7XOeodXiXOLQ4rJCvK8Hf8",
        #             "structured_formatting": {
        #                 "main_text": "2022 ZJ",
        #                 "main_text_matched_substrings": [
        #                     {
        #                         "length": 7,
        #                         "offset": 0
        #                     }
        #                 ],
        #                 "secondary_text": "Haarlem, Netherlands"
        #             },
        #             "terms": [
        #                 {
        #                     "offset": 0,
        #                     "value": "2022 ZJ"
        #                 },
        #                 {
        #                     "offset": 8,
        #                     "value": "Haarlem"
        #                 },
        #                 {
        #                     "offset": 17,
        #                     "value": "Netherlands"
        #                 }
        #             ],
        #             "types": ["postal_code", "geocode"]
        #         }
        #     ],
        #     "status": "OK"
        # }


