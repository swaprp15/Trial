# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    
    session.hotelPhotos = []
    session.hotelIds = []
    query = db.Advertisement.hotel_id == 1
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(1)

    response.flash=''

    query = db.Advertisement.hotel_id == 2
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(2)
    
    query = db.Advertisement.hotel_id == 3
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(3)
    
    query = db.Advertisement.hotel_id == 4
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(4)
    

    response.flash = T("Welcome CafeHunt!")
    form=FORM(INPUT(_name='keyword', requiures=IS_NOT_EMPTY(), _placeholder='Please enter hotel name'), INPUT(_type='submit', _value='Search'))
    #if form.process().accepted:
    #    if form.accepts(request,session):
    #       redirect(URL('search', args=[form.vars.keyword]))
    ##    redirect(URL('search'))

    if form.accepts(request,session):
        redirect(URL('search', vars=dict(key=form.vars.keyword)))


    if request.args != []:
        if request.args[0] == 'changeCity':
            # check if this city is available..
            cityQuery=db.Hotel_Info.city == request.args[1]
            cityPresent=db(cityQuery).select(db.Hotel_Info.city)
            if len(cityPresent) >= 1:
                session.city = request.args[1]

    response.menu = [
    (T('Home'), False, URL('default', 'index'), [])]

    query = db.Hotel_Info.id > 0

    cities = db(query).select(db.Hotel_Info.city, distinct=True)

    menuList = []

    for city in cities:
        t = (T(city.city), False, URL('index', args=['changeCity', city.city]))
        menuList.append(t)

    L = [
        (T('Hyderabad'), False, URL('index', args=['changeCity', 'Hyderabad'])),
        (T('Pune'), False, URL('index', args=['changeCity', 'Pune'])),
        (T('Mumbai'), False, URL('index', args=['changeCity', 'Mumbai']))]

    response.menu += [
        (SPAN(session.city, _class='highlighted'), False, URL('index'), menuList)]

    response.menu += [(SPAN('Add', _class='highlighted'), False, URL('index'), [
        (T('Hotel'), False, URL('addHotel'))])]

    if len(request.vars) != 0:
        response.flash=request.vars['flash']
        
    return dict(message=T('Welcome to CafeHunt!!'), form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def search():

    # if normal flow
    if len(request.args) == 0:

        if len(request.vars) == 0:
            redirect(URL('index'))

        # add a city filter here
        query=(db.Hotel_Info.name.contains(request.vars['key']) & (db.Hotel_Info.city == session.city))

        hotels = db(query).select(db.Hotel_Info.ALL)

        #response.flash = len(hotels)

        if len(hotels) == 0:
            response.flash = 'Sorry no hotels found of your interest in city ' + session.city

            redirect(URL('search', args=['noresult'], vars=dict(key=request.vars['key'])))



        # Add few recommondations

        query = ((db.Hotel_Info.overall_rating >= 4.0) & (db.Hotel_Info.city == session.city))

        recommondations = db(query).select(db.Hotel_Info.ALL)

        recommondationMessage='Our recommondations for you:'

        return dict(content=hotels, recommondations=recommondations, recommondationMessage=recommondationMessage)
    else:
        # if earlier no results were found, do this is a new page... /search/noresult

        newSearchForm=FORM(INPUT(_name='keyword', requiures=IS_NOT_EMPTY(), _placeholder='Please enter hotel name'), INPUT(_type='submit', _value='Search'))
        #if form.process().accepted:
        #    if form.accepts(request,session):
        #       redirect(URL('search', args=[form.vars.keyword]))
        ##    redirect(URL('search'))

        if newSearchForm.accepts(request,session):
            redirect(URL('search', vars=dict(key=newSearchForm.vars.keyword)))

        hotels = []

        query = ((db.Hotel_Info.overall_rating >= 4.0) & (db.Hotel_Info.city == session.city))

        recommondations = db(query).select(db.Hotel_Info.ALL)


        recommondationMessage='Or you may try our recommondations:'

        return dict(content=hotels, newSearchForm=newSearchForm, recommondations=recommondations, recommondationMessage=recommondationMessage)
        pass


@auth.requires_login()
def details():

    #if adding a review
    # /addReview/hotel_id

    session.hotel_id = request.args[0]

    #addReviewForm=FORM(INPUT(_name='description', requiures=IS_NOT_EMPTY(), _placeholder='What\'s your opinion?'), INPUT(_type='submit', _value='Post it..'), INPUT(_type='reset', _value='reset'))

    addReviewForm=SQLFORM(db.Review, fields=['rating', 'description'], submit_button='Post')

    import datetime

    #if addReviewForm.accepts(request,session):
    #    # /addReview/hotel_id
    #    db.Review.insert(user_id=auth.user_id, hotel_id=session.hotel_id, rating=addReviewForm.vars.rating, time_of_post=datetime.datetime.now(), description=addReviewForm.vars.description)
    #
    #   redirect(URL('details', args=[session.hotel_id]))
    
    if addReviewForm.process().accepted:
        # Add this review...
        db.Review.insert(user_id=auth.user_id, hotel_id=session.hotel_id, rating=addReviewForm.vars.rating, time_of_post=datetime.datetime.now(), description=addReviewForm.vars.description)

        # Update the overall rating of this hotel.
        row = db(db.Hotel_Info.id == session.hotel_id).select(db.Hotel_Info.overall_rating, db.Hotel_Info.no_of_reviewes)
        currentRating = row[0].overall_rating
        currentNoOfReviews = row[0].no_of_reviewes

        import decimal

        #getcontext().prec = 1

        newNoOfReviews = currentNoOfReviews + 1
        newRating = (currentRating + int(addReviewForm.vars.rating)/1.0)/newNoOfReviews

        db(db.Hotel_Info.id == session.hotel_id).update(overall_rating=newRating, no_of_reviewes=newNoOfReviews)

        redirect(URL('details', args=[session.hotel_id]))
    elif addReviewForm.errors:
        redirect(URL('details', args=[session.hotel_id], vars=dict(flash='Please correct the errors')))

    query=db.Hotel_Info.id == request.args[0]
    hotels = db(query).select()
    if len(hotels) == 0:
        hotels = ['Sorry, details are not available...']

    query=((db.Review.hotel_id == session.hotel_id) & (db.Review.user_id == db.auth_user.id))
    reviews = db(query).select()
    if len(reviews) == 0:
        reviews = []


    # Get photos if any

    query = db.Hotel_Photos.hotel_id == session.hotel_id

    images = db(query).select(db.Hotel_Photos.photo)

    query = db.Hotel_MenuCard.hotel_id == session.hotel_id

    menus = db(query).select(db.Hotel_MenuCard.menu)

    session.hotel_name = hotels[0].name
    session.hotel_address = hotels[0].address
    session.rating = hotels[0].overall_rating
    session.hotel_cost = hotels[0].costPerTwo
    session.hotel_hours = hotels[0].hours
    session.url = request.url

    return dict(details=hotels[0], reviews=reviews, addReviewForm=addReviewForm, images=images, menus=menus)

def userDetails():
    userId = request.args[0]

    query = ((db.Review.user_id == userId) & (db.Review.hotel_id == db.Hotel_Info.id))

    userReviews = db(query).select(db.Hotel_Info.name, db.Review.hotel_id, db.Review.description, db.Review.rating)

    query = db.auth_user.id == userId

    userInfo = db(query).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.photo)

    return dict(userReviews=userReviews, id=userInfo[0].id, fname=userInfo[0].first_name, lname=userInfo[0].last_name, photo=userInfo[0].photo)

#@auth.requires_membership('moderator')
def addHotel():

    if not auth.has_membership('moderator'):
        response.flash='Only moderators can add a new hotel information'
        redirect(URL('index', vars=dict(flash='Only moderators can add a new hotel information')))

    newHotelForm = SQLFORM(db.Hotel_Info)
    if newHotelForm.process().accepted:
        response.flash = 'New hotel added'
    elif newHotelForm.errors:
        response.flash = 'Please correct the errors'
    else:
        response.flash = 'Please fill out the form'
    return dict(newHotelForm=newHotelForm)    

@auth.requires_membership('moderator')
def deleteReview():
    #/deleteReview/hotel_id/review_id
    # delete review
    if len(request.args) > 1 :
        reviewRating = db(db.Review.id == request.args[1]).select(db.Review.rating)
        db(db.Review.id == request.args[1]).delete()

        # Update the overall rating of this hotel.
        row = db(db.Hotel_Info.id == request.args[0]).select(db.Hotel_Info.overall_rating, db.Hotel_Info.no_of_reviewes)
        currentRating = row[0].overall_rating
        currentNoOfReviews = row[0].no_of_reviewes

        import decimal

        newNoOfReviews = currentNoOfReviews - 1
        if newNoOfReviews == 0:
            newRating = 0
        else:
            newRating = (currentRating - int(reviewRating)/1.0)/newNoOfReviews

        db(db.Hotel_Info.id == session.hotel_id).update(overall_rating=newRating, no_of_reviewes=newNoOfReviews)

        redirect(URL('details', args=[request.args[0]]))
    elif len(request.args == 1):
        redirect(URL('details', args=[request.args[0]]))
    else:
        request(URL('index'))

@auth.requires_membership('moderator')
def editReview():
    #/deleteReview/hotel_id/review_id
    if len(request.args) > 1 :
        crud.settings.update_next = URL('details', args=[request.args[0]])
        crud.messages.submit_button = 'Update'
        editForm=crud.update(db.Review, request.args[1], fields=['rating', 'description'])
        #redirect(URL('details', args=[request.args[0]]))
        return dict(editForm=editForm)
    elif len(request.args == 1):
        redirect(URL('details', args=[request.args[0]]))
    else:
        request(URL('index'))

@auth.requires_membership('moderator')
def makeModerator():
    
    #makeModerator/user_id
    if len(request.args) > 0 :
        response.flash = request.args[0]
        auth.add_membership('moderator', int(request.args[0]))
        redirect(URL('userDetails', args=[request.args[0]]))
    else:
        request(URL('index'))

def sendMail():
    mailForm = FORM('Send this info via e-mail:',
                    INPUT(_name='To', requiures=IS_EMAIL()),
                    INPUT(_name='Subject', requiures=IS_NOT_EMPTY()),
                    INPUT(_name='Body', requiures=IS_NOT_EMPTY()),
                    INPUT(_type='submit'),
                    submit_button='Send')

    mailForm.vars.Subject = 'Hotel information - ' + session.hotel_name
    mailForm.vars.Body = session.hotel_name + '\n' + session.hotel_address + '\n' + str(session.rating) + '\n' + str(session.hotel_cost) + '\n' + session.hotel_hours + '\n' + 'http://127.0.0.1:8000' + session.url 

    htmlbody = '<html><p><b>Name: ' + session.hotel_name + '</b>\r\n</br></p><p><b>Address:</b> '+session.hotel_address + '</br></p><p><b>Rating: </b>' + str(session.rating) + '</br></p><p><b>Cost per 2 :</b> ' + str(session.hotel_cost) + '</br></p><p><b>Timings: </b> ' + session.hotel_hours + '</br></p><p>For details please visit ' + 'http://127.0.0.1:8000' + session.url + '</p></html>'


    if mailForm.accepts(request,session):
        #mail.send(to=[mailForm.vars.To], subject=mailForm.vars.Subject, reply_to='swap.andro24@gmail.com', message=mailForm.vars.Body)
        mail.send(to=[mailForm.vars.To], subject=mailForm.vars.Subject, reply_to='contactus@cafehunt.com', message=htmlbody)
        redirect(URL('details', args=[session.hotel_id]))
    

    return dict(mailForm=mailForm)

def addHotelPhoto():

    if len(request) <= 0:
        redirect('index')

    hotelId = request.args[0];

    photoForm = SQLFORM(db.Hotel_Photos, fields=['photo'], submit_button='Upload')
    photoForm.vars.hotel_id = request.args[0]
    if photoForm.process().accepted:
        response.flash = 'New photo added'

        #db.Hotel_Photos.insert(hotel_id=hotelId, photo=photoForm.vars.photo)

    elif photoForm.errors:
        response.flash = 'Please correct the errors'
    else:
        response.flash = 'Please fill out the form'
    return dict(photoForm=photoForm)


def addHotelMenu():
    if len(request) <= 0:
        redirect('index')

    hotelId = request.args[0];

    menuForm = SQLFORM(db.Hotel_MenuCard, fields=['menu'], submit_button='Upload')
    menuForm.vars.hotel_id = request.args[0]
    if menuForm.process().accepted:
        response.flash = 'New photo added'

        #db.Hotel_Photos.insert(hotel_id=hotelId, photo=photoForm.vars.photo)

    elif menuForm.errors:
        response.flash = 'Please correct the errors'
    else:
        response.flash = 'Please fill out the form'
    return dict(menuForm=menuForm)

def incrClicks():
    hotelId = request.args[0]
    
    # db query to increment click of this hotel id
    query = db.Advertisement.hotel_id == hotelId
    clicksRow= db(query).select(db.Advertisement.clicks)[0]
    nclicks= int(clicksRow.clicks) + 1
    db(db.Advertisement.hotel_id==hotelId).update(clicks=nclicks)
    # redirect to original page
    redirect(URL('details', args=[request.args[0]]))