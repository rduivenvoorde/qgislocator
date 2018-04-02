# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon, QDesktopServices
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication
from .locatorfilters import googlegeocoder, googleplaces, nominatim, pdoklocatieserver

import os

# QUESTION: should we create base classes for the GeocoderLocator and GeocoderFilter (in cpp or python)
# QUESTION: IF a service does not have a suggest-service (like Nominatim) adding a space ' ' at the end to force a search
# QUESTION: is a normal plugin the right thing to do?
# QUESTION: put 'name' in constructor of baseclass?
# QUESTION: should we have a cpp/python NetworkAccessManager(factory) somewhere?
# QUESTION: should a Filter already have a NAM and an iface
# QUESTION: if a geocoder filter needs to check crs (to reproject) or zoom in mapcanvas, where comes handle to mapcanvas from
# QUESTION: having different geocoder locators running: synchron or asynchron networking? (now I do synchro)
# QUESTION: why only 3 chars for prefix? (better make this configurable?)
# QUESTION: what to do with the zoomlevel of scale to zoom to? Always sent an extent? Or Extent + scale (better for TilingServices and then the locator can assure it is a nice map, or viewed on a suitable zoom level?)
#    would be cool to be able to have a object-type to scale mapping for all geocoders, so
#    you determine for every object type on which z-level (exact) you want to come...
# QUESTION: if you open te result again by just going to the search input and click after some time: segfault I think a nullpointer
# QUESTION: why short result texts with osm (missing the types)
# QUESTION: should the BaseGeocoderLocator set a point or label? As Option?



# TODO: handle network problems
# TODO: handle feedback from locatorfilter
# TODO: setting widget (for example for an (google) api key)

class QgisLocator:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.filter = nominatim.NominatimFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter)

        self.pdok_filter = pdoklocatieserver.PdokFilter(self.iface)
        self.iface.registerLocatorFilter(self.pdok_filter)

        self.google_geocode_filter = googlegeocoder.GoogleGeocodeFilter(self.iface)
        self.iface.registerLocatorFilter(self.google_geocode_filter)

        #self.google_places_filter = googleplaces.GooglePlacesFilter(self.iface)
        #self.iface.registerLocatorFilter(self.google_places_filter)

    def initGui(self):
        # about action
        self.aboutAction = QAction(QIcon(os.path.join(os.path.dirname(__file__), "icons", "icon.svg")),
                                  self.tr("About"), self.iface.mainWindow())
        self.aboutAction.setWhatsThis(self.tr("QGIS Locator Plugin"))
        self.aboutAction.triggered.connect(self.about)
        # help/documentation action
        help_icon = QgsApplication.getThemeIcon('/mActionHelpContents.svg')
        self.helpAction = QAction(help_icon, self.tr("Help"), self.iface.mainWindow())
        self.helpAction.setWhatsThis(self.tr("QGIS Locator Plugin Documentation"))
        self.helpAction.triggered.connect(self.show_help)
        # add about to plugin menu
        self.iface.addPluginToWebMenu(self.tr("QGIS &Locator Plugin"), self.helpAction)
        self.iface.addPluginToWebMenu(self.tr("QGIS &Locator Plugin"), self.aboutAction)

    def unload(self):
        self.iface.deregisterLocatorFilter(self.filter)
        self.iface.deregisterLocatorFilter(self.pdok_filter)
        self.iface.deregisterLocatorFilter(self.google_geocode_filter)
        #self.iface.deregisterLocatorFilter(self.google_places_filter)
        # Remove the web menu item and icon
        self.iface.removePluginWebMenu(self.tr("QGIS &Locator Plugin"), self.helpAction)
        self.iface.removePluginWebMenu(self.tr("QGIS &Locator Plugin"), self.aboutAction)

    def about(self):
        infoString = self.tr("Written by Richard Duivenvoorde\nEmail - richard@duif.net\n")
        infoString += self.tr("Company - Zuidt - https://www.zuidt.nl\n")
        infoString += self.tr("Source: https://github.com/rduivenvoorde/qgislocator")
        QMessageBox.information(self.iface.mainWindow(), self.tr("QGIS Locator Plugin About"), infoString)

    def show_help(self):
        docs = os.path.join(os.path.dirname(__file__), "help", "index.html")
        QDesktopServices.openUrl(QUrl("file:" + docs))

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QgsApplication.translate('QGIS Locator Plugin', message)