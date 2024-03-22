import sys
sys.path.append('/home/ec2-user/environment')
import pytest
from flask import Flask, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
# from your_app_module import app, db, User, Product, insert_user_if_not_exists
from ProductRegistrationApp import ProdRegApp
from ProductRegistrationApp.ProdRegApp import app,db, User, Product,insert_user_if_not_exists
from datetime import datetime

# manufacture_date = datetime.strptime(data['manufacture_date'], '%Y-%m-%d').date()
@pytest.fixture
def client():
    app.config['TESTING'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_registration.db'
    app.config['SQLALCHEMY_ECHO'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a dummy user for testing
            user = insert_user_if_not_exists('test_user2', generate_password_hash('password'))
            db.session.commit()
        yield client

def test_login(client):
    response = client.post('/login', json={'username': 'test_user2', 'password': 'password'})
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data

def test_register_product(client):
    login_response = client.post('/login', json={'username': 'test_user2', 'password': 'password'})
    assert login_response.status_code == 200
    date_str = '2022-03-25'

    response = client.post('/products', json={
        'product_name': 'Test Product123',
        'product_description': 'This is a test product',
        'manufacturer_info': 'Test Manufacturer',
        'serial_number': '123',
        
        'manufacture_date': date_str,
        'product_category': 'Test Category'
    })
    if response.status_code == 201:
        assert response.status_code == 201
        assert b'Product registered successfully' in response.data
    else:
        assert response.status_code == 409
        assert b'Serial number already exists' in response.data

def test_get_products(client):
    login_response = client.post('/login', json={'username': 'test_user2', 'password': 'password'})
    assert login_response.status_code == 200
    date_str = '2022-03-25'

    # Register a product for testing retrieval
    client.post('/products', json={
        'product_name': 'Test Product123',
        'product_description': 'This is a test product',
        'manufacturer_info': 'Test Manufacturer',
        'serial_number': '123',
        'manufacture_date': date_str,
        'product_category': 'Test Category'
    })

    response = client.get('/products')
    assert response.status_code == 200
    assert b'Test Product' in response.data

def test_update_product(client):
    login_response = client.post('/login', json={'username': 'test_user2', 'password': 'password'})
    assert login_response.status_code == 200

    # Register a product for testing update
    client.post('/products', json={
        'product_name': 'Test Product123',
        'product_description': 'This is a test product',
        'manufacturer_info': 'Test Manufacturer',
        'serial_number': '123',
        'manufacture_date': '2022-03-25',
        'product_category': 'Test Category'
    })

    response = client.get('/products')
    assert response.status_code == 200
    products = response.json.get('products', [])
    assert len(products) == 1
    product_id = products[0].get('id')
    print("**********************")
    print(product_id)
    print("**************ddddddddddddd********")

    update_response = client.put(f'/products/{product_id}', json={'product_name': 'Updated Product'})
    assert update_response.status_code == 200
    assert b'Product updated successfully' in update_response.data

def test_delete_product(client):
    login_response = client.post('/login', json={'username': 'test_user2', 'password': 'password'})
    assert login_response.status_code == 200

    # Register a product for testing deletion
    client.post('/products', json={
        'product_name': 'Test Product123',
        'product_description': 'This is a test product',
        'manufacturer_info': 'Test Manufacturer',
        'serial_number': '123',
        'manufacture_date': '2022-03-25',
        'product_category': 'Test Category'
    })

    response = client.get('/products')
    assert response.status_code == 200
    products = response.json.get('products', [])
    assert len(products) == 1
    product_id = products[0].get('id')

    delete_response = client.delete(f'/products/{product_id}')
    assert delete_response.status_code == 200
    assert b'Product deleted successfully' in delete_response.data
