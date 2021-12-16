import cloudscraper
import datetime
import random
import json
import time
import re

class OGBumper:
    """
    Constructor
    This function is being called upon class initialisation
    """
    def __init__(self):
        #Loading the config
        self.config = json.load(open('config.json'))

        #Proxy
        self.proxy = ""

        #Creating our cloudscraper instance and setting headers and cookies
        self.scraper = cloudscraper.create_scraper()
        self.scraper.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        self.scraper.cookies.set("ogusersmybbuser", self.config['mybbuser'], domain="ogusers.com")

        #Last post variable so we don't send the same content twice in a row
        self.last_post = ""

        #Starting the bot
        self.StartBumper()

    """
    Pull a random proxy
    """
    def GetProxy(self):
        with open('proxy.txt', 'r') as file:
            allLines = file.read()
            proxies = list(map(str, allLines.split()))
            return random.choice(proxies) 

    """
    This function is pulling the 'my_post_key' value from the website below.
    This key is required to perform the actual bumping
    """
    def GetPostKey(self):
        #Requesting the webpage
        result = self.scraper.get(url = "https://ogusers.com/misc.php?action=help&hid=33")

        #Checking if we are ip blocked by cloudflare
        if re.search("<title>Please Wait... | Cloudflare</title>", result.text):
            print("[GetPostKey] You are currently ip blocked by Cloudflare! Please try again in 15-45 minutes.")
            exit()
        #Checking if we are blocked by OGUsers
        elif re.search("<title>OGUsers</title>", result.text) and re.search("<span>Access Denied.</span>", result.text):
            print("[GetPostKey] You are currently ip blocked by OGUsers! Please try again later.")
            exit()
        #We are not blocked so we return the post key
        else:
            return re.search("my_post_key = \"(.+?)\";", result.text).group(1)
              
    
    """
    This function pulls the threadid from a given thread
    This id is required to perform the actual bumping
    """
    def GetThreadID(self, threadURL):
        #Requesting the webpage
        result = self.scraper.get(url = threadURL)

        #Checking if we are ip blocked by cloudflare
        if re.search("<title>Please Wait... | Cloudflare</title>", result.text):
            print("[GetThreadID] You are currently ip blocked by Cloudflare! Please try again in 15-45 minutes.")
            exit()
        #Checking if we are blocked by OGUsers
        elif re.search("<title>OGUsers</title>", result.text) and re.search("<span>Access Denied.</span>", result.text):
            print("[GetThreadID] You are currently ip blocked by OGUsers! Please try again later.")
            exit()
        #We are not blocked so we return the threadid
        else:
            return re.findall("newreply\.php\?tid=(\d+)", result.text)[0]

    """
    This functions pulls a random post from the config
    """
    def GetRandomPost(self):
        post = random.choice(self.config["settings"]["content"])
        return post if not post == self.last_post else self.GetRandomPost()
    
    """
    This functions performs the bumping
    """
    def SendBump(self, message, threadURL):
        #Creating timestamp
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')

        #Webresult
        result = ""

        #Checking if proxy is enabled
        if self.config['proxy']:
            #Setting the proxy and printing it to console
            self.proxy = {"http": f"http://{self.GetProxy()}"}
            print(f"[SendBump] Using proxy {self.proxy['http']}")

            result = self.scraper.post(
                url = "https://ogusers.com/newreply.php?ajax=1",
                data = {
                    'my_post_key': self.GetPostKey(),
                    'subject': '',
                    'action': 'do_newreply',
                    'posthash': '',
                    'quoted_ids': '',
                    'lastpid': 0,
                    'tid': self.GetThreadID(threadURL),
                    'method': 'quickreply',
                    'message': ' %s' % message
                },
                proxies=self.proxy
            )
        else:
            result = self.scraper.post(
                url = "https://ogusers.com/newreply.php?ajax=1",
                data = {
                    'my_post_key': self.GetPostKey(),
                    'subject': '',
                    'action': 'do_newreply',
                    'posthash': '',
                    'quoted_ids': '',
                    'lastpid': 0,
                    'tid': self.GetThreadID(threadURL),
                    'method': 'quickreply',
                    'message': ' %s' % message
                }
            )
        
        #Checking if we are ip blocked by cloudflare
        if re.search("<title>Please Wait... | Cloudflare</title>", result.text):
            print("[SendBump] You are currently ip blocked by Cloudflare! Please try again in 15-45 minutes.")
            exit()
        #Checking if we are blocked by OGUsers
        elif re.search("<title>OGUsers</title>", result.text) and re.search("<span>Access Denied.</span>", result.text):
            print("[SendBump] You are currently ip blocked by OGUsers! Please try again later.")
            exit()
        #We are not blocked so we return error or success message depending on the result we get
        else:
            data = json.loads(result.text)
            if "data" in data:
                return f"[SendBump] Successfully bumped post with url {threadURL} on {st}!"
            elif "errors" in data:
                return f"[SendBump] Error while bumping! {result.text}"

    """
    This function starts the bot
    """
    def StartBumper(self):
        while True:
            for thread in self.config['settings']['threads']:
                if '~~' in thread:
                    thread, message = thread.split('~~')
                    print(self.SendBump(message, thread))

                elif len(self.SendBump(self.GetRandomPost(), thread)):
                    print(self.SendBump(self.config['settings']['content'][0], thread))
                
                else:
                    print(self.SendBump(self.config['settings']['content'][0], thread))

                time.sleep(10)
            
            print("[StartBumper] Waiting for cooldown before sending next bump!")
            time.sleep(self.config['settings']['delay'])


if __name__ == "__main__":
    OGBumper()