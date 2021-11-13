#!/usr/bin/env python

import sys
import urllib2
import urllib
import httplib
from xml.etree import ElementTree as etree

class wolfram(object):
    def __init__(self, appid):
        self.appid = appid
        self.base_url = 'http://api.wolframalpha.com/v2/query?'
        self.headers = {'User-Agent':None}

    def _get_xml(self, ip):
        url_params = {'input':ip, 'appid':self.appid}
        data = urllib.urlencode(url_params)
        req = urllib2.Request(self.base_url, data, self.headers)
        xml = urllib2.urlopen(req).read()
        return xml

    def _xmlparser(self, xml):
        data_dics = {}
        tree = etree.fromstring(xml)
        #retrieving every tag with label 'plaintext'
        for e in tree.findall('pod'):
            for item in [ef for ef in list(e) if ef.tag=='subpod']:
                for it in [i for i in list(item) if i.tag=='plaintext']:
                    if it.tag=='plaintext':
                        data_dics[e.get('title')] = it.text
        return data_dics

    def search(self, ip):
        xml = self._get_xml(ip)
        result_dics = self._xmlparser(xml)
        #return result_dics
        results = []
        if 'Result' in result_dics:
            results.append(result_dics['Result'].encode('ascii', 'ignore'))
        if 'Decimal approximation' in result_dics:
            results.append(result_dics['Decimal approximation'].encode('ascii', 'ignore'))
        if 'Solution' in result_dics:
            results.append(result_dics['Solution'].encode('ascii', 'ignore'))
        if 'Solutions' in result_dics:
            results.append(result_dics['Solutions'].encode('ascii', 'ignore'))
        if 'Derivative' in result_dics:
            results.append(result_dics['Derivative'].encode('ascii', 'ignore'))
        if 'Indefinite integral' in result_dics:
            results.append(result_dics['Indefinite integral'].encode('ascii', 'ignore'))
        if 'Exact result' in result_dics:
            results.append(result_dics['Exact result'].encode('ascii', 'ignore'))
        if 'Decimal form' in result_dics:
            results.append(result_dics['Decimal form'].encode('ascii', 'ignore'))
        print "\n".join(results)
        #print result_dics

if __name__ == "__main__":
    appid = sys.argv[1]
    #print appid
    query = sys.argv[2]
    #print query
    w = wolfram(appid)
    w.search(query)
