from app.models import Class

def test_add_class(client, auth, app):
    auth.login()
    response = client.post('/add-class', data={
        'class_name': 'Test Class',
        'section': 'T'
    }, follow_redirects=True)

    assert b'Class Test Class-T added!' in response.data

    with app.app_context():
        cls = Class.query.filter_by(class_name='Test Class').first()
        assert cls is not None
        assert cls.section == 'T'
