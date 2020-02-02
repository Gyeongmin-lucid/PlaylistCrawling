import os
import json

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

MELON_URL = 'https://www.melon.com/mymusic/dj/mymusicdjplaylistview_inform.htm?plylstSeq=439916153'
GENIE_URL = 'https://www.genie.co.kr/'
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

class Selenium :
    def __init__(self) :
        self.browser    = None
        self.MAX_RETRY  = 10
        self.MAIN_WINDOW = None
        self.POPUP_WINDOW = None

    def setWebdriver(self, url) :
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('window-size=1920x1080')

        # chrome_options.add_argument("disable-gpu")

        self.browser = webdriver.Chrome(os.path.join(ROOT_DIR, 'lib/chromedriver4MAC'), \
                                        chrome_options=chrome_options)
        self.browser.get(url)
        self.MAIN_WINDOW = self.browser.current_window_handle

    def setUrl(self, url) :
        self.browser.get(url)

    def clickButtionByXPath(self, XPath) :
        try :
            wait = WebDriverWait(self.browser, 1)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, XPath)))

            pageButton = self.browser.find_element_by_xpath(XPath)
            pageButton.click()
            return True
        except NoSuchElementException as e :
            print("[FAIL] No Element on {}".format(XPath))
            return False
        except TimeoutException as e : 
            print("[TIMEOUT] {}".format(e))
            return False
        except Exception as e :
            print("[EXCEPT] {}".format(e))
            return False

        return True
    
    def getXPathList(self, XPath) :
        RetryCount = 1
        while RetryCount < self.MAX_RETRY :
            content = []
            try :
                elements = self.browser.find_elements_by_xpath(XPath)
                for element in elements : 
                    content.append(element.text)
                return content

            except StaleElementReferenceException as e :
                print("[FAIL] Please Retry on {} \n".format(RetryCount))
                RetryCount += 1
                continue
            except Exception as e :
                print("{}".format(e))
                break

                # continue
        self.browser.implicitly_wait(2)
        
        if RetryCount == self.MAX_RETRY :
            raise StaleElementReferenceException
    
    def setAlertOK(self) :
        try:
            WebDriverWait(self.browser, 3).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')

            alert = self.browser.switch_to.alert
            alert.accept()
        except TimeoutException:
            print("no alert")
    
    def setInputElement(self, XPath, value) :
        # print("input Element :: Path {}, value {}".format(XPath, value))
        while True :
            try : 
                inputElement = self.browser.find_element_by_xpath(XPath)
                if not inputElement :
                    print("no input element")
                else :
                    inputElement.clear()
                    inputElement.send_keys(value)
                    break
                    
            except NoSuchElementException as e :
                print("execpt no element")
                continue
        self.browser.implicitly_wait(2)

    def keepWebView(self) :
        self.browser.execute_script('alert("Focus window");')
        self.browser.switch_to.alert.accept()
        self.browser.implicitly_wait(2)

    def switchPopUpView(self) :
        for handle in self.browser.window_handles: 
            if handle != self.MAIN_WINDOW: 
                self.POPUP_WINDOW = handle 
        self.browser.switch_to.window(self.POPUP_WINDOW)
        self.browser.implicitly_wait(2)

        # newWindow = self.browser.window_handles[viewIndex]
        # self.browser.switch_to.window(newWindow)
        print("switch Window")

    def switchMainView(self) :
        self.browser.implicitly_wait(2)
        # self.browser.switch_to.default_content()
        self.browser.execute_script('window.focus();')
        while True :
            try : 
                # for handle in self.browser.window_handles: 
                #     self.browser.switch_to.window(handle)
                # self.browser.close();
                
                self.browser.switch_to.window(self.MAIN_WINDOW)
                break

            except NoSuchWindowException as e:
                print("no window")
                continue
        # self.browser.switch_to.default_content()


    

class Melon :
    def __init__(self, url) :
        self.MELON_URL          = url
        # self.MELON_XPATH_SONG   = '//*[@id="frm"]/div/table/tbody/tr[*]/td[5]/div/div/div[1]/span/a'
        self.MELON_XPATH_SONG   = '//*[@id="frm"]/div/table/tbody/tr[*]/td[5]/div/div/div[1]'
        self.MELON_XPATH_SINGER = '//*[@id="frm"]/div/table/tbody/tr[*]/td[5]/div/div/div[2]'
        self.MELON_XPATH_PAGES  = '//*[@id="pageObjNavgation"]/div/span/a[*]'

        self.PAGES_SIZE         = 10
        self.CLICK_FAIL         = False
        self.PARSING_FAIL       = False
        
        self.playListSingers    = [ [] ] *self.PAGES_SIZE
        self.playListSongs      = [ [] ] *self.PAGES_SIZE
        self.melonBrowser       = Selenium()
        self.melonBrowser.setWebdriver(self.MELON_URL)
    
    def makeListFromPlaylist(self) :
        for pageIndex in range(1,self.PAGES_SIZE) :
            print("[GET CRAWLING...] {}".format(pageIndex))
            self.playListSongs[pageIndex] = self.getListByXPath(self.MELON_XPATH_SONG)
            self.playListSingers[pageIndex] = self.getListByXPath(self.MELON_XPATH_SINGER)

            pageXPath = self.getPageXPath(pageIndex)
            print("path " + pageXPath)

            if self.melonBrowser.clickButtionByXPath(pageXPath) == self.CLICK_FAIL :
                print("[END PAGE] {}".format(pageIndex+1))
                break

    def getListByXPath(self, XPath) :
        resList = self.melonBrowser.getXPathList(XPath)
        if not resList : 
            print("[GET PATH FAIL] {}\n".format(XPath))

        print("List Size :: {}".format(len(resList)))
        return resList

    def getPageXPath(self, pageIndex) :
        resXPath = self.MELON_XPATH_PAGES[:-2] + str(pageIndex) + self.MELON_XPATH_PAGES[-1]
        return resXPath
    
    def getPlaylist(self) :
        resSongs    = self.playListSongs
        resSingers  = self.playListSingers

        return resSongs, resSingers

    def printPlaylist(self) :
        for songs, singers in zip(self.playListSongs, self.playListSingers) :
            for song, singer in zip(songs, singers) :
                print("{} - {}".format(song, singer))

class Genie :
    
    def  __init__(self, url) :
        self.username = None
        self.password = None
        self.playlist = None
        self.GENIE_URL              = url
        # self.GENIE_MY_MUSIC       = "https://www.genie.co.kr/myMusic/myMusicPlayList"

        self.GENIE_LOGIN_TOGGLE     = '//*[@id="gnb"]/div/div/button'
        self.GENIE_LOGIN            = '//*[@id="gnb"]/div/div/div/div/a/span'
        self.GENIE_ID               = '//*/input[@id="gnb_uxd"]'
        self.GENIE_PASSWORD         = '//*/input[@id="gnb_uxx"]'
        self.GENIE_LOGIN_FIN        = '//*[@id="f_login_layer"]/input[2]'

        self.GENIE_MY_MUSIC         = '//*[@id="gnb"]/div/div[2]/button'
        self.GENIE_GET_PLAYLIST     = '//*[@id="myAlbum"]/a'
        self.GENIE_MAKE_PLAYLIST    = '//*[@id="body-content"]/div[3]/div[2]/a[1]'
        self.GENIE_SONG_SEARCH      = '//*[@id="sc-fd"]'
        self.GENIE_SONG_SEARCH_ICON = '//*[@id="frmGNB"]/fieldset/input[3]'
        self.GENIE_PLAYLIST_NAME    = '//*[@id="albumName"]'
        self.GENIE_PLAYLIST_SAVE    = '//*[@id="playlistLayerPopup"]/div[1]/a[2]'

        self.GENIE_SONG_CHECKBOX    = '//*[@id="body-content"]/div[3]/div[2]/div/table/tbody/tr[1]/td[1]/input'
        self.GENIE_ADD_SONG         = '//*[@id="add_my_album_list"]'
        self.GENIE_CLICK_PLAYLIST   = '//*[@id="mCSB_1_container"]/li[1]/a[@title='

        self.CLICK_FAIL = False
        
        self.genieBrowser       = Selenium()
        self.genieBrowser.setWebdriver(self.GENIE_URL)

    def login(self) :
        config = json.loads(open(os.path.join(ROOT_DIR, 'config/config.json')).read())
        self.username = config['username']
        self.password = config['password']
        print(type(self.username))
        print(type(self.password))
        print(type(config['username']))
        print(type(config['password']))

        if self.genieBrowser.clickButtionByXPath(self.GENIE_LOGIN_TOGGLE) == self.CLICK_FAIL or \
           self.genieBrowser.clickButtionByXPath(self.GENIE_LOGIN) == self.CLICK_FAIL :
            print("[FAIL] GENIE Login")

        self.genieBrowser.switchPopUpView()

        self.genieBrowser.setInputElement(self.GENIE_ID, self.username)
        self.genieBrowser.setInputElement(self.GENIE_PASSWORD, self.password)

        if self.genieBrowser.clickButtionByXPath(self.GENIE_LOGIN_FIN) == self.CLICK_FAIL :
            print("[FAIL] GENIE Login")


        self.genieBrowser.switchMainView()
        
        # self.genieBrowser.keepWebView()
    
    def makeNewPlayList(self) :

        if self.genieBrowser.clickButtionByXPath(self.GENIE_MY_MUSIC) == self.CLICK_FAIL or \
           self.genieBrowser.clickButtionByXPath(self.GENIE_GET_PLAYLIST) == self.CLICK_FAIL or \
           self.genieBrowser.clickButtionByXPath(self.GENIE_MAKE_PLAYLIST) == self.CLICK_FAIL :
            print("[FAIL] GENIE make playlist")

        self.setPlayList()
        self.genieBrowser.setInputElement(self.GENIE_PLAYLIST_NAME, self.playlist)

        if self.genieBrowser.clickButtionByXPath(self.GENIE_PLAYLIST_SAVE) == self.CLICK_FAIL :
            print("[FAIL] GENIE make playlist")

        self.genieBrowser.setAlertOK();
        songCmds = self.getPlaylist()

        for songCmd in songCmds : 
            self.genieBrowser.setInputElement(self.GENIE_SONG_SEARCH, songCmd)

            if self.genieBrowser.clickButtionByXPath(self.GENIE_SONG_SEARCH_ICON) == self.CLICK_FAIL or \
                self.genieBrowser.clickButtionByXPath(self.GENIE_SONG_CHECKBOX) == self.CLICK_FAIL or \
                self.genieBrowser.clickButtionByXPath(self.GENIE_ADD_SONG) == self.CLICK_FAIL or \
                self.genieBrowser.clickButtionByXPath(self.GENIE_CLICK_PLAYLIST) == self.CLICK_FAIL :
                print("[FAIL] Search Song : {}".format(songCmd))
                continue
            # print("[SUCCESS]")
            self.genieBrowser.setAlertOK();


    def getPlaylist(self) :
        melon = Melon(MELON_URL)
        melon.makeListFromPlaylist()
        melonSong, melonSinger = melon.getPlaylist()

        songCmdList = []
        for songs, singers in zip(melonSong, melonSinger) :
            for song, singer in zip(songs, singers) :
                songSearchCmd = song + " - " + singer
                songCmdList.append(songSearchCmd)

        return songCmdList


    def setPlayList(self) :
        now = datetime.now()
        self.playlist = now.strftime("%Y%m%d_%H%M%S")
        self.GENIE_CLICK_PLAYLIST = self.GENIE_CLICK_PLAYLIST + '"' + self.playlist + '"]'
        print(self.GENIE_CLICK_PLAYLIST)



def main() :
    # melon = Melon(MELON_URL)
    # melon.makeListFromPlaylist()
    # melon.printPlaylist()

    genie = Genie(GENIE_URL)
    genie.login()
    genie.makeNewPlayList()

if __name__ == '__main__' :
    main()