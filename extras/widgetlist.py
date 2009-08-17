import xbmc, xbmcgui, os
from xbmcgui import Window

# Current Working Directory
CWD = os.getcwd()
if CWD[-1] == ';': CWD = CWD[0:-1]
if CWD[-1] != '//': CWD = CWD + '//'
#extras scrapers folder
EXTRAS_FILE =  CWD + 'scrapers//'

dialog = xbmcgui.DialogProgress()

class Main:
    # grab the home window
    WINDOW = Window ( 10000 )

    def __init__( self ):
        dialog.create("Aeon Mod","Loading Widget List...")
        # clear properties
        self._clear_properties()
		# fetch media
        self._fetch_widget_list()
        dialog.close()
		
    def _clear_properties( self ):
        for count in range( 30 ):
            # clear Property
            self.WINDOW.clearProperty( "widget.%d.name" % ( count + 1, ) )
            #if count == 1:
            #    self.WINDOW.clearProperty( "ExtrasWidget.Got" )
            #    self.WINDOW.clearProperty( 'ExtrasWidget.PubDate' )
            #    self.WINDOW.clearProperty( 'ExtrasWidget.Title' )
            #    self.WINDOW.clearProperty( 'ExtrasWidget.ContentTitle' )
            #    self.WINDOW.clearProperty( 'ExtrasWidget.Picture' )
            #    self.WINDOW.clearProperty( 'ExtrasWidget.Content' )
            #    self.WINDOW.clearProperty( "PictureWidget.Got" )
            #    self.WINDOW.clearProperty( 'PictureWidget.PubDate' )
            #    self.WINDOW.clearProperty( 'PictureWidget.Title' )
            #    self.WINDOW.clearProperty( 'PictureWidget.ContentTitle' )
            #    self.WINDOW.clearProperty( 'PictureWidget.Picture' )
            #    self.WINDOW.clearProperty( 'PictureWidget.Content' )

    def _fetch_widget_list( self ):
        count = 0
        for filename in os.listdir(EXTRAS_FILE):
            basename, extension = filename.split('.')
            self.WINDOW.setProperty( "widget.%d.name" % ( count + 1, ) , basename )
            count = count + 1
		
if ( __name__ == "__main__" ):
    Main()
