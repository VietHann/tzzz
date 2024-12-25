let currentQuestion = null;
let currentQuestionType = 'word';

async function startQuiz() {
    const numQuestions = document.getElementById('numQuestions').value;
    
    try {
        const response = await fetch('/start-quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                num_questions: parseInt(numQuestions)
            })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            // Reset UI
            document.getElementById('quizSection').style.display = 'block';
            document.getElementById('finalResult').style.display = 'none';
            document.getElementById('result').innerHTML = '';
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('questionProgress').textContent = 'Câu hỏi: 0/0';
            document.getElementById('scoreProgress').textContent = 'Điểm: 0/0';
            
            getNextQuestion();
        } else {
            alert('Lỗi khi bắt đầu bài test: ' + data.message);
        }
    } catch (error) {
        alert('Lỗi: ' + error);
    }
}

async function getNextQuestion() {
    try {
        const response = await fetch(`/get-question?type=${currentQuestionType}`);
        const data = await response.json();
        
        if (data.completed) {
            showFinalResult(data.score, data.total);
            return;
        }

        displayQuestion(data);
        currentQuestion = data;
        updateProgress(data.current_number, data.total);
        
        // Reset UI
        document.getElementById('checkBtn').style.display = 'block';
        document.getElementById('nextBtn').style.display = 'none';
        document.getElementById('result').innerHTML = '';
    } catch (error) {
        alert('Lỗi: ' + error);
    }
}

function updateProgress(current, total) {
    const percent = (current / total) * 100;
    document.getElementById('progressBar').style.width = `${percent}%`;
    document.getElementById('questionProgress').textContent = `Câu hỏi: ${current}/${total}`;
}

function displayQuestion(question) {
    const questionText = document.getElementById('questionText');
    questionText.innerHTML = question.question.replace(
        /'([^']+)'/g, 
        (match, word) => `<span class="chinese-text">${word}</span>`
    );
    
    const choicesContainer = document.getElementById('choices');
    choicesContainer.innerHTML = '';
    
    question.choices.forEach((choice, index) => {
        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'form-check mb-2';
        choiceDiv.innerHTML = `
            <input class="form-check-input" type="radio" name="answer" value="${choice}" id="choice${index}">
            <label class="form-check-label" for="choice${index}">
                <span class="${question.type === 'word' ? 'chinese-text' : ''}">${choice}</span>
            </label>
        `;
        choicesContainer.appendChild(choiceDiv);
    });
}

async function checkAnswer() {
    const selectedAnswer = document.querySelector('input[name="answer"]:checked');
    if (!selectedAnswer) {
        alert('Vui lòng chọn một đáp án');
        return;
    }

    try {
        const response = await fetch('/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                questionId: currentQuestion.id,
                answer: selectedAnswer.value
            })
        });
        const result = await response.json();
        
        // Hiển thị kết quả
        const resultDiv = document.getElementById('result');
        if (result.correct) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-check-circle"></i> Chính xác!</h5>
                    <div class="word-details">
                        <p class="chinese-word">${result.wordDetails.word}</p>
                        <p class="pinyin">${result.wordDetails.pronunciation}</p>
                        <p class="meaning">${result.wordDetails.meaning}</p>
                        <p><i class="fas fa-volume-up"></i> ${result.wordDetails.sound}</p>
                    </div>
                </div>`;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-times-circle"></i> Sai!</h5>
                    <p>Đáp án đúng: <span class="chinese-text">${result.correctAnswer}</span></p>
                    <div class="word-details">
                        <p class="chinese-word">${result.wordDetails.word}</p>
                        <p class="pinyin">${result.wordDetails.pronunciation}</p>
                        <p class="meaning">${result.wordDetails.meaning}</p>
                        <p><i class="fas fa-volume-up"></i> ${result.wordDetails.sound}</p>
                    </div>
                </div>`;
        }
        
        // Cập nhật điểm số
        document.getElementById('scoreProgress').textContent = `Điểm: ${result.score}/${result.total}`;
        
        // Hiển thị nút next
        document.getElementById('checkBtn').style.display = 'none';
        document.getElementById('nextBtn').style.display = 'block';
    } catch (error) {
        alert('Lỗi: ' + error);
    }
}

async function showFinalResult(score, total) {
    document.getElementById('quizSection').style.display = 'none';
    document.getElementById('finalResult').style.display = 'block';
    document.getElementById('finalScore').textContent = `${score}/${total}`;
    
    try {
        // Lưu kết quả
        const response = await fetch('/save-result', {
            method: 'POST'
        });
        const result = await response.json();
        
        // Load lại lịch sử
        await loadHistory();
        
        // Hiển thị nút ôn tập nếu có câu sai
        const wrongAnswers = await fetch('/get-wrong-answers').then(res => res.json());
        document.getElementById('reviewBtn').style.display = 
            wrongAnswers.length > 0 ? 'inline-block' : 'none';
    } catch (error) {
        console.error('Lỗi khi lưu kết quả:', error);
    }
}

function changeQuestionType(type) {
    currentQuestionType = type;
    // Đổi active button
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

function nextQuestion() {
    getNextQuestion();
}

// Thêm CSS cho word-details
const style = document.createElement('style');
style.textContent = `
    .word-details {
        background-color: rgba(255,255,255,0.8);
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .word-details p {
        margin-bottom: 5px;
    }
`;
document.head.appendChild(style);

// Thêm hàm để load và hiển thị lịch sử
async function loadHistory() {
    try {
        const response = await fetch('/get-history');
        const history = await response.json();
        
        if (Array.isArray(history)) {  // Kiểm tra history có phải là mảng
            updateHistoryTable(history);
            updateStats(history);
        } else {
            console.error('History không phải là mảng:', history);
        }
    } catch (error) {
        console.error('Lỗi khi load history:', error);
    }
}

// Cập nhật bảng lịch sử
function updateHistoryTable(history) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;  // Kiểm tra element tồn tại
    
    tbody.innerHTML = '';
    
    history.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.total_questions}</td>
            <td>${record.correct_answers}</td>
            <td>${record.score}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Cập nhật thống kê
function updateStats(history) {
    if (!Array.isArray(history) || history.length === 0) return;
    
    const totalQuizzes = history.length;
    const averageScore = history.reduce((sum, record) => sum + record.score, 0) / totalQuizzes;
    const totalWrong = history.reduce((sum, record) => 
        sum + (record.total_questions - record.correct_answers), 0);
    
    document.getElementById('totalQuizzes').textContent = totalQuizzes;
    document.getElementById('averageScore').textContent = `${averageScore.toFixed(1)}%`;
    document.getElementById('totalWrong').textContent = totalWrong;
}

// Load lịch sử khi trang được tải
document.addEventListener('DOMContentLoaded', loadHistory);

// Thêm hàm ôn tập câu sai
async function reviewWrongAnswers() {
    try {
        const response = await fetch('/start-review', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('finalResult').style.display = 'none';
            document.getElementById('quizSection').style.display = 'block';
            getNextReviewQuestion();
        } else {
            alert(data.message);
        }
    } catch (error) {
        alert('Lỗi: ' + error);
    }
}

async function getNextReviewQuestion() {
    try {
        const response = await fetch('/get-review-question');
        const question = await response.json();
        
        if (!question) {
            alert('Đã hoàn thành ôn tập!');
            document.getElementById('quizSection').style.display = 'none';
            document.getElementById('finalResult').style.display = 'block';
            return;
        }
        
        displayQuestion({
            question: question.question,
            choices: question.choices,
            id: question.id,
            type: question.type
        });
    } catch (error) {
        alert('Lỗi: ' + error);
    }
} 