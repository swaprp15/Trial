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
    response.flash = T("Welcome CafeHunt!")
    form=FORM(INPUT(_name='keyword', requiures=IS_NOT_EMPTY(), _placeholder='Please enter hotel name'), INPUT(_type='submit', _value='Search'))
    #if form.process().accepted:
    #    if form.accepts(request,session):
    #       redirect(URL('search', args=[form.vars.keyword]))
    ##    redirect(URL('search'))

    if form.accepts(request,session):
        redirect(URL('search', args=[form.vars.keyword]))

    

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
    query=db.Hotel_Info.name.contains(request.args[0])
    hotels = db(query).select()
    if len(hotels) == 0:
        hotels = ['Sorry no hotels found of your interest...']

    return dict(content=hotels)

@auth.requires_login()
def details():
    #if adding a review
    # /addReview/hotel_id

    session.hotel_id = request.args[0]

    addReviewForm=FORM(INPUT(_name='description', requiures=IS_NOT_EMPTY(), _placeholder='What\'s your opinion?'), INPUT(_type='submit', _value='Post it..'), INPUT(_type='reset', _value='reset'))

    import datetime

    if addReviewForm.accepts(request,session):
        # /addReview/hotel_id
        db.Review.insert(user_id=auth.user_id, hotel_id=session.hotel_id, rating=2.5, time_of_post=datetime.datetime.now(), description=addReviewForm.vars.description)

        redirect(URL('details', args=[session.hotel_id]))
    

    query=db.Hotel_Info.id == request.args[0]
    hotels = db(query).select()
    if len(hotels) == 0:
        hotels = ['Sorry, details are not available...']

    query=((db.Review.hotel_id == session.hotel_id) & (db.Review.user_id == db.auth_user.id))
    reviews = db(query).select()
    if len(reviews) == 0:
        reviews = []

    return dict(details=hotels[0], reviews=reviews, addReviewForm=addReviewForm)

def userDetails():
    userId = request.args[0]

    query = ((db.Review.user_id == userId) & (db.Review.hotel_id == db.Hotel_Info.id))

    userReviews = db(query).select(db.Hotel_Info.name, db.Review.hotel_id, db.Review.description, db.Review.rating)

    query = db.auth_user.id == userId

    userInfo = db(query).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.photo)

    return dict(userReviews=userReviews, id=userInfo[0].id, fname=userInfo[0].first_name, lname=userInfo[0].last_name, photo=userInfo[0].photo)
