from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

#### END SETUP ####



@app.route('/')
def start_page():
    """Shows the user the title of the survey, instructions, and button to start the survey"""
    title = surveys.satisfaction_survey.title
    instructions = surveys.satisfaction_survey.instructions

    return render_template('home.html', title=title, instructions=instructions)

@app.route('/survey-responses', methods=['POST'])
def make_response_list():
    session['responses'] = []
    responses = session['responses']
    session['q_num'] = 0
    q_num = session['q_num']
    return redirect(f'/questions/{q_num}')

@app.route('/questions/<int:q_num>')
def show_question(q_num):
    """Shows question and answer choices from list based on current question number"""
    responses = session['responses']

    # if all questions already answered send user to thanks.html
    if len(responses) == len(surveys.satisfaction_survey.questions):
        flash("You have already completed this survey.")
        return render_template('thanks.html')

    # make sure user starts with first question (in case they come straight to some question page)
    if q_num > 0 and session['q_num'] == 0:
        flash("Let's start with the first question, shall we?")
        q_num = session['q_num']
  
    # question number is not the next question number, flash error and redirect to next valid question
    for item in responses:
        if str(q_num) in item:
            flash("You already answered that one. Here's the next question.")
    if q_num > session['q_num']:
        flash("No skipping! Let's stick with the next question in the survey. ")

    # get q_num question and answer choices
    session['q_num'] = len(responses)
    q_num = session['q_num']
    question = surveys.satisfaction_survey.questions[q_num].question
    choices = surveys.satisfaction_survey.questions[q_num].choices
    return render_template('question.html', question=question, q_num=q_num, choices=choices)

@app.route('/answer', methods=['POST'])
def handle_answer():
    """Appends answer to responses list, sends user back to next question
       or to thanks.html when done"""
    responses = session['responses']
    session['q_num'] = int(request.form['question_num'])
    q_num = session['q_num']
    answer = request.form[f'question{q_num}'] 

    responses.append({q_num:answer})

    session['responses'] = responses

    q_num += 1
    session['q_num'] = q_num

    # next question or end survey
    if q_num < len(surveys.satisfaction_survey.questions):
        return redirect(f'/questions/{q_num}')
    else:
        return render_template('/thanks.html')
