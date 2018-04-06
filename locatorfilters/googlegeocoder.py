
from qgis.core import QgsProject, QgsLocatorResult, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsSettings
from .. import networkaccessmanager
from .basefilter import GeocoderFilter
from .base_api_key_dialog import BaseApiKeyDialog

import json

class GoogleGeocodeFilter(GeocoderFilter):

    def __init__(self, iface):
        super().__init__(iface)
        # setting the key name to use for the Google Geocode key
        self.settings_key = '/qgisGeoLocator/qoogleGeocodeFilter/qoogleKey'

    def clone(self):
        return GoogleGeocodeFilter(self.iface)

    def displayName(self):
        if self.settings.contains(self.settings_key, QgsSettings.Plugins):
            return 'Google Geocoder Api'
        else:
            return 'Google Geocoder Api needs a KEY first, see Configure'

    def prefix(self):
        return 'ggeo'

    def hasConfigWidget(self):
        return True

    def openConfigWidget(self, parent=None):
        self.info('parent: {}'.format(parent))
        # parent of the google config dialog should actually be the locatortab in the options dialog
        # but dunno how to get a handle to it easily
        google_config = BaseApiKeyDialog(parent)
        # to be able to see the config, we need to search for a QgsLocatorOptionsWidget ?
        google_config.raise_()
        google_config.activateWindow()

        # check for Google key, if available prefill dialog
        google_config.le_geocoding_api_key.setText(self.settings.value(self.settings_key, defaultValue='', type=str, section=QgsSettings.Plugins))

        #google_config.show()
        # Run the dialog event loop
        result = google_config.exec_()
        # See if OK was pressed
        if result:
            key = google_config.le_geocoding_api_key.text()
            if len(key) > 0:
                self.settings.setValue(self.settings_key, key, QgsSettings.Plugins)

    def fetchResults(self, search, context, feedback):
        key = self.settings.value(self.settings_key, defaultValue='', type=str, section=QgsSettings.Plugins)
        # self.info('fetchResults KEY: "{}" self: {}'.format(key, self))
        if key == '':
            result = QgsLocatorResult()
            result.filter = self
            result.displayString = self.displayName()
            self.resultFetched.emit(result)
            return

        if len(search) < 3:
            return

        search = search.strip()

        # Google geocoding api
        # https://developers.google.com/maps/documentation/geocoding/get-api-key
        # https://developers.google.com/maps/documentation/geocoding/usage-limits  # 2500 requests per day
        url = 'https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}'.format(key, search)

        try:
            self.info('{}'.format(url))
            (response, content) = self.nam.request(url)
            # TODO: check statuscode etc

            content_string = content.decode('utf-8')
            obj = json.loads(content_string)

            docs = obj['results']
            for doc in docs:
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = '{} ({})'.format(doc['formatted_address'], doc['types'])
                result.userData = doc
                self.resultFetched.emit(result)

        except networkaccessmanager.RequestsException:
            # Handle exception
            print('!!!!!!!!!!! EXCEPTION !!!!!!!!!!!!!: \n{}'. format(RequestsException.args))


    def triggerResult(self, result):

        doc = result.userData
        bounds = None
        viewport = None
        if doc is not None and 'geometry' in doc:
            g = doc['geometry']
            if 'bounds' in g:
                bounds = g['bounds']
            if 'location' in g:
                location = g['location']
            if 'viewport' in g:
                viewport = g['viewport']

            location_type = doc['geometry']['location_type']
            self.info(location_type)

        dest_crs = QgsProject.instance().crs()
        results_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId)
        transform = QgsCoordinateTransform(results_crs, dest_crs, QgsProject.instance())
        if bounds is not None:
            rect = QgsRectangle(float(bounds['southwest']['lng']), float(bounds['northeast']['lat']), float(bounds['northeast']['lng']), float(bounds['southwest']['lat']))
            extent = transform.transformBoundingBox(rect)
            self.info(extent.toString())
            self.iface.mapCanvas().setExtent(extent)
        elif viewport is not None:
            rect = QgsRectangle(float(viewport['southwest']['lng']), float(viewport['northeast']['lat']), float(viewport['northeast']['lng']), float(viewport['southwest']['lat']))
            extent = transform.transformBoundingBox(rect)
            self.info(extent.toString())
            self.iface.mapCanvas().setExtent(extent)

        self.iface.mapCanvas().refresh()




        # https://maps.googleapis.com/maps/api/geocode/json?types=geocode&key=AIzaSyCSnHVDNVTboIagNdfbQLt2howajtzx8wM&address=2022zj
        # {
        #     "results": [
        #         {
        #             "address_components": [
        #                 {
        #                     "long_name": "2022 ZJ",
        #                     "short_name": "2022 ZJ",
        #                     "types": ["postal_code"]
        #                 },
        #                 {
        #                     "long_name": "Westoever Noord Buitenspaarne",
        #                     "short_name": "Westoever Noord Buitenspaarne",
        #                     "types": ["political", "sublocality", "sublocality_level_1"]
        #                 },
        #                 {
        #                     "long_name": "Haarlem",
        #                     "short_name": "Haarlem",
        #                     "types": ["locality", "political"]
        #                 },
        #                 {
        #                     "long_name": "Haarlem",
        #                     "short_name": "Haarlem",
        #                     "types": ["administrative_area_level_2", "political"]
        #                 },
        #                 {
        #                     "long_name": "Noord-Holland",
        #                     "short_name": "NH",
        #                     "types": ["administrative_area_level_1", "political"]
        #                 },
        #                 {
        #                     "long_name": "Netherlands",
        #                     "short_name": "NL",
        #                     "types": ["country", "political"]
        #                 }
        #             ],
        #             "formatted_address": "2022 ZJ Haarlem, Netherlands",
        #             "geometry": {
        #                 "bounds": {
        #                     "northeast": {
        #                         "lat": 52.39805459999999,
        #                         "lng": 4.6496457
        #                     },
        #                     "southwest": {
        #                         "lat": 52.3966001,
        #                         "lng": 4.646135399999999
        #                     }
        #                 },
        #                 "location": {
        #                     "lat": 52.39726959999999,
        #                     "lng": 4.6480526
        #                 },
        #                 "location_type": "APPROXIMATE",
        #                 "viewport": {
        #                     "northeast": {
        #                         "lat": 52.39867633029149,
        #                         "lng": 4.6496457
        #                     },
        #                     "southwest": {
        #                         "lat": 52.39597836970849,
        #                         "lng": 4.646135399999999
        #                     }
        #                 }
        #             },
        #             "place_id": "ChIJ80KL8HfvxUcRUot4fROycn4",
        #             "types": ["postal_code"]
        #         }
        #     ],
        #     "status": "OK"
        # }

        # https://maps.googleapis.com/maps/api/geocode/json?types=geocode&key=AIzaSyCSnHVDNVTboIagNdfbQLt2howajtzx8wM&address=riouwstraat+23+haarlem
        # {
        #     "results": [
        #         {
        #             "address_components": [
        #                 {
        #                     "long_name": "23",
        #                     "short_name": "23",
        #                     "types": ["street_number"]
        #                 },
        #                 {
        #                     "long_name": "Riouwstraat",
        #                     "short_name": "Riouwstraat",
        #                     "types": ["route"]
        #                 },
        #                 {
        #                     "long_name": "Westoever Noord Buitenspaarne",
        #                     "short_name": "Westoever Noord Buitenspaarne",
        #                     "types": ["political", "sublocality", "sublocality_level_1"]
        #                 },
        #                 {
        #                     "long_name": "Haarlem",
        #                     "short_name": "Haarlem",
        #                     "types": ["locality", "political"]
        #                 },
        #                 {
        #                     "long_name": "Haarlem",
        #                     "short_name": "Haarlem",
        #                     "types": ["administrative_area_level_2", "political"]
        #                 },
        #                 {
        #                     "long_name": "Noord-Holland",
        #                     "short_name": "NH",
        #                     "types": ["administrative_area_level_1", "political"]
        #                 },
        #                 {
        #                     "long_name": "Netherlands",
        #                     "short_name": "NL",
        #                     "types": ["country", "political"]
        #                 },
        #                 {
        #                     "long_name": "2022 ZJ",
        #                     "short_name": "2022 ZJ",
        #                     "types": ["postal_code"]
        #                 }
        #             ],
        #             "formatted_address": "Riouwstraat 23, 2022 ZJ Haarlem, Netherlands",
        #             "geometry": {
        #                 "location": {
        #                     "lat": 52.39724409999999,
        #                     "lng": 4.6482735
        #                 },
        #                 "location_type": "ROOFTOP",
        #                 "viewport": {
        #                     "northeast": {
        #                         "lat": 52.39859308029149,
        #                         "lng": 4.649622480291502
        #                     },
        #                     "southwest": {
        #                         "lat": 52.3958951197085,
        #                         "lng": 4.646924519708498
        #                     }
        #                 }
        #             },
        #             "place_id": "ChIJpRehHHjvxUcRQqdyrzU46Dw",
        #             "types": ["street_address"]
        #         }
        #     ],
        #     "status": "OK"
        # }
