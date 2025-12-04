# app.py

from flask import Flask
from api.routes.books import books_bp
from api.routes.users import users_bp
from api.routes.authors import authors_bp
from api.routes.orders import orders_bp

app = Flask(__name__)

app.register_blueprint(books_bp)
app.register_blueprint(users_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(orders_bp)

if __name__ == '__main__':
    app.run(debug=True)
