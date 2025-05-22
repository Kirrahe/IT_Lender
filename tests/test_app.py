import os
import tempfile
import json
import pytest

import app

@pytest.fixture
def client():
    db_fd, app.DB_NAME = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        with app.app.app_context():
            app.init_db()
        yield client
    os.close(db_fd)
    os.unlink(app.DB_NAME)

def test_add_and_list_items(client):
    # Add item
    resp = client.post('/items', json={'name': 'Laptop', 'description': 'Dell XPS'})
    assert resp.status_code == 201
    data = json.loads(resp.data)
    item_id = data['id']

    # List items
    resp = client.get('/items')
    assert resp.status_code == 200
    items = json.loads(resp.data)
    assert any(item['id'] == item_id for item in items)

def test_reservation_conflict(client):
    # Add item
    resp = client.post('/items', json={'name': 'Laptop'})
    item_id = resp.get_json()['id']
    # Make reservation
    resp = client.post(f'/items/{item_id}/reserve', json={
        'user': 'Alice',
        'start': '2030-01-01T10:00:00',
        'end': '2030-01-01T12:00:00'
    })
    assert resp.status_code == 201
    # Make conflicting reservation
    resp = client.post(f'/items/{item_id}/reserve', json={
        'user': 'Bob',
        'start': '2030-01-01T11:00:00',
        'end': '2030-01-01T13:00:00'
    })
    assert resp.status_code == 409
