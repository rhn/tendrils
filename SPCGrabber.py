import urllib

import htmllib
import formatter
import httplib
import urlparse
import os
import sys
import traceback
import re

COOKIES={}

class ImageFinder(htmllib.HTMLParser):
    def __init__(self,*args,**kw):
        htmllib.HTMLParser.__init__(self,formatter.NullFormatter(),*args,**kw)
        self.ImageList=[]
    def handle_image(self,Source,Alt,*stuff):
        self.ImageList.append(Source)
    def FindImageLinks(self):
        self.ImageLinks = []
        for Anchor in self.anchorlist:
            Extension = os.path.splitext(Anchor)[1].upper()
            if Extension in [".JPG",".JPEG",".GIF",".BMP"]:
                self.ImageLinks.append(Anchor)
        return self.ImageLinks
    def FindRARLinks(self):
        self.ImageLinks = []
        for Anchor in self.anchorlist:
            Extension = os.path.splitext(Anchor)[1].upper()
            if Extension in [".RAR",".ZIP"]:
                self.ImageLinks.append(Anchor)
        return self.ImageLinks
        
def GrabCookies(Msg):
    CookieHeader=Msg.get("Set-Cookie",None)
    if CookieHeader:
        print "---GRAB THIS:",CookieHeader
        CookieHeader=CookieHeader.strip()
        ColonBits=CookieHeader.split(";")
        print ColonBits
        DomainName=FixHostName(ColonBits[-1].split("=")[1])
        if not COOKIES.has_key(DomainName):
            COOKIES[DomainName]={}
        EqualPos=ColonBits[0].find("=")
        CookieName=ColonBits[0][0:EqualPos]
        CookieValue=ColonBits[0][EqualPos+1:]
        COOKIES[DomainName][CookieName]=CookieValue
        #Morsels=ColonBits[0].split("&")
        #for Morsel in Morsels:
        #    (CookieName,CookieValue)=Morsel.split("=")
        #    COOKIES[DomainName][CookieName]=CookieValue            
##        print "---Grabbed cookies:",COOKIES
    
def RetrieveWithCookies(URL,FileName):
    global COOKIES
    print "=====Get %s to %s..."%(URL,FileName)
    Pieces=urlparse.urlparse(URL)
    print Pieces
    conn = httplib.HTTPConnection(Pieces[1])
    conn._http_vsn_str = 'HTTP/1.0'
    ##conn.set_debuglevel(100)
    CookieString = ""
    for CookieKey in COOKIES.keys():
        DomainCookies=COOKIES[CookieKey]
        if URL.find(CookieKey)!=-1:
            for CookieName in DomainCookies.keys():
                if CookieString!="":
                    CookieString+="; "
                print "++ cookie name '%s' value '%s'"%(CookieName,DomainCookies[CookieName])
                CookieString+="%s=%s"%(CookieName,DomainCookies[CookieName])    
    Headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/html",
               "Cookie": CookieString}
    Remainder = Pieces[2] + "?" + Pieces[4]
    conn.request("GET",Remainder,headers=Headers)
    response = conn.getresponse()
    GrabCookies(response.msg)
    print response.status, response.reason, response.msg
    File=open(FileName,"wb")
    ##URLFile=request.getfile()
    Text=response.read() ##
    File.write(Text)
    File.close()
    conn.close()
    return

    
    Request=httplib.HTTP(Pieces[1])
    
    TheStuff=Pieces[2]
    if len(Pieces[4])>0:
        TheStuff="%s?%s"%(TheStuff,Pieces[4])
    Request.putrequest("GET",TheStuff)
##    print "----",TheStuff
    Request.putheader("Accept","text/html")
    CookieString=""
    if CookieString!="":
        Request.putheader("Cookie",CookieString)
##        print "*** COOKIE: ",CookieString
    Request.endheaders()
    TheReply = Request.getreply()
    #print TheReply
    GrabCookies(TheReply[2])
    if TheReply[0]==302:        
##        print "HEADERS:",TheReply[2].headers
        NewURL=TheReply[2].get("Location").strip()
        RetrieveWithCookies(NewURL,FileName)
        return
        #print TheReply[2].fp.read()
    File=open(FileName,"wb")
    URLFile=Request.getfile()
    Text=URLFile.read() ##
    #print Text ##
    File.write(Text) ##
    #File.write(URLFile.read())
    URLFile.close()
    File.close()


def LootImagePage(ImagePageURL,ClubName,AlbumName,ImageCount):
    TempFileName="%sAlbum"%ClubName
    RetrieveWithCookies(ImagePageURL,TempFileName)
    File=open(TempFileName,"r")
    TheParser=ImageFinder(formatter=formatter.NullFormatter())
    TheParser.feed(File.read())
    File.close()
    Images = []
    ##print "IMAGE PAGE ANCHORS:",TheParser.anchorlist
    for ImageURL in TheParser.ImageList:
        if ImageURL.find("a/to/topnotch")!=-1:
            print "***SKIP ImageURL:",ImageURL
            continue
        if ImageURL.find("/i/yg/img/")!=-1:
            print "***SKIP ImageURL:",ImageURL
            continue        
        ImageCount+=1
        ThePos = ImageURL.rfind("?")
        NextPos = ImageURL.rfind("/")
        FileName = ImageURL[NextPos+1:ThePos]
        FileName = FileName.replace("+"," ")
        FilePath = "%s.%s"%(AlbumName,FileName)
        if os.path.exists(FilePath) and os.stat(FilePath).st_size > 2048:
            print "Already got %s, skip it"%FilePath
            continue
        try:    
            RetrieveWithCookies(ImageURL,FilePath)
        except:
            traceback.print_exc()
        
    print "Retrieved the images!",ImagePageURL
    ##sys.stdin.readline()
    return ImageCount

def LootAlbum(ClubName,AlbumURL,ImageCount):    
    TempFileName="%sAlbum"%ClubName
    RetrieveWithCookies(AlbumURL,TempFileName)
    File=open(TempFileName,"r")
    TheParser=htmllib.HTMLParser(formatter=formatter.NullFormatter())
    TheParser.feed(File.read())
    File.close()
    ImageURLs=[]
    for Anchor in TheParser.anchorlist:
        if Anchor.find("?ge&.alabel=")!=-1:
            ImageURLs.append(Anchor)
    for ImageURL in ImageURLs:
        try:
            ImageCount = LootImagePage(ImageURL,ClubName,ImageCount)                    
        except:
            print "Could not get image %s"%ImageURL
            traceback.print_exc()
    return ImageCount

def LootGroupAlbum(GroupName,AlbumURL,ImageCount):
    print "Group album start!"
    ThePos = AlbumURL.find("dir=/")
    NextPos = AlbumURL.find("&",ThePos+5)
    AlbumName = AlbumURL[ThePos+5:NextPos].replace("+"," ")
    TempFileName="%sAlbum"%GroupName
    ThePos = AlbumURL.find(".src=gr")
    AlbumURL = AlbumURL[:ThePos]+".begin=9999&"+AlbumURL[ThePos:]
    RetrieveWithCookies(AlbumURL,TempFileName)
    File=open(TempFileName,"r")
    TheParser=htmllib.HTMLParser(formatter=formatter.NullFormatter())
    TheParser.feed(File.read())
    File.close()
    ImageURLs=[]
    print "Anchors:",TheParser.anchorlist
    for Anchor in TheParser.anchorlist:
        if Anchor.find(".dnm=")!=-1:
            ImageURLs.append(Anchor)
    print "-"*80
    print "Good URLs:"
    for URL in ImageURLs:
        print URL
    ##sys.stdin.readline()
    for ImageURL in ImageURLs:
        try:
            ImageCount = LootImagePage(ImageURL,GroupName,AlbumName,ImageCount)
        except:
            print "Could not get image %s"%ImageURL
            traceback.print_exc()
    return ImageCount

def LootClub(ClubName):
    ImageCount=0
    PictureURL="http://clubs.yahoo.com/clubs/%s?ga"%ClubName
    IndexFileName="%sAlbums"%ClubName
    RetrieveWithCookies(PictureURL,IndexFileName)
    File=open(IndexFileName,"r")
    TheParser=htmllib.HTMLParser(formatter=formatter.NullFormatter())
    TheParser.feed(File.read())
    File.close()
    AlbumURLs=[]
    for Anchor in TheParser.anchorlist:
        if Anchor.find("?gc&.alabel=")!=-1:
            AlbumURLs.append(Anchor)
    #print AlbumURLs    
    for AlbumURL in AlbumURLs:
        try:
            ImageCount=LootAlbum(ClubName,AlbumURL,ImageCount)
        except:
            print "Error looting album %s",AlbumURL
            traceback.print_exc()


    

def LootGenericImagePage(URL,Club,Album):
    TempFileName = "%s.%s.html"%(Club,Album)
    print URL
    print Club
    print Album
    print TempFileName
    urllib.urlretrieve(URL,TempFileName)
    File = open(TempFileName,"r")
    Text=  File.read()
    File.close()
    Bob = htmllib.HTMLParser(formatter=formatter.NullFormatter())
    Bob.feed(Text)
    Bits = list(urlparse.urlparse(URL))
    RootDir = os.path.split(Bits[2])[0]
    for Anchor in Bob.anchorlist:
        print Anchor
        Extension = os.path.splitext(Anchor)[1].upper()
        if Extension not in [".JPG",".GIF",".JPEG",".BMP"]:
            continue
        FileName = "%s.%s"%(Album,Anchor)
        if os.path.exists(FileName):
            continue
        Bits[2] = RootDir+"/"+Anchor
        TheURL = urlparse.urlunparse(Bits)
        print Bits,TheURL
        urllib.urlretrieve(TheURL,FileName)

def LootGroup(GroupName):
    print "Group start!"
    ImageCount=0
    PictureURL="http://photos.groups.yahoo.com/group/%s/lst"%GroupName
    print PictureURL
    IndexFileName="%sList.html"%GroupName
    RetrieveWithCookies(PictureURL,IndexFileName)
    File=open(IndexFileName,"r")
    TheParser=htmllib.HTMLParser(formatter=formatter.NullFormatter())
    TheParser.feed(File.read())
    File.close()
    AlbumURLs={}
    print "Anchors:",TheParser.anchorlist
    for Anchor in TheParser.anchorlist:
        if Anchor.find("lst?")!=-1 and Anchor.find("&.src=gr&.order=&.view=t&.done=http%3a//briefcase.yahoo.com/")!=-1: #Anchor.find(".view=t")!=-1 and 
            AlbumURLs[Anchor]=1
    AlbumURLs = AlbumURLs.keys()
    print "*"*200
    print "Good URLs:",AlbumURLs
    for AlbumURL in AlbumURLs:
        try:
            ImageCount=LootGroupAlbum(GroupName,AlbumURL,ImageCount)            
        except:
            print "Error looting album %s",AlbumURL
            traceback.print_exc()
            

def FixHostName(HostName):
    if HostName[0]==".":
        HostName=HostName[1:]
    if HostName[-1]=="/":
        HostName=HostName[:-1]
    return HostName

def GetCookies():
    CookieDir = r"d:\Documents and Settings\swt\Cookies"
    global COOKIES
    for FileName in os.listdir(CookieDir):        
        FilePath=os.path.join(CookieDir,FileName)
        File=open(FilePath,"r")
        LineNumber=0
        for FileLine in File.readlines():            
            # Name, value, host, 6 lines of filler
            FileLine=FileLine.strip()
            if (LineNumber%9==0):
                CookieName=FileLine
            if (LineNumber%9==1):
                CookieValue=FileLine
            if (LineNumber%9==2):
                CookieHost=FixHostName(FileLine)
                if not COOKIES.has_key(CookieHost):
                    COOKIES[CookieHost]={}
##                Morsels=CookieText.split("&")
##                for Morsel in Morsels:
##                    print Morsel
##                    (CookieName,CookieValue)=Morsel.split("=")
##                    COOKIES[CookieHost][CookieName]=CookieValue
                COOKIES[CookieHost][CookieName]=CookieValue
            LineNumber+=1

def ClubsMain():
    for GroupName in sys.argv[1:]:
        os.chdir("d:\\research\\Clubs\\")
        try:
            os.makedirs(GroupName)
        except:
            pass        
        if len(os.listdir(GroupName)) > 5:
            continue # Already got it, more or less
        os.chdir("d:\\research\\Clubs\\"+GroupName)
        LootGroup(GroupName)
    
def LootImageWrap(URL,Club,Album):
    try:
        os.makedirs(Club)
    except:
        pass
    os.chdir(Club)
    LootGenericImagePage(URL,Club,Album)
    os.chdir("..")

def LootTypeA(URL, Prefix=None, Twig = 0):
    FirstURL = URL
    if not Prefix:
        FileName = os.path.split(URL)[1]
        Prefix = os.path.splitext(FileName)[0]
    URLFile = urllib.urlopen(URL,"r")
    Text = URLFile.read()
    URLFile.close()
    Finder = ImageFinder()
    Finder.feed(Text)
    for ImageLink in Finder.FindImageLinks():
        FullURL = urlparse.urljoin(URL, ImageLink)
        print FullURL
        FileName = "%s.%s"%(Prefix,os.path.split(FullURL)[1])
        if os.path.exists(FileName):
            print "Skip %s; exists already"%FileName
        else:
            urllib.urlretrieve(FullURL, FileName)
    if Twig:
        return
    Pages = []
    for Anchor in Finder.anchorlist:
        x = re.search("\?page=([\d+])&",Anchor)
        if x:
            Pages.append(x.groups(1))
    for Page in Pages:
        NextURL = URL+"?page=%s&perpage=50&columns=6"%Page
        print "Follow link to next page:",NextURL
        LootTypeA(NextURL, Prefix, 1)

def LootTypeB(URL):
##    Thing = urllib.urlopen("http://www.seifukuheaven.com/photobooks_frameset.htm","r")
##    #Thing = urllib.urlopen("http://www.seifukuheaven.com/koodi/short-red.php","r")
##    URLFile = urllib.urlopen(URL,"r")
##    print URLFile.read()
##    URLFile.close()
##    URLFile = urllib.urlopen(URL,"r")
##    Text = URLFile.read()
##    URLFile.close()
##    print Text
    
##    Finder.feed(Text)
    PhotoBookList = ["http://www.seifukuheaven.com/images/photobooks/nandee/nandee.htm"]
    for ImagePageURL in PhotoBookList: ##Finder.anchorlist:
        print "ImagePage:",ImagePageURL
        # Get prefix:
        FileName = os.path.split(ImagePageURL)[1]
        Prefix = os.path.splitext(FileName)[0]
        # Open each photo book:
        URLFile = urllib.urlopen(ImagePageURL,"r")
        Text = URLFile.read()
        URLFile.close()
        Finder = ImageFinder()
        Finder.feed(Text)
        print Text
        # Get all the photos from the book:
        for ImageLink in Finder.FindImageLinks():
            FullURL = urlparse.urljoin(ImagePageURL, ImageLink)
            FileName = "%s.%s"%(Prefix,os.path.split(FullURL)[1])
            if os.path.exists(FileName):
                print "Skip %s; exists already"%FileName
            else:
                print "Get %s to %s"%(FullURL, FileName)
                urllib.urlretrieve(FullURL, FileName)
        

def LootSeiFuku():
##    PhotoPage = "http://www.seifukuheaven.com/photobooks.htm"
##    LootTypeB(PhotoPage)    
##    return
    FirstPages = ["http://www.seifukuheaven.com/koodi/lingerie.php",
                  "http://www.seifukuheaven.com/koodi/lingerie-sei.php",
##                  "http://www.seifukuheaven.com/koodi/short-red.php",
##                  "http://www.seifukuheaven.com/koodi/short-blue.php",
##                  "http://www.seifukuheaven.com/koodi/short-muu.php",
##                  "http://www.seifukuheaven.com/koodi/long-white.php",
##                  "http://www.seifukuheaven.com/koodi/long-dark.php",
##                  "http://www.seifukuheaven.com/koodi/cardigan.php",
##                  "http://www.seifukuheaven.com/futari_frameset.htm",
##                  "http://www.seifukuheaven.com/koodi/shirtskirt.php",
##                  "http://www.seifukuheaven.com/koodi/coat.php",
##                  "http://www.seifukuheaven.com/koodi/other.php",
                  "http://www.seifukuheaven.com/koodi/mizugi-one.php"
                  "http://www.seifukuheaven.com/koodi/mizugi-two.php",
                  ]
    for FirstPage in FirstPages:
        LootTypeA(FirstPage)

def Grab():
    File = open(r"d:\tendrils\cell7.htm","r")
    HTML = File.read()
    Parser = ImageFinder()
    Parser.feed(HTML)
    for Anchor in Parser.FindRARLinks():
        #Anchor = "http://www.zophar.net/nsf/"+Anchor
        print "Get:", Anchor
        FileName = os.path.split(Anchor)[1]
        try:
            urllib.urlretrieve(Anchor, FileName)
        except:
            traceback.print_exc()

if __name__=="__main__":
    Grab()
    for FileName in os.listdir("."):
        Bits = os.path.splitext(FileName)
        if Bits[1].upper() == ".RAR":
            try:
                os.makedirs(Bits[0])
            except:
                pass
            os.chdir(Bits[0])
            Str = '"C:\Program Files\WinRAR\unrar.exe" x -y ..\%s'%Bits[0]
            os.system(Str)
            os.chdir("..")
            