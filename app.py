from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

#### END SETUP ####

responses = []
q_num = len(responses)

@app.route('/')
def start_page():
    """Shows the user the title of the survey, instructions, and button to start the survey"""
    title = surveys.satisfaction_survey.title
    instructions = surveys.satisfaction_survey.instructions

    return render_template('home.html', title=title, instructions=instructions, q_num=q_num)

@app.route('/questions/<int:q_num>')
def show_question(q_num):
    """Shows question and answer choices from list based on current question number"""

    # if all questions already answered send user to thanks.html
    if len(responses) == len(surveys.satisfaction_survey.questions):
        flash("You have already completed this survey.")
        return render_template('thanks.html')

    # make sure user starts with first question (in case they come straight to some question page)
    if q_num > 0 and len(responses) == 0:
        flash("Let's start with the first question, shall we?")
        q_num = 0;
      
    # question number is not the next question number, flash error and redirect to next valid question
    for item in responses:
        if q_num in item:
            flash("You already answered that one. Here's the next question.")
    if q_num > len(responses):
        flash("No skipping! Let's stick with the next question in the survey. ")

    # get q_num question and answer choices
    q_num = len(responses)
    question = surveys.satisfaction_survey.questions[q_num].question
    choices = surveys.satisfaction_survey.questions[q_num].choices
    return render_template('question.html', question=question, q_num=q_num, choices=choices)

@app.route('/answer', methods=['POST'])
def handle_answer():
    """Appends answer to responses list, sends user back to next question
       or to thanks.html when done"""
    q_num = int(request.form['question_num'])
    answer = request.form[f'question{q_num}'] 

    global responses

    # if all questions already answered send user to thanks.html
    if len(responses) == len(surveys.satisfaction_survey.questions):
        flash("You have already completed this survey.")
        return render_template('thanks.html')

    # if q/a already in list, flash error and redirect to next valid question
    for item in responses:
        if q_num in item  or q_num > len(responses):
            flash("We have an answer for that one already. Here's the next question.")
            q_num = len(responses)
            question = surveys.satisfaction_survey.questions[q_num].question
            choices = surveys.satisfaction_survey.questions[q_num].choices
            return render_template('question.html', question=question, q_num=q_num, choices=choices)

    responses.append({q_num:answer})

    q_num += 1

    # next question or end survey
    if q_num < len(surveys.satisfaction_survey.questions):
        return redirect(f'/questions/{q_num}')
    else:
        return render_template('/thanks.html')
