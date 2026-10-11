const questionContainer = document.getElementById('questions');
const examForm = document.getElementById('exam-form');
const loading = document.getElementById('loading');
const resultPanel = document.getElementById('result-panel');
const resultSummary = document.getElementById('result-summary');
const resultDetails = document.getElementById('result-details');

async function loadQuestions() {
  try {
    const response = await fetch('/api/questions');
    const data = await response.json();

    questionContainer.innerHTML = data.questions
      .map(
        (question, index) => `
          <div class="question-block">
            <h3>${index + 1}. ${question.question}</h3>
            <div class="options">
              ${question.options
                .map(
                  (option, optionIndex) => `
                    <label class="option">
                      <input type="radio" name="${question.id}" value="${optionIndex}" required />
                      <span>${option}</span>
                    </label>
                  `
                )
                .join('')}
            </div>
          </div>
        `
      )
      .join('');

    loading.classList.add('hidden');
    examForm.classList.remove('hidden');
  } catch (error) {
    loading.textContent = 'Failed to load exam questions. Please refresh the page.';
    console.error(error);
  }
}

examForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(examForm);
  const answers = {};

  formData.forEach((value, key) => {
    answers[key] = Number(value);
  });

  try {
    const response = await fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ answers }),
    });

    const data = await response.json();

    examForm.classList.add('hidden');
    resultPanel.classList.remove('hidden');

    const statusClass = data.passed ? 'pass' : 'fail';
    const statusText = data.passed ? 'Passed' : 'Failed';

    resultSummary.innerHTML = `
      <div class="${statusClass}">${statusText}</div>
      <div>You scored ${data.score} / ${data.total} (${data.percentage}%)</div>
    `;

    resultDetails.innerHTML = data.results
      .map(
        (result) => `
          <div class="result-item ${result.isCorrect ? 'correct' : 'incorrect'}">
            <strong>Q:</strong> ${result.question}<br />
            <strong>Your answer:</strong> ${result.selectedAnswer}<br />
            <strong>Correct answer:</strong> ${result.correctAnswer}
          </div>
        `
      )
      .join('');
  } catch (error) {
    alert('Something went wrong while submitting the exam.');
    console.error(error);
  }
});

loadQuestions();
