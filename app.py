from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
db = SQLAlchemy(app)

# Define the Sale model
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    photographs = db.Column(db.String(200), nullable=False)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to display form for creating a sale
@app.route('/create_sale')
def create_sale():
    return render_template('create_sale.html')

# Route to add a new sale
@app.route('/add_sale', methods=['POST'])
def add_sale():
    name = request.form['name']
    date_str = request.form['date']
    url = request.form['url']
    photographs = request.form['photographs']

    # Convert date string to a Python date object
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    new_sale = Sale(name=name, date=date, url=url, photographs=photographs)
    db.session.add(new_sale)
    db.session.commit()

    return redirect(url_for('view_sales'))

# Route to view existing sales
@app.route('/view_sales')
def view_sales():
    with app.app_context():  # Ensures that operations are performed within the application context
        sales = Sale.query.all()
        return render_template('view_sales.html', sales=sales)

if __name__ == '__main__':
    with app.app_context():  # Ensures that operations are performed within the application context
        db.create_all()
    app.run(debug=True)
