from flask import Flask, render_template, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    description = db.Column(db.String(500))

@app.route('/')
def dashboard():
    today = datetime.now().strftime('%Y-%m-%d')
    events = Event.query.filter_by(date=today).all()
    return render_template('dashboard.html', events=events, today=today)

@app.route('/api/sessions/<date>')
def get_sessions(date):
    events = Event.query.filter_by(date=date).all()
    sessions = [{'id': e.id, 'title': e.title, 'time': e.time, 'description': e.description} for e in events]
    return jsonify({'date': date, 'sessions': sessions})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        today = datetime.now().strftime('%Y-%m-%d')
        existing = Event.query.filter_by(date=today, title='Team Meeting').first()
        if not existing:
            team_meeting = Event(title='Team Meeting', date=today, time='10:00', description='Daily standup and planning')
            db.session.add(team_meeting)
            db.session.commit()
    app.run(debug=True, port=5000)
