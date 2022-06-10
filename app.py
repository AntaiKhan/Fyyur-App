#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

#from __future__ import generator_stop
from crypt import methods
from csv import excel
from itertools import count
import json
from os import abort
from unicodedata import name
from unittest import result
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  recent_venues =Venue.query.order_by(Venue.id.desc()).limit(10).all()

  return render_template('pages/home.html', data=recent_artists, info=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  venues = Venue.query.order_by('name').all()
  return render_template('pages/venues.html', areas=venues)

def venue_search_results(search_term):
  try:
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).order_by('name').all()
    return result
  except Exception as e:
    print(e)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  result = venue_search_results(request.form['search_term'])
  
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  venues = []
  for data in result:
    venue = {}
    venue['id'] = data.id
    venue['name'] = data.name
    venue['num_upcoming_shows'] = Show.query.filter(db.and_(Show.start_time > datetime.now(), Show.venue_id==data.id)).count()
  
  venues.append(venue)
  
  response={
    "count": count(result),
    "data": venues
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = Venue.query.get(venue_id)

  info = {}
  info['id'] = venues.id
  info['name'] = venues.name
  info['genres'] = venues.genres
  info['city'] = venues.city
  info['state'] = venues.state
  info['phone'] = venues.phone
  info['image_link'] = venues.image_link
  info['website'] = venues.website
  info['facebook_link'] = venues.facebook_link
  info['seeking_talent'] = venues.seeking_talent
  past_shows=[]
  upcoming_shows=[]
  get_past_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id and Show.show_time < datetime.now()).all()
  get_upcoming_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id and Show.show_time > datetime.now()).all()
  
  if count(get_past_shows) != 0:
    for i,j in get_past_shows:
      past_show={}
      past_show['artist_id'] = j.artist_id
      past_show['artist_name'] = j.Artist.name
      past_show['artist_image_link'] = j.Artist.image_link
      past_show['start_time'] = str(i.start_time)
      past_shows.append(past_show)
  

  else:
    past_shows=[]

  if count(get_upcoming_shows) != 0:
    for i,j in get_upcoming_shows:
      upcoming={}
      upcoming['artist_id'] = j.artist_id
      upcoming['artist_name'] = j.Artist.name
      upcoming['artist_image_link'] = j.Artist.image_link
      upcoming['start_time'] = str(i.start_time)
      upcoming_shows.append(upcoming)

  info['past_shows'] = past_shows
  info['upcoming_shows'] = upcoming_shows
  info['past_shows_count'] = count(get_past_shows)
  info['upcoming_shows_count'] = count(get_upcoming_shows)

  data = list(filter(lambda d: d['id'] == venue_id, info))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if form.validate_on_submit():
    try:
      create_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      genres=form.genres.data,
      website=form.website.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )

      db.session.add(create_venue)
      db.session.commit()

  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      return redirect(url_for('venues'))
    
    except:
      db.session.rollback()
      flash('Venue ' + request.form['name'] + ' could not be listed!')
      
    finally:
      db.session.close()


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  all_artists = Artist.query.order_by('name').all()

  return render_template('pages/artists.html', artists=all_artists)

def artist_search_results(search_term):
  try:
    result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).order_by('name').all()
    return result
  except Exception as e:
    print(e)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  
  result = artist_search_results(request.form['search_term'])
  
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists = []
  for data in result:
    artist = {}
    artist['id'] = data.id
    artist['name'] = data.name
    artist['num_upcoming_shows'] = Show.query.filter(db.and_(Show.start_time > datetime.now(), Show.artist_id==data.id)).count()
  
  artists.append(artist)
  
  response={
    "count": count(result),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  info = {}
  info['id'] = artist.id
  info['name'] = artist.name
  info['genres'] = artist.genres
  info['city'] = artist.city
  info['state'] = artist.state
  info['phone'] = artist.phone
  info['image_link'] = artist.image_link
  info['website'] = artist.website
  past_shows=[]
  upcoming_shows=[]
  get_past_shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==artist_id and Show.show_time < datetime.now()).all()
  get_upcoming_shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==artist_id and Show.show_time > datetime.now()).all()
  
  if count(get_past_shows) != 0:
    for i,j in get_past_shows:
      past_show={}
      past_show['venue_id'] = j.venue_id
      past_show['venue_name'] = j.Venue.name
      past_show['venue_image_link'] = j.Venue.image_link
      past_show['show_time'] = str(i.show_time)
      past_shows.append(past_show)
  

  else:
    past_shows=[]

  if count(get_upcoming_shows) != 0:
    for i,j in get_upcoming_shows:
      upcoming={}
      upcoming['venue_id'] = j.venue_id
      upcoming['venue_name'] = j.Venue.name
      upcoming['venue_image_link'] = j.Venue.image_link
      upcoming['show_time'] = str(i.show_time)
      upcoming_shows.append(upcoming)

  info['past_shows'] = past_shows
  info['upcoming_shows'] = upcoming_shows
  info['past_shows_count'] = count(get_past_shows)
  info['upcoming_shows_count'] = count(get_upcoming_shows)


  data = list(filter(lambda d: d['id'] == artist_id, info))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists=Venue.query.get(artist_id)
  artist={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genre,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  if form.validate_on_submit():
  
    try:
      artists=Artist.query.get(artist_id)
      artists.name=form.name.data,
      artists.city=form.city.data,
      artists.state=form.state.data,
      artists.phone=form.phone.data,
      artists.image_link=form.image_link.data,
      artists.facebook_link=form.facebook_link.data,
      artists.genres=form.genres.data,
      artists.website=form.website.data,
      artists.seeking_venue=form.seeking_venue.data,
      artists.seeking_description=form.seeking_description.data
    
      db.session.commit()

      return redirect(url_for('show_artist', artist_id=artist_id))
    except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues=Venue.query.get(venue_id)
  venue={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genre,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link
  }
  # venue={
  #   "id": venue_id,
  #   "name": venues.name,
  #   "genres": venues.genre,
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  form = VenueForm()
  if form.validate_on_submit():
    try:
      venues=Venue.query.get(venue_id)
      venues.name=form.name.data,
      venues.city=form.city.data,
      venues.state=form.state.data,
      venues.address=form.address.data,
      venues.phone=form.phone.data,
      venues.image_link=form.image_link.data,
      venues.facebook_link=form.facebook_link.data,
      venues.genres=form.genres.data,
      venues.website=form.website.data,
      venues.seeking_talent=form.seeking_talent.data,
      venues.seeking_description=form.seeking_description.data
    
      db.session.commit()
  # venue record with ID <venue_id> using the new attributes
      return redirect(url_for('show_venue', venue_id=venue_id))
    except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if form.validate_on_submit():
    try:
      create_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website=form.website.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )

      db.session.add(create_artist)
      db.session.commit()

  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
    except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  all_shows = db.session.query(Artist, Venue, Show).select_from(Artist).join(Venue).join(Show).all()
  data = {}
  for artist,venue,show in all_shows:
    datas={}
    datas['venue_id'] = show.venue_id
    datas['venue_name'] = venue.name
    datas['artist_id'] = show.artist_id
    datas['artist_name'] = artist.name
    datas['artist_image_link'] = artist.image_link
    datas['start_time'] =show.start_time
  
  data.append(datas)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  if form.validate_on_submit():
    try:
      create_show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data )
     
      db.session.add(create_show)
      db.session.commit()
  # on successful db insert, flash success
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''
# Or specify port manually:

if __name__ == '__main__':
   # port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5000)

