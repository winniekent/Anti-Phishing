document.addEventListener("DOMContentLoaded", () => {
  const analyzeDataButton = document.getElementById("analyzeData");
  const liveStatus = document.getElementById("liveStatus");
  const overlay = document.getElementById("overlay");
  const popup = document.getElementById("popup");
  const popupClose = document.getElementById("popupClose");
  const predictionText = document.getElementById("predictionText");

  chrome.storage.local.get({ flaggedEmails: [] }, (result) => {
    const count = result.flaggedEmails.length;
    liveStatus.textContent =
      count > 0
        ? `${count} phishing email${count === 1 ? "" : "s"} flagged so far. Automatic scanning is active.`
        : "Open an email in Gmail or Outlook to start scanning.";
  });

  analyzeDataButton.addEventListener("click", () => {
    chrome.tabs.create({ url: "http://localhost:6500/learn" });
  });

  popupClose.addEventListener("click", () => {
    closePopup();
  });

  overlay.addEventListener("click", () => {
    closePopup();
  });

  function openPopup(message) {
    predictionText.textContent = message;
    popup.style.display = "block";
    overlay.style.display = "block";
  }

  function closePopup() {
    popup.style.display = "none";
    overlay.style.display = "none";
  }

  window.showPopupMessage = openPopup;
});
