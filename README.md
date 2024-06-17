# Recipe Manager API

## Overview
Recipe Manager is a RESTful API built with Flask that allows users to manage recipes.

## Features
- User Registration and Login
- Create, Read, Update, Delete Recipes
- Get all users and recipes
- Search recipes

## Endpoints
- `/register` - User registration
- `/login` - User login
- `/logout` - User logout
- `/recipe` - Create a new recipe (POST)
- `/recipe/<id>` - Get a recipe (GET), Update a recipe (PUT), Delete a recipe (DELETE)
- `/recipes` - Get all recipes
- `/users` - Get all users
- `/recipes/search` - Search recipes based on title and ingredients, also it has pagination


## Setup Instructions
- Navigate to the project directory and create a virtual environment:
    python3 -m venv venv
    source venv/bin/activate

- Install the required dependencies:
    pip install -r requirements.txt

- Set Flask app and environment variables
    set FLASK_APP=manage.py
    set FLASK_ENV=development

- Initialize the database:
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade

- Run the application:
    flask run

## Testing
- To run the tests, use the following command:
    pytest
