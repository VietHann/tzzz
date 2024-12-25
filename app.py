from flask import Flask, render_template, request, jsonify
from quiz_generator import QuizGenerator
import traceback

app = Flask(__name__)

# Khởi tạo QuizGenerator
try:
    quiz_gen = QuizGenerator()
except Exception as e:
    print(f"Lỗi khởi tạo QuizGenerator: {e}")
    quiz_gen = None

@app.route('/')
def index():
    return render_template('quiz.html')

@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    if quiz_gen is None:
        return jsonify({"status": "error", "message": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        data = request.json
        num_questions = data.get('num_questions', 10)
        quiz_gen.start_new_quiz(num_questions)
        return jsonify({"status": "success"})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get-question', methods=['GET'])
def get_question():
    if quiz_gen is None:
        return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        question_type = request.args.get('type', 'word')
        question = quiz_gen.generate_question(question_type)
        return jsonify(question)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    if quiz_gen is None:
        return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        data = request.json
        is_correct = quiz_gen.check_answer(
            data['questionId'], 
            data['answer']
        )
        progress = quiz_gen.get_progress()
        word_details = quiz_gen.get_word_details(data['questionId'])
        
        return jsonify({
            "correct": is_correct,
            "correctAnswer": quiz_gen.get_correct_answer(data['questionId']),
            "score": progress['correct'],
            "total": progress['total'],
            "wordDetails": word_details
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/save-result', methods=['POST'])
def save_result():
    if quiz_gen is None:
        return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        result = quiz_gen.save_quiz_result()
        return jsonify(result)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/get-history', methods=['GET'])
def get_history():
    if quiz_gen is None:
        return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        history = quiz_gen.get_history()
        return jsonify(history)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/get-wrong-answers', methods=['GET'])
def get_wrong_answers():
    if quiz_gen is None:
        return jsonify({"error": "Hệ thống chưa sẵn sàng"}), 500
        
    try:
        wrong_answers = quiz_gen.get_wrong_answers()
        return jsonify(wrong_answers)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/start-review', methods=['POST'])
def start_review():
    if quiz_gen.start_review_wrong_answers():
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Không có câu sai để ôn tập"})

@app.route('/get-review-question', methods=['GET'])
def get_review_question():
    question = quiz_gen.get_next_review_question()
    return jsonify(question)

if __name__ == '__main__':
    app.run(debug=True) 