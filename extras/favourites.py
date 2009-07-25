import xbmc
from xbmcgui import Window
from xml.dom.minidom import parse, parseString
import os


class Main:
   # grab the home window
   WINDOW = Window ( 10004 )

   def __init__( self ):
      self._clear_properties()
      self._read_file()
      self._parse_String()
      self.count = 0
      self._fetch_favourites()
      self.doc.unlink()

   def _clear_properties( self ):
      for count in range( 20 ):
         # clear Property
         self.WINDOW.clearProperty( "favourite.%d.value" % ( count + 1, ) )
         self.WINDOW.clearProperty( "favourite.%d.name" % ( count + 1, ) )

   def _read_file( self ):
      # read file
      self.fav = open('special://masterprofile//favourites.xml', 'r')
      self.favourites_xml = self.fav.read()
      self.fav.close()

   def _parse_String( self ):
      self.doc = parseString( self.favourites_xml )
      self.favourites = self.doc.documentElement.getElementsByTagName ( 'favourite' )

   def _fetch_favourites( self ):
      # Go through each favourites
      for self.doc in self.favourites:
         self.WINDOW.setProperty( "favourite.%d.value" % ( self.count + 1, ) , self.doc.childNodes [ 0 ].nodeValue )
         self.WINDOW.setProperty( "favourite.%d.name" % ( self.count + 1, ) , self.doc.attributes [ 'name' ].nodeValue )
         self.count = self.count+1

if ( __name__ == "__main__" ):
    Main()




