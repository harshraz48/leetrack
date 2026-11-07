import mysql.connector
from flask import abort, redirect
from flask import Flask, render_template, request
import os 
from dotenv import load_dotenv 
load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route('/')
def home():
    difficulty = request.args.get('difficulty')
    tag = request.args.get('tag')
    q = request.args.get('q', '').strip()

    query = """
        SELECT p.id, p.problem_name, p.leetcode_num, p.difficulty,
               COALESCE(GROUP_CONCAT(t.tag_name SEPARATOR ', '), '') AS tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.id
    """
    params = []
    conditions = []

    if difficulty:
        conditions.append("p.difficulty = %s")
        params.append(difficulty)
    if tag:
        conditions.append("p.id in (SELECT problem_id FROM problem_tags WHERE tag_id = %s)") #tag id is a string here cuh
        params.append(tag)
    if q:
        conditions.append("p.problem_name LIKE %s")
        params.append(f"%{q}")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY p.id"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    problems = cursor.fetchall()

    cursor.execute("SELECT id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('home.html', problems=problems, selected_tag=tag, tags=tags, selected_difficulty=difficulty, q=q)

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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    message = None

    if request.method == 'POST':
        tag_name = request.form['tag_name'].strip()
        if not tag_name:
            message = "Tag name can't be empty."
        else:
            cursor.execute("SELECT id FROM tags WHERE LOWER(tag_name) = LOWER(%s)", (tag_name,))
            if cursor.fetchone():
                message = f"Tag '{tag_name}' already exists."
            else:
                cursor.execute("INSERT INTO tags (tag_name) VALUES (%s)", (tag_name,))
                conn.commit()
                message = f"Tag '{tag_name}' added."

    cursor.execute("SELECT id, tag_name FROM tags ORDER BY tag_name")
    all_tags = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_tags.html', message=message, tags=all_tags)

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
   cursor = conn.cursor(dictionary=True)

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
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM problems WHERE id=%s", (problem_id,))
    problem = cursor.fetchone()

    cursor.execute("SELECT * FROM solutions WHERE problem_id=%s", (problem_id,))
    solutions=cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("show_solution.html", problem=problem, solutions=solutions)



@app.route('/edit_solution/<int:solution_id>', methods = ['GET', 'POST'])
def edit_solution(solution_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM solutions WHERE id = %s", (solution_id,))
    solution = cursor.fetchone()
    if solution is None:
        cursor.close()
        conn.close()
        abort(404)

    if request.method == 'POST':
        intuition = request.form['intuition']
        code = request.form['code']
        time_taken = request.form['time_taken']
        time_complexity = request.form['time_complexity']
        space_complexity = request.form['space_complexity']
        property = request.form['property_val']
        need_to_revisit = request.form['need_to_revisit']
        date_solved = request.form['date_solved']

        cursor.execute(
            """UPDATE solutions
                SET intuition = %s, code = %s, time_taken = %s, time_complexity = %s, space_complexity = %s, property = %s, need_to_revisit = %s, date_solved = %s
                WHERE id = %s""",
                (intuition, code, time_taken, time_complexity, space_complexity, property, need_to_revisit, date_solved, solution_id)
        )
        conn.commit()
        problem_id = solution['problem_id']
        cursor.close()
        conn.close()
        return redirect(f"/solution/{problem_id}")
    
    cursor.close()
    conn.close()
    return render_template('edit_solution.html', solution=solution) 

@app.route('/delete_solution/<int:solution_id>', methods = ['POST'])
def delete_solution(solution_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary= True)

    cursor.execute("SELECT  * FROM solutions WHERE id = %s", (solution_id,))
    solution = cursor.fetchone()
    if solution is None:
            cursor.close()
            conn.close()
            abort(404)

    problem_id = solution['problem_id']
    cursor.execute("DELETE FROM solutions WHERE id = %s", (solution_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(f"/solution/{problem_id}")

@app.route('/delete_problem/<int:problem_id>', methods = ['POST'])
def delete_problem(problem_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM problems WHERE id = %s", (problem_id,))
    if cursor.fetchone() is None:
       cursor.close()
       conn.close()
       abort(404)

    cursor.execute("DELETE FROM  problem_tags WHERE problem_id =%s", (problem_id,))
    cursor.execute("DELETE FROM  solutions WHERE problem_id =%s", (problem_id,))
    cursor.execute("DELETE FROM  problems WHERE id =%s", (problem_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/")

@app.route('/delete_tag/<int:tag_id>', methods = ['POST'])
def delete_tag(tag_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id from tags WHERE id = %s", (tag_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        abort(404)

    cursor.execute("DELETE FROM problem_tags WHERE  tag_id = %s", (tag_id,))
    cursor.execute("DELETE from tags WHERE id = %s", (tag_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/add_tags")

@app.route('/edit_problem/<int:problem_id>', methods = ['GET', 'POST'])
def edit_problem(problem_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM problems WHERE id = %s", (problem_id,))
    problem = cursor.fetchone()
    if problem is None:
        cursor.close()
        conn.close()
        abort(404)

    if request.method == 'POST':
        problem_name = request.form['problem_name']
        leetcode_num = request.form['leetcode_num']
        difficulty = request.form['difficulty']

        cursor.execute(
            """UPDATE problems 
                SET problem_name = %s, leetcode_num = %s, difficulty = %s WHERE id = %s""",
                (problem_name, leetcode_num, difficulty, problem_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/")

    cursor.close()
    conn.close()
    return render_template('edit_problems.html', problem=problem)

if __name__ == '__main__':
    app.run(debug=True)