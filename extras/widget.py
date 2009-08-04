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

    def __init__( self ):
        dialog.create("Aeon Mod","Loading Widget List...")
        self._fetch_widget_list()
        dialog.close()

    def _clear_properties( self ):
        for count in range( 20 ):
            # clear Property
            self.WINDOW.clearProperty( "widget.%d.name" % ( count + 1, ) )

    def _fetch_widget_list( self ):
        count = 0
        for filename in os.listdir(EXTRAS_FILE):
            if '.txt' in filename:
            	basename, extension = filename.split('.')
            	self.WINDOW.setProperty( "widget.%d.name" % ( count + 1, ) , basename )
            	count = count + 1
		
if ( __name__ == "__main__" ):
    Main()
