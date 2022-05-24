import sys
import requests
import time
from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'So-Seckrekt'
api_key = 'bc02810b02c5dd52aa434227c02617f7'


class City(db.Model):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    temperature = Column(String)
    state = Column(String)
    card = Column(String)


db.create_all()


def find_day_time(timezone):
    offset = timezone / 3600
    hour = time.gmtime().tm_hour + offset
    if 5 <= hour < 19 or hour >= 29:
        return "card afternoon"
    elif 19 <= hour < 21:
        return "card evening"
    return "card night"


def add_city(city_name):
    if city_name.strip():
        name = str(city_name).upper()
        if City.query.filter_by(name=name).first():
            flash("The city has already been added to the list!")
            return redirect('/')
        try:
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}'
            if requests.get(url):
                response = requests.get(url).json()
                temperature = round(int(response['main']['temp']))
                state = response['weather'][0]['main']
                card = find_day_time(int(response['timezone']))
                db.session.add(City(name=name, temperature=temperature, state=state, card=card))
                db.session.commit()
            else:
                flash("The city doesn't exist!")
            return redirect('/')
        except:
            pass


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        add_city(request.form['city_name'])
    all_rows = City.query.all()
    cities = reversed(all_rows)
    return render_template('index.html', cities=cities)


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()