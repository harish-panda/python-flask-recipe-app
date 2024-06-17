from flask import Blueprint, request, jsonify, abort, session
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
from app import db, bcrypt
from app.models import User, Recipe
from datetime import timedelta

router = Blueprint('main', __name__)


# Route for user registration
@router.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # Check if user already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'User already exists!'}), 400
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(username=data['username'], password=hashed_password, is_admin=data.get('isAdmin', False))
        db.session.add(user)
        db.session.commit()
        session.permanent = True
        router.permanent_session_lifetime = timedelta(hours=1)
        return jsonify({'message': 'Account created successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for user login
@router.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            login_user(user)
            session.permanent = True
            router.permanent_session_lifetime = timedelta(hours=1)
            return jsonify({'message': 'Login successful!'}), 200
        return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for user logout
@router.route('/logout', methods=['GET'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for creating a new recipe
@router.route('/recipe', methods=['POST'])
@login_required
def createRecipe():
    try:
        data = request.get_json()
        recipe = Recipe(title=data['title'], description=data['description'],
                        ingredients=data['ingredients'], instructions=data['instructions'],
                        author=current_user)
        db.session.add(recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe created successfully!', 'recipeId': recipe.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for retrieving a recipe by ID
@router.route('/recipe/<int:recipe_id>', methods=['GET'])
def getRecipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        return jsonify({'title': recipe.title, 'description': recipe.description,
                        'ingredients': recipe.ingredients, 'instructions': recipe.instructions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for updating a recipe by ID
@router.route('/recipe/<int:recipe_id>', methods=['PUT'])
@login_required
def updateRecipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        # Checking if current user is the author of the recipe
        if recipe.author != current_user:
            return jsonify({'error': 'You cannot update this recipe!'}), 403
        data = request.get_json()
        recipe.title = data['title']
        recipe.description = data['description']
        recipe.ingredients = data['ingredients']
        recipe.instructions = data['instructions']
        db.session.commit()
        return jsonify({'message': 'Recipe updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for deleting a recipe by ID
@router.route('/recipe/<int:recipe_id>', methods=['DELETE'])
@login_required
def deleteRecipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        # Checking if current user is the author of the recipe
        if recipe.author != current_user:
            return jsonify({'error': 'You cannot delete this recipe!'}), 403
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for retrieving all recipes
@router.route('/recipes', methods=['GET'])
def getAllRecipes():
    try:
        recipes = Recipe.query.all()
        recipe_list = []
        for recipe in recipes:
            recipe_list.append({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions
            })
        return jsonify({'recipes': recipe_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for retrieving all users (admin access required)
@router.route('/users', methods=['GET'])
@login_required
def getUsers():
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized access!'}), 403
        users = User.query.all()
        user_list = [{'username': user.username, 'id': user.id} for user in users]
        return jsonify({'users': user_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for searching recipes by title or ingredients
@router.route('/recipes/search', methods=['GET'])
def searchRecipes():
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('perPage', 10, type=int)
        if not query:
            abort(400, 'Query parameter "q" is required for search.')
        
        recipes = Recipe.query.filter(or_(Recipe.title.ilike(f'%{query}%'),
                                          Recipe.ingredients.ilike(f'%{query}%'))) \
                              .paginate(page=page, per_page=per_page, error_out=False)
        recipe_list = []
        for recipe in recipes.items:
            recipe_list.append({
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions
            })
        return jsonify({
            'recipes': recipe_list,
            'totalPages': recipes.pages,
            'currentPage': recipes.page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
