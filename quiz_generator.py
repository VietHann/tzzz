import random
import pandas as pd
import os

class QuizGenerator:
    def __init__(self):
        self.df = self.load_data()
        self.questions = {}
        self.current_id = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.current_question_number = 0
        self.wrong_answers = []
        try:
            self.history = self.load_history()
        except Exception as e:
            print(f"Lỗi khi load history: {e}")
            self.history = []
        
    def load_data(self):
        """Load dữ liệu từ file Excel"""
        try:
            # Thư mục chứa file data
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            # File Excel mặc định
            excel_path = os.path.join(data_dir, 'Lesson_1.xlsx')
            
            # Nếu file không tồn tại, tạo file mẫu
            if not os.path.exists(excel_path):
                df = pd.DataFrame({
                    'Chữ viết': ['hello', 'world', 'computer', 'language'],
                    'Phiên âm': ['/həˈləʊ/', '/wɜːld/', '/kəmˈpjuːtə/', '/ˈlæŋɡwɪdʒ/'],
                    'Phát âm': ['hello.mp3', 'world.mp3', 'computer.mp3', 'language.mp3'],
                    'Nghĩa': ['xin chào', 'thế giới', 'máy tính', 'ngôn ngữ']
                })
                df.to_excel(excel_path, index=False)
                return df
                
            # Load dữ liệu từ file Excel
            df = pd.read_excel(excel_path)
            if df.empty:
                raise Exception("File Excel không có dữ liệu")
            return df
            
        except Exception as e:
            print(f"Lỗi khi đọc file Excel: {e}")
            # Trả về DataFrame mẫu nếu có lỗi
            return pd.DataFrame({
                'Chữ viết': ['hello', 'world'],
                'Phiên âm': ['/həˈləʊ/', '/wɜːld/'],
                'Phát âm': ['hello.mp3', 'world.mp3'],
                'Nghĩa': ['xin chào', 'thế giới']
            })
            
    def load_history(self):
        """Load lịch sử làm bài từ file Excel"""
        try:
            history_path = os.path.join(os.path.dirname(__file__), 'data', 'history.xlsx')
            if os.path.exists(history_path):
                df = pd.read_excel(history_path)
                # Chuyển datetime thành string để tránh lỗi JSON
                if 'date' in df.columns:
                    df['date'] = df['date'].astype(str)
                return df.to_dict('records')
            return []
        except Exception as e:
            print(f"Lỗi khi đọc file lịch sử: {e}")
            return []
            
    def save_history(self):
        """Lưu lịch sử làm bài vào file Excel"""
        try:
            history_path = os.path.join(os.path.dirname(__file__), 'data', 'history.xlsx')
            # Tạo DataFrame từ history
            df = pd.DataFrame(self.history)
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            # Lưu file
            df.to_excel(history_path, index=False)
        except Exception as e:
            print(f"Lỗi khi lưu lịch sử: {e}")

    def start_new_quiz(self, num_questions=10):
        """Bắt đầu một bài quiz mới"""
        if self.df.empty:
            raise Exception("Không có dữ liệu từ vựng")
            
        self.total_questions = min(num_questions, len(self.df))
        self.correct_answers = 0
        self.current_question_number = 0
        self.questions = {}
        
    def generate_question(self, question_type):
        """Tạo câu hỏi dựa trên loại câu hỏi"""
        if self.current_question_number >= self.total_questions:
            return {
                'completed': True,
                'score': self.correct_answers,
                'total': self.total_questions
            }
            
        self.current_id += 1
        self.current_question_number += 1
        
        # Chọn ngẫu nhiên một từ làm đáp án đúng
        correct_row = self.df.sample(n=1).iloc[0]
        
        # Lưu thông tin chi tiết của từ
        word_details = {
            'word': correct_row['Chữ viết'],
            'pronunciation': correct_row['Phiên âm'],
            'sound': correct_row['Phát âm'],
            'meaning': correct_row['Nghĩa']
        }
        
        # Tạo các lựa chọn sai từ các từ khác
        wrong_choices = self.df.sample(n=3)
        
        if question_type == 'word':
            question = f"Đâu là phiên âm đúng của từ '{correct_row['Chữ viết']}'?"
            correct_answer = correct_row['Phiên âm']
            choices = [correct_answer] + list(wrong_choices['Phiên âm'])
            
        elif question_type == 'pronunciation':
            question = f"Nghe âm thanh và chọn từ đúng: {correct_row['Phát âm']}"
            correct_answer = correct_row['Chữ viết']
            choices = [correct_answer] + list(wrong_choices['Chữ viết'])
            
        else:  # meaning
            question = f"Đâu là nghĩa của từ '{correct_row['Chữ viết']}'?"
            correct_answer = correct_row['Nghĩa']
            choices = [correct_answer] + list(wrong_choices['Nghĩa'])

        random.shuffle(choices)
        
        self.questions[self.current_id] = {
            'correct_answer': correct_answer,
            'choices': choices,
            'word_details': word_details,
            'type': question_type
        }
        
        return {
            'id': self.current_id,
            'question': question,
            'choices': choices,
            'current_number': self.current_question_number,
            'total': self.total_questions,
            'type': question_type
        }
    
    def check_answer(self, question_id, answer):
        """Kiểm tra câu trả lời có đúng không"""
        if question_id not in self.questions:
            return False
        is_correct = answer == self.questions[question_id]['correct_answer']
        if is_correct:
            self.correct_answers += 1
        return is_correct
    
    def get_correct_answer(self, question_id):
        """Lấy đáp án đúng của câu hỏi"""
        if question_id not in self.questions:
            return None
        return self.questions[question_id]['correct_answer']

    def get_progress(self):
        """Lấy thông tin tiến độ làm bài"""
        return {
            'current': self.current_question_number,
            'total': self.total_questions,
            'correct': self.correct_answers
        }
        
    def save_wrong_answer(self, question_data, user_answer):
        """Lưu câu trả lời sai"""
        self.wrong_answers.append({
            'question': question_data['question'],
            'correct_answer': self.questions[question_data['id']]['correct_answer'],
            'user_answer': user_answer,
            'type': question_data.get('type', 'word')
        })
    
    def save_quiz_result(self):
        """Lưu kết quả bài làm"""
        result = {
            'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score': round(self.correct_answers * 100 / self.total_questions, 2),
            'wrong_answers': self.wrong_answers.copy()
        }
        self.history.append(result)
        self.save_history()  # Lưu vào file
        return result
        
    def get_history(self):
        """Lấy lịch sử làm bài"""
        return self.history
        
    def get_wrong_answers(self):
        """Lấy danh sách câu trả lời sai"""
        return self.wrong_answers
        
    def start_review_wrong_answers(self):
        """Bắt đầu ôn tập các câu sai"""
        if not self.wrong_answers:
            return False
        self.review_questions = self.wrong_answers.copy()
        random.shuffle(self.review_questions)
        self.current_review_index = 0
        return True
        
    def get_next_review_question(self):
        """Lấy câu hỏi ôn tập tiếp theo"""
        if self.current_review_index >= len(self.review_questions):
            return None
        question = self.review_questions[self.current_review_index]
        self.current_review_index += 1
        return question 

    def get_word_details(self, question_id):
        """Lấy thông tin chi tiết của từ"""
        if question_id not in self.questions:
            return None
        return self.questions[question_id]['word_details'] 