#################################################################################
# usage of the script
# usage: python search-terms.py -k APIKEY -v VERSION -s STRING
# see https://documentation.uts.nlm.nih.gov/rest/search/index.html for full docs
# on the /search endpoint
#################################################################################

from __future__ import print_function
from Authentication import *
import requests
import json
import argparse

'''
parser = argparse.ArgumentParser(description='process user given parameters')
#parser.add_argument("-u", "--username", required =  True, dest="username", help = "enter username")
#parser.add_argument("-p", "--password", required =  True, dest="password", help = "enter passowrd")
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-s", "--string", required =  True, dest="string", help = "enter a search term, like 'diabetic foot'")
'''
'''
args = parser.parse_args()
#username = args.username
#password = args.password
apikey = args.apikey
version = args.version
string = args.string
'''

class search_terms:
    def __init__(self, apikey, version = 'current'):
        self.version = version
        self.apikey = apikey
        
    def search(self,input):
        uri = "https://uts-ws.nlm.nih.gov"
        content_endpoint = "/rest/search/"+self.version
        ##get at ticket granting ticket for the session
        AuthClient = Authentication(self.apikey)
        tgt = AuthClient.gettgt()
        #pageNumber=0
        
        ##generate a new service ticket for each page if needed
        ticket = AuthClient.getst(tgt)
        #pageNumber += 1
        #query = {'string':input,'ticket':ticket, 'pageNumber':pageNumber}
        query = {'string':input,'ticket':ticket}
        #query['includeObsolete'] = 'true'
        #query['includeSuppressible'] = 'true'
        #query['returnIdType'] = "sourceConcept"
        #query['sabs'] = "SNOMEDCT_US"
        r = requests.get(uri+content_endpoint,params=query)
        r.encoding = 'utf-8'
        items  = json.loads(r.text)
        self.jsonData = items["result"]
        #print (json.dumps(items, indent = 4))
        
        
    def printresult(self):
        #print("Results for page " + str(pageNumber)+"\n")
        print("\n")
        print("*********")
        
        for result in self.jsonData["results"]:
            
            try:
                print("ui: " + result["ui"])
            except:
                NameError
            try:
                print("uri: " + result["uri"])
            except:
                NameError
            try:
                print("name: " + result["name"])
            except:
                NameError
            try:
                print("Source Vocabulary: " + result["rootSource"])
            except:
                NameError
            
            print("\n")
            
        
        ##Either our search returned nothing, or we're at the end
        #if jsonData["results"][0]["ui"] == "NONE":
        #   break
        print("*********")
    
    def ifumls(self):
        if self.jsonData["results"][0]["ui"] == "NONE" or self.jsonData["results"][0]["name"] == "NO RESULT":
            return 0
        else:
            return 1

        
def main():
    #apikey = input("input your api >")
    apikey = '81602583-1f6f-400a-a49f-618975025bec'
    searchterms = search_terms(apikey)
    string = input("search > ")
    searchterms.search(string)
    searchterms.printresult()
    #print(searchterms.ifumls())
    
    
if __name__ == '__main__':
    main()
    




    