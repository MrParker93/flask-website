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

def test_index_page_gives_200_response(set_up_test_client):
    response = set_up_test_client.get('/', content_type='html/text')
    assert response.status_code == 200

def test_database_exists(set_up_test_client):
    assert Path('test.db').is_file()

def test_database_is_empty_when_page_is_first_loaded(set_up_test_client):
    db_table = set_up_test_client.get('/')
    assert b'No entries yet. Add some!' in db_table.data

def test_index_page_can_save_a_POST_request(set_up_test_client):
    response = set_up_test_client.post('/add', data={'blog title': 'blog post'})
    assert b'blog post' in response.get_data()
