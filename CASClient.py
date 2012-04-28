import sys, os, cgi, urllib, re
from flask import Flask, request, render_template, make_response, redirect

class CASClient:

    def __init__(self, url='https://fed.princeton.edu/cas/'):
        self.cas_url = url

    def Authenticate(self, ticket):
        # If the request contains a login ticket, try to validate it
        if ticket != "":
            netid = self.Validate(ticket)
            if netid != None:
                return netid
        # No valid ticket; redirect the browser to the login page to get one
        login_url = self.cas_url + 'login' + '?service=' + self.ServiceURL()
        response = redirect(login_url, code=307)
        return response

    def Validate(self, ticket):
        val_url = self.cas_url + "validate" + \
            '?service=' + urllib.quote(self.ServiceURL()) + \
            '&ticket=' + urllib.quote(ticket)
        r = urllib.urlopen(val_url).readlines()    # returns 2 lines
        if len(r) == 2 and re.match("yes", r[0]) != None:
            return r[1].strip()
        return None

    def ServiceURL(self):
        return "http://istreetsvr.herokuapp.com/login"
        
def main():
    print "CASClient does not run standalone"

if __name__ == '__main__':
    main()
