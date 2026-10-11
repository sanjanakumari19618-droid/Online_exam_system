const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const questions = [
  {
    id: 'q1',
    question: 'Which HTML tag is used to define a large heading?',
    options: ['<h1>', '<head>', '<header>', '<heading>'],
    correctIndex: 0,
  },
  {
    id: 'q2',
    question: 'Which JavaScript keyword declares a block-scoped variable?',
    options: ['var', 'let', 'const', 'function'],
    correctIndex: 1,
  },
  {
    id: 'q3',
    question: 'Which CSS property changes the text color?',
    options: ['background-color', 'font-size', 'color', 'margin'],
    correctIndex: 2,
  },
  {
    id: 'q4',
    question: 'What does HTTP stand for?',
    options: ['HyperText Transfer Protocol', 'High Transfer Text Process', 'Hyperlink Text Transport Program', 'Home Tool Transfer Protocol'],
    correctIndex: 0,
  },
  {
    id: 'q5',
    question: 'Which method is used to add an element to the end of an array?',
    options: ['push()', 'append()', 'add()', 'concat()'],
    correctIndex: 0,
  },
];

app.get('/api/questions', (req, res) => {
  res.json({ questions });
});

app.post('/api/submit', (req, res) => {
  const submittedAnswers = req.body.answers || {};
  let correct = 0;
  const results = questions.map((question) => {
    const selectedIndex = submittedAnswers[question.id];
    const isCorrect = selectedIndex === question.correctIndex;

    if (isCorrect) {
      correct += 1;
    }

    return {
      id: question.id,
      question: question.question,
      selectedAnswer: selectedIndex !== undefined ? question.options[selectedIndex] : 'Not answered',
      correctAnswer: question.options[question.correctIndex],
      isCorrect,
    };
  });

  const total = questions.length;
  const percentage = Math.round((correct / total) * 100);

  res.json({
    score: correct,
    total,
    percentage,
    passed: percentage >= 60,
    results,
  });
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Online Exam System running at http://localhost:${PORT}`);
});
