import spotipy
from flask import Flask, request, url_for, session, redirect, render_template
import time
import random
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
app.secret_key = ""
app.config['SESSION_COOKIE_NAME'] = ""
for i in range(0,10):
    char = random.choice(['A','B','C','D','5','7','JH','LK','34','76','M'])
    app.secret_key += char
    char = random.choice(['7465','45','G','BEN','NA','EN','YU','HI','7','4','55','952'])
    app.config['SESSION_COOKIE_NAME'] += char
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/spotify-login')
def spotify_login():
    sp_oauth = create_spotify_oauth()
    url = sp_oauth.get_authorize_url()
    return redirect(url)

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="3804183cf9f44b37a8eecaf3aed8c4b1",
        client_secret="d412d8ddf0394bfc81e9926febfedf44",
        redirect_uri=url_for('redirectPage', _external=True),
        scope=['user-library-read', 'user-read-recently-played', 'user-top-read']
    )

@app.route('/redirect')
def redirectPage():
    sp_oath = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oath.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('get_alltime_leaders', _external=True))

@app.route('/recent')
def get_recent_tracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    songs = {}
    artists = {}
    for i in range(0, len(sp.current_user_recently_played(limit=50)['items'])):
        song = sp.current_user_recently_played()['items'][i]['track']['name']
        artist = sp.current_user_recently_played()['items'][i]['track']['artists'][0]['name']
        if song in songs.keys():
            songs[song] += 1
        else:
            songs[song] = 1
        if artist in artists.keys():
            artists[artist] += 1
        else:
            artists[artist] = 1
    return artists

@app.route("/alltime")
def get_alltime_leaders():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    song_rankings = []
    artist_rankings = []
    for i in range(0, 50):
        song = sp.current_user_top_tracks(limit=50, time_range="long_term")['items'][i]['name']
        artist = sp.current_user_top_tracks(limit=50, time_range="long_term")['items'][i]['artists'][0]['name']
        song_rankings.append({"rank": i+1, "name": song, "artist": artist})
        top_artist = sp.current_user_top_artists(limit=50, time_range="long_term")['items'][i]['name']
        artist_rankings.append({"rank": i+1, "name": top_artist})
    return render_template('index.html', songs=song_rankings, artists=artist_rankings)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if token_info is None:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info
