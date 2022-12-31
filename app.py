from flask import Flask, render_template, request, redirect, session
import psycopg2
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'epic_secret_key'
phone_pattern = r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$"
email_pattern = r"[^@]+@[^@]+\.[^@]+"


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='Database_Project',
                            user="postgres",
                            password="Mustafa2323")
    return conn


conn = get_db_connection()
cur = conn.cursor()


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    status = ""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cur.execute(f"SELECT id,user_name FROM users WHERE email = '{email}' AND password = '{password}'")
        status = cur.fetchall()
        status = [tuple for sublist in status for tuple in sublist]
        if status != []:
            session["uname"] = status[1]
            session["id"] = status[0]
            return redirect("/home")
        else:
            return render_template("login.html", status="False email or password")
    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("pass")
        phone = request.form.get("phone")
        email = request.form.get("email")
        gender = request.form.get("gender")
        age = request.form.get("age")
        weight = request.form.get("weight")
        height = request.form.get("height")
        date = datetime.now().strftime("%Y-%m-%d")
        if not re.match(phone_pattern, phone):
            return render_template("register.html", status='<p>Invalid Phone Number</p>')
        if not re.match(email_pattern, email):
            return render_template("register.html", status='<p>Invalid Email</p>')
        if password != request.form.get("pass-confirm"):
            return render_template("register.html", status='<p>Passwords not equal</p>')
        query = "INSERT INTO public.users(user_name, phone, email, password, gender, age, weight,created_at, height)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        values = (uname, phone, email, password, gender, age, weight, date, height)
        cur.execute(query, values)
        conn.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/home", methods=['GET', 'POST'])
def home():
    # For table
    cur.execute(
        f"SELECT f.food_name, mel.name, f.calorie, mac.macro_name, f.created_at FROM foods f JOIN macros mac ON mac.id = f.macro_id JOIN meals mel ON mel.id = f.meal_id WHERE f.user_id = {session['id']}")
    food_info = cur.fetchall()
    food_info = [tuple for sublist in food_info for tuple in sublist]

    food_info = [food_info[i:i + 5] for i in range(0, len(food_info), 5)]
    # For calculator
    cur.execute(f"SELECT height,weight,age FROM users WHERE id = {session['id']}")
    calc_info = cur.fetchall()
    calc_info = [tuple for sublist in calc_info for tuple in sublist]
    # For Sum Calories
    created_at = datetime.now().strftime("%Y-%m-%d")
    cur.execute(f"SELECT SUM(calorie) as total_calories FROM foods WHERE user_id = {session['id']} AND created_at = '{created_at}' UNION ALL SELECT SUM(burning_calories) as total_calories FROM exercises WHERE user_id = {session['id']} AND created_at = '{created_at}'")
    all_calories = cur.fetchall()
    all_calories = [tuple for sublist in all_calories for tuple in sublist]
    sum_calories = sum_calorie(all_calories)

    if request.method == "POST":
        if request.form.get("meal_button"):
            food_name = request.form.get("food_name")
            meal_name = request.form.get("meal")
            macro_name = request.form.get("macro")
            calorie = request.form.get("calorie")
            """cur.execute(
                f"INSERT INTO foods (food_name, calorie, meal_id,user_id, macro_id) SELECT  '{food_name}', {calorie}, m.id, {session['id']}, ma.id FROM meals m, macros ma WHERE m.name = '{meal_name}' AND ma.macro_name = '{macro_name}'")
            conn.commit()"""

            cur.execute(f"SELECT id FROM meals WHERE name = '{meal_name}'")
            meal_id = (cur.fetchone()[0])

    
            cur.execute(f"SELECT id FROM macros WHERE macro_name = '{macro_name}'")
            macro_id = cur.fetchone()[0]
    
            created_at = datetime.now().strftime("%Y-%m-%d")
            cur.execute(
                f"INSERT INTO foods (food_name, calorie,  meal_id, user_id, macro_id,created_at) VALUES ('{food_name}', {calorie}, {meal_id},{session['id']}, {macro_id}, '{created_at}')")
            conn.commit()


            return redirect("/home")
        if request.form.get("calc_button"):
            status = ""
            calc_info[0] = int(request.form.get("height"))
            calc_info[1] = int(request.form.get("weight"))
            calc_info[2] = int(request.form.get("age"))
            bmi = calculate_bmi(calc_info[0],calc_info[1],calc_info[2])*10000
            if bmi < 16:
                status = "Severe Thinness"
            elif bmi >= 16 and bmi < 17:
                status = "Moderate Thinness"
            elif bmi >= 17 and bmi < 18.5:
                status = "Mild Thinness"
            elif bmi >= 18.5 and bmi < 25:
                status = "Normal"
            elif bmi >= 25 and bmi < 30:
                status = "Overweight"
            elif bmi >= 30 and bmi < 35:
                status= "Obese Class I"
            elif bmi >= 35 and bmi < 40:
                status= "Obese Class II"
            else:
                status = "Obese Class III"

            return render_template("main.html", rows= food_info,uname=session["uname"],info=calc_info,status=status,sum_calories=sum_calories)

        if request.form.get("workout_button"):
            exercise_name = request.form.get("exercise-name")
            calories_burned = request.form.get("calories-burned")
            created_at = datetime.now().strftime("%Y-%m-%d")
            cur.execute(f"INSERT INTO exercises(name, burning_calories, user_id,created_at) VALUES ('{exercise_name}',{calories_burned}, {session['id']},'{created_at}')")
            conn.commit()
            # return render_template("main.html", rows= food_info,uname=session["uname"],info=calc_info,sum_calories=sum_calories)
            return redirect("/home")
        if request.form.get("save_delete_button"):
            foodtd = request.form.get("food_delete")
            cur.execute(f"DELETE FROM foods WHERE food_name = '{foodtd}' and created_at = '{created_at}'")
            conn.commit()
            return redirect("/home")
    return render_template("main.html", rows= food_info,uname=session["uname"],info=calc_info,sum_calories=sum_calories)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    status = ""
    cur.execute(f"SELECT user_name, phone, email, password, age, weight, height FROM users WHERE id = {session['id']}")
    user_info = cur.fetchall()
    user_info = [tuple for sublist in user_info for tuple in sublist]

    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        if password != request.form.get("confpass"):
            return render_template("editProfile.html", status='<a style = "color:orange;">Passwords not equal</a>')
        phone = request.form.get("phonenum")
        if not re.match(phone_pattern, phone):
            return render_template("editProfile.html", status='<a style = "color:orange;">Invalid Phone Number</a>')
        email = request.form.get("email")
        if not re.match(email_pattern, email):
            return render_template("editProfile.html", status='<a style = "color:orange;">Invalid Email</a>')
        age = request.form.get("age")
        weight = request.form.get("weight")
        height = request.form.get("height")
        query = f"UPDATE users SET  user_name= %s, phone= %s, email= %s, password= %s, age=%s, weight=%s, height=%s WHERE id = {session['id']}"
        values = (uname,phone,email,password,age,weight,height)
        cur.execute(query, values)
        conn.commit()
        return redirect("/home")
    return render_template("editProfile.html",
                           uname=user_info[0],
                           phone=user_info[1],
                           email=user_info[2],
                           passw=user_info[3],
                           age=user_info[4],
                           weight=user_info[5],
                           height=user_info[6])


@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect("/login")


def calculate_bmi(height, weight, age):
    bmi = weight / (height * height)
    if age < 45:
        return bmi
    elif age >= 45 and age < 60:
        return bmi - 0.1
    else:
        return bmi - 0.2


def sum_calorie(allcal):
    if allcal[0] == None and allcal[1] == None:
        return "You neither gained nor burned calories today"
    elif allcal[0] == None:
        return f"You burned {allcal[1]} calories today"
    elif allcal[1] == None:
        return f"You gained {allcal[0]} calories today"
    else:
        sum_calories = allcal[0] - allcal[1]
        print(sum_calories)
        if sum_calories < 0:
            return f"You burned {abs(sum_calories)} calories today"
        else:
            return f"You gained {sum_calories} calories today"

