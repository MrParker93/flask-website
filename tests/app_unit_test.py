import pytest
from pathlib import Path

from project.app import app, init_db

TEST_DB = 'test.db'


@pytest.fixture
def set_up_test_client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config['TESTING'] = True
    app.config['DATABASE'] = BASE_DIR.joinpath(TEST_DB)

    init_db()  # setUp 
    yield app.test_client()
    init_db()  # tearDown

def login_helper(set_up_test_client, username, password):
    return set_up_test_client.post(
        '/login',
        data=dict(username=username, password=password),
        follow_redirects=True,
    )

def logout_helper(set_up_test_client):
    return set_up_test_client.get('/logout', follow_redirects=True)

def test_index_page_gives_200_response(set_up_test_client):
    response = set_up_test_client.get('/', content_type='html/text')
    assert response.status_code == 200

def test_database_exists(set_up_test_client):
    assert Path('test.db').is_file()

def test_database_is_empty_when_page_is_first_loaded(set_up_test_client):
    db_table = set_up_test_client.get('/')
    assert b'No entries yet. Add some!' in db_table.data

def test_user_can_login_and_logout(set_up_test_client):
    log_status = login_helper(set_up_test_client, app.config['USERNAME'], app.config['PASSWORD'])
    assert b'Successfully logged in!' in log_status.data
    log_status = logout_helper(set_up_test_client)
    assert b'Successfully logged out!' in log_status.data
    log_status = login_helper(set_up_test_client, app.config['USERNAME'] + 'x', app.config['PASSWORD'])
    assert b'Invalid username' in log_status.data
    log_status = login_helper(set_up_test_client, app.config['USERNAME'], app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in log_status.data

# def test_index_page_can_save_a_POST_request(set_up_test_client):
#     response = set_up_test_client.post('/add', data=dict())
#     assert 'blog post'
