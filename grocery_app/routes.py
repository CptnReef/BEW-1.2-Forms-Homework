from flask import Blueprint, request, render_template, redirect, url_for, flash
from datetime import date, datetime
from grocery_app.models import GroceryStore, GroceryItem, User
# from grocery_app.forms import GroceryStoreForm, GroceryItemForm
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, LoginForm, SignUpForm
from flask_login import login_required, login_user, logout_user, current_user

# Import app and db from events_app package so that we can run app
from grocery_app import app, db, bcrypt

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    print(all_stores)
    return render_template('home.html', all_stores=all_stores)

@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    # TODO: Create a GroceryStoreForm
    groceryStoreForm = GroceryStoreForm()

    # TODO: If form was submitted and was valid:
    # - create a new GroceryStore object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the store detail page.
    if groceryStoreForm.validate_on_submit():
        newGroceryStore = GroceryStore(
            title=groceryStoreForm.title.data,
            address=groceryStoreForm.address.data,
            created_by=current_user
        )
        db.session.add(newGroceryStore)
        db.session.commit()
        flash('Success')

        return redirect(url_for('main.store_detail', store_id=newGroceryStore.id))

    # TODO: Send the form to the template and use it to render the form fields
    return render_template('new_store.html', groceryStoreForm=groceryStoreForm, current_user=current_user)

@main.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    # TODO: Create a GroceryItemForm
    groceryItemForm = GroceryItemForm()

    # TODO: If form was submitted and was valid:
    # - create a new GroceryItem object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the item detail page.
    if groceryItemForm.validate_on_submit():
        newGroceryItem = GroceryItem(
            name=groceryItemForm.name.data,
            price=groceryItemForm.price.data,
            category=groceryItemForm.category.data,
            photo_url=groceryItemForm.photo_url.data,
            store=groceryItemForm.store.data,
            created_by=current_user
        )
        db.session.add(newGroceryItem)
        db.session.commit()
        flash('Success')
        # Send to created GroceryItem page 
        return redirect(url_for('main.item_detail', item_id=newGroceryItem.id))

    # TODO: Send the form to the template and use it to render the form fields
    return render_template('new_item.html', groceryItemForm=groceryItemForm, current_user=current_user)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
@login_required
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    # TODO: Create a GroceryStoreForm and pass in `obj=store`
    groceryStoreForm = GroceryStoreForm(obj=store)

    # TODO: If form was submitted and was valid:
    # - update the GroceryStore object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the store detail page.
    
    if groceryStoreForm.validate_on_submit():
        store.title = groceryStoreForm.title.data
        store.address = groceryStoreForm.address.data
        db.session.commit()
        flash('Success')
        return redirect(url_for('main.store_detail', store_id=store_id))

    # TODO: Send the form to the template and use it to render the form fields
    store = GroceryStore.query.get(store_id)
    return render_template('store_detail.html', store=store, groceryStoreForm=groceryStoreForm, current_user=current_user)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
@login_required
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    # TODO: Create a GroceryItemForm and pass in `obj=item`
    groceryItemForm = GroceryItemForm(obj=item)
    
    # TODO: If form was submitted and was valid:
    # - update the GroceryItem object and save it to the database,
    # - flash a success message, and
    # - redirect the user to the item detail page.
    if groceryItemForm.validate_on_submit():
        item.name = groceryItemForm.name.data
        item.price = groceryItemForm.price.data
        item.category = groceryItemForm.category.data
        item.photo_url = groceryItemForm.photo_url.data
        item.store = groceryItemForm.store.data
        db.session.commit()
        flash('Success')
        # Send to updated GroceryItem page (same resource) 
        return redirect(url_for('main.item_detail', item_id=item_id))

    # TODO: Send the form to the template and use it to render the form fields
    item = GroceryItem.query.get(item_id)
    return render_template('item_detail.html', item=item, groceryItemForm=groceryItemForm, current_user=current_user)

@main.route('/shopping_list', methods=['GET'])
@login_required
def shopping_list():
    return render_template('shopping_list.html')

######################################################################################################
######################################################################################################
######################################################################################################

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        print('created')
        return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form, current_user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form, current_user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))