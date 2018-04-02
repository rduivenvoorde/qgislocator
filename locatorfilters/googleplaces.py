import json
from qgis.core import QgsProject, QgsLocatorResult, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsSettings
from .basefilter import GeocoderFilter
from .base_api_key_dialog import BaseApiKeyDialog
from ..networkaccessmanager import RequestsException


class GooglePlacesFilter(GeocoderFilter):

    def __init__(self, iface):
        super().__init__(iface)
        # setting the key name to use for the Google Geocode key
        self.settings_key = '/qgisGeoLocator/qooglePlacesFilter/qoogleKey'

    def clone(self):
        return GooglePlacesFilter(self.iface)

    def displayName(self):
        if self.settings.contains(self.settings_key, QgsSettings.Plugins):
            return 'Google Places Api (end with space to search)'
        else:
            return 'Google Places Api needs a KEY first, see Configure'

    def prefix(self):
        return 'gapi'

    def hasConfigWidget(self):
        return True

    def openConfigWidget(self, parent=None):
        # parent of the google config dialog should actually be the locatortab in the options dialog
        # but dunno how to get a handle to it easily
        google_config = BaseApiKeyDialog(self.iface.mainWindow())
        # to be able to see the config, we need to search for a QgsLocatorOptionsWidget ?
        #notworking self.google_config.activateWindow()
        #notworking self.google_config.raise_()

        # check for Google key, if available prefill dialog
        google_config.le_geocoding_api_key.setText(self.settings.value(self.settings_key, defaultValue='', type=str, section=QgsSettings.Plugins))

        google_config.show()
        # Run the dialog event loop
        result = google_config.exec_()
        # See if OK was pressed
        if result:
            key = google_config.le_geocoding_api_key.text()
            if len(key) > 0:
                self.settings.setValue(self.settings_key, key, QgsSettings.Plugins)

    def fetchResults(self, search, context, feedback):
        key = self.settings.value(self.settings_key, defaultValue='', type=str, section=QgsSettings.Plugins)
        self.info('KEY: "{}" self: {}'.format(key, self))
        if key == '':
            result = QgsLocatorResult()
            result.filter = self
            result.displayString = self.displayName()
            self.resultFetched.emit(result)
            return

        if len(search) < 3:
            return

        search = search.strip()

        # Google places api
        # https://developers.google.com/places/web-service/query
        # https://developers.google.com/places/web-service/get-api-key
        # https://developers.google.com/places/web-service/usage  # 1000 requests per day
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?types=geocode&key={}&input={}'.format(key, search)

        try:
            self.info('{}'.format(url))
            (response, content) = self.nam.request(url)
            # TODO: check statuscode etc
            #  see https://developers.google.com/places/web-service/search#PlaceSearchResponses for Google status codes
            #self.info('{}'.format(response))
            content_string = content.decode('utf-8')
            obj = json.loads(content_string)

            docs = obj['predictions']
            for doc in docs:
                result = QgsLocatorResult()
                result.filter = self
                self.info('{}'.format(doc['description']))
                result.displayString = '{} ({})'.format(doc['description'], doc['types'])
                result.userData = doc
                self.resultFetched.emit(result)

        except RequestsException:
            # Handle exception
            print('!!!!!!!!!!! EXCEPTION !!!!!!!!!!!!!: \n{}'. format(RequestsException.args))

    def triggerResult(self, result):

        # now try to use Google geocoding service to retrieve more/spatial information
        doc = result.userData
        self.info(doc)
        #self.info(doc)

        # bounds = None
        # if doc is not None and 'geometry' in doc:
        #     g = doc['geometry']
        #     if 'bounds' in g:
        #         bounds = g['bounds']
        #     if 'location' in g:
        #         location = g['location']
        #     if 'viewport' in g:
        #         viewport = g['viewport']
        #
        #     location_type = doc['geometry']['location_type']
        #     self.info(location_type)


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


