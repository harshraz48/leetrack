import mysql.connector
from flask import Flask, render_template, request

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "leetcode_app",
        database = "leetcode_tracker",
        password = "TestPass123!"
    )

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems")
    problems = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', problems=problems)

@app.route('/add_problem', methods =['GET', 'POST'])
def add_problems():
    if request.method == "POST":
        problem_name = request.form['problem_name']
        leetcode_num = request.form['leetcode_num']
        difficulty = request.form['difficulty']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT  INTO problems (problem_name, leetcode_num, difficulty) VALUES(%s, %s, %s)",
            (problem_name, leetcode_num, difficulty)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return "problem added! <a href='/'>GO home</a>"
    return render_template('add_problem.html')

@app.route('/add_tags', methods=['GET', 'POST'])
def add_tags():
    if request.method == 'POST':
       tag_name = request.form['tag_name'].strip()

       conn = get_db_connection()
       cursor = conn.cursor()
       cursor.execute("SELECT id FROM tags WHERE LOWER(tag_name) = LOWER(%s)", (tag_name,))
       existing = cursor.fetchone()

       if existing:
           message = f"Tag '{tag_name}' already exists. No dupllicates will be made."
       else:
           cursor.execute("INSERT INTO  tags (tag_name) VALUES (%s)", (tag_name,))
           conn.commit()
           message = f"Tag '{tag_name}' added."

       cursor.close()
       conn.close()
       return message + "<a href='/'> Go home</a>"
    
    return render_template('add_tags.html')

@app.route('/add_problem_tags', methods = ['GET', 'POST'])
def add_problem_tag():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        problem_id = request.form['problem_id']
        tag_id = request.form['tag_id']
        cursor.execute("INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)", (problem_id, tag_id))
        conn.commit()
        cursor.close()
        conn.close()
        return "Tag is now linked to the problem <a href='/'>Go Home</a>"

    cursor.execute("SELECT id, problem_name FROM problems")
    problems = cursor.fetchall()

    cursor.execute("SELECT id, tag_name FROM tags")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('add_problem_tags.html', problems=problems , tags=tags)

@app.route('/add_solution', methods =['GET', 'POST'])
def add_solutions():
   conn = get_db_connection()
   cursor = conn.cursor()

   if request.method == 'POST':
       problem_id = request.form['problem_id']
       intuition = request.form['intuition']
       code = request.form['code']
       time_taken = request.form['time_taken']
       time_complexity = request.form['time_complexity']
       space_complexity = request.form['space_complexity']
       property = request.form['property_val']
       need_to_revisit = request.form['need_to_revisit']
       date_solved = request.form['date_solved']

       cursor.execute("INSERT INTO solutions (problem_id, intuition, code, time_taken, time_complexity, space_complexity, property, need_to_revisit, date_solved) VALUES(%s, %s, %s,%s, %s, %s,%s, %s, %s)",(problem_id, intuition, code, time_taken, time_complexity, space_complexity, property, need_to_revisit, date_solved) )
       conn.commit()
       cursor.close()
       conn.close()
       return "The solution has been added <a href='/'>Go home</a>"

   cursor.execute("SELECT id, problem_name FROM problems")
   problems = cursor.fetchall()

   cursor.close()
   conn.close()
   return render_template('add_solution.html', problems=problems)

@app.route('/solution/<int:problem_id>')
def show_solution(problem_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM problems WHERE id=%s", (problem_id,))
    problem = cursor.fetchone()

    cursor.execute("SELECT * FROM solutions WHERE problem_id=%s", (problem_id,))
    solutions=cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("show_solution.html", problem=problem, solutions=solutions)

if __name__ == '__main__':
    app.run(debug=True)