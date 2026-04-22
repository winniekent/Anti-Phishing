const resetButton = document.getElementById("resetChecklist");
const checks = document.querySelectorAll(".check-item input");

if (resetButton) {
  resetButton.addEventListener("click", () => {
    checks.forEach((check) => {
      check.checked = false;
    });
  });
}

// Quiz functionality
const quizQuestions = [
  {
    prompt: "You receive an email from a clinic asking you to confirm an upcoming appointment by clicking a link. What should you do?",
    options: [
      { text: "Click the link to confirm the appointment right away", correct: false },
      { text: "Call the clinic using the number on their website instead", correct: true },
      { text: "Reply to the email asking if it's legitimate", correct: false }
    ],
    explanation: "Always verify appointment requests through known clinic contact details, not email links."
  },
  {
    prompt: "An email appears from your insurer asking you to download a new benefits form. The attachment is an unfamiliar file type. What should you do?",
    options: [
      { text: "Download the file and complete the form", correct: false },
      { text: "Contact your insurer directly before opening it", correct: true },
      { text: "Forward the email to a friend to see if they think it's safe", correct: false }
    ],
    explanation: "Unexpected attachments from insurance or healthcare providers should be confirmed directly."
  },
  {
    prompt: "You get a message from 'support@patientportal.com' asking you to reset your password immediately. What should you do?",
    options: [
      { text: "Use the link in the email to reset your password", correct: false },
      { text: "Open the patient portal manually and reset it there", correct: true },
      { text: "Ignore the email because it might be spam", correct: false }
    ],
    explanation: "Security messages are safest when handled on the official site instead of through email links."
  },
  {
    prompt: "A healthcare provider email says your medical record has been released and asks for a payment to view it. What should you do?",
    options: [
      { text: "Pay the fee to access your record", correct: false },
      { text: "Verify the request with the provider by phone", correct: true },
      { text: "Reply with your payment details", correct: false }
    ],
    explanation: "Legitimate providers do not request payment or sensitive data via email without prior secure communication."
  },
  {
    prompt: "You receive an email from a doctor with a link to a lab result. The link preview shows a strange domain. What should you do?",
    options: [
      { text: "Click the link because it looks like lab results", correct: false },
      { text: "Visit the provider portal manually and check the results there", correct: true },
      { text: "Reply to ask if the doctor sent it", correct: false }
    ],
    explanation: "Always verify that lab and medical links go to the official portal before clicking."
  },
  {
    prompt: "Your health app emails you about a new security alert and asks for your login details. How should you respond?",
    options: [
      { text: "Enter your details in the email form", correct: false },
      { text: "Open the app directly and review your account security settings", correct: true },
      { text: "Delete the message and ignore it", correct: false }
    ],
    explanation: "Security alerts should be handled through the app or website, not by giving credentials in email."
  },
  {
    prompt: "A pharmacy sends a message saying your prescription is ready if you verify your identity. What is the safest choice?",
    options: [
      { text: "Verify with the link in the message", correct: false },
      { text: "Call the pharmacy using the number on your prescription label", correct: true },
      { text: "Send your ID information in a reply", correct: false }
    ],
    explanation: "Verify prescription and identity requests using known pharmacy contact information."
  },
  {
    prompt: "An urgent email says your insurance is canceled unless you update payment details immediately. What should you do?",
    options: [
      { text: "Update your payment details through the link", correct: false },
      { text: "Contact your insurance provider directly to confirm the notice", correct: true },
      { text: "Ignore it and hope it goes away", correct: false }
    ],
    explanation: "Urgent billing notices should be confirmed directly with the insurance company."
  },
  {
    prompt: "A message from a lab says your test results are attached, but the attachment is a .zip file. What should you do?",
    options: [
      { text: "Open the .zip file to see the results", correct: false },
      { text: "Ask the lab to resend the results through a secure portal", correct: true },
      { text: "Reply with your computer details", correct: false }
    ],
    explanation: "Medical results are rarely sent as unrequested compressed files; use secure portals instead."
  },
  {
    prompt: "Your mental health provider sends a link to complete a new consent form. The sender address looks odd. What should you do?",
    options: [
      { text: "Complete the form using the link", correct: false },
      { text: "Confirm the sender with your provider before clicking", correct: true },
      { text: "Ignore the sender and trust the message", correct: false }
    ],
    explanation: "Any unusual sender or consent request should be verified directly with the provider."
  }
];

let currentQuestionIndex = 0;
let score = 0;
let userAnswers = [];

const quizPrompt = document.getElementById("quizPrompt");
const quizActions = document.getElementById("quizActions");
const quizResult = document.getElementById("quizResult");
const prevButton = document.getElementById("prevQuestion");
const nextButton = document.getElementById("nextQuestion");
const questionCounter = document.getElementById("questionCounter");
const quizScore = document.getElementById("quizScore");
const scoreValue = document.getElementById("scoreValue");
const scoreTotal = document.getElementById("scoreTotal");
const scoreMessage = document.getElementById("scoreMessage");
const restartButton = document.getElementById("restartQuiz");

function loadQuestion(index) {
  const question = quizQuestions[index];
  quizPrompt.textContent = question.prompt;
  quizActions.innerHTML = "";
  quizResult.textContent = "";

  question.options.forEach((option, optionIndex) => {
    const button = document.createElement("button");
    button.className = "btn answer";
    button.textContent = option.text;
    button.dataset.index = optionIndex;
    button.addEventListener("click", () => selectAnswer(optionIndex));
    quizActions.appendChild(button);
  });

  questionCounter.textContent = `Question ${index + 1} of ${quizQuestions.length}`;
  prevButton.disabled = index === 0;
  nextButton.textContent = index === quizQuestions.length - 1 ? "Finish Quiz" : "Next";
}

function selectAnswer(optionIndex) {
  const question = quizQuestions[currentQuestionIndex];
  const isCorrect = question.options[optionIndex].correct;
  userAnswers[currentQuestionIndex] = optionIndex;

  if (isCorrect) {
    quizResult.textContent = "Correct! " + question.explanation;
    quizResult.style.color = "green";
  } else {
    quizResult.textContent = "Incorrect. " + question.explanation;
    quizResult.style.color = "red";
  }

  // Highlight the selected answer
  const buttons = quizActions.querySelectorAll(".btn");
  buttons.forEach((btn, idx) => {
    if (idx === optionIndex) {
      btn.classList.add(isCorrect ? "correct" : "incorrect");
    } else {
      btn.classList.remove("correct", "incorrect");
    }
  });
}

function showScore() {
  score = userAnswers.reduce((acc, answerIndex, index) => {
    return acc + (quizQuestions[index].options[answerIndex].correct ? 1 : 0);
  }, 0);

  scoreValue.textContent = score;
  scoreTotal.textContent = quizQuestions.length;

  if (score === quizQuestions.length) {
    scoreMessage.textContent = "Excellent! You're well-prepared against phishing attacks.";
  } else if (score >= Math.ceil(quizQuestions.length * 0.6)) {
    scoreMessage.textContent = "Good job! Review the explanations to improve further.";
  } else {
    scoreMessage.textContent = "Keep learning! Phishing awareness is crucial for online safety.";
  }

  document.getElementById("quizCard").style.display = "none";
  document.querySelector(".quiz-navigation").style.display = "none";
  quizScore.style.display = "block";
}

prevButton.addEventListener("click", () => {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    loadQuestion(currentQuestionIndex);
  }
});

nextButton.addEventListener("click", () => {
  if (currentQuestionIndex < quizQuestions.length - 1) {
    currentQuestionIndex++;
    loadQuestion(currentQuestionIndex);
  } else {
    showScore();
  }
});

restartButton.addEventListener("click", () => {
  currentQuestionIndex = 0;
  score = 0;
  userAnswers = [];
  document.getElementById("quizCard").style.display = "block";
  document.querySelector(".quiz-navigation").style.display = "flex";
  quizScore.style.display = "none";
  loadQuestion(0);
});

// Initialize quiz
loadQuestion(0);
