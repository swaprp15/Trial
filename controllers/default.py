# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import random

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    response.title = 'Welcome to CafeHunt!'
    
    session.hotelPhotos = []
    session.hotelIds = []
    
    row = db(db.Advertisement.hotel_id!=None).select()
    numOfAds=len(row)
    adId=[]
        
    while len(adId) < 4 and len(adId)<numOfAds:
	j=0
	flag=False
	 
	num=random.randint(1,numOfAds)
	query = db.Advertisement.id == num
	print num 	
	"""if not db(query).select(db.Advertisement.id)[0]:"""
	res = db(query).select(db.Advertisement.id)
	
	while len(res) == 0:
            num=random.randint(1,numOfAds)
            query = db.Advertisement.id == num
	       
            res = db(query).select(db.Advertisement.id)
	
			     
	while j < len(adId):
		flag=False
		
		if len(adId) == j:
			break;
			
		if num==adId[j]:
			j=0
			
			num=random.randint(1,numOfAds)
			query = db.Advertisement.id == num
			
			while len(res) == 0:
				num=random.randint(1,numOfAds)
				query = db.Advertisement.id == num
				res = db(query).select(db.Advertisement.id)
							
			flag=True
		else:
				
			j=j+1
	
	if flag==False:
			adId.append(num)
     
    print adId
        
    query = db.Advertisement.id == adId[0]
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(db(query).select(db.Advertisement.hotel_id)[0].hotel_id)

    response.flash=''
    session.showFlash = False

    query = db.Advertisement.id == adId[1]
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(db(query).select(db.Advertisement.hotel_id)[0].hotel_id)
    
    query = db.Advertisement.id == adId[2]
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(db(query).select(db.Advertisement.hotel_id)[0].hotel_id)
    
    query = db.Advertisement.id == adId[3]
    session.hotelPhotos.append(db(query).select(db.Advertisement.banner)[0])
    session.hotelIds.append(db(query).select(db.Advertisement.hotel_id)[0].hotel_id)
    

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

        query = ((db.Hotel_Info.city == session.city))

        records = db(query).select(db.Hotel_Info.ALL, orderby=~db.Hotel_Info.overall_rating)

        i=0

        recommondations = []

        for record in records:
            if i > 3:
                break
            recommondations.append(record)
            i += 1 

        recommondationMessage='Our recommondations for you:'

        return dict(content=hotels, recommondations=recommondations, recommondationMessage=recommondationMessage)
    elif request.args[0] == 'noresult':
        # if earlier no results were found, do this is a new page... /search/noresult

        newSearchForm=FORM(INPUT(_name='keyword', requiures=IS_NOT_EMPTY(), _placeholder='Please enter hotel name'), INPUT(_type='submit', _value='Search'))
        #if form.process().accepted:
        #    if form.accepts(request,session):
        #       redirect(URL('search', args=[form.vars.keyword]))
        ##    redirect(URL('search'))

        if newSearchForm.accepts(request,session):
            redirect(URL('search', vars=dict(key=newSearchForm.vars.keyword)))

        hotels = []

        query = ((db.Hotel_Info.city == session.city))

        records = db(query).select(db.Hotel_Info.ALL)

        recommondations = []

        i = 0

        for record in records:
            if i > 3:
                break
            recommondations.append(record)
            i += 1

        recommondationMessage='Or you may try our recommondations:'

        return dict(content=hotels, newSearchForm=newSearchForm, recommondations=recommondations, recommondationMessage=recommondationMessage)
        pass
    elif request.args[0] == 'advancedSearch':
        # We have a dictionary here

        
        '''
        keywords = request.vars
        keys = request.vars.keys()

        if ('cost' not in keys) or  ('rating' not in keys) or (keywords['costValue'] == '') or (keywords['ratingValue'] == '') :
            message = 'At least provide preferences for cost and rating'
            redirect(URL('advancedSearch', vars={'flash':'At least provide preferences for cost and rating'}))

        try:
            val = int(keywords['costValue'])
            val = int(keywords['ratingValue'])
        except ValueError:
            redirect(URL('advancedSearch', vars={'flash':'Please provide numeric value for cost and rating'}))

        if int(keywords['costValue']) < 0 or int(keywords['ratingValue']) < 0:
            redirect(URL('advancedSearch', vars={'flash':'Please provide non-negative for cost and rating'}))

        '''

        hotel_locality=session.advancedSearch['hotel_locality']
        type_of_food=session.advancedSearch['type_of_food']

        if 'cost' not in session.advancedSearch.keys():
            cost = ''
            costValue = ''
        else:
            cost=session.advancedSearch['cost']
            costValue=session.advancedSearch['costValue']
        
        if 'rating' not in session.advancedSearch.keys():
            rating = ''
            ratingValue=''
        else:
            rating=session.advancedSearch['rating']
            ratingValue=session.advancedSearch['ratingValue']
        

        #(hotel_locality in str(db.Hotel_Info.address)) & (str(db.Hotel_Info.type_of_food).find(type_of_food) != -1) &
        
        hotelsIdsWithReqCriteria = []

        if cost != '' and costValue != '':
            if cost == 'lesser':
                query=((db.Hotel_Info.costPerTwo < float(costValue)) & (db.Hotel_Info.city == session.city))
            else:
                query=((db.Hotel_Info.costPerTwo >= float(costValue)) & (db.Hotel_Info.city == session.city))

            rows = db(query).select(db.Hotel_Info.id)

            for row in rows:
                hotelsIdsWithReqCriteria.append(row.id)


        if rating != '' and ratingValue != '':
            if rating == 'lesser':
                query=((db.Hotel_Info.overall_rating < float(ratingValue)) & (db.Hotel_Info.city == session.city))
            else:
                query=((db.Hotel_Info.overall_rating >= float(ratingValue)) & (db.Hotel_Info.city == session.city))

            rows = db(query).select(db.Hotel_Info.id)

            for row in rows:
                hotelsIdsWithReqCriteria.append(row.id)


        
        if hotel_locality != '':
            rows = db(db.Hotel_Info.id > 0).select(db.Hotel_Info.id, db.Hotel_Info.address)

            for row in rows:
                if row.address.lower().find(hotel_locality.lower()) != -1:
                    hotelsIdsWithReqCriteria.append(row.id)


        #addresses = db(db.Hotel_Info.id in hotelsWithRequiredCostAndRating).select(db.Hotel_Info.address, db.Hotel_Info.id)

        if type_of_food != '':
            rows = db(db.Hotel_Info.id > 0).select(db.Hotel_Info.id, db.Hotel_Info.type_of_food)

            for row in rows:
                if row.type_of_food.lower().find(type_of_food.lower()) != -1:
                    hotelsIdsWithReqCriteria.append(row.id)

        #response.flash = len(hotels)

        '''

        hotels = []

        query=(((db.Hotel_Info.costPerTwo < float(costValue)) | (db.Hotel_Info.overall_rating < float(ratingValue))) & (db.Hotel_Info.city == session.city))

        result = db(query).select(db.Hotel_Info.id)

        for item in result:
            hotels.append(item.id)

        '''

        hotels = []

        if len(hotelsIdsWithReqCriteria) == 0:
            response.flash = 'Sorry no hotels found of your interest in city ' + session.city

            redirect(URL('search', args=['noresult'], vars=dict(key=request.vars['key'])))
        else:
            for hotel_id in hotelsIdsWithReqCriteria:
                rows = db(db.Hotel_Info.id == hotel_id).select()

                if len(rows) > 0:
                    hotels.append(rows[0])

        return dict(content=hotels, recommondations=[])


@auth.requires_login()
def details():

    #if adding a review
    # /addReview/hotel_id

    session.hotel_id = request.args[0]

    query = ((db.Review.user_id == auth.user_id) & (db.Review.hotel_id == session.hotel_id))

    result = db(query).select(db.Review.id)

    alreadySubmittedAReview = False

    if len(result) > 0:
        alreadySubmittedAReview = True



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
        newRating = (currentRating*currentNoOfReviews + int(addReviewForm.vars.rating)/1.0)/newNoOfReviews

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

    return dict(details=hotels[0], reviews=reviews, addReviewForm=addReviewForm, images=images, menus=menus, alreadySubmittedAReview=alreadySubmittedAReview)

def userDetails():
    userId = request.args[0]

    query = ((db.Review.user_id == userId) & (db.Review.hotel_id == db.Hotel_Info.id))

    userReviews = db(query).select(db.Hotel_Info.name, db.Review.hotel_id, db.Review.description, db.Review.rating, db.Review.time_of_post, db.Review.id, db.Review.user_id)

    query = db.auth_user.id == userId

    userInfo = db(query).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.photo)

    return dict(userReviews=userReviews, id=userInfo[0].id, fname=userInfo[0].first_name, lname=userInfo[0].last_name, photo=userInfo[0].photo)

#@auth.requires_membership('moderator')
def addHotel():

    response.flash = ''

    if not auth.has_membership('moderator'):
        response.flash='Only moderators can add a new hotel information'
        session.showFlash=True
        redirect(URL('index', vars=dict(flash='Only moderators can add a new hotel information')))

    newHotelForm = SQLFORM(db.Hotel_Info)
    if newHotelForm.process().accepted:
        response.flash = 'New hotel added'
    elif newHotelForm.errors:
        response.flash = 'Please correct the errors'
    else:
        response.flash = 'Please fill out the form'
    return dict(newHotelForm=newHotelForm)    

#@auth.requires_membership('moderator')
def deleteReview():

    #/deleteReview/hotel_id/review_id
    # delete review
    if len(request.args) > 1 :
        reviewRating = db(db.Review.id == request.args[1]).select(db.Review.rating, db.Review.user_id)

        #No record found
        if len(reviewRating) <= 0:
            if len(request.args) == 2:
                redirect(URL('details', args=[request.args[0]]))
            else:
                redirect(URL('index'))


        # Before deleting check if the id is same as currently loggen in user or is moderator
        
        if ((auth.user_id != reviewRating[0].user_id) and (not auth.has_membership('moderator'))):
            if len(request.args) == 2:
                redirect(URL('details', args=[request.args[0]]))
            else:
                redirect(URL('index'))

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
            newRating = (currentRating*currentNoOfReviews - int(reviewRating[0].rating)/1.0)/newNoOfReviews

        if newRating < 0:
            newRating = 0;

        db(db.Hotel_Info.id == session.hotel_id).update(overall_rating=newRating, no_of_reviewes=newNoOfReviews)

        #if len(request.vars) > 0 and 'redirect' in request.vars.keys() and request.vars['redirect'] == True:
        #    pass
        #else:

        if request.vars['redirect'] == 'False':  
            redirect(session.last_url)
        else:
            redirect(URL('details', args=[request.args[0]]))
    elif len(request.args) == 1:
        redirect(URL('details', args=[request.args[0]]))
    else:
        redirect(URL('index'))

#@auth.requires_membership('moderator')
def editReview():
    #/deleteReview/hotel_id/review_id
    if len(request.args) > 1 :
        crud.settings.update_next = URL('details', args=[request.args[0]])
        crud.messages.submit_button = 'Update'


        # First get the user id of this review...
        review = db(db.Review.id == request.args[1]).select(db.Review.user_id)

        # Check if record does exists.
        if len(review) <= 0:
            if len(request.args) == 2:
                redirect(URL('details', args=[request.args[0]]))
            else:
                redirect(URL('index'))

        # Before updating check if the id is same as currently loggen in user or is moderator
        if ((auth.user_id != review[0].user_id) and (not auth.has_membership('moderator'))):
            if len(request.args) == 2:
                redirect(URL('details', args=[request.args[0]]))
            else:
                redirect(URL('index'))


        query = db.Review.id == request.args[1]
        reviewDetails = db(query).select(db.Review.rating, db.Review.description, db.Review.hotel_id)

        if len(reviewDetails) <= 0:
            redirect(URL('details', args=[request.args[0]]))

        hotel_id = reviewDetails[0].hotel_id
        currentReviewRating = reviewDetails[0].rating
        currentReviewDescription = reviewDetails[0].description

        editForm = FORM(TABLE(TR(TD(LABEL('Rating')), TD(INPUT(_type='text', _name='rating', requires=IS_IN_SET([1,2,3,4,5]))), LABEL('Please enter value between 1 to 5')), TR(TD(LABEL('Description')), TD(TEXTAREA(_name='description', requires=IS_NOT_EMPTY()))), TR(TD(), TD(INPUT(_type='submit', _value='Update')))))

        editForm.vars.rating = currentReviewRating
        editForm.vars.description = currentReviewDescription

        if editForm.process().accepted :
             # Update the overall rating of this hotel.
            row = db(db.Hotel_Info.id == hotel_id).select(db.Hotel_Info.overall_rating, db.Hotel_Info.no_of_reviewes)
            currentRating = row[0].overall_rating
            noOfReviews = row[0].no_of_reviewes

            import decimal

            newRating = (currentRating*noOfReviews - int(currentReviewRating)/1.0)

            newRating += float(editForm.vars.rating)

            newRating = newRating/noOfReviews

            if newRating < 0:
                newRating = 0;

            db(db.Hotel_Info.id == session.hotel_id).update(overall_rating=newRating)

            db(db.Review.id == request.args[1]).update(description=editForm.vars.description, rating=editForm.vars.rating)

        #editForm=crud.update(db.Review, request.args[1], fields=['rating', 'description'])
        #redirect(URL('details', args=[request.args[0]]))
        return dict(editForm=editForm, hotelId=session.hotel_id)
    elif len(request.args) == 1:
        redirect(URL('details', args=[request.args[0]]))
    else:
        redirect(URL('index'))

@auth.requires_membership('moderator')
def makeModerator():
    
    #makeModerator/user_id
    if len(request.args) > 0 :
        response.flash = request.args[0]
        auth.add_membership('moderator', int(request.args[0]))
        redirect(URL('userDetails', args=[request.args[0]]))
    else:
        redirect(URL('index'))

def sendMail():

    hotelId = session.hotel_id

    mailForm = FORM(TABLE(
                    TR(TD(B('To')), TD(':'), TD(INPUT(_name='To', requiures=IS_EMAIL()))),
                    TR(TD(B('Subject')), TD(':'), TD(INPUT(_name='Subject', requiures=IS_NOT_EMPTY()))),
                    TR(TD(B('Body')), TD(':'), TD(INPUT(_name='Body', requiures=IS_NOT_EMPTY()))),
                    TR(TD(), TD(), TD(INPUT(_type='submit', _value='Send')))),
                    submit_button='Send')

    mailForm.vars.Subject = 'Hotel information - ' + session.hotel_name
    mailForm.vars.Body = session.hotel_name + '\n' + session.hotel_address + '\n' + str(session.rating) + '\n' + str(session.hotel_cost) + '\n' + session.hotel_hours + '\n' + 'http://127.0.0.1:8000' + session.url 

    htmlbody = '<html><p><b>Name: ' + session.hotel_name + '</b>\r\n</br></p><p><b>Address:</b> '+session.hotel_address + '</br></p><p><b>Rating: </b>' + str(session.rating) + '</br></p><p><b>Cost per 2 :</b> ' + str(session.hotel_cost) + '</br></p><p><b>Timings: </b> ' + session.hotel_hours + '</br></p><p>For details please visit ' + 'http://127.0.0.1:8000' + session.url + '</p></html>'


    if mailForm.accepts(request,session):
        #mail.send(to=[mailForm.vars.To], subject=mailForm.vars.Subject, reply_to='swap.andro24@gmail.com', message=mailForm.vars.Body)
        mail.send(to=[mailForm.vars.To], subject=mailForm.vars.Subject, reply_to='contactus@cafehunt.com', message=htmlbody)
        redirect(URL('details', args=[session.hotel_id]))
    

    return dict(mailForm=mailForm, hotelId=hotelId)

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
    return dict(photoForm=photoForm, hotelId=hotelId)


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
    return dict(menuForm=menuForm, hotelId=hotelId)

def incrClicks():
    hotelId = request.args[0]
    
    # db query to increment click of this hotel id
    query = db.Advertisement.hotel_id == hotelId
    clicksRow= db(query).select(db.Advertisement.clicks)[0]
    nclicks= int(clicksRow.clicks) + 1
    db(db.Advertisement.hotel_id==hotelId).update(clicks=nclicks)
    # redirect to original page
    redirect(URL('details', args=[request.args[0]]))

def advancedSearch():
    session.advancedSearch={}

    if request.vars.submit == 'Search':
        
        keywords = request.vars
        keys = request.vars.keys()

        '''
        if ('cost' not in keys) or  ('rating' not in keys) or (keywords['costValue'] == '') or (keywords['ratingValue'] == '') :
            message = 'At least provide preferences for cost and rating'
            redirect(URL('advancedSearch', vars={'flash':'At least provide preferences for cost and rating'}))

        '''

        try:
            if 'cost' in keys:
                val = float(keywords['costValue'])
                if float(keywords['costValue']) < 0:
                    redirect(URL('advancedSearch', vars={'flash':'Please provide non-negative for cost'}))

            if 'rating' in keys:
                val = float(keywords['ratingValue'])
                if float(keywords['ratingValue']) < 0:
                    redirect(URL('advancedSearch', vars={'flash':'Please provide non-negative for rating'}))

        except ValueError:
            redirect(URL('advancedSearch', vars={'flash':'Please provide numeric value for cost and rating'}))



        if (keywords['hotel_locality']== '') and (keywords['type_of_food'] == '') and ('cost' not in keys) and ('rating' not in keys):
            redirect(URL('advancedSearch', vars={'flash':'Please provide at least one crieteria'}))

        for key in request.vars.keys():
            session.advancedSearch[key]=request.vars[key]

        redirect(URL('search', args=['advancedSearch']))

    return dict()
