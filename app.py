from flask import Flask, request, render_template, jsonify,redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import random
import re
import requests
from io import TextIOWrapper
from flask import Flask, render_template, request, redirect, url_for, session

import csv


app = Flask(__name__)
app.secret_key = "suriya"  # 🔐 Required for sessions and forms

@app.route('/ads.txt')
def ads():
    return app.send_static_file('ads.txt')


# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'questions.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = "tgp_v1_xBNB02dvPqRWkdOrorqGV3xbQA0jBM2jFHd5i2KiKNw"
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam = db.Column(db.String(50))
    section = db.Column(db.String(100))
    topic = db.Column(db.String(100), nullable=True)
    question_text = db.Column(db.Text)
    option_a = db.Column(db.Text)
    option_b = db.Column(db.Text)
    option_c = db.Column(db.Text)
    option_d = db.Column(db.Text)
    answer = db.Column(db.String(1))

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question_text,
            "options": {
                "A": self.option_a,
                "B": self.option_b,
                "C": self.option_c,
                "D": self.option_d
            },
            "answer": self.answer
        }

from flask import Response
from datetime import datetime

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    base_url = "https://www.testifyy.online"

    # Add your static pages here
    static_pages = [
        '',
        '/about',
        '/terms',
        '/privacy',
        '/trick',
        '/doubtsolver',
        '/start-exam',
        '/result',
        '/review'
        
        
        
        # this should be a GET-rendered result page
    ]

    for page in static_pages:
        pages.append(f"""
        <url>
            <loc>{base_url}{page}</loc>
            <lastmod>{datetime.now().date()}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.8</priority>
        </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {''.join(pages)}
    </urlset>"""

    return Response(xml, mimetype='application/xml')


@app.route("/about")
def about():
    return render_template("about.html")

from flask import send_from_directory

@app.route('/robot.txt')
def robot():
    return send_from_directory(app.static_folder, 'robot.txt')


@app.route("/dates")
def dates():
    return render_template("dates.html")

@app.route("/cutoff")
def cutoff():
    return render_template("cutoff.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/adsense")
def adsense():
    return render_template("adsense.html")

@app.route('/formula')
def formula():
    return render_template('formula.html')

@app.route('/trick')
def trick():
    return render_template('trick.html')
@app.route("/syllabus")
def syllabus():
    return render_template("syllabus.html")




@app.route('/doubt')
def doubt_page():
    return render_template('doubt.html')


@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    mode = data.get('mode')
    topic = data.get('topic')
    question = data.get('question', '')

    # Basic validation
    if not mode or not topic or (mode == 'doubt' and not question):
        return jsonify({"error": "Missing required fields: mode, topic, and question (for doubt mode)"}), 400

    # Build AI prompt
    if mode == "doubt":
        prompt = (
            f"You are a government exam tutor. Explain this question in a simple, step-by-step way with examples.\n\n"
            f"Topic: {topic}\n"
            f"Question: {question}\n"
        )
    elif mode == "trick":
        prompt = (
            f"You are an expert exam coach. Provide 5 useful shortcut tricks or memory hacks for solving questions fast "
            f"on the topic '{topic}' in government exams like TNPSC, SSC, or Railway.\n\n"
            f"Each trick should be practical and beginner-friendly.\n"
           f" All questions must be strictly based on the **Indian syllabus, current exam pattern, and standards followed by Indian competitive exams** like SSC, RRB, UPSC, TNPSC, etc.\n\n"

        )
    else:
        return jsonify({"error": "Invalid mode. Use 'doubt' or 'trick'."}), 400

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "model": "meta-llama/Llama-Vision-Free",  # You can update this to your preferred model
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.2,
        "top_p": 0.9
    }

    try:
        res = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        if res.status_code != 200:
            return jsonify({"answer": "⚠️ AI model error. Please try again later."}), 500

        result = res.json()
        ai_text = result.get("output")

        # Fallback for models that use "choices"
        if not ai_text:
            choices = result.get("choices", [])
            ai_text = choices[0].get("text", "") if choices else ""

        if not ai_text.strip():
            ai_text = "⚠️ AI returned no answer. Please try again."

        return jsonify({"answer": ai_text.strip()})

    except Exception as e:
        # Log the error for debugging if needed
        return jsonify({"answer": "❌ Error while connecting to AI server."}), 500


import json
@app.route('/start-exam', methods=['GET'])
def start_exam_page():
    exams = ['SSC', 'TNPSC', 'Railway', 'UPSC']
    sections = {
        'SSC': ['CGL', 'CHSL'],
        'TNPSC': ['Group 1', 'Group 2', 'Group 3', 'Group 4'],
        'Railway': ['ALP', 'Group D'],
        'UPSC': ['Prelims', 'Mains']
    }
    sub_topics = {
        'SSC': {
            'CGL': ['Reasoning', 'Quantitative Aptitude'],
            'CHSL': ['English', 'General Awareness']
        },
        'TNPSC': {
            'Group 1': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 2': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 3': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 4': ['History', 'Geography', 'Tamil', 'Polity', 'Economy'],
        },
        'Railway': {
            'ALP': ['Physics', 'Technical'],
            'Group D': ['Current Affairs', 'Biology']
        },
        'UPSC': {
            'Prelims': ['CSAT', 'General Studies'],
            'Mains': ['Essay', 'Ethics']
        }
    }
    return render_template("start-exam.html", exams=exams, sections=sections, sub_topics=json.dumps(sub_topics))


@app.route('/')
def index():
    exams = ['SSC', 'TNPSC', 'Railway', 'UPSC']
    sections = {
        'SSC': ['CGL', 'CHSL'],
        'TNPSC': ['Group 1', 'Group 2', 'Group 3', 'Group 4'],
        'Railway': ['ALP', 'Group D'],
        'UPSC': ['Prelims', 'Mains']
    }
    sub_topics = {
        'SSC': {
            'CGL': ['Reasoning', 'Quantitative Aptitude'],
            'CHSL': ['English', 'General Awareness']
        },
        'TNPSC': {
            'Group 1': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 2': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 3': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 4': ['History', 'Geography', 'Tamil', 'Polity', 'Economy'],
        },
        'Railway': {
            'ALP': ['Physics', 'Technical'],
            'Group D': ['Current Affairs', 'Biology']
        },
        'UPSC': {
            'Prelims': ['CSAT', 'General Studies'],
            'Mains': ['Essay', 'Ethics']
        }
    }
    return render_template("index.html", exams=exams, sections=sections, sub_topics=json.dumps(sub_topics))

def generate_ai_questions(exam, section, topic=None, count=20, retries=0):
    MAX_RETRIES = 3

    # ✅ Prompt generation
    if exam == "TNPSC":
        topic_line = f'"{topic}" தலைப்பில் ' if topic else ''
        prompt = f""" 
{section} பிரிவுக்கான TNPSC தேர்விற்கு {topic_line}{count} தமிழ் பன்மை தேர்வுக் கேள்விகள் (MCQ) இந்திய நெறிமுறைகள் மற்றும் பாடத்திட்டத்தின் அடிப்படையில் உருவாக்கவும்.


தொடரமைப்பு:

Q1: கேள்வி
A: விருப்பம் A
B: விருப்பம் B
C: விருப்பம் C
D: விருப்பம் D
Answer: சரியான விடை (A/B/C/D)

Q2: ...
Q{count} வரை தொடரவும்.
"""
    else:
        prompt = f"""
Generate {count} multiple-choice questions for the **{exam}** exam under the **{section}** section{" on topic: " + topic if topic else ""}.
All questions must be strictly based on the **Indian syllabus, current exam pattern, and standards followed by Indian competitive exams** like SSC, RRB, UPSC, TNPSC, etc.

Format:
Q1: question text
A: option A
B: option B
C: option C
D: option D
Answer: A

Repeat this format from Q1 to Q{count}.
"""

    # ✅ API Call
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "prompt": prompt,
        "max_tokens": 1800,
        "temperature": 0.3
    }

    response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("❌ API Error:", response.status_code, response.text)
        return []

    output = response.json().get("choices", [{}])[0].get("text", "")
    print("🧠 AI Raw Output:\n", output)

    # ✅ Parse questions
    blocks = re.split(r"Q\d+:", output)[1:]
    if not blocks:
        print("❌ No questions matched Q pattern.")
        return []

    questions = []
    for block in blocks:
        lines = block.strip().split('\n')
        q_text = ""
        opts = {}
        ans = ""

        for line in lines:
            line = line.strip()
            if line.startswith("A:"):
                opts["A"] = line[2:].strip()
            elif line.startswith("B:"):
                opts["B"] = line[2:].strip()
            elif line.startswith("C:"):
                opts["C"] = line[2:].strip()
            elif line.startswith("D:"):
                opts["D"] = line[2:].strip()
            elif line.lower().startswith("answer:"):
                ans = line.split(":")[1].strip().upper()
            elif line:
                q_text += line + " "

        if opts and ans in opts:
            q = Question(
                exam=exam,
                section=section,
                topic=topic or "",  # Avoid None in DB
                question_text=q_text.strip(),
                option_a=opts.get("A", ""),
                option_b=opts.get("B", ""),
                option_c=opts.get("C", ""),
                option_d=opts.get("D", ""),
                answer=ans
            )
            questions.append(q)

    # ✅ Retry if not enough questions
    if len(questions) < count and retries < MAX_RETRIES:
        print(f"⚠️ Got only {len(questions)}. Retrying {MAX_RETRIES - retries} more...")
        more_questions = generate_ai_questions(exam, section, topic, count - len(questions), retries + 1)
        questions.extend(more_questions)

    return questions[:count]




# Mock exam patterns
EXAM_PATTERNS = {
    'TNPSC': {
        'Group 1': {
            'General Studies': 10,
            'Aptitude': 10,
            'General tamil': 10,
        },
        'Group 2': {
            'General Studies': 10,
            'Aptitude': 10,
            'General tamil': 10,
        },
        'Group 3': {
            'General Studies': 10,
            'Aptitude': 10,
            'General tamil': 10
        },
        'Group 4': {
            'General Studies': 10,
            'Aptitude': 10,
            'General tamil': 10
        }
    },
    'SSC': {
        'CGL': {
            'General Intelligence & Reasoning': 10,
            'Quantitative Aptitude': 10,
            'General Awareness': 10,
            'English Comprehension': 5
        },
        'CHSL': {
            'General Intelligence': 10,
            'Quantitative Aptitude': 10,
            'General Awareness': 10,
            'English Language': 10
        }
    },
    'Railway': {
        'ALP': {
            'Mathematics': 15,
            'General Intelligence and Reasoning': 15,
            'General Science': 10,
            'General Awareness': 10
        },
        'Group D': {
            'Mathematics': 15,
            'General Intelligence and Reasoning': 15,
            'General Science': 5,
            'General Awareness and Current Affairs': 5
        }
    },
    'UPSC': {
        'Prelims': {
            'General Studies Paper 1': 15,
            'CSAT (Aptitude)': 15
        },
        'Mains': {
            'General Studies Paper 1': 15,
            'General Studies Paper 2': 15,
            'General Studies Paper 3': 15,
            'General Studies Paper 4': 15
        }
    }
}


def get_hybrid_questions(exam, section, topic, count=20):
    # Step 1: Get cached questions from DB
    cached_questions = Question.query.filter_by(exam=exam, section=section, topic=topic).all()
    cached_count = len(cached_questions)

    half_count = count // 2
    use_cached = min(half_count, cached_count)   # Use as many cached as possible up to half_count
    use_ai = count - use_cached

    selected_cached = random.sample(cached_questions, use_cached) if use_cached > 0 else []

    # Step 2: Generate remaining with AI if needed
    ai_questions = []
    if use_ai > 0:
        ai_questions = generate_ai_questions(exam, section, topic, use_ai)
        for q in ai_questions:
            # Save new AI questions to DB for future reuse
            db.session.add(q)
        db.session.commit()

    combined_questions = selected_cached + ai_questions
    random.shuffle(combined_questions)
    return combined_questions


@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    data = request.form
    exam = data.get('exam')
    section = data.get('section')
    topic = data.get('topic')  # might be None
    mode = data.get('mode')

    if mode == 'practice':
        count = 10  # or 10, as you want
        questions = get_hybrid_questions(exam, section, topic, count=count)

        if not questions:
            return "Unable to generate questions for this topic.", 400

        return render_template('exam_onebyone.html', questions=[q.to_dict() for q in questions],
                               exam=exam, section=section, topic=topic, mode=mode)

    elif mode == 'mock':
        pattern = EXAM_PATTERNS.get(exam, {}).get(section)
        if not pattern:
            return f"No mock exam pattern defined for {exam} - {section}", 400

        all_questions = []

        for sec_name, count in pattern.items():
            qs = Question.query.filter_by(exam=exam, section=sec_name).limit(count).all()
            if len(qs) < count:
                ai_questions = generate_ai_questions(exam, sec_name, topic=None, count=count - len(qs))
                for q in ai_questions:
                    db.session.add(q)
                qs.extend(ai_questions)

            all_questions.extend(qs)

        # Commit once after all additions
        db.session.commit()

        if not all_questions:
            return "No questions available for mock exam.", 400

        random.shuffle(all_questions)
        return render_template('exam_onebyone.html',
                               questions=[q.to_dict() for q in all_questions],
                               exam=exam, section=section, topic=None, mode=mode)
    else:
        return "Invalid mode selected", 400
from flask import session
import json

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    question_ids = request.form.getlist('question_id')
    correct_answers = request.form.getlist('correct_answer')
    sections = request.form.getlist('section')

    score = 0
    total = len(question_ids)
    weak_tracker = {}
    results_data = []

    for i, qid in enumerate(question_ids):
        user_answer = request.form.get(f"user_answer_{qid}")
        correct = correct_answers[i]
        section = sections[i]
        q_obj = Question.query.get(int(qid))  # Ensure it's int

        if section not in weak_tracker:
            weak_tracker[section] = {'total': 0, 'correct': 0}
        weak_tracker[section]['total'] += 1
        if user_answer == correct:
            score += 1
            weak_tracker[section]['correct'] += 1

        results_data.append({
            'question': q_obj.question_text,
            'options': {
                'A': q_obj.option_a,
                'B': q_obj.option_b,
                'C': q_obj.option_c,
                'D': q_obj.option_d,
            },
            'correct': correct,
            'user': user_answer,
            'is_correct': user_answer == correct
        })

    weak_areas = [sec for sec, data in weak_tracker.items()
                  if data['correct'] / data['total'] < 0.6]

    # ✅ Save to session as JSON string
    session['results_data'] = json.dumps(results_data)  # 💥 DON'T store directly!
    session['score'] = score
    session['total'] = total
    session['weak_areas'] = weak_areas

    return render_template("result.html", score=score, total=total,
                           weak_areas=weak_areas)

    

@app.route('/admin_upload', methods=['GET', 'POST'])
def admin_upload():
    exams = ['SSC', 'TNPSC', 'Railway', 'UPSC']
    sections = {
        'SSC': ['CGL', 'CHSL'],
        'TNPSC': ['Group 1', 'Group 2', 'Group 3', 'Group 4'],
        'Railway': ['ALP', 'Group D'],
        'UPSC': ['Prelims', 'Mains']
    }
    topics = {
        'SSC': {
            'CGL': ['General Intelligence & Reasoning', 'Quantitative Aptitude', 'General Awareness', 'English Comprehension'],
            'CHSL': ['General Intelligence', 'Quantitative Aptitude', 'General Awareness', 'English Language']
        },
        'TNPSC': {
            'Group 1': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 2': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 3': ['History', 'Geography', 'Polity', 'Aptitude', 'Economy', 'Reasoning', 'Tamil'],
            'Group 4': ['History', 'Geography', 'Tamil', 'Polity', 'Economy'],
        },
        'Railway': {
            'ALP': ['Physics', 'Technical'],
            'Group D': ['Current Affairs', 'Biology']
        },
        'UPSC': {
            'Prelims': ['CSAT', 'General Studies'],
            'Mains': ['Essay', 'Ethics']
        }
    }

    if request.method == 'POST':
        exam = request.form.get('exam')
        section = request.form.get('section')
        topic = request.form.get('topic')
        file = request.files.get('csv_file')

        if not exam or not section or not topic or not file:
            flash('Please fill all fields and upload a CSV file.', 'error')
            return redirect(request.url)

        try:
            # Read CSV file
            csv_file = TextIOWrapper(file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            count = 0
            for row in reader:
                question_text = row.get('question')
                option_a = row.get('option_a')
                option_b = row.get('option_b')
                option_c = row.get('option_c')
                option_d = row.get('option_d')
                answer = row.get('answer')

                # Validate minimal data
                if not (question_text and option_a and option_b and option_c and option_d and answer):
                    continue  # skip incomplete rows

                # Add question to DB
                q = Question(
                    exam=exam,
                    section=section,
                    topic=topic,
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    answer=answer.upper()
                )
                db.session.add(q)
                count += 1

            db.session.commit()
            flash(f'Successfully uploaded {count} questions!', 'success')
            return redirect(url_for('admin_upload'))

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('admin_upload.html', exams=exams, sections=sections, topics=topics)

@app.route("/exam", methods=["GET", "POST"])
def exam():
    questions = session.get("qs", [])  # already generated questions

    if request.method == "POST":
        # Loop through questions and store user's selected answers
        for i, q in enumerate(questions):
            q["user"] = request.form.get(f"q_{i}")  # Store selected option (A/B/C/D)

        session["qs"] = questions  # Save updated with user's answers
        return redirect(url_for("review"))

    return render_template("exam.html", questions=questions)
@app.route('/review_answers')
def review_answers():
    import json
    results_json = session.get('results_data')

    if not results_json:
        return "No answers found. Please complete the exam first.", 400

    # ✅ Convert string back to list of dicts
    results_data = json.loads(results_json)

    score = session.get('score', 0)
    total = session.get('total', 0)
    weak_areas = session.get('weak_areas', [])

    return render_template("review.html",
                           results=results_data,
                           score=score, total=total,
                           weak_areas=weak_areas)



@app.route('/sample-result')
def sample_result():
    score = 18
    total = 25
    weak_areas = ["History - Modern India", "Aptitude - Number Series", "Geography - Indian Rivers"]
    return render_template("submit_exam.html", score=score, total=total, weak_areas=weak_areas)

@app.route('/sample-review')
def sample_review():
    return render_template("sample-review.html")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
