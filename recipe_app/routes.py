from flask import Flask, render_template, flash, redirect, url_for, request
import requests
from recipe_app.models import User, History,Liked
from flask_login import login_user, current_user, logout_user, login_required
from recipe_app.forms import RegistrationForm, LoginForm
from recipe_app import app, db, bcrypt




@app.route('/', methods=["POST","GET"])
@app.route('/home', methods=["POST","GET"])
def home():
    all_recipe=[]
    url ='https://www.themealdb.com/api/json/v1/1/search.php?s={}'
    if request.method == 'POST':
        food_name = request.form['name']
        r = requests.get(url.format(food_name)).json()

        #print(r)
        try:

            for i in range(0,len(r['meals'])):
                food={
                    'title' : r['meals'][i]['strMeal'],
                    'id' : r['meals'][i]['idMeal'],
                    #'ingredient': r['results'][i]['ingredients'],
                    'youtube': r['meals'][i]['strYoutube'],
                    'picture':r['meals'][i]['strMealThumb']
                    }

                all_recipe.append(food)

        except:
            flash("Your sentence isn't correct", "danger")
            return redirect(url_for("home"))


    return render_template('home.html',all_recipe=all_recipe)

@app.route("/recipe/<int:id>")
def recipe_page(id):
    ingredients = []
    measure = []
    i=0
    ingredient_for_loop = "strIngredient"
    measure_for_loop = "strMeasure"
    saved = ""
    url ="https://www.themealdb.com/api/json/v1/1/lookup.php?i={}"
    r = requests.get(url.format(id)).json()
    #print(r)
    while True:
        i+=1
        try:
            ingredients.append(r["meals"][0][ingredient_for_loop+str(i)])
            measure.append(r["meals"][0][measure_for_loop+str(i)])

        except:
            break
    recipe={
        'title' : r['meals'][0]['strMeal'],
        'ingredients': ingredients,
        'youtube': r['meals'][0]['strYoutube'],
        'picture':r['meals'][0]['strMealThumb'],
        'measures':measure,
        'instruction':r['meals'][0]['strInstructions']
            }
    if current_user.is_authenticated:
        saved = Liked.query.filter_by(user_id=current_user.id,recipe_id=id).first()

        if saved:
            saved = "It's saved"
        user = History(title=r['meals'][0]['strMeal'],user_id=current_user.id,recipe_id=id)
        db.session.add(user)
        db.session.commit()



    return render_template('recipe.html',recipe=recipe, saved=saved,id=id)
@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        check_username = User.query.filter_by(username=form.username.data).first()
        check_email = User.query.filter_by(username=form.email.data).first()
        print(check_email)
        if check_username:
            flash(f'That username is taken. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        elif check_email:
            flash(f'That email is taken. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/history")
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    #history = History.query.filter_by(user_id=current_user.id)
    history = History.query.filter_by(searcher=user)\
    .order_by(History.date_searched.desc())\
    .paginate(page=page, per_page=20)
    #print(saved)
    return render_template('history.html',history = history)
@app.route("/saved")
@login_required
def saved():
    page = request.args.get('page', 1, type=int)

    user = User.query.filter_by(username=current_user.username).first_or_404()

    history = Liked.query.filter_by(liker=user)\
    .order_by(Liked.date_searched.desc())\
    .paginate(page=page, per_page=10)


    #print(saved)
    return render_template('saved.html',history = history)

@app.route("/save/<int:id>")
@login_required
def save(id):
    url ="https://www.themealdb.com/api/json/v1/1/lookup.php?i={}"
    r = requests.get(url.format(id)).json()
    user = Liked(title=r['meals'][0]['strMeal'],user_id=current_user.id,recipe_id=id)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('recipe_page',id=id))


@app.route("/delete/<int:id>")
@login_required
def delete_recipe(id):
    print("It working")
    saved = Liked.query.get_or_404(id)
    print(saved)
    if saved.liker != current_user:
        abort(403)
    db.session.delete(saved)
    db.session.commit()
    flash('Your saved recipe has been deleted from your list!', 'success')
    return redirect(url_for('saved'))
