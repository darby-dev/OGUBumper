import cloudscraper
import random
import json
import time
import re

#   Original GitHub:
#           https://github.com/AdventurefulGIT/OGUsers-Bumper/
#   
#   Since the old version was not giving any information about blocks.. 
#   I decided to rewrite it.
#
#   If you have any question message me.
#   Contact: darby#0001 on Discord

class OGBumper:
    def __init__(self):
        self.session = cloudscraper.create_scraper({
            'browser': 'chrome',
            'platform': 'android',
            'desktop': 'false'
        })

        self.session.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        self.config = json.load(open('config.json'))
        self.session.cookies.set("ogusersmybbuser", self.config['mybbuser'], domain="ogusers.com")

        self.last_post = ""
        self.StartBumper()
    
    # This method pulls your posting key from ogusers
    def GetPostKey(self):
        r = self.session.get(url = "https://ogusers.com/misc.php?action=help&hid=33")     
        if self.IsBlocked():
            return "[GetPostKey] You are currently ip blocked! The block should resolve itself after 15-45 minutes."
        else:
            try:
                return re.search("my_post_key = \"(.+?)\";", r.text).group(1)
            except:
                return "No post key was found!"
    
    # This method pulls a thread id from a given url
    def GetThreadID(self, threadURL):
        r = self.session.get(url = threadURL)
        if self.IsBlocked():
            return "[GetThreadID] You are currently ip blocked! The block should resolve itself after 15-45 minutes."
        else:
            try:
                return re.findall("newreply\.php\?tid=(\d+)", r.text)[0]
            except:
                return f"No id found for thread {threadURL}"

    # This methods checks if we are blocked by cloudflare
    def IsBlocked(self):
        r = self.session.get(url = "https://ogusers.com/misc.php?action=help&hid=33")
        if re.search("<title>Please Wait... | Cloudflare</title>", r.text):
            return True
        else:
            return False

    # This method pulls a random post from the config.json file
    def GetRandomPost(self):
        post = random.choice(self.config["settings"]["content"])
        return post if not post == self.last_post else self.GetRandomPost()
    
    # This method sends the auto bump
    def SendBump(self, message, threadURL):
        r = self.session.post(
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

        if self.IsBlocked():
            return "[SendBump] You are currently ip blocked! The block should resolve itself after 15-45 minutes."
        else:
            try:
                return f"[SendBump] Successfully bumped thread with url {threadURL}"
            except:
                return f"[SendBump] Unknown error while auto bumping thread with url {threadURL}"

    # Starting the bot
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
