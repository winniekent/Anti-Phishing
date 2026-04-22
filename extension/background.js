const API_BASE = "http://localhost:6500";
const LEARN_URL = `${API_BASE}/learn`;
const PHISHING_SCORE_THRESHOLD = 0.995;
const SUSPICIOUS_SCORE_THRESHOLD = 0.90;

chrome.runtime.onInstalled.addListener(() => {
  console.log("Email phishing detector installed.");
})

chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
  if (buttonIndex === 0) {
    chrome.tabs.create({ url: LEARN_URL });
  }
});

chrome.notifications.onClicked.addListener(() => {
  chrome.tabs.create({ url: LEARN_URL });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "analyzeEmail" && request.email) {
    analyzeEmail(request.email, sender.tab?.id);
    sendResponse({ status: "analysis_started" });
    return true;
  }

  if (request.type === "retrainModel") {
    retrainModel();
    sendResponse({ status: "retraining_started" });
    return true;
  }

  return false;
});

async function analyzeEmail(email, tabId) {
  try {
    await logCollectedEmail(email);

    console.debug("Sending email payload to predict API", {
      sender: email.sender,
      subject: email.subject,
      textPreview: email.text?.slice(0, 300)
    });

    const response = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: email.text })
    });

    if (!response.ok) {
      throw new Error(`Prediction request failed with status ${response.status}`);
    }

    const data = await response.json();
    const score = typeof data.score === "number" ? data.score : 0;
    const isPhishing = score >= PHISHING_SCORE_THRESHOLD;
    const isSuspicious = score >= SUSPICIOUS_SCORE_THRESHOLD;
    const prediction = isPhishing ? "phishing" : isSuspicious ? "suspicious" : "safe";

    if (isPhishing) {
      await saveDetectedEmail(email, score);
    }

    console.debug("Email analysis raw:", {
      sender: email.sender,
      subject: email.subject,
      score,
      prediction
    });

    await sendAnalytics(email, prediction, score);

    if (isPhishing) {
      notifyUser(email, prediction, score, email.sender, email.subject);
    }

    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        type: "emailAnalysisResult",
        prediction,
        score,
        sender: email.sender,
        subject: email.subject
      });

      if (isPhishing) {
        const alertSender = formatSenderForAlert(email.sender);
        const senderText = alertSender ? `from ${alertSender}` : "";
        chrome.tabs.sendMessage(tabId, {
          type: "showThreatPopup",
          message: `Phishing detected ${senderText}.\nSubject: ${email.subject || "No subject"}.\nScore: ${(score * 100).toFixed(0)}%.\nPlease avoid clicking any links or replying.`
        });
      }
    }
  } catch (error) {
    console.error("Email analysis error:", error);
  }
}

function notifyUser(email, prediction, score, rawSender, rawSubject) {
  if (prediction !== "phishing") {
    return;
  }

  const sender = formatSenderForAlert(rawSender);
  const subject = rawSubject || "No subject";
  const scoreText = `Score: ${(score * 100).toFixed(0)}%`;
  const senderLine = sender ? `Sender: ${sender}\n` : "";

  chrome.notifications.create({
    type: "basic",
    iconUrl: chrome.runtime.getURL("healthcare-icon.svg"),
    title: "⚠️ Phishing Email Detected",
    message: `${senderLine}Subject: ${subject}\n${scoreText}\nThis email is likely malicious. Do not click links or provide credentials.`,
    buttons: [{ title: "Learn More" }],
    priority: 2
  }).catch((error) => {
    console.error("Notification error:", error);
  });
}

function formatSenderForAlert(sender) {
  if (!sender || typeof sender !== "string") {
    return null;
  }

  const normalized = sender.trim();
  if (!normalized) {
    return null;
  }

  const emailMatch = normalized.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/);
  const candidate = emailMatch ? emailMatch[0] : normalized;
  const genericProvider = /(gmail|yahoo|hotmail|outlook|live|aol)\.(com|net|co|org)$/i;

  if (!candidate.includes("@") || genericProvider.test(candidate)) {
    return null;
  }

  return candidate;
}

function saveDetectedEmail(email, score) {
  return new Promise((resolve) => {
    chrome.storage.local.get({ flaggedEmails: [] }, (result) => {
      const updated = [
        ...result.flaggedEmails,
        {
          ...email,
          score: score ?? null,
          detectedAt: new Date().toISOString()
        }
      ];

      chrome.storage.local.set({ flaggedEmails: updated }, resolve);
    });
  });
}

function logCollectedEmail(email) {
  return fetch(`${API_BASE}/api/collect_url`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      provider: email.provider,
      sender: email.sender,
      subject: email.subject,
      links: email.links,
      text: email.text,
      timestamp: new Date().toISOString()
    })
  }).catch((error) => {
    console.error("Collection error (backend may be offline):", `${API_BASE}/api/collect_url`, error);
  });
}

function sendAnalytics(email, prediction, score) {
  return fetch(`${API_BASE}/api/track`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      event: "email_prediction",
      provider: email.provider,
      sender: email.sender,
      subject: email.subject,
      linkCount: Array.isArray(email.links) ? email.links.length : 0,
      prediction,
      score: score ?? null,
      timestamp: new Date().toISOString()
    })
  }).catch((error) => {
    console.error("Analytics error:", error);
  });
}

function retrainModel() {
  fetch(`${API_BASE}/api/retrain`, {
    method: "POST"
  })
    .then((res) => res.json())
    .then((data) => {
      chrome.notifications.create({
        type: "basic",
        iconUrl: chrome.runtime.getURL("healthcare-icon.svg"),
        title: "Model Retraining",
        message: data.message || "Retraining completed"
      }).catch((error) => {
        console.error("Retraining notification error:", error);
      });
    })
    .catch((error) => {
      console.error("Retraining error:", error);
    });
}
