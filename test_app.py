import pytest
from app import createApp, db


@pytest.fixture
def app():
    app = createApp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# Fixture to provide a client for testing
@pytest.fixture
def client(app):
    return app.test_client()


def registerUser(client, username, password, isAdmin=False):
    return client.post('/register', json={'username': username, 'password': password, 'is_admin': isAdmin})


def loginUser(client, username, password):
    return client.post('/login', json={'username': username, 'password': password})


def testRegister(client):
    response = registerUser(client, 'testuser', 'password')
    assert response.status_code == 201
    assert b'Account created successfully!' in response.data

    response = registerUser(client, 'testuser', 'password')
    assert response.status_code == 400
    assert b'User already exists!' in response.data


def testLoginLogout(client):
    registerUser(client, 'testuser', 'password')
    response = loginUser(client, 'testuser', 'password')
    assert response.status_code == 200
    assert b'Login successful!' in response.data

    response = client.get('/logout')
    assert response.status_code == 200
    assert b'Logged out successfully!' in response.data


def testRecipeCRUD(client):
    registerUser(client, 'testuser', 'password')
    loginUser(client, 'testuser', 'password')

    response = client.post('/recipe', json={
        'title': 'Test Recipe',
        'description': 'Test Recipe Description',
        'ingredients': 'Ingredient 1, Ingredient 2',
        'instructions': 'Step 1, Step 2'
    })
    assert response.status_code == 201
    assert b'Recipe created successfully!' in response.data

    recipeId = response.json['recipeId']

    response = client.get(f'/recipe/{recipeId}')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data

    response = client.put(f'/recipe/{recipeId}', json={
        'title': 'Updated Recipe',
        'description': 'Updated Recipe Description',
        'ingredients': 'New Ingredient 1, New Ingredient 2',
        'instructions': 'New Step 1, New Step 2'
    })
    assert response.status_code == 200
    assert b'Recipe updated successfully!' in response.data

    response = client.delete(f'/recipe/{recipeId}')
    assert response.status_code == 200
    assert b'Recipe deleted successfully!' in response.data


def testGetAllRecipes(client):
    registerUser(client, 'testuser', 'password')
    loginUser(client, 'testuser', 'password')

    client.post('/recipe', json={
        'title': 'Recipe 1',
        'description': 'Recipe 1 Description',
        'ingredients': 'Ingredient A, Ingredient B',
        'instructions': 'Step A, Step B'
    })

    client.post('/recipe', json={
        'title': 'Recipe 2',
        'description': 'Recipe 2 Description',
        'ingredients': 'Ingredient X, Ingredient Y',
        'instructions': 'Step X, Step Y'
    })

    response = client.get('/recipes')
    assert response.status_code == 200
    assert b'Recipe 1' in response.data
    assert b'Recipe 2' in response.data


def testSearchRecipes(client):
    registerUser(client, 'testuser', 'password')
    loginUser(client, 'testuser', 'password')

    client.post('/recipe', json={
        'title': 'Pasta Recipe',
        'description': 'Delicious pasta with cheese',
        'ingredients': 'Pasta, Cheese, Tomato Sauce',
        'instructions': 'Boil pasta, mix with cheese and tomato sauce'
    })

    client.post('/recipe', json={
        'title': 'Salad Recipe',
        'description': 'Healthy salad with vegetables',
        'ingredients': 'Lettuce, Tomato, Cucumber',
        'instructions': 'Chop vegetables, mix with dressing'
    })

    response = client.get('/recipes/search?q=Pasta')
    assert response.status_code == 200
    assert b'Pasta Recipe' in response.data
    assert b'Salad Recipe' not in response.data

    response = client.get('/recipes/search?q=Salad')
    assert response.status_code == 200
    assert b'Salad Recipe' in response.data
    assert b'Pasta Recipe' not in response.data


def testGetUsers(client):
    registerUser(client, 'admin', 'adminpass', isAdmin=True)
    loginUser(client, 'admin', 'adminpass')
    
    registerUser(client, 'testuser', 'password')

    response = client.get('/users')
    assert response.status_code == 200
    assert b'testuser' in response.data
    assert b'admin' in response.data


def testLogoutClearsSession(client):
    registerUser(client, 'testuser', 'password')
    loginUser(client, 'testuser', 'password')
    with client as c:
        with c.session_transaction() as sess:
            assert sess['_user_id'] is not None

    client.get('/logout')
    with client as c:
        with c.session_transaction() as sess:
            assert '_user_id' not in sess
