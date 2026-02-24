def test_home_redirects_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

def test_login_success(auth):
    response = auth.login()
    assert b'Logged in successfully' in response.data
    assert b'Dashboard Overview' in response.data
