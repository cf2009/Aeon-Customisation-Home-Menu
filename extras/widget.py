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
    WINDOW = Window ( 10004 )
    Home_CLEAN = Window ( 10000 )

    def __init__( self ):
        dialog.create("Aeon Mod","Loading Widget List...")
        # clear properties
        self._clear_properties()
		# fetch media
        self._fetch_widget_list()
        dialog.close()
		
    def _clear_properties( self ):
        for count in range( 20 ):
            # clear Property
            self.WINDOW.clearProperty( "widget.%d.name" % ( count + 1, ) )
            self.Home_CLEAN.clearProperty( "ExtrasWidget.Got" )
            self.Home_CLEAN.clearProperty( 'ExtrasWidget.PubDate' )
            self.Home_CLEAN.clearProperty( 'ExtrasWidget.Title' )
            self.Home_CLEAN.clearProperty( 'ExtrasWidget.ContentTitle' )
            self.Home_CLEAN.clearProperty( 'ExtrasWidget.Picture' )
            self.Home_CLEAN.clearProperty( 'ExtrasWidget.Content' )
            self.Home_CLEAN.clearProperty( "PictureWidget.Got" )
            self.Home_CLEAN.clearProperty( 'PictureWidget.PubDate' )
            self.Home_CLEAN.clearProperty( 'PictureWidget.Title' )
            self.Home_CLEAN.clearProperty( 'PictureWidget.ContentTitle' )
            self.Home_CLEAN.clearProperty( 'PictureWidget.Picture' )
            self.Home_CLEAN.clearProperty( 'PictureWidget.Content' )

    def _fetch_widget_list( self ):
        count = 0
        for filename in os.listdir(EXTRAS_FILE):
            basename, extension = filename.split('.')
            self.WINDOW.setProperty( "widget.%d.name" % ( count + 1, ) , basename )
            count = count + 1
		
if ( __name__ == "__main__" ):
    Main()
