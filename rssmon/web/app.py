from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from qbittorrent import Client
from flask_crontab import Crontab
from flask_apscheduler import APScheduler
from flask_caching import Cache
import os
import feedparser
import subprocess
import certifi
import urllib3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/prod.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
crontab = Crontab(app)
scheduler = APScheduler()


class tvShows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tvShow_name = db.Column(db.String(8), unique=True, nullable=False)
    tvShow_resolution = db.Column(db.String(8), unique=False, nullable=False)
    tvShow_date = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<tvShows %r>' % self.tvShow_name


class setTorrents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    settorr_clientName = db.Column(db.String(20), unique=True, nullable=False)
    settorr_username = db.Column(db.String(10), unique=False, nullable=False)
    settorr_password = db.Column(db.String(10), unique=False, nullable=False)
    settorr_uri = db.Column(db.String(40), unique=True, nullable=False)
    settorr_port = db.Column(db.String(5), unique=True, nullable=False)
    settorr_category = db.Column(db.String(20), unique=False, nullable=False)
    settorr_downloadPath = db.Column(db.String(60), unique=True, nullable=False)
    settorr_date = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<setTorrents %r>' % self.settorr_clientName


db.create_all()


class rssFeed():

    def get_paramTorrentFromBD(id):
        """ Функция возвращает из базы настройки, для подключения и параметры
        к торрент клиенту в виде списка по id """
        for setup in setTorrents.query.filter_by(id=id).all():
            return [setup.settorr_clientName,
                    setup.settorr_username,
                    setup.settorr_password,
                    setup.settorr_uri,
                    setup.settorr_port,
                    setup.settorr_category,
                    setup.settorr_downloadPath,
                    setup.settorr_date]

    def get_paramTvShowsFromBD(id):
        """ Функция возвращает из базы имя, качество
        и время добавления записи, в виде списка по id."""
        paramShow = dict()
        for el in tvShows.query.filter_by(id=id).all():
            return [el.tvShow_name,
                    el.tvShow_resolution,
                    el.tvShow_date]

    def get_linkTorrentFromRSS(id):
        """ Функция выполняет парсинг."""
        url = "https://rss.bzda.ru/rss.xml"
        bzda = feedparser.parse(url)
        set_list = rssFeed.get_paramTvShowsFromBD(id=id)
        tvName = set_list[0]
        tvResolution = set_list[1]
        tvDate = set_list[2]
        if bzda.status == 200:
            numberOfHeadlines = len(bzda['entries'])
            for i in range(0, numberOfHeadlines):
                if tvName in bzda['entries'][i]['title']:
                    if tvResolution in bzda['entries'][i]['title']:
                        rssFeed.post_toTorrentClient(bzda['entries'][i]['link'])

    def post_toTorrentClient(link):
        """ Функция добавлет ссылку на торент файл в клиент торента."""
        torrent_id = "1"
        set_list = rssFeed.get_paramTorrentFromBD(id=torrent_id)
        name = set_list[0]
        username = set_list[1]
        password = set_list[2]
        uri = set_list[3]
        port = set_list[4]
        category = set_list[5]
        downloadPath = set_list[6]
        qb = Client(uri, verify=False)
        qb.login(username, password)
        print(link)
        qb.download_from_link(link, savepath=downloadPath, category=category)

    def run_linkTorrentFromRSS():
        for el in tvShows.query.order_by(tvShows.id).all():
            rssFeed.get_linkTorrentFromRSS(el.id)


def scheduleTask():
    """print("This test runs every 3 seconds")"""
    rssFeed.run_linkTorrentFromRSS()


@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


@app.route("/rssmon_page", methods=["GET", "POST"])
def rssmon_page():
    if request.method == 'POST':
        addtv_show = tvShows(tvShow_name=request.form['tv_name'],
                             tvShow_resolution=request.form['tv_resolution'])
        db.session.add(addtv_show)
        db.session.commit()
        return redirect('/rssmon_page')
    else:
        listtv_show = tvShows.query.order_by(tvShows.id).all()
        return render_template("rssmon_page.html", listshow=listtv_show)


@app.route("/setup_page", methods=["GET"])
def setup_page():
    listtorrent_client = setTorrents.query.order_by(setTorrents.id).all()
    return render_template("setup_page.html",
                           listtorrent_client=listtorrent_client)


@app.route('/add_torrent', methods=['POST', 'GET'])
def add_torrnet():
    if request.method == 'POST':
        addTorrent = setTorrents(
                     settorr_clientName=request.form['settorr_clientName'],
                     settorr_username=request.form['settorr_username'],
                     settorr_password=request.form['settorr_password'],
                     settorr_uri=request.form['settorr_uri'],
                     settorr_port=request.form['settorr_port'],
                     settorr_category=request.form['settorr_category'],
                     settorr_downloadPath=request.form['settorr_downloadPath'])
        db.session.add(addTorrent)
        db.session.commit()
        return redirect('/setup_page')
    else:
        return render_template("add_torrent.html")


@app.route('/detail/runShow/<int:id>', methods=['GET'])
def run_torrent(id):
    rssFeed.get_linkTorrentFromRSS(id=id)
    return redirect('/rssmon_page')


@app.route('/delete/tvShows/<int:id>', methods=['GET'])
def del_show(id):
    delete = tvShows.query.get_or_404(id)
    db.session.delete(delete)
    db.session.commit()
    return redirect('/rssmon_page')


@app.route('/delete/setTorrents/<int:id>', methods=['GET'])
def del_torrent(id):
    delete = setTorrents.query.get_or_404(id)
    db.session.delete(delete)
    db.session.commit()
    return redirect('/setup_page')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/errors/404.html'), 404


@app.route('/contacts', methods=['GET'])
def contacts():
    return render_template("contacts.html")


scheduler.init_app(app)
scheduler.add_job(id='Scheduled Task',
                  func=scheduleTask,
                  trigger="interval",
                  hours=1)
scheduler.start()

if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host="0.0.0.0", port="5000")
