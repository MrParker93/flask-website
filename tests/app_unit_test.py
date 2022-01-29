from project.app import app

def test_index_page_gives_200_response():
    tester = app.test_client()
    response = tester.get('/', content_type='html/text')

    assert response.status_code == 200
    assert response.data == b"Hello, World!"