import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost' # For subdomain routing simulation
    })

    with app.app_context():
        _db.create_all()
        # Setup basic SaaS context for tests
        from app.models import School, Session
        s = School(name='Test School', subdomain='test')
        _db.session.add(s)
        _db.session.commit()

        sess = Session(name='2024/2025', is_current=True, school_id=s.id)
        _db.session.add(sess)
        _db.session.commit()

        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username='admin', password='admin123'):
            from app.models import User, School
            from app.extensions import db
            with self._client.application.app_context():
                school = School.query.first()
                user = User(username=username, role='admin', school_id=school.id)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()

            return self._client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

        def logout(self):
            return self._client.get('/logout')

    return AuthActions(client)
