from flask import Flask, render_template, request, make_response, session, redirect, url_for, g 
from flask_session import Session
from database import get_db, close_db
from forms import productCategoryForm , productOrderPreferencesForm, customerLoginForm, customerRegistrationForm, reviewForm, passwordResetForm, adminLoginForm, updateQuantityForm, removeProductForm, addProductForm, sendMessageForm, adminSendMessageForm, indexMens, indexWomens
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_requests(e = None):
    close_db(e)

@app.before_request
def load_logged_in_user():
    g.user = session.get("customer_username", None)
    g.admin = session.get("admin_username", None)

def login_required_user(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next = request.url))
        return view(**kwargs)
    return wrapped_view

def login_required_admin(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for("login", next = request.url))
        return view(**kwargs)
    return wrapped_view


@app.route("/register", methods = ["GET", "POST"])
def register():
    customerForm = customerRegistrationForm()
    if customerForm.validate_on_submit():
        username = customerForm.username1.data
        password = customerForm.password1.data
        db = get_db()
        if db.execute("""SELECT * FROM customers WHERE username = ?;""", (username, )).fetchone() is not None:
            customerForm.username1.errors.append("This username already exists")
        else:
            db.execute("""INSERT INTO customers (username, password) VALUES (?, ?);""", (username, generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
    return render_template("registration.html", customerForm = customerForm)    
        

@app.route("/login", methods = ["GET", "POST"])
def login():
    customerForm = customerLoginForm()
    adminForm = adminLoginForm()
    return render_template("login.html", customerForm = customerForm, adminForm = adminForm)

@app.route("/customer_login", methods = ["GET", "POST"])
def customer_login():
    customerForm = customerLoginForm()
    adminForm = adminLoginForm()
    if customerForm.validate_on_submit():
        username = customerForm.username1.data
        password = customerForm.password1.data
        db = get_db()
        user = db.execute("""SELECT * FROM customers WHERE username = ?;""", (username,)).fetchone()
        if user is None:
            customerForm.username1.errors.append("Invalid Username")
        elif not check_password_hash(user["password"], password):
            customerForm.password1.errors.append("Incorrect Password")
        else:
            session.clear()
            session["customer_username"] = username
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", customerForm = customerForm, adminForm = adminForm)

@app.route("/admin_login", methods = ["GET", "POST"])
def admin_login():
    customerForm = customerLoginForm()
    adminForm = adminLoginForm()
    if adminForm.validate_on_submit():
        username = adminForm.username2.data
        password = adminForm.password2.data
        secret_code = adminForm.secret_code.data

        true_username = "admin1"
        true_password = "THE_passworD"
        true_secret_code = "6789998212"
       
        if username != true_username or password != true_password or secret_code != true_secret_code:
            adminForm.secret_code.errors.append("Log In Failed. Try Again.")
        else:
            session.clear()
            session["admin_username"] = username
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", customerForm = customerForm, adminForm = adminForm)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    db = get_db()

    #Updates hidden fields which are used to display specific products in the '/shop' route
    mensForm = indexMens()
    mensForm.gender.data = "Male"
    mensForm.category.data = "All"
    womensForm = indexWomens()
    womensForm.gender.data = "Female"
    womensForm.category.data = "All"

    #Gets the three most purchased products
    products = db.execute("""SELECT * FROM products WHERE product_id IN (
                                SELECT product_id FROM (
                                    SELECT product_id, COUNT(product_quantity) AS quantity
                                    FROM orders
                                    GROUP BY product_id
                                    ORDER BY quantity DESC
                                    LIMIT 3));""").fetchall()

    return render_template("index.html", products = products, mensForm = mensForm, womensForm = womensForm)
                                        
#Displays All Products
@app.route("/shop", methods = ["GET", "POST"])
def shop():
    form = productCategoryForm()
    mensForm = indexMens()
    womensForm = indexWomens()
    db = get_db()
   
    #Gets the dictinct categories of products and appends it to a form from which a user can narrow down their search for a product
    categories = db.execute("""SELECT DISTINCT category FROM products;""").fetchall()
    choices = [("All", "All")]
    for row in categories:
        for item in row:
            choices.append((item, item))
    form.category.choices = choices
    
    #If the user selects a specific category then only products from that category are presented, otherwise all products are shown
    if form.validate_on_submit():
        category = form.category.data
        gender = form.gender.data
    elif mensForm.validate_on_submit():
        category = mensForm.category.data
        gender = mensForm.gender.data
    elif womensForm.validate_on_submit():
        category = womensForm.category.data
        gender = womensForm.gender.data
    else:
        category =  "All"
        gender = "All"
        
    if category == "All" and gender == "All":
        products = db.execute("""SELECT * FROM products;""").fetchall()
    elif category == "All" and gender != "All":
        products = db.execute("""SELECT * FROM products WHERE gender = ?;""", (gender,)).fetchall()
    elif category != "All" and gender == "All":
        products = db.execute("""SELECT * FROM products WHERE category = ?;""", (category,)).fetchall()
    else:
        products = db.execute("""SELECT * FROM products WHERE category = ? AND gender = ?;""", (category, gender)).fetchall()

    return render_template("shop.html", form = form, products = products)


#Shows a single product and allows the user to add that product to the cart
@app.route("/product/<int:product_id>", methods = ["GET", "POST"])
def product(product_id):
    db = get_db()
    form = productOrderPreferencesForm()
    quantity_demanded = 0
    #Shows all product info
    product = db.execute("""SELECT * FROM products WHERE product_id = ?;""", (product_id,)).fetchone()
    #Gets the average rating of the product which is then used to determine the amount of full and empty stars are shown
    average_rating = db.execute("""SELECT SUM(rating)/COUNT(rating) AS average_rating FROM reviews WHERE product_id = ?;""", (product_id, )).fetchone()["average_rating"]

    if form.validate_on_submit():
        size = form.size.data 
        quantity_demanded = form.quantity.data
        stock = db.execute("""SELECT * FROM stock WHERE product_id = ? AND size = ?;""", (product_id, size)).fetchone()
        quantity_in_stock = stock["quantity"]

        #Checks to see if there is enough of the product in stock. If so, it adds the product to the cart
        if quantity_in_stock >= quantity_demanded:
            return redirect(url_for("add_to_cart", product_id = product['product_id'], quantity = quantity_demanded, size = size))
        else:
            form.quantity.errors.append(f"Sorry! We only have {quantity_in_stock} units in size {size} left in stock.")

    #Gets the three highest rated products other than the product the customer is viewing
    products = db.execute("""SELECT * FROM products WHERE product_id IN (
                                SELECT product_id FROM (
                                    SELECT DISTINCT product_id, SUM(rating)/COUNT(rating) AS average_ratings
                                    FROM reviews
                                    WHERE product_id != ?
                                    GROUP BY product_id
                                    ORDER BY average_ratings DESC
                                    LIMIT 3));""", (product_id, )).fetchall()

    return render_template("product.html", form = form, product = product, average_rating = average_rating, products = products)
    

#Adds a product in a specific size to the cart
@app.route("/add_to_cart/<int:product_id>/<size>/<int:quantity>")
@login_required_user
def add_to_cart(product_id,size, quantity):
    if "cart" not in session:
        session["cart"] = {}
    if product_id not in session["cart"]:
        session["cart"][product_id] = {}
    if size not in session["cart"][product_id]:
        session["cart"][product_id][size] = 0
     
    session["cart"][product_id][size] += quantity
    return redirect(url_for('cart'))


#Shows the user their cart and the total amount to be paid
@app.route("/cart")
@login_required_user
def cart():
    if "cart" not in session:
        session["cart"] = {}

    productInfo = {}
    subTotal = 0
    delivery = 0.00
    db = get_db()

    #Gets info on every item in the cart
    for product_id in session["cart"]:
        query = db.execute("""SELECT * FROM products WHERE product_id = ?""",(product_id,)).fetchone()
        name = query["name"]
        price_per_unit = query["price"]
        productInfo[product_id] = []
        productInfo[product_id].append(name)
        productInfo[product_id].append(price_per_unit)

        #Calculates the total price to be paid
        for size in session["cart"][product_id]:
            quantity = session["cart"][product_id][size]
            subTotal += quantity * price_per_unit

    subTotal = round(subTotal,2)
    total = round(subTotal + delivery, 2)
    return render_template("cart.html", cart = session["cart"], productInfo = productInfo, subTotal = subTotal, delivery = delivery, total = total)


#Removes a product in a specific size from the cart
@app.route("/remove_from_cart/<int:product_id>/<size>")
@login_required_user
def remove_from_cart(product_id, size):
    del session["cart"][product_id][size]
    return redirect(url_for('cart'))
  

#Confirms the customers purchase by adding the necessary info into the db's
@app.route("/order_products")
@login_required_user
def order_products():
    db = get_db()
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for product_id in session["cart"]:
        query = db.execute("""SELECT * FROM products WHERE product_id = ?;""", (product_id,)).fetchone()
        price_per_unit = query["price"]
        
        for size in session["cart"][product_id]:
            quantity = session["cart"][product_id][size]

            #Inserts customers order into the db
            cost = price_per_unit * quantity
            cost = round(cost, 2)
            db.execute("""INSERT INTO orders (username, product_id, product_size, product_quantity, date_of_order, order_cost) 
                    VALUES (?, ?, ?, ?, ?, ?);""", (g.user, product_id, size, quantity, current_date, cost))
            db.commit()

            #Updates the quantity of the product left in stock 
            db.execute("""UPDATE stock SET quantity = quantity - ? WHERE product_id = ? AND size = ?;""", (quantity, product_id, size))
            db.commit()

    #Sends a confirmation message to the customer
    message = f"Thank you for your order {g.user}."
    db.execute("""INSERT INTO messages (sender, recipient, message, date_sent) VALUES (?,?,?,?);""", ("admin", g.user, message, current_date))
    db.commit()

    session.clear()
    return redirect(url_for('cart'))
    
#Shows reviews of a specific product and allows a signed-in user who has purchased that product to leave a review
@app.route("/reviews/<int:product_id>", methods = ["GET", "POST"])
def reviews(product_id):
    form = reviewForm()
    db = get_db()
    if form.validate_on_submit():
        if g.user is None:
            form.review.errors.append("You must be signed in to leave a review.")
        #Checks to see if the user has purchased the product before
        elif db.execute("""SELECT * FROM orders WHERE product_id = ? AND username = ?;""", (product_id, g.user)).fetchone() is None:
            form.review.errors.append("You must have purchased this product if you wish to leave a review")
        else:
            review = form.review.data
            rating = form.rating.data
            current_date = datetime.now().strftime("%Y-%m-%d")
            #Inserts a review into the review db
            db.execute("""INSERT INTO reviews (username, product_id, review, date_of_review , rating) 
                            VALUES (?, ?, ?, ?, ?);""",(g.user, product_id, review, current_date, rating))
            db.commit()
    #Shows all reviews of a specific product
    reviews = db.execute("""SELECT * FROM reviews WHERE product_id = ? ORDER BY date_of_review DESC;""", (product_id,)).fetchall()
    return render_template("reviews.html", form = form, reviews = reviews, product_id = product_id)


#Allows the admin to perform admin-only actions
@app.route("/admin", methods = ["GET", "POST"])
@login_required_admin
def admin():
    db = get_db()
    updateQuantity = updateQuantityForm()
    removeProduct = removeProductForm()
    addProduct = addProductForm()
    messageForm = adminSendMessageForm()
    orders = db.execute("""SELECT * FROM orders;""").fetchall()
    total_income = db.execute("""SELECT SUM(order_cost) FROM orders;""").fetchone()
    products = db.execute("""SELECT * FROM stock;""").fetchall()
    messages = db.execute("""SELECT * FROM messages WHERE recipient = ? ORDER BY date_sent DESC;""", ("admin", )).fetchall()

    #Allows the admin to send a message to a customer
    if messageForm.validate_on_submit():
        message = messageForm.message.data
        recipient = messageForm.recipient.data
        current_date = datetime.now().strftime("%Y-%m-%d")
        db.execute("""INSERT INTO messages (sender, recipient, message, date_sent) VALUES (?, ?, ?, ?);""", ("admin", recipient, message, current_date))
        db.commit()

    return render_template("admin.html", orders = orders, total_income = total_income, products = products, form = updateQuantity, removeProductForm = removeProduct, addProductForm = addProduct, adminSendMessageForm = messageForm, messages = messages)


#Allows the admin to update the quantity in stock of a specific product in a specific size 
@app.route("/update_quantity", methods = ["GET", "POST"])
@login_required_admin
def update_quantity():
    form = updateQuantityForm()
    if form.validate_on_submit():
        id = form.id.data
        size = form.size.data
        quantity = form.quantity.data
        db = get_db()
        if db.execute("""SELECT * FROM stock WHERE product_id = ? and size = ?;""", (id, size)).fetchone() is not None:
            db.execute("""UPDATE stock SET quantity = quantity + ? WHERE product_id = ? AND size = ?;""", (quantity, id, size))
        else:
            db.execute("""INSERT INTO stock (product_id, size, quantity) VALUES (?,?,?);""", (id, size, quantity))
        db.commit()    
    return redirect(url_for('admin'))

#Allows the admin to remove a specific product from the db's
@app.route("/remove_product", methods = ["GET", "POST"])
@login_required_admin
def remove_product():
    form = removeProductForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        db = get_db()
        db.execute("""DELETE FROM products WHERE product_id = ?;""", (product_id,))
        db.commit()
        db.execute("""DELETE FROM stock WHERE product_id = ?;""", (product_id, ))
        db.commit()
    return redirect(url_for('admin'))

#Allows the admin to add a brand new product to the website
@app.route("/add_product", methods = ["GET", "POST"])
@login_required_admin
def add_product():
    form = addProductForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        description = form.description.data
        category = form.category.data
        gender = form.gender.data
        
        #Checks if the file the user is uploading is secure. If so, it uploads the image to the 'static' folder
        image = form.image.data
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        #Adds new product to the database
        db = get_db()
        if db.execute("""SELECT * FROM products WHERE image_url = ?;""", (filename,)).fetchone() is None:
            db.execute("""INSERT INTO products (name, price, description, category, gender, image_url)
                VALUES (?,?,?,?,?,?);""", (name, price, description, category, gender, filename))
            db.commit()
        else:
            form.image.errors.append("Error. File Name is not unique")

    return redirect(url_for('admin'))

#Allows the user to change their password, see their past orders, see their messages and send a message
@app.route("/account", methods = ["GET", "POST"])
@login_required_user
def account():
    passwordForm = passwordResetForm()
    messageForm = sendMessageForm()
    confirmation = ""
    db = get_db()

    #Changes the users password
    if passwordForm.validate_on_submit():
        old_password = passwordForm.old_password.data
        new_password = passwordForm.new_password.data
        confirmation = "You have successfully changed your password."
        user = db.execute("""SELECT * FROM customers WHERE username = ?;""", (g.user,)).fetchone()
        if not check_password_hash(user["password"], old_password):
            passwordForm.old_password.errors.append("Incorrect Password")
        else:
            db.execute("""UPDATE customers SET password = ? WHERE username = ?;""", (generate_password_hash(new_password), g.user))
            db.commit()

    #Shows the users past orders
    past_orders = db.execute("""SELECT * 
                                FROM orders AS o
                                JOIN products AS p 
                                ON o.product_id = p.product_id 
                                WHERE o.username = ?
                                ORDER BY o.date_of_order DESC;""", (g.user,)).fetchall()     
    #Shows the users messages from the admin                  
    messages = db.execute("""SELECT * FROM messages WHERE recipient = ? ORDER BY date_sent DESC;""", (g.user,)).fetchall()
    return render_template("account.html", passwordResetForm = passwordForm, sendMessageForm = messageForm, past_orders = past_orders, messages = messages, confirmation = confirmation )

#Allows the user to send a message to the admin
@app.route("/messages", methods = ["GET", "POST"])
@login_required_user
def messages():
    form = sendMessageForm()
    db = get_db() 
    if form.validate_on_submit():
        message = form.message.data
        current_date = datetime.now().strftime("%Y-%m-%d")
        db.execute("""INSERT INTO messages (sender, recipient, message, date_sent) VALUES (?, ?, ?, ?);""", (g.user, "admin", message, current_date))
        db.commit()
    return redirect(url_for('account'))
