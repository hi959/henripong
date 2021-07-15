import random
from flask import Flask, render_template, url_for, redirect, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FileField, FloatField, PasswordField, TextField
from wtforms.validators import DataRequired, Length
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLAlCHEMY_TRACK_MODIFICATION'] = False
app.config['SECRET_KEY'] = "1428kjhg"
app.config['UPLOADED_IMAGES_DEST'] = 'static/images/products'
app.config['UPLOADED_GALLERY_DEST'] = 'static/images/gallery'
app.permanent_session_lifetime = timedelta(minutes=30)
db = SQLAlchemy(app)


images = UploadSet('images', IMAGES)
gallery = UploadSet('gallery', IMAGES)
configure_uploads(app, images)
configure_uploads(app, gallery)


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


# GALLERY-START
class GalleryForm(FlaskForm):
    image = FileField("הוסף תמונה או סרטון")
    text = StringField("טקסט לתמונה", validators=[Length(max=20)])


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.Text(20), nullable=True)
    imageName = db.Column(db.Text)
    width = db.Column(db.Text)
    height = db.Column(db.Text)
# GALLERY-END


class ChangeForm(FlaskForm):
    image_name = StringField("שם התמונה")
    submish = SubmitField("שנה מוצר")


class Login(FlaskForm):
    username = StringField('שם משתמש')
    password = PasswordField('סיסמה')


@app.route('/')
def home():

    items = Items.query.order_by(Items.price).all()
    chosed = []
    while len(chosed) < 8:
        good = random.choice(items)
        if good not in chosed:
            chosed.append(good)

    return render_template('home.html', data=chosed)  #צריך להוסיף , data=chosed


@app.route('/gallery/')
def gallerypage():
    images = Gallery.query.all()
    return render_template('gallery.html', images=images)


@app.route('/add-image', methods=['GET', 'POST'])
def addImage():
    if "loged" in session:
        form = GalleryForm()
        if form.validate_on_submit():
            all_height = ['h-1', 'h-2', 'h-3', 'h-4', 'h-5', 'h-6']
            all_width = ['w-1', 'w-2', 'w-3', 'w-4', 'w-5', 'w-6']
            image = form.image.data
            imagename = gallery.save(image)
            text = form.text.data
            width = random.choice(all_width)
            height = random.choice(all_height)
            if width == 'w-5' or 'w-6':
                if random.choice(['true', 'false']) == 'true':
                    width = random.choice(all_width)
                else:
                    pass
            if height == 'h-5' or 'h-6':
                if random.choice(['true', 'false']) == 'true':
                    width = random.choice(all_width)
                else:
                    pass

            item = Gallery(text=text, imageName=imagename, width=width, height=height)
            print(text+'   '+imagename+'   '+width+'   '+height)
            try:
                db.session.add(item)
                db.session.commit()
                return redirect(url_for("addImage"))
            except:
                return "נמצאה בעיה"

        return render_template('add_to_gallery.html', form=form)
    else:
        return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if request.method == "POST":
        if request.form["username"] == "henri" and request.form["password"] == "123456":
            session["loged"] = "loged"
            return redirect(url_for("addImage"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template('login.html', form=form)


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
            return redirect('https://pongexamplefinal.herokuapp.com/create')
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
    app.run(debug=True)
