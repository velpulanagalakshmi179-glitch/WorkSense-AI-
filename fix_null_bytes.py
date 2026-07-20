import os

blueprints = ['meetings', 'documents', 'assistant', 'reports', 'email']

for bp in blueprints:
    with open(f'flask_app/blueprints/{bp}.py', 'w', encoding='utf-8') as f:
        f.write(f"from flask import Blueprint\n{bp}_bp = Blueprint('{bp}', __name__)\n")

with open('flask_app/blueprints/__init__.py', 'w', encoding='utf-8') as f:
    f.write('')
