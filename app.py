from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

#### END SETUP ####

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

@app.route('/')
def show_surveys():
    """Show survey selection box"""

    return render_template('home.html', surveys=surveys)

@app.route('/', methods=["POST"])
def pick_survey():
    """Select a survey"""
    survey_id = request.form['survey_selector']

    # don't let them re-take a survey until cookie times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template('completed.html')

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("start.html", survey=survey)

@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session cookie for responses"""
    session[RESPONSES_KEY] = []

    return redirect("/questions/0")

@app.route("/questions/<int:q_num>")
def show_question(q_num):
    """Display current question"""
    responses = session.get(RESPONSES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        # trying to access question page too soon
        flash("Let's start with the first question, shall we?")
        return redirect("/") 

    if (len(responses) == len(survey.questions)):
        # survey is complete
        return redirect("/complete")

    if (len(responses) != q_num):
        # Trying to access questions out of order
        flash("Let's stick with the next question in the survey.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[q_num]

    return render_template("question.html", question_num=q_num, question=question)

@app.route("/answer", methods=["POST"])
def handle_answer():
    """Save response and redirect to next question or thanks when done"""
    choice = request.form['answer']
    text = request.form.get("text", "")

    # add this response to the list in the session
    responses = session[RESPONSES_KEY]
    responses.append({"choice": choice, "text": text})

    # add this response to the session
    session[RESPONSES_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        # survey is complete
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/complete")
def say_thanks():
    """Thank user and list responses"""
    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("thanks.html", survey=survey, responses=responses)

    # Set cookie noting this survey is done so they can't retake it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response


# @app.route('/answer', methods=['POST'])
# def handle_answer():
#     """Appends answer to responses list, sends user back to next question
#        or to thanks.html when done"""
#     selected_survey = session['survey']
#     survey = surveys.surveys[f'{selected_survey}']
#     responses = session[f'{selected_survey}_responses']

#     #session['q_num'] = int(request.form['question_num'])
#     session['q_num'] = request.form.get('question_num', type=int)
#     q_num = session['q_num']
#     answer = request.form[f'question{q_num}'] 

#     #responses.append({q_num:answer})
#     responses[str(q_num)] = answer

#     session[f'{selected_survey}_responses'] = responses
#     q_num += 1
#     session['q_num'] = q_num

#     # next question or end survey
#     if q_num < len(survey.questions):
#         return redirect(f'/questions/{q_num}')
#     else:
#         survey.complete = True
#         qkeys = []
#         for key in responses:
#             qkeys.append(int(key))    
        
#         return render_template('/thanks.html', responses=responses, qkeys=qkeys, survey=survey)
