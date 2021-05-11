import random
from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField, FloatField
from wtforms.validators import DataRequired, Length
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLAlCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = "1428kjhg"
app.config['UPLOADED_IMAGES_DEST'] = 'static/images/products'
db = SQLAlchemy(app)


images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class CreateForm(FlaskForm):
    title = StringField("שם של המוצר", validators=[DataRequired(), Length(min=2, max=70)])
    price = FloatField("מחיר של המוצר", validators=[DataRequired()])
    shortDescribe = StringField("תיאור קצר", validators=[DataRequired(), Length(max=100)])
    describe = StringField("תיאור ארוך")
    image_name = FileField("תמונה או ג'יפ")
    submit = SubmitField("הוסף מוצר")


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    shortDescribe = db.Column(db.Text, nullable=False)
    describe = db.Column(db.Text, nullable=True)
    imageName = db.Column(db.Text)

    def __repr__(self):
        return self.title


class ChangeForm(FlaskForm):
    image_name = StringField("שם התמונה")
    submish = SubmitField("שנה מוצר")


@app.route('/')
def home():
    items = Items.query.order_by(Items.price).all()
    chosed = []
    while len(chosed) < 8:
        good = random.choice(items)
        if good not in chosed:
            chosed.append(good)

    return render_template('home.html', data=chosed)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():

    items = Items.query.order_by(Items.price).all()
    name = None
    form = CreateForm()

    if form.validate_on_submit():
        title = form.title.data
        price = form.price.data
        shortdescribe = form.shortDescribe.data
        image = form.image_name.data
        print(image)
        filename = images.save(image)
        if form.describe.data is None:
            pass
        else:
            describe = form.describe.data

        item = Items(title=title, price=price, shortDescribe=shortdescribe, describe=describe, imageName=filename)

        print(f"filename is: {filename}")

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('http://127.0.0.1:5000/create')
        except:
            return "נמצאה בעיה"
    else:
        return render_template("create.html", name=name, form=form, data=items)


@app.route('/change/<int:id>', methods=['GET', 'POST'])
def change(id):

    form = CreateForm()
    name = None
    name_to_change = Items.query.get_or_404(id)

    if form.validate_on_submit():
        name_to_change.title = form.title.data
        print(name_to_change.title)
        name_to_change.price = form.price.data
        name_to_change.shortDescribe = form.shortDescribe.data
        image = form.image_name.data
        filename = images.save(image)
        name_to_change.imageName = filename

        print(f"filename is: {filename}")

        try:
            db.session.commit()
            print("worked!")
            return redirect('http://127.0.0.1:5000/create')
        except:
            print("didnt work!")
            return render_template("update.html",
                                   form=form,
                                   name_to_change=name_to_change)
    else:
        return render_template("update.html",
                               form=form,
                               name_to_change=name_to_change)


if __name__ == '__main__':
    app.run()
