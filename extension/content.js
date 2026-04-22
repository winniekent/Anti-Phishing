const EMAIL_HOSTS = ["mail.google.com", "outlook.live.com", "outlook.office.com"];
const SCAN_DEBOUNCE_MS = 1500;

let lastFingerprint = null;
let scanTimer = null;

function isSupportedMailbox() {
  return EMAIL_HOSTS.includes(window.location.hostname);
}

function debounceScan() {
  window.clearTimeout(scanTimer);
  scanTimer = window.setTimeout(scanCurrentEmail, SCAN_DEBOUNCE_MS);
}

function extractLinks(root) {
  return Array.from(root.querySelectorAll("a[href]"))
    .map((link) => link.href)
    .filter(Boolean)
    .slice(0, 50);
}

function getText(root) {
  return (root.innerText || root.textContent || "").replace(/\s+/g, " ").trim();
}

function extractGmailEmail() {
  const subjectNode =
    document.querySelector("h2[data-thread-perm-id]") ||
    document.querySelector("h2.hP") ||
    document.querySelector("[role='main'] h2");

  const senderNode =
    document.querySelector("span[email]") ||
    document.querySelector(".gD[email]") ||
    document.querySelector("[data-hovercard-id]");

  const bodyNode =
    document.querySelector("div.a3s.aiL") ||
    document.querySelector("div[role='listitem'] div.a3s") ||
    document.querySelector("div.gs");

  if (!bodyNode) {
    return null;
  }

  const subject = subjectNode ? getText(subjectNode) : "";
  const sender = senderNode?.getAttribute("email") || getText(senderNode || document.createElement("div"));
  const body = getText(bodyNode);
  const links = extractLinks(bodyNode);

  if (!subject && !sender && !body) {
    return null;
  }

  return {
    provider: "gmail",
    subject,
    sender,
    body,
    links
  };
}

function extractOutlookEmail() {
  const subjectNode =
    document.querySelector('[role="heading"]') ||
    document.querySelector('[data-app-section="MailReadCompose"] h1') ||
    document.querySelector("div[aria-label='Message header'] span");

  const senderNode =
    document.querySelector('[data-testid="message-from"]') ||
    document.querySelector('[aria-label^="From:"]') ||
    document.querySelector("span[title*='@']");

  const bodyNode =
    document.querySelector('[data-app-section="MailReadCompose"] div[role="document"]') ||
    document.querySelector('[aria-label="Message body"]') ||
    document.querySelector('div[contenteditable="true"][aria-label*="Message body"]');

  if (!bodyNode) {
    return null;
  }

  const subject = subjectNode ? getText(subjectNode) : "";
  const sender = senderNode ? getText(senderNode) : "";
  const body = getText(bodyNode);
  const links = extractLinks(bodyNode);

  if (!subject && !sender && !body) {
    return null;
  }

  return {
    provider: "outlook",
    subject,
    sender,
    body,
    links
  };
}

function extractEmailContent() {
  if (!isSupportedMailbox()) {
    return null;
  }

  if (window.location.hostname === "mail.google.com") {
    return extractGmailEmail();
  }

  return extractOutlookEmail();
}

function fingerprintEmail(emailData) {
  return JSON.stringify({
    provider: emailData.provider,
    sender: emailData.sender,
    subject: emailData.subject,
    bodyPreview: emailData.body.slice(0, 500)
  });
}

function scanCurrentEmail() {
  const emailData = extractEmailContent();

  if (!emailData) {
    return;
  }

  const fingerprint = fingerprintEmail(emailData);
  if (fingerprint === lastFingerprint) {
    return;
  }

  lastFingerprint = fingerprint;

  chrome.runtime.sendMessage({
    type: "analyzeEmail",
    email: {
      ...emailData,
      text: [emailData.subject, emailData.sender, emailData.body].filter(Boolean).join("\n\n")
    }
  });
}

if (isSupportedMailbox()) {
  const observer = new MutationObserver(() => {
    debounceScan();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  debounceScan();
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "showThreatPopup" && request.message) {
    showThreatPopup(request.message);
  }
});

function showThreatPopup(message) {
  let popup = document.getElementById("phishing-detector-threat-popup");
  if (!popup) {
    popup = document.createElement("div");
    popup.id = "phishing-detector-threat-popup";
    popup.style.position = "fixed";
    popup.style.top = "16px";
    popup.style.right = "16px";
    popup.style.zIndex = "2147483647";
    popup.style.width = "340px";
    popup.style.maxWidth = "calc(100vw - 32px)";
    popup.style.padding = "16px";
    popup.style.borderRadius = "14px";
    popup.style.background = "#fff6f6";
    popup.style.color = "#1f2937";
    popup.style.boxShadow = "0 16px 32px rgba(0,0,0,0.18)";
    popup.style.fontFamily = "Arial, sans-serif";
    popup.style.fontSize = "13px";
    popup.style.lineHeight = "1.5";
    popup.style.border = "1px solid #f5c2c7";
    popup.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
        <div>
          <strong style="display:block;margin-bottom:8px;color:#b91c1c;">⚠️ Phishing email detected</strong>
          <div id="phishing-detector-threat-message"></div>
        </div>
        <button id="phishing-detector-threat-close" style="background:none;border:none;color:#1f2937;font-size:18px;cursor:pointer;line-height:1;padding:0;">×</button>
      </div>
    `;
    document.body.appendChild(popup);
    popup.querySelector("#phishing-detector-threat-close").addEventListener("click", () => {
      popup.remove();
    });
  }
  const messageEl = popup.querySelector("#phishing-detector-threat-message");
  if (messageEl) {
    messageEl.textContent = message;
  }

  window.setTimeout(() => {
    popup?.remove();
  }, 12000);
}
