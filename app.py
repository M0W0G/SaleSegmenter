from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    render_template_string,
    Markup
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import jinja2
import os
import base64



app = Flask(__name__)

@app.template_filter('b64encode')
def b64encode_filter(data):
    encoded_data = base64.b64encode(data)
    return encoded_data.decode('utf-8')

# Set maximum upload file size to 50 megabytes
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sales.db"
db = SQLAlchemy(app)


# Define the Sale model
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    photographs = db.Column(db.LargeBinary, nullable=True)


# Route for the homepage
@app.route("/")
def index():
    return render_template("index.html")


# Route to display form for creating a sale
@app.route("/create_sale")
def create_sale():
    return render_template("create_sale.html")


# Route to add a new sale
@app.route("/add_sale", methods=["POST"])
def add_sale():
    name = request.form["name"]
    date_str = request.form["date"]  # Get the date string from the form
    date = datetime.strptime(
        date_str, "%Y-%m-%d"
    ).date()  # Convert the date string to a Python date object
    url = request.form["url"]

    # Check if the file is included in the request
    if "image" not in request.files:
        return "No file part"

    image_file = request.files["image"]

    # If the user does not select a file, the browser submits an empty file without a filename.
    if image_file.filename == "":
        return "No selected file"

    # Check if the file is an allowed type
    if image_file and allowed_file(image_file.filename):
        # Process the image file
        photographs = image_file.read()
    else:
        # Return an error if the file type is not allowed
        return "File type not allowed"

    new_sale = Sale(name=name, date=date, url=url, photographs=photographs)
    db.session.add(new_sale)
    db.session.commit()

    return redirect(url_for("view_sales"))


# Route to view existing sales
@app.route("/view_sales")
def view_sales():
    with app.app_context():  # Ensures that operations are performed within the application context
        sales = Sale.query.all()
        return render_template("view_sales.html", sales=sales)


# Route to delete all sales
@app.route("/delete_all_sales", methods=["POST"])
def delete_all_sales():
    with app.app_context():  # Ensure operations are performed within the application context
        # Delete all rows in the Sale table
        Sale.query.delete()

        # Commit the changes to the database
        db.session.commit()

    return redirect(url_for("index"))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "gif",
    }


if __name__ == "__main__":
    with app.app_context():  # Ensures that operations are performed within the application context
        db.create_all()
    app.run(debug=True)
