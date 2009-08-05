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
		# parse argv for any preferences
        self._parse_argv()
        # clear properties
        self._clear_properties()
		# fetch media
        if self.EX_TYPE: self._fetch_widget_list('[' + self.EX_TYPE + ']')
        dialog.close()
		
    def _parse_argv( self ):
        try:
            # parse sys.argv for params
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            # no params passed
            params = {}
        # set our preferences
        self.EX_TYPE = params.get( "type", "" )

    def _clear_properties( self ):
        for count in range( 20 ):
            # clear Property
            self.WINDOW.clearProperty( "widget.%d.name" % ( count + 1, ) )

    def _fetch_widget_list( self , type ):
        count = 0
        for filename in os.listdir(EXTRAS_FILE):
            if type in filename:
            	basename, extension = filename.split('.')
            	basename, extension = basename.split(']')
            	self.WINDOW.setProperty( "widget.%d.name" % ( count + 1, ) , extension )
            	count = count + 1
		
if ( __name__ == "__main__" ):
    Main()
