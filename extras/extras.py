import xbmc
from xbmcgui import Window, DialogProgress
from urllib import quote_plus, unquote_plus, urlopen, urlretrieve
import re, sys, os, time, htmlentitydefs

# Current Working Directory
CWD = os.getcwd()
if CWD[-1] == ';': CWD = CWD[0:-1]
if CWD[-1] != '//': CWD = CWD + '//'

#picture save temp
IMAGE_TEMP =  CWD + 'temp_pic.png'
#extras scrapers folder
EXTRAS_FILE =  CWD + 'scrapers//'

class Main:
    # grab the home window
    WINDOW = Window( 10000 )

    def _clear_properties( self ):
        # we enumerate thru and clear individual properties in case other scripts set window properties
        for count in range( self.LIMIT ):
            # we clear title for visible condition
            self.WINDOW.clearProperty( "LatestMovie.%d.Title" % ( count + 1, ) )
            self.WINDOW.clearProperty( "LatestEpisode.%d.ShowTitle" % ( count + 1, ) )
            self.WINDOW.clearProperty( "LatestSong.%d.Title" % ( count + 1, ) )
            self.WINDOW.clearProperty( "Fun.quote_got" )
            self.WINDOW.clearProperty( "Fun.picture_got" )

    def _get_media( self, path, file ):
        # set default values
        play_path = fanart_path = thumb_path = path + file
        # we handle stack:// media special
        if ( file.startswith( "stack://" ) ):
            play_path = fanart_path = file
            thumb_path = file[ 8 : ].split( " , " )[ 0 ]
        # we handle rar:// and zip:// media special
        if ( file.startswith( "rar://" ) or file.startswith( "zip://" ) ):
            play_path = fanart_path = thumb_path = file
        # return media info
        return xbmc.getCacheThumbName( thumb_path ), xbmc.getCacheThumbName( fanart_path ), play_path

    def _parse_argv( self ):
        try:
            # parse sys.argv for params
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            # no params passed
            params = {}
        # set our preferences
        self.LIMIT = int( params.get( "limit", "5" ) )
        self.RECENT = not params.get( "partial", "" ) == "True"
        self.ALBUMS = params.get( "albums", "" ) == "True"
        self.UNPLAYED = params.get( "unplayed", "" ) == "True"
        self.RECENTADDED = params.get( "recentadded", "" ) == "true"
        self.TOTALS = params.get( "totals", "" ) == "true"
        self.EXTRAS_CONTENT = params.get( "extrapopup", "" )
        self.PICTURE = params.get( "picture", "" ) == "true"

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        # clear properties
        self._clear_properties()
        if ( self.RECENTADDED ) or ( self.TOTALS ):
            # format our records start and end
            xbmc.executehttpapi( "SetResponseFormat()" )
            xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )
        # fetch media info
        if ( self.RECENTADDED ):
            self._fetch_movie_info()
            self._fetch_tvshow_info()
            self._fetch_music_info()
        if ( self.TOTALS ):
            self._fetch_totals()
        if ( self.EXTRAS_CONTENT ):
            self.get_extra_content(self.EXTRAS_CONTENT)
        if ( self.PICTURE ):
            self.get_picture()

    def _fetch_movie_info( self ):
        # set our unplayed query
        unplayed = ( "", "where playCount isnull ", )[ self.UNPLAYED ]
        # sql statement
        if ( self.RECENT ):
            # recently added
            sql_movies = "select * from movieview %sorder by idMovie desc limit %d" % ( unplayed, self.LIMIT, )
        else:
            # movies not finished
            sql_movies = "select movieview.*, bookmark.timeInSeconds from movieview join bookmark on (movieview.idFile = bookmark.idFile) %sorder by movieview.c00 limit %d" % ( unplayed, self.LIMIT, )
        # query the database
        movies_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_movies ), )
        # separate the records
        movies = re.findall( "<record>(.+?)</record>", movies_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, movie in enumerate( movies ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", movie, re.DOTALL )
            # set properties
            self.WINDOW.setProperty( "LatestMovie.%d.Title" % ( count + 1, ), fields[ 1 ] )
            self.WINDOW.setProperty( "LatestMovie.%d.Plot" % ( count + 1, ), fields[ 2 ] )
            self.WINDOW.setProperty( "LatestMovie.%d.Rating" % ( count + 1, ), fields[ 6 ] )
            self.WINDOW.setProperty( "LatestMovie.%d.Year" % ( count + 1, ), fields[ 8 ] )
            self.WINDOW.setProperty( "LatestMovie.%d.RunningTime" % ( count + 1, ), fields[ 12 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 24 ], fields[ 23 ] )
            self.WINDOW.setProperty( "LatestMovie.%d.Path" % ( count + 1, ), play_path )
            self.WINDOW.setProperty( "LatestMovie.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "LatestMovie.%d.Thumb" % ( count + 1, ), thumb )

    def _fetch_tvshow_info( self ):
        # set our unplayed query
        unplayed = ( "", "where playCount isnull ", )[ self.UNPLAYED ]
        # sql statement
        if ( self.RECENT ):
            # recently added
            sql_episodes = "select * from episodeview %sorder by idepisode desc limit %d" % ( unplayed, self.LIMIT, )
        else:
            # tv shows not finished
            sql_episodes = "select episodeview.*, bookmark.timeInSeconds from episodeview join bookmark on (episodeview.idFile = bookmark.idFile) %sorder by episodeview.strTitle limit %d" % ( unplayed, self.LIMIT, )
        # query the database
        episodes_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_episodes ), )
        # separate the records
        episodes = re.findall( "<record>(.+?)</record>", episodes_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, episode in enumerate( episodes ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", episode, re.DOTALL )
            # set properties
            self.WINDOW.setProperty( "LatestEpisode.%d.ShowTitle" % ( count + 1, ), fields[ 27 ] )
            self.WINDOW.setProperty( "LatestEpisode.%d.EpisodeTitle" % ( count + 1, ), fields[ 1 ] )
            self.WINDOW.setProperty( "LatestEpisode.%d.EpisodeNo" % ( count + 1, ), "s%02de%02d" % ( int( fields[ 13 ] ), int( fields[ 14 ] ), ) )
            self.WINDOW.setProperty( "LatestEpisode.%d.Plot" % ( count + 1, ), fields[ 2 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 24 ], fields[ 23 ] )
            self.WINDOW.setProperty( "LatestEpisode.%d.Path" % ( count + 1, ), play_path )
            self.WINDOW.setProperty( "LatestEpisode.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "LatestEpisode.%d.Thumb" % ( count + 1, ), thumb )

    def _fetch_music_info( self ):
        # sql statement
        if ( self.ALBUMS ):
            sql_music = "select DISTINCT idAlbum from albumview order by idAlbum desc limit %d" % ( 1, )
            # query the database for recently added albums
            music_xml = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % quote_plus( sql_music ), )
            # separate the records
            albums = re.findall( "<record>(.+?)</record>", music_xml, re.DOTALL )
            # set our unplayed query
            unplayed = ( "(idAlbum = %s)", "(idAlbum = %s and lastplayed isnull)", )[ self.UNPLAYED ]
            # sql statement
            sql_music = "select songview.* from songview where %s limit 1" % ( unplayed, )
            # clear our xml data
            music_xml = ""
            # enumerate thru albums and fetch info
            for album in albums:
                # query the database and add result to our string
                music_xml += xbmc.executehttpapi( "QueryMusicDatabase(%s)" % quote_plus( sql_music % ( album.replace( "<field>", "" ).replace( "</field>", "" ), ) ), )
        else:
            # set our unplayed query
            unplayed = ( "", "where lastplayed isnull ", )[ self.UNPLAYED ]
            # sql statement
            sql_music = "select * from songview %sorder by idSong desc limit %d" % ( unplayed, 1, )
            # query the database
            music_xml = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % quote_plus( sql_music ), )
        # separate the records
        items = re.findall( "<record>(.+?)</record>", music_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, item in enumerate( items ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", item, re.DOTALL )
            # set properties
            self.WINDOW.setProperty( "LatestSong.%d.Title" % ( count + 1, ), fields[ 3 ] )
            self.WINDOW.setProperty( "LatestSong.%d.Year" % ( count + 1, ), fields[ 6 ] )
            self.WINDOW.setProperty( "LatestSong.%d.Artist" % ( count + 1, ), fields[ 24 ] )
            self.WINDOW.setProperty( "LatestSong.%d.Album" % ( count + 1, ), fields[ 21 ] )
            path = fields[ 22 ]
            # don't add song for albums list TODO: figure out how toplay albums
            ##if ( not self.ALBUMS ):
            path += fields[ 8 ]
            self.WINDOW.setProperty( "LatestSong.%d.Path" % ( count + 1, ), path )
            # get cache name of path to use for fanart
            cache_name = xbmc.getCacheThumbName( fields[ 24 ] )
            self.WINDOW.setProperty( "LatestSong.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Music/%s/%s" % ( "Fanart", cache_name, ) )
            self.WINDOW.setProperty( "LatestSong.%d.Thumb" % ( count + 1, ), fields[ 27 ] )

    def _fetch_totals( self ):
        # query the database
        movies_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( "select COUNT(*), COUNT(playcount>0) from movieview" ), )
        episodes_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( "select COUNT(DISTINCT strTitle), COUNT(*), COUNT(playCount>0) from episodeview" ), )
        songs_xml = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % quote_plus( "select COUNT(*), COUNT(DISTINCT idArtist) from song" ), )
        album_xml = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % quote_plus( "select COUNT(DISTINCT idAlbum), COUNT(DISTINCT idArtist) from albumview" ), )
        # separate individual fields
        movies_fields = re.findall( "<field>(.*?)</field>", movies_xml, re.DOTALL )
        episodes_fields = re.findall( "<field>(.*?)</field>", episodes_xml, re.DOTALL )
        songs_fields = re.findall( "<field>(.*?)</field>", songs_xml, re.DOTALL )
        album_fields = re.findall( "<field>(.*?)</field>", album_xml, re.DOTALL )
        # set properties
        self.WINDOW.setProperty( "Movie.Count" , movies_fields [0] )
        self.WINDOW.setProperty( "Movie.Played" , movies_fields [1] )
        self.WINDOW.setProperty( "Episodes.Count" , episodes_fields [1] )
        self.WINDOW.setProperty( "Episodes.Played" , episodes_fields [2] )
        self.WINDOW.setProperty( "TVShows.Count" , episodes_fields [0] )
        self.WINDOW.setProperty( "Songs.Count" , songs_fields [0] )
        self.WINDOW.setProperty( "Songs.ArtistCount" , songs_fields [1] )
        self.WINDOW.setProperty( "Album.Count" , album_fields [0] )
        self.WINDOW.setProperty( "Album.ArtistCount" , album_fields [1] )

 
    def get_extra_content(self, scraper):
        #open extras scraper file
        SET_LINES = open(EXTRAS_FILE + scraper + '.txt','r').readlines()
        #open URL
        URL_FILE = urlopen(SET_LINES [ 1 ].strip()).read()
        #find content
        CONTENT = re.findall(SET_LINES [ 2 ].strip(), URL_FILE, re.DOTALL)
        #find title
        TITLE = re.findall(SET_LINES [ 3 ].strip(), URL_FILE, re.DOTALL)
        #find NAME
        NAME_EX = SET_LINES [ 0 ].strip()
        #ITEM NUBER
        ITEM_NUBER = int( SET_LINES [ 4 ].strip() )
        if CONTENT: 
            CONTENT_EX = htmlentitydecode( CONTENT[ ITEM_NUBER ] )
            CONTENT_EX = remove_html_tags( CONTENT_EX ) 
        else: 
            CONTENT_EX = 'not available'
        if TITLE: 
            TITLE_EX = TITLE [ ITEM_NUBER ] 
        else: 
            TITLE_EX = 'No Title'
        if NAME_EX == False: NAME_EX = 'No Name'
        # set properties
        self.WINDOW.setProperty( "Fun.ExGot" , 'yes' )
        self.WINDOW.setProperty( "Fun.ExName" , NAME_EX )
        self.WINDOW.setProperty( "Fun.ExContent" , CONTENT_EX.strip() )
        self.WINDOW.setProperty( "Fun.ExTitle" , TITLE_EX.strip() )

 
    def get_picture(self): 
        base_url = 'http://backend.deviantart.com/rss.xml?q=&type=deviation' 
        content = urlopen(base_url).read() 
        m = re.search('<media:thumbnail url="(.*?)" height', content) 
        n = re.search('media:credit role="author" scheme="urn:ebu">(.*?)<', content) 
        if m: 
            picture = m.group(1)
            DownloaderClass(picture, IMAGE_TEMP)
            if n: 
                pictureby = n.group(1) 
            else: 
                pictureby = ''
        else: 
            picture = ''
            pictureby = 'no pictureby available'
        for i in range(1, 5):
            time.sleep(2)
            if (os.path.isfile( IMAGE_TEMP )):
                self.WINDOW.setProperty( "Fun.picture_got" , 'yes' )
                self.WINDOW.setProperty( "Fun.picture" , IMAGE_TEMP )
                self.WINDOW.setProperty( "Fun.pictureby" , pictureby )
                i = 5

def DownloaderClass(url,dest):
    #dp = DialogProgress()
    #dp.create("Extras","Downloading Image",url)
    urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url))
 
def _pbhook(numblocks, blocksize, filesize, url=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        #dp.update(percent)
    except:
        percent = 100
        #dp.update(percent)
    #if dp.iscanceled(): 
        #print "DOWNLOAD CANCELLED" # need to get this part working
        #dp.close()
        
def htmlentitydecode(s):
    # code from http://snipplr.com/view.php?codeview&id=15261
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return u" "  # Unknown entity: We replace with a space.
    t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)
  
    # Then convert numerical entities (such as &#233;)
    t = re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))), t)
   
    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(u'&#x(\w+);', lambda x: unichr(int(x.group(1),16)), t)

def decodeEntities(data):
    data = data or ''
    data = data.replace('&lt;', '<')
    data = data.replace('&gt;', '>')
    data = data.replace('&quot;', '"')
    data = data.replace('&apos;', "'")
    data = data.replace('&amp;', '&')
    return data

	
def remove_html_tags(data):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub(' ', data)

if ( __name__ == "__main__" ):
    Main()
