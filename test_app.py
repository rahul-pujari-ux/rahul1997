import unittest
from datetime import datetime
from app import app, db, Event


class TestAppFunctions(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_route_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_contains_title(self):
        response = self.client.get('/')
        self.assertIn(b'Calendar Dashboard', response.data)

    def test_dashboard_displays_today_date(self):
        response = self.client.get('/')
        today = datetime.now().strftime('%Y-%m-%d')
        self.assertIn(today.encode(), response.data)

    def test_dashboard_no_events_initially(self):
        response = self.client.get('/')
        self.assertIn(b'No events scheduled for this date', response.data)

    def test_dashboard_shows_event_when_exists(self):
        with app.app_context():
            today = datetime.now().strftime('%Y-%m-%d')
            event = Event(title='Test Event', date=today, time='14:00', description='Test description')
            db.session.add(event)
            db.session.commit()

        response = self.client.get('/')
        self.assertIn(b'Test Event', response.data)
        self.assertIn(b'14:00', response.data)
        self.assertIn(b'Test description', response.data)

    def test_dashboard_with_date_parameter(self):
        with app.app_context():
            event = Event(title='Future Event', date='2026-06-20', time='15:00', description='Future event')
            db.session.add(event)
            db.session.commit()

        response = self.client.get('/?date=2026-06-20')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Future Event', response.data)
        self.assertIn(b'2026-06-20', response.data)

    def test_dashboard_date_picker_displays(self):
        response = self.client.get('/')
        self.assertIn(b'datepicker', response.data)
        self.assertIn(b'Select Date:', response.data)

    def test_dashboard_filters_events_by_query_date(self):
        with app.app_context():
            event1 = Event(title='Event 1', date='2026-06-11', time='10:00', description='First')
            event2 = Event(title='Event 2', date='2026-06-12', time='11:00', description='Second')
            db.session.add(event1)
            db.session.add(event2)
            db.session.commit()

        response = self.client.get('/?date=2026-06-12')
        self.assertIn(b'Event 2', response.data)
        self.assertNotIn(b'Event 1', response.data)

    def test_get_sessions_returns_json(self):
        response = self.client.get('/api/sessions/2026-06-11')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    def test_get_sessions_returns_correct_date(self):
        response = self.client.get('/api/sessions/2026-06-11')
        data = response.get_json()
        self.assertEqual(data['date'], '2026-06-11')

    def test_get_sessions_no_events_returns_empty_list(self):
        response = self.client.get('/api/sessions/2026-06-11')
        data = response.get_json()
        self.assertEqual(data['sessions'], [])

    def test_get_sessions_returns_events_for_date(self):
        with app.app_context():
            event = Event(title='Meeting', date='2026-06-11', time='10:00', description='Team standup')
            db.session.add(event)
            db.session.commit()

        response = self.client.get('/api/sessions/2026-06-11')
        data = response.get_json()
        self.assertEqual(len(data['sessions']), 1)
        self.assertEqual(data['sessions'][0]['title'], 'Meeting')
        self.assertEqual(data['sessions'][0]['time'], '10:00')
        self.assertEqual(data['sessions'][0]['description'], 'Team standup')

    def test_get_sessions_filters_by_date(self):
        with app.app_context():
            event1 = Event(title='Event 1', date='2026-06-11', time='10:00', description='First event')
            event2 = Event(title='Event 2', date='2026-06-12', time='11:00', description='Second event')
            db.session.add(event1)
            db.session.add(event2)
            db.session.commit()

        response = self.client.get('/api/sessions/2026-06-11')
        data = response.get_json()
        self.assertEqual(len(data['sessions']), 1)
        self.assertEqual(data['sessions'][0]['title'], 'Event 1')

    def test_get_sessions_multiple_events_same_date(self):
        with app.app_context():
            event1 = Event(title='Event 1', date='2026-06-11', time='10:00', description='First')
            event2 = Event(title='Event 2', date='2026-06-11', time='14:00', description='Second')
            db.session.add(event1)
            db.session.add(event2)
            db.session.commit()

        response = self.client.get('/api/sessions/2026-06-11')
        data = response.get_json()
        self.assertEqual(len(data['sessions']), 2)

    def test_event_model_creation(self):
        with app.app_context():
            event = Event(title='Test', date='2026-06-11', time='10:00', description='Test event')
            db.session.add(event)
            db.session.commit()

            retrieved = Event.query.filter_by(title='Test').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.title, 'Test')
            self.assertEqual(retrieved.date, '2026-06-11')
            self.assertEqual(retrieved.time, '10:00')
            self.assertEqual(retrieved.description, 'Test event')

    def test_event_model_required_fields(self):
        with app.app_context():
            event = Event(title='', date='', time='')
            db.session.add(event)
            db.session.commit()

            retrieved = Event.query.first()
            self.assertEqual(retrieved.title, '')
            self.assertEqual(retrieved.date, '')


class TestEventModel(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_event_attributes(self):
        with app.app_context():
            event = Event(
                title='Team Meeting',
                date='2026-06-11',
                time='10:00',
                description='Daily standup'
            )
            self.assertEqual(event.title, 'Team Meeting')
            self.assertEqual(event.date, '2026-06-11')
            self.assertEqual(event.time, '10:00')
            self.assertEqual(event.description, 'Daily standup')

    def test_event_without_description(self):
        with app.app_context():
            event = Event(title='Meeting', date='2026-06-11', time='10:00')
            db.session.add(event)
            db.session.commit()

            retrieved = Event.query.first()
            self.assertIsNone(retrieved.description)


if __name__ == '__main__':
    unittest.main()
