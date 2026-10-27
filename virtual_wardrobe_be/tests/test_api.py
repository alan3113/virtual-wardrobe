from conftest import clothing

def test_authentication_and_protection(client):
    assert client.get('/api/v1/auth/me').status_code == 403
    payload = {'name':'Alex','email':'Alex@example.com','password':'long-password'}
    registered = client.post('/api/v1/auth/register', json=payload)
    assert registered.status_code == 201
    assert registered.json()['user']['email'] == 'alex@example.com'
    assert client.post('/api/v1/auth/register', json=payload).status_code == 409
    assert client.post('/api/v1/auth/login', json={'email':payload['email'],'password':'wrong'}).status_code == 401
    logged_in = client.post('/api/v1/auth/login', json={'email':payload['email'],'password':payload['password']})
    assert logged_in.status_code == 200
    headers = {'Authorization':'Bearer ' + logged_in.json()['access_token']}
    assert client.get('/api/v1/auth/me', headers=headers).json()['name'] == 'Alex'

def test_wardrobe_crud_filter_pagination_and_isolation(client, auth):
    first = client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('Blue shirt','Tops','Blue'))
    assert first.status_code == 201, first.text
    item_id = first.json()['id']
    client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('Black shoes','Shoes'))
    filtered = client.get('/api/v1/wardrobe/items?category=Tops&limit=1', headers=auth)
    assert [x['id'] for x in filtered.json()] == [item_id]
    assert len(client.get('/api/v1/wardrobe/items?limit=1&offset=1', headers=auth).json()) == 1
    assert client.patch(f'/api/v1/wardrobe/items/{item_id}', headers=auth, json={'color':'Navy'}).json()['color'] == 'Navy'
    assert client.get('/api/v1/wardrobe/stats', headers=auth).json()['total_items'] == 2
    assert client.get('/api/v1/wardrobe/gaps', headers=auth).status_code == 200
    other = client.post('/api/v1/auth/register', json={'name':'Bea','email':'bea@example.com','password':'long-password'}).json()
    assert client.get(f'/api/v1/wardrobe/items/{item_id}', headers={'Authorization':'Bearer '+other['access_token']}).status_code == 404
    assert client.delete(f'/api/v1/wardrobe/items/{item_id}', headers=auth).status_code == 204
    assert client.get(f'/api/v1/wardrobe/items/{item_id}', headers=auth).status_code == 404

def test_similarity_and_duplicate_classification(client, auth):
    client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('White tee','Tops','White',style='Casual'))
    result = client.post('/api/v1/products/analyze', headers=auth, json={'product':clothing('Another tee','Tops','White',style='Casual')})
    assert result.status_code == 200, result.text
    assert result.json()['similar_items'][0]['classification'] == 'likely_duplicate'
    assert result.json()['duplicate_risk'] == 'High'

def test_outfit_generation_and_shopping(client, auth):
    top = client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('Cream shirt','Tops','Cream',style='Casual')).json()
    client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('Blue jeans','Bottoms','Blue',style='Casual'))
    client.post('/api/v1/wardrobe/items', headers=auth, json=clothing('White sneakers','Shoes','White',style='Casual'))
    generated = client.post('/api/v1/outfits/generate', headers=auth, json={'item_id':top['id']})
    assert generated.status_code == 200, generated.text
    assert generated.json() and top['id'] in generated.json()[0]['item_ids']
    saved = client.post('/api/v1/outfits', headers=auth, json=generated.json()[0])
    assert saved.status_code == 201, saved.text
    assert len(client.get('/api/v1/outfits', headers=auth).json()) == 1
    shopping = client.post('/api/v1/shopping/analyze', headers=auth, json={'product':clothing('New jacket','Outerwear','Black',style='Casual')})
    assert shopping.status_code == 200, shopping.text
    body = shopping.json()
    assert body['compatible_items'] >= 2
    assert body['new_outfits'] >= 1
    assert body['wardrobe_gap'] is True
    assert body['possible_new_outfits']
    assert client.delete(f"/api/v1/outfits/{saved.json()['id']}", headers=auth).status_code == 204

def test_image_upload_and_replaceable_vision_provider(client, auth, tmp_path, monkeypatch):
    import base64
    from app.main import app
    from app.api.routes import vision_provider
    from app.core.config import settings
    from app.ai.providers import VisionProvider

    class TestVision(VisionProvider):
        def analyze(self, image_url):
            return {'category':'Shoes','color':'Red','style':'Sporty','season':'Summer'}

    monkeypatch.setattr(settings, 'upload_dir', tmp_path)
    app.dependency_overrides[vision_provider] = lambda: TestVision()
    image = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9V9VkAAAAASUVORK5CYII=')
    uploaded = client.post('/api/v1/wardrobe/analyze', headers=auth,
                           files={'file':('shoe.png', image, 'image/png')})
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()['category'] == 'Shoes'
    assert uploaded.json()['color'] == 'Red'
    assert len(list(tmp_path.iterdir())) == 1
    assert client.post('/api/v1/wardrobe/upload', headers=auth,
                       files={'file':('bad.txt', b'not an image', 'text/plain')}).status_code == 415
