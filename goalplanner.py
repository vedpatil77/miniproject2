from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
password = quote_plus("VEDpatil7508")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete")

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, try again.", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "warning")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    goals = Goal.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, goals=goals)

@app.route('/add_goal', methods=['POST'])
def add_goal():
    if 'user_id' in session:
        goal_text = request.form['goal']
        new_goal = Goal(user_id=session['user_id'], goal=goal_text)
        db.session.add(new_goal)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_goal/<int:goal_id>')
def update_goal(goal_id):
    if 'user_id' in session:
        goal = Goal.query.get(goal_id)
        if goal and goal.user_id == session['user_id']:
            goal.status = "Completed"
            db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_goal/<int:goal_id>')
def delete_goal(goal_id):
    if 'user_id' in session:
        goal = Goal.query.get(goal_id)
        if goal and goal.user_id == session['user_id']:
            db.session.delete(goal)
            db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
