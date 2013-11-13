# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('CafeHunt'),XML('&trade;&nbsp;'),
                  _class="brand",_href=URL('index'))
response.title = 'CafeHunt'
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller

    #response.menu += [(T('City'), False, URL('default', 'index'), [])]

    # useful links to internal and external resources

    response.flash=session.city

    #if(session.city != 'Pune' and session.city != 'Hyderabad'):
    #session.city = 'Hyderabad'

    if session.city == None:
        session.city = 'Hyderabad'

    response.menu += [
        (SPAN(session.city, _class='highlighted'), False, URL('index'), [
        (T('Hyderabad'), False, URL('index', args=['changeCity', 'Hyderabad'])),
        (T('Pune'), False, URL('index', args=['changeCity', 'Pune'])),
        (T('Mumbai'), False, URL('index', args=['changeCity', 'Mumbai']))])]

    response.menu += [(SPAN('Add', _class='highlighted'), False, URL('index'), [
        (T('Hotel'), False, URL('addHotel'))])]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
