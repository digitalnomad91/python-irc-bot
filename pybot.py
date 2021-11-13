#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import subprocess
import socket
import re
import string
import sys
import json as simplejson
import time
from xml.dom import minidom
import json
import urllib2
import wolframalpha

try:
     from urllib.request import urlopen
     from urllib.parse import urlencode
except ImportError:
     from urllib import urlopen, urlencode

from twisted.internet.protocol import Factory, Protocol
import HTMLParser
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import datetime
import random
import cleverbot
#import wikipedia
import pprint

from googleapiclient.discovery import build

import os
os.chdir("/root/pybot/Google-Search-API")
from google import google


LAST_BTC_PRICE = 1.0
CLEVERBOT = cleverbot.Session()
TELL_DICT = {}

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub(' ', data)


def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


class Bot():

    # Change into values that suit you.
    NETWORK = 'fuge.it'
    PORT = 6667
    nick = 'dangler'
    channel = '#root'
    owner = 'Fuge'

    def __init__(self):
        self.quit_bot = False
        self.command_list = []  # initialy we have not received any command.
        self.data_buffer = ''  # no data received yet.
        self.rexp_general = re.compile(r'^(:[^ ]+)?[ ]*([^ ]+)[ ]+([^ ].*)?$')
 
    def connect_to_server(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.NETWORK, self.PORT))
        self.irc.send('NICK ' + self.nick + '\r\n')
        self.irc.send('USER ' + self.nick + ' moose moose :Python IRC Bot\r\n')


    def init(self):
        self.irc.send('PRIVMSG %s :Hello, I am %s, a pythonic IRC bot.\r\n' %
                      (self.channel, self.nick))

    def check_output(self, *popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output

    def pretty_date(self, time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.datetime.now()
        #time = time.split(".")[0]
        time1 = datetime.datetime.strptime(time, '%a %b %d %H:%M:%S %Y')
        diff = now - time1
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return  "a minute ago"
            if second_diff < 3600:
                return str( second_diff / 60 ) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str( second_diff / 3600 ) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        #if day_diff < 7:
        return str(day_diff) + " days ago"
        #if day_diff < 31:
        #    return str(day_diff/7) + " weeks ago"
        #if day_diff < 365:
        #    return str(day_diff/30) + " months ago"
        #return str(day_diff/365) + " years ago"

    def parse_command(self, data):
        p = self.rexp_general
        r = p.search(data)
        if r is None:
            # command does not match.
            #print "command does not match."
            return

        g = r.groups()
        #print "g =", g
        sender = g[0]
        if sender is not None:
            sender = sender[1:]

        cmd = g[1]
        params = g[2]

        if cmd == 'PING':
            self.irc.send('PONG ' + params + '\r\n')
            return
        elif cmd == 'KICK':
            self.irc.send('JOIN ' + self.channel + '\r\n')
            return
        elif cmd == 'ERROR':
            self.main()
        elif cmd == 'NOTICE':
            #print "params =", params
            query = params.split(":", 1)[1]
            if query.startswith('This nickname is registered and protected.'):
                self.irc.send('PRIVMSG NickServ IDENTIFY m00s3\r\n')
                self.irc.send('OPER dfoolz fuckyou.\r\n')
                self.irc.send('SAJOIN moose #dev\r\n')
                self.irc.send('SAJOIN moose #subtlefuge\r\n')
                #self.irc.send('SAJOIN moose #notifications\r\n')
        elif cmd == 'JOIN':
            if params[1:] == '#fuge':   # on join to fuge, send the following notice
                nick = sender.split("!")[0].lower()
                notice =  "Welcome to fuge.it IRC. If you need help, ask your question. "
                notice += "Please be patient and wait for a response. If you leave right"
                notice += " away, your question won't be answered."
                self.irc.send("NOTICE %s :%s\r\n" % (nick, notice))
        elif cmd == 'PRIVMSG':
            channel, query = params.split(":", 1)
            channel = channel.strip()
            query = query.lstrip()
            nick = sender.split("!")[0].lower()
            global TELL_DICT

            if channel == "#subtlefuge":
                nick = nick.lower()
                if nick in TELL_DICT:
                    for line in TELL_DICT[nick]:
                        self.irc.send('PRIVMSG %s :%s\r\n' % (channel, line))
                    TELL_DICT.pop(nick, None)

            hi_rex = r'(hi|hello|hola)[ ]+%s' % self.nick
            if re.search(hi_rex, query) is not None:
                msg = 'Hi, I am a pythonic irc bot!'
                self.irc.send('PRIVMSG %s :%s\r\n' % (channel, msg))
                return


            if re.search(r'^!(w|f|forecast|weather)[ ]', query) is not None:
                given_location = query.split(" ", 1)[1]
                geo_url = 'http://maps.googleapis.com/maps/api/geocode/json?%s&sensor=false' % urlencode({'address': given_location})
                try:
                    res = urllib2.urlopen(geo_url, timeout=3)
                    json = simplejson.loads(res.read())
                    address = json['results'][0]['formatted_address']
                    latitude = json['results'][0]['geometry']['location']['lat']
                    longitude = json['results'][0]['geometry']['location']['lng']
                    #print address, latitude, longitude
                    forecast_url = 'https://api.forecast.io/forecast/6cbb075063c8a6ecc3ef6b8f898ac6da/%s,%s' % (latitude, longitude)
                    try:
                        res = urllib2.urlopen(forecast_url, timeout=5)
                        json = simplejson.loads(res.read())
                        print json
                        summary = json['currently']['summary']
                        temp = str(json['currently']['temperature'])
                        wind = str(json['currently']['windSpeed'])
                        humidity = str(json['currently']['humidity']*100)
                        hourly = ''
                        minutely = ''
                        try:
                            if 'minutely' in json:
                                minutely = 'next hour: ' + json['minutely']['summary']
                            if 'hourly' in json:
                                hourly = 'next 24 hours: ' + json['hourly']['summary']
                        except:
                            pass
                        forecast_str = 'Forecast for %s: %s  %sF  Humidity: %s%%  Wind: %smph  %s  %s' % (address, summary, temp, humidity, wind, minutely, hourly)
                        self.irc.send('PRIVMSG %s :%s\r\n' % (channel, forecast_str))
                    except:
                        try:
                            url = 'http://api.wunderground.com/api/cae7729a7e3a51a5/conditions/q/%s,%s.json' % (latitude, longitude)
                            res = urlopen(url)
                            json = simplejson.loads(res.read())
                            current = json['current_observation']
                            full_location = current['display_location']['full']
                            date_time = current['observation_time_rfc822'][5:]
                            weather = current['weather']
                            temperature = current['temperature_string'].replace(" F", "F").replace(" C", "C")
                            humidity = current['relative_humidity']
                            wind_str = current['wind_string'][9:].replace(" MPH", "MPH").replace(" at", "").replace(" to", "")
                            weather_string = 'Weather for %s: %s  %s  Humidity: %s  Wind: %s  %s' % (full_location, weather, temperature, humidity, wind_str, date_time)
                            self.irc.send('PRIVMSG %s :%s\r\n' % (channel, weather_string))
                        except:
                            self.irc.send('PRIVMSG %s :No forecast info available for %s\r\n' % (channel, address))
                except:
                    self.irc.send('PRIVMSG %s :No forecast info available for %s\r\n' % (channel, given_location))


            if re.search(r'^(!wolfram)[ ]', query) is not None:
                math_query = query.split(" ", 1)[1]
                url = 'http://www.wolframalpha.com/input/?'+\
                      urlencode({'i': math_query})
                self.irc.send('PRIVMSG %s :%s\r\n' % (channel, url))


            if re.search(r'^!(m|math)[ ]', query) is not None:
               client = wolframalpha.Client("6YRRH5-62GJRE47GP")
               math_query = query.split(" ", 1)[1]
               res = client.query(math_query)
               self.irc.send('PRIVMSG %s :%s\r\n' % (channel, next(res.results).text))
                        
                        
            if re.search(r'^(dangler gif)[ ]', query) is not None:
                google_query = query.split(" ", 2)[2]
                url = "http://api.giphy.com/v1/gifs/search?%s&api_key=dc6zaTOxFJmzC"% urlencode({"q": google_query})
                try:
                    res = urllib2.urlopen(url, timeout=5)
                    json = simplejson.loads(res.read())
                    first = json['data']
                    if first:
                        first = first[0]
                        url = first['url'].encode('ascii', 'ignore')
                        msg = "tet %s: %" (url)
                        self.irc.send('PRIVMSG %s :%s\r\n' % (channel, msg))
                        return true
                except:
                    self.irc.send('PRIVMSG %s :No response from giphy %s %s \r\n' % (channel, google_query, url))


            if re.search(r'^!(g|google)[ ]', query) is not None:
                google_query = query.split(" ", 1)[1]
				
                num_page = 3
                res = google.search(google_query, num_page)


                if res[0]:
					first = res[0]
					title = first.name
					pars = HTMLParser.HTMLParser()
					title = pars.unescape(title)
					title = title.encode('ascii','ignore')
					url = first.link.encode('ascii', 'ignore')
					msg = "02G05o08o02g03l05e %s: %s" % (title,
								  urllib2.unquote(url).replace("(", "%28").replace(")", "%29"))
					self.irc.send('PRIVMSG %s :%s\r\n' % (channel, msg))
                else:
					self.irc.send('PRIVMSG %s :No results found. -_-\r\n' % channel)



            ip_apikey = '3e6d40bfec81a7e0585c88fcbaf15f0ba426c3c0ac9ff85c0275bd040b12f745'
            if re.search(r'^!(i|ipinfo)[ ]', query) is not None:
                try:
                    ip_query = query.split(" ", 1)[1]
                    url = "http://api.ipinfodb.com/v3/ip-city/?key=%s&ip=%s" %\
                          (ip_apikey, ip_query)
                    res = urllib2.urlopen(url, timeout=3)
                    contents = res.read()
                    contents = contents[4:]
                    if contents != ";;;;;;;;":
                        loc_arr = contents.split(';')
                        loc_arr = loc_arr[2:]
                        loc_arr.pop()
                        self.irc.send('PRIVMSG %s :%s\r\n' % (channel, ", ".join(loc_arr)))
                except: pass

                try:
                    url = "http://whatismyipaddress.com/ip/" + ip_query
                    res = urllib2.urlopen(url, timeout=3)
                    html = res.read()
                    html = remove_html_tags(html)
                    rest0 = html.split("Hostname:")[1]
                    hostname = rest0.lstrip().split("  ")[0]
                    hostname = hostname.strip()
                    rest1 = rest0.split("ISP:")[1]
                    isp = rest1.lstrip().split("  ")[0]
                    isp = isp.strip()
                    rest2 = rest1.split("Organization:")[1]
                    org = rest2.lstrip().split("  ")[0];
                    org = org.strip()
                    rest3 = rest2.split("Services:")[1]
                    services = rest3.lstrip().split("   ")[0]
                    services = services.strip()
                    rest4 = rest3.split("Type:")[1]
                    type_ = rest4.lstrip().split("   ")[0]
                    type_ = type_.strip()
                    rest5 = rest4.split("Assignment:")[1]
                    assignment = rest5.lstrip().split("   ")[0]
                    assignment = assignment.strip()
                    #rest6 = rest5.split("Blacklist:")[1]
                    #blacklist = rest6.lstrip().split("   ")[0]
                    #blacklist = remove_extra_spaces(blacklist.strip())
                    #
                    #if blacklist != "":
                    #    blacklist = "Blacklist: " + blacklist

                    ipinfo = [hostname, isp, org, services, type_, assignment, ]  # blacklist

                    self.irc.send('PRIVMSG %s :%s\r\n' % (channel, ", ".join(ipinfo)))
                except: pass


            if re.search(r'^!(s|seen)[ ]', query) is not None:
                seen_query = query.split(" ", 1)[1]
                seen_query = seen_query.strip()
                seen_response = "I don't remember seeing %s." % seen_query
                self.irc.send('NAMES %s\r\n' % channel)
                try:
                    users = self.get_command().split('%s :' % channel)[1]
                    _ = self.get_command() # end of names list
                    users = re.sub('[+@%~&]', '', users).split()

                    for u in users:
                        if seen_query.lower() == u.lower():
                            seen_response = '%s is right here!' % u
                            self.irc.send('PRIVMSG %s :%s\r\n' % (channel, seen_response))
                            return
                except: pass

                try:
                    self.irc.send('WHOWAS %s\r\n' % seen_query)
                    whowas_lines = []
                    whowas_lines.append(self.get_command().split("moose ", 1)[1])
                    whowas_lines.append(self.get_command().split("moose", 1)[1])
                    if 'There was no such nickname' not in whowas_lines[1]:
                        nick = whowas_lines[0].split()[0]
                        dt = whowas_lines[1].split(":", 1)[1]
                        seen_response = "%s was last seen quitting %s." %\
                                        (nick, self.pretty_date(dt))
                except: pass
                self.irc.send('PRIVMSG %s :%s\r\n' % (channel, seen_response))
                

            if re.search(r'^!fml', query) is not None:
                try:
                    response = urllib2.urlopen('http://fmylife.com/random',
                                               timeout=3)
                    html = response.read()
                    fml = html.split('Today,', 1)[1].split('FML</a>')[0]
                    soup = ''.join(BeautifulSoup(fml,
                    convertEntities=BeautifulSoup.HTML_ENTITIES).findAll(text=True))
                    self.irc.send('PRIVMSG %s :\00304Today, %s -FML-\r\n' % (channel, soup.strip()))
                except:
                    self.irc.send('PRIVMSG %s :Bad response from fmylife.com/random.\r\n' % channel)

            #User: kstigs / Connectable: Waiting... / Class: User / Uploaded: (5.00 GB) / Downloaded: (0.00 B) / Ratio: (0.00) / Joined : 3d ago / Profile: http://bitleechers.me/account-details.php?id=2268

            if re.search(r'^!(u|user)[ ]', query) is not None:
                user = query.split(" ", 1)[1]
                url = 'http://fuge.it/api/get?username=%s&api_key=nfvx89sadjklncsjAGmzsxcJoiuJnmsdadnjSD12dvcje' %\
                user.strip()
                try:
                    response = urllib2.urlopen(url, timeout=5)
                    json = simplejson.loads(response.read())

                    if int(json['access_level']) <= 9000:
                        user_class = 'user'
                    else:
                        user_class = 'admin'

                    upload = str(sizeof_fmt(int(json['web_seed_up_total'].split(".")[0])))
                    download = str(sizeof_fmt(int(json['web_seed_down_total'].split(".")[0])))
                    xfer_available = str(sizeof_fmt(int(json['web_seed_transfer_available'].split(".")[0])))
                    #print xfer_available
                    space_free = str(sizeof_fmt(int(json['disk_space_total']) - int(json['disk_space_used'])))
                    joined = json['created_at']

                    banned = ''
                    if int(json['disabled']) == 1:
                         banned = ' | \00304BANNED'

                    profile_url = "https://fuge.it/user/" + json['username']

                    message = "%s | Class: %s | Uploaded: %s | Downloaded: %s | Free Space: %s | Transfer Left: %s | Joined: %s | Profile: %s%s"\
                               % (json['username'], user_class, upload, download, space_free,
                                  xfer_available, joined, profile_url, banned)
                    self.irc.send('PRIVMSG %s :%s\r\n' % (channel, message))
                except:
		    print sys.exc_info()
                    self.irc.send('PRIVMSG %s :User not found. \r\n' % channel)


            if re.search(r'^!(r|roll)[ ]', query) is not None:
                try:
                    dice_str = query.split(" ", 1)[1]
                    lower_bound, rest = dice_str.split("-")
                    if len(rest.split(" ")) > 1:
                        upper_bound, n = rest.split(" ")
                    else:
                        upper_bound = rest
                        n = 1
                    return_str = ''
                    n = int(n)
                    if n > 125:
                        return
                    while n > 0:
                        return_str += str(random.randrange(int(lower_bound), int(upper_bound)+1)) + ", "
                        n -= 1
                    nick = sender.split("!")[0]
                    return_str = return_str[:-1]  # removes final comma
                    self.irc.send("PRIVMSG %s :%s's roll(s) are %s\r\n" % (channel, nick, return_str[:-1]))
                except:
                    pass


            if re.search(r'^!(b |b$|btc|bitcoin)', query.lower()) is not None:
                try:
                    btc_str = query.split(" ", 1)[1]
                    url = 'https://api.bitcoinaverage.com/ticker/%s' % btc_str.strip().upper()
                    response = urllib2.urlopen(url, timeout=3)
                    json = simplejson.loads(response.read())
                    last_price = str(json['last'])
                    self.irc.send("PRIVMSG %s :last: %s\r\n" % (channel, last_price))
                except:
                    pass


            if re.search(r'^!(d|down)', query.lower()) is not None:
                try:
                    site_str = query.split()[1]
                    #print site_str
                    url = 'http://www.downforeveryoneorjustme.com/' + site_str
                    response = urllib2.urlopen(url, timeout = 5)
                    html = response.read()
                    if "It's just you." in html:
                        self.irc.send("PRIVMSG %s :%s is up!\r\n" % (channel, site_str))
                    if "It's not just you!" in html:
                        self.irc.send("PRIVMSG %s :%s is down!\r\n" % (channel, site_str))
                except:
                    pass


            if re.search(r'^!(t|tr|translate)[ ]', query) is not None:
                try:
                    translate_str = query.split(" ", 1)[1]
                    help_url = 'http://msdn.microsoft.com/en-us/library/hh456380.aspx'
                    help_str1 = 'PRIVMSG %s :!t <from language code> <to language code><text to be translated>\r\n' % channel
                    help_str2 = 'PRIVMSG %s :For language codes visit %s\r\n' % (channel, help_url)
                    if translate_str.strip().lower() == "help":
                        self.irc.send(help_str1)
                        self.irc.send(help_str2)
                        return

                    from_lang, rest  = translate_str.split(" ", 1)
                    to_lang, text = rest.split(" ", 1)
                    result = ''
                    try:
                        cmd = 'php translate.php "%s" "%s" "%s"' % (from_lang, to_lang, text)
                        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                        result = proc.stdout.read()
                    except:
                        if not result:
                            result = "Try !t help"
                    self.irc.send('PRIVMSG %s :%s\r\n' % (channel, result))
                except:
                    pass


            if re.search(r'^!(c|cleverbot)[ ]', query) is not None or\
               re.search(r'^moose(,|:| )', query) is not None:
                cleverbot_query = query.split(" ", 1)[1]
                try:
                    global CLEVERBOT
                    cleverbot_response = CLEVERBOT.Ask(cleverbot_query)
                    response = BeautifulSoup(cleverbot_response,
                                             convertEntities=BeautifulSoup.HTML_ENTITIES)
                    self.irc.send('PRIVMSG %s :%s\r\n' % (channel, response))
                except:
                    pass


            if re.search(r'^!(v|vhost)[ ]', query) is not None:
                vhost_query = query.split(" ", 1)[1]
                nick = sender.split("!")[0]
                if vhost_query.strip().lower() == 'help':
                    self.irc.send('PRIVMSG %s :To set a vhost for a registered nick, use the following command in a channel: !vhost <desired vhost>. Your vhost must have at least two dots and you must use the following command to activate it: /msg hostserv on\r\n' % nick)
                elif vhost_query.count('.') < 2:
                    self.irc.send('PRIVMSG %s :Your vhost must contain at least two dots.\r\n' % nick)
                else:
                    try:
                        self.irc.send('PRIVMSG HostServ set %s %s\r\n' % (nick, vhost_query))
                        self.irc.send('PRIVMSG %s :To activate, type /msg hostserv on\r\n' % nick)
                        self.irc.send('PRIVMSG %s :To deactivate, type /msg hostserv off\r\n' % nick)
                    except:
                        pass


            if re.search(r'^!barf[ ]', query) is not None: 
                barf_query = query.split(" ", 1)[1]
                modifiers = ['on', 'at', 'all over']
                modifier = random.choice(modifiers)
                barf_query = u"\u0001ACTION barfs %s %s\u0001" % (modifier, barf_query.strip())
                self.irc.send('PRIVMSG %s :%s\r\n' % (channel, barf_query))

            if re.search(r'^!tell[ ]', query) is not None and channel == "#subtlefuge":
                tell_query = query.split(" ", 1)[1]
                tell_nick, tell = tell_query.split(" ", 1)
                nick = sender.split("!")[0]
                tell_string = "%s wanted to tell %s: %s" % (nick, tell_nick, tell)
                tell_nick = tell_nick.lower()
                if tell_nick in TELL_DICT:
                    TELL_DICT[tell_nick] = TELL_DICT[tell_nick] + [tell_string]
                else:
                    TELL_DICT[tell_nick] = [tell_string]


#           if re.search(r'^!(wiki|wikipedia)[ ]', query) is not None:
#                wiki_query = query.split(' ', 1)[1].strip()
#               try:
#                    wiki_page = wikipedia.page(wiki_query)
#                    wiki_summary = wiki_page.summary.split('\n')[0].encode('ascii','ignore').strip()
#                    max_len = 460
#                   messages = int(math.ceil(len(wiki_summary) / max_len))
#                    for i in range(messages + 1):
#                        end = (i+1) * max_len
#                        if ((i+1) * max_len) > len(wiki_summary):
#                           end = len(wiki_summary)
#                        self.irc.send('PRIVMSG %s :%s\r\n' %\
#                                      (channel, wiki_summary[(i*max_len):end]))
#                        time.sleep(0.1)
#                except Exception as e:
#                    self.irc.send('PRIVMSG %s :Wikipedia page not found.\r\n' % (channel))


            if re.search(r'^!drug[ ]', query) is not None:

                try:
                    drug_query = query.split(' ', 1)[1].strip().lower()
                    drug_name, info_rq = drug_query.split(" ")
                    
                    if drug_name is not None:
                         drug_url = "http://nourishedcloud.com:1337/api/tripsit/getDrug?name="+drug_name
                         
                         response = urllib2.urlopen(drug_url)
                         json = response.read()
                         json = simplejson.loads(json)
                         return_str = "Couldn't parse"
                         
                         print response
                         if info_rq == 'dose':
                              return_str = json["data"][0]["properties"]["dose"]
                         if info_rq == 'categories':
                              return_str = json["data"][0]["categories"]
                         if info_rq == 'alias':
                              return_str = json["data"][0]["properties"]["aliases"]
                         if info_rq == 'effects':
                              return_str = json["data"][0]["formatted_effects"]
                         if info_rq == 'duration':
                              return_str = json["data"][0]["formatted_duration"]
                         if info_rq == 'onset':
                              return_str = json["data"][0]["formatted_onset"]
                    
                         self.irc.send('PRIVMSG %s :%s\r\n' % (channel, return_str))
                except Exception as e:
                    self.irc.send('PRIVMSG %s :Drug page not found. %s -- %s %s \r\n' % (channel, e.message, drug_name, info_rq))




            response_dict = {
                r'there is no need to be upset': 'http://i.imgur.com/I67XC.gif',
                r'maximum over-rustle': 'http://i.imgur.com/1Auof.gif',
                r'^people change': 'http://bit.ly/U7nCkn',
                r'^\.slap': 'no u',
                r"(flop|flops|stumble|stumbles) off to bed": "goodnight from everyone at the fuge :)",
                r"(night/nighty) night": "goodnight from everyone at the fuge :)",
                r"goes to bed\. nini": "goodnight from everyone at the fuge :)",
                r"^nini": "goodnight from everyone at the fuge :)",
                ur"\u0001action goes to bed": "goodnight from everyone at the fuge :)",
                r"^ihu$": "aw, you hug me. how nice... :)",
                r"^oaky\.$": "http://bit.ly/JBmsXu",
                r"oh noes": "http://bit.ly/LXjbEb",
                r"^no\.$": "http://i.imgur.com/bUUab.gif",
                r"^(!pb$|pb$|!pastebin|pastebin)": "http://hastebin.com http://pastebin.com http://pastee.org http://pastebin.ca http://crunchbanglinux.org/pastebin/ http://hpaste.org http://codepad.org ...use pastebins. dont flood.",
                r"^that's right.$": "http://blogfiles.wfmu.org/KF/2010/11/30/gif_clint_yes350.gif",
                r"^sweet bro": "http://i.imgur.com/7YEKN.gif",
                r"^well done.$": "http://i.imgur.com/JSBTl.gif",
                r"^(unclear\.|unclear)": "http://67.media.tumblr.com/9853f19c39b9480a844cdc973bfc3e84/tumblr_oejxgdqepC1sdv4q6o3_r1_500.gif",

                r"^(okay\.|oaky|okay|oaky\.) :c": "http://i.imgur.com/PlRh0.gif",
                r"(blew|blown) my mind": "http://i.imgur.com/D3lON.gif",
                r"^wat\.$": "http://bit.ly/wrjIkD",
                r"^\.\.\.\.$": "http://i.imgur.com/SmhCS.png",
                r"^soon\.": "http://bit.ly/MdCZEw",
                r"^yes\.$": "http://bit.ly/Jg1P4K",
                r"^slap\.": "http://bit.ly/JCpnzn",
                r"^!racist": "http://bit.ly/xA84Zr",
                r"^\:oo$": "http://bit.ly/KX24OV",
                r"^win\.": "http://bit.ly/Jxvupl",
                r"^derp\.": "http://www.youtube.com/watch?v=nQB4nAjZIdE",
                r"^both\.": "http://i.imgur.com/hXfBd.png",
                r"^good good\.": "http://bit.ly/Y9Cil8",
		r"^!pc": "http://i.imgur.com/7rw1Qwb.gifv",
                r"^you're awesome": "http://i.imgur.com/zXfZ4.gif",
                ur"\u0001action slowclaps": "http://gifs.gifbin.com/1233928590_citizen%20kane%20clapping.gif",
                r"^okay\.$": "http://i.imgur.com/UzTta.gif",
                r"^!morning": "http://i.imgur.com/gzLu5zU.png",
                r"^!got": "If all you ever do is all you've ever done, then all you'll ever get is all you ever got.",
                r"^!reality": "Everything is energy and that's all there is to it. Match the frequency of the reality you want and you cannot help but get that reality. It can be no other way. This is not philosophy. This is physics. - Albert Einstein.",
                r"^!bertolt": "https://joindiaspora.s3.amazonaws.com/uploads/images/scaled_full_9086f0662b7c01bacbd9.jpg",
                r"^!brecht": "https://joindiaspora.s3.amazonaws.com/uploads/images/scaled_full_9086f0662b7c01bacbd9.jpg",
                r"^!imbicile": "https://joindiaspora.s3.amazonaws.com/uploads/images/scaled_full_9086f0662b7c01bacbd9.jpg",
                r"^!bakunin": "We are convinced that freedom without Socialism is privilege and injustice, and that Socialism without freedom is slavery and brutality.-Mikhail Bakunin",
                r"^!accept": "People said I should accept the world. Bullshit! I don't accept the world. - Richard M. Stallman",
                r"^!politics": "Geeks like to think that they can ignore politics.  You can leave politics alone, but politics won't leave you alone. - Richard M. Stallman",
                r"^!win": "I am a pessimist by nature. Many people can only keep on fighting when they expect to win. I'm not like that, I always expect to lose. I fight anyway, and sometimes I win. - Richard M. Stallman",
                r"^askhole": "https://fbcdn-sphotos-f-a.akamaihd.net/hphotos-ak-snc7/394631_502427473120044_828805403_n.jpg",
                r"^tesla$": "http://www.wimp.com/nikolatesla/ http://www.funnyordie.com/videos/ef668caf14/drunk-history-vol-6-w-john-c-reilly-crispin-glover http://www.youtube.com/watch?v=VqhZDOXGiBQ http://archive.org/details/The-Eye-of-the-Storm_The-Inventions-of-Nikola-Tesla http://video.google.com/videoplay?docid=-5982928426839678882",
                r"^frog$": "http://i.imgur.com/ZHFfq.jpg",
                r"^!police": "http://25.media.tumblr.com/tumblr_lw5217efh71qg7xwvo1_500.jpg",
                r"^!beards": "http://bit.ly/X0SfVH",
                r"^!headcat": "http://bit.ly/XEXvy5",
                r"^shap\.$": "http://i.imgur.com/2eB0Eh.jpg",
                r"^hwat\.$": "http://i.imgur.com/4R51W.jpg",
                r"^nod\.$": "http://bit.ly/ToMn8e",
                r"calling bullshit": "http://bit.ly/WvFL9h",
                r"^srsly\.$": "http://bit.ly/V1ZQ9E",
                r"^nice\.\.\.$": "https://www.youtube.com/watch?v=kIfOjkB17BA",
                r"^are your jimmies rustled\?$": "https://www.youtube.com/watch?v=iGBVEpR_vdE",
                r"bro, do you even science": "http://bit.ly/WzMiS0",
                r"what the fuck am i reading": "http://bit.ly/zy2HVa",
                r"nopenopenope": "http://i.imgur.com/m1sge9O.gif",
                r"it's happening!": "http://bit.ly/YfA54b",
                r"^!bowl": "http://bit.ly/YS6n9m",
                r"what the fuck|what the fuck am i reading": "http://i.imgur.com/bpW6Xkd.gif",
                r"^magic\.": "http://bit.ly/SscKYH",
                r"^!fuck": "http://ompldr.org/vaTZldw/fuck.gif",
                r"^!ghandi": "First they ignore you, then they laugh at you, then they fight you, then you win.",
                r"^!dont": "http://bit.ly/1dgMqw6",
                r"^!casual": "http://bit.ly/15ixMEU",
                r"^!barf$": u"\u0001ACTION barfs\u0001",
                r"^!cream$": "http://bit.ly/1bsjgeu",
                r"^!joint": "http://bit.ly/1fUxMjE",
                r"^!moon": u"TO THE MOON \u2517(\u00B00\u00B0)\u251B".encode('utf-8'),
                r"^hold!": "http://i.imgur.com/DjLAsir.jpg",
                r"^!vape": "http://bit.ly/1eVKwrJ",
		r"^!lsd": "http://i.imgur.com/qUCEDAn.jpg",
                r"^10 years since sing strim": "i walk through the empty streets trying to think of something else but my path always leads to the stream. i stare at the screen for hours and try to summon the lord. i watch other asian girls streaming but it is no good. i flame dendi in his channel and try to resist the nazi mods but it is all meaningless. the end is near.i then usually watch some old sing vods and cry myself to sleep.",
               r"don't lose your way": "https://www.youtube.com/watch?v=uc7EcuqVhPE",
               r"!mako": "http://bit.ly/Quy8n4", 
               r"ship it": "http://i.imgur.com/Dxx4mOM.gif",
            }

            sent = 0
            for regexp, link in response_dict.iteritems():
                if query.lower().startswith('all my '):
                    query = query[7:]
                if re.search(regexp, query.lower()) is not None:
                    self.irc.send("PRIVMSG %s :%s\r\n" % (channel, link))
                    sent = 1
                    break

            query_after_space = "a^"
            query1 = query.lower().split()

            if sent == 0:
                if len(query1) > 1:
                    query_after_space = " ".join(query1[1:])
                    if query1[0][-1] == ":" or query1[0][-1] == ",":
                        for regexp, link in response_dict.iteritems():
                            if re.search(regexp, query_after_space) is not None:
                                self.irc.send("PRIVMSG %s :%s\r\n" % (channel, link))


            if re.search(r'^!responses', query) is not None:
                self.irc.send('PRIVMSG %s :This is a dump of my response dictionary. Keys are python regular expressions and the values are my responses that match said regexps. Note that only the first key to match the regexp will return its response.\r\n' % nick)
                for key, val in response_dict.iteritems():
                    self.irc.send('PRIVMSG %s : %s: %s\r\n' % (nick, key, val))


            urls = re.findall('https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', query)
            for url in urls:
		if url == "https://reddit.com/r/forhire/new":
                    return

                content_length = 0
                try:
                    headers_ = { 'User-Agent' : 'Mozilla/5.0' }
                    req = urllib2.Request(url, headers=headers_)
                    response = urllib2.urlopen(req, timeout=3)
                except:
                    return
                try:
                    content_length = response.headers['content-length']
                    #print "Content length =", content_length
                except: pass

                try:
                    maxlength = 2 * 1024 * 1024  # 2 Megabytes
                    if content_length != 0 and content_length < maxlength:
                       maxlength = content_length 
                    html = response.read(maxlength+1)
                    soup = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)
                    title_block = soup.find('title')
                    if title_block:
                        title = title_block.renderContents().strip()
                        if title:
                            title = title.replace("\n", " ")
                            self.irc.send('PRIVMSG %s :[ %s ]\r\n' % (channel, title))
                            params = urlencode({"full_url": url, "title": title})
                            urllib2.urlopen("http://fuge.it/link/IRC_Add?%s" % params, timeout=3)
                except:
                    try:
                        maxlength = 2 * 1024 * 1024  # 2 Megabytes
                        if content_length != 0 and content_length < maxlength:
                            maxlength = content_length
                        title0 = response.read(maxlength+1).split('<title>')[1].split('</title>')[0].strip()
                        if title0:
                            title0 = title0.replace("\n", " ")
                            self.irc.send('PRIVMSG %s :[ %s ]\r\n' % (channel, title0))
                            params = urlencode({"full_url": url, "title": title0})
                            urllib2.urlopen("http://fuge.it/link/IRC_Add?%s" % params, timeout=3)

                    except: pass


    def get_command(self):

        if len(self.command_list) > 0:
            result = self.command_list.pop(0)
            return result

        # There is no command available, we read more bytes.
        chunk = self.irc.recv(4096)
        self.data_buffer = ''.join([self.data_buffer, chunk])

        self.command_list = self.data_buffer.split('\r\n')
        self.data_buffer = self.command_list.pop()
        if len(self.command_list) == 0:
            return None

        result = self.command_list.pop(0)
        return result

    def main(self):

        self.connect_to_server()
        self.init()
        count = 0
        while count < 20:
            com = self.get_command()
            while com is None:
                com = self.get_command()
            print "com: ", com

            self.parse_command(com)
            if self.quit_bot == True:
                break
            count += 1

        self.irc.send('PRIVMSG NickServ IDENTIFY joker1\r\n')
        self.irc.send('OPER dfoolz fuckyou.\r\n')
        self.irc.send('SAJOIN dangler #dev\r\n')
        #self.irc.send('SAJOIN dangler #notifications\r\n')
        self.irc.send('SAJOIN dangler #subtlefuge\r\n')


        while True:

            com = self.get_command()

            while com is None:
                com = self.get_command()

            #print "com: ", com
            self.parse_command(com)


if __name__ == '__main__':
    myBot = Bot()
    myBot.main()
