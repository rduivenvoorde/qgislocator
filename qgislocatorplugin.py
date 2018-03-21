# -*- coding: utf-8 -*-

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from qgis.core import QgsProject, QgsLocator, QgsLocatorFilter, QgsLocatorResult, \
                      QgsRectangle, QgsPoint, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform

from .networkaccessmanager import NetworkAccessManager, RequestsException

from .locatorfilters import googlegeocoder, googleplaces, nominatim, pdoklocatieserver

import json


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

        self.filter2 = pdoklocatieserver.PdokFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter2)

        self.filter3 = googleplaces.GooglePlacesFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter3)

        self.filter4 = googlegeocoder.GoogleGeocodeFilter(self.iface)
        self.iface.registerLocatorFilter(self.filter4)

    def initGui(self):

        # about
        self.aboutAction = QAction(QIcon("icons/icon.png"), "About", self.iface.mainWindow())
        self.aboutAction.setWhatsThis("QGIS Locator Plugin")
        self.aboutAction.triggered.connect(self.about)
        self.iface.addPluginToWebMenu("QGIS &Locator Plugin", self.aboutAction)

    def unload(self):
        self.iface.deregisterLocatorFilter(self.filter)
        self.iface.deregisterLocatorFilter(self.filter2)
        self.iface.deregisterLocatorFilter(self.filter3)
        self.iface.deregisterLocatorFilter(self.filter4)
        # Remove the web menu item and icon
        self.iface.removePluginWebMenu("QGIS &Locator Plugin", self.aboutAction)

    def about(self):
        infoString =  "Written by Richard Duivenvoorde\nEmail - richard@duif.net\n"
        infoString += "Company - Zuidt - http://www.zuidt.nl\n"
        infoString += "Source: https://github.com/rduivenvoorde/qgislocator"
        QMessageBox.information(self.iface.mainWindow(), "QGIS Locator Plugin About", infoString)
