# Anti-Phishing Extension

## Overview

The Anti-Phishing Extension is a comprehensive browser-based solution designed to detect and prevent phishing attacks in email communications. Leveraging machine learning models, the extension integrates seamlessly with popular email clients like Gmail and Outlook, providing real-time analysis of email content to identify malicious messages. In addition to detection, the extension offers user education resources and behavioral tracking to enhance cybersecurity awareness.

## Features

- **Real-Time Phishing Detection**: Analyzes email content using advanced machine learning models to classify messages as legitimate or phishing attempts.
- **Browser Extension Integration**: Works as a Chrome/Firefox extension with content scripts injected into Gmail and Outlook web interfaces.
- **User Education**: Includes a dedicated landing page with educational resources and an interactive phishing awareness quiz to help users recognize and avoid phishing scams.
- **Behavioral Tracking**: Monitors user interactions to provide insights and improve detection accuracy over time.
- **API Backend**: Powered by a FastAPI server that handles model inference and serves predictions to the extension.
- **Notifications and Alerts**: Provides in-browser notifications for detected threats.

## Architecture

The project is structured into several key components:

- **Backend (`backend/`)**: A FastAPI-based web server that loads pre-trained machine learning models and exposes prediction endpoints. It uses Hugging Face Transformers for sequence classification.
- **Extension (`extension/`)**: Browser extension files including manifest, background scripts, content scripts, and popup interface.
- **Landing Page (`landing/`)**: Educational website served by the backend, accessible via the extension.
- **Models (`models/`)**: Directory containing trained model checkpoints and configurations.
- **Notebooks (`notebooks/`)**: Jupyter notebooks for model training, evaluation, and experimentation.
- **Data (`data/`)**: Placeholder for datasets used in model training (currently empty).

## Technologies Used

- **Backend**: FastAPI, Uvicorn, Transformers, PyTorch, Scikit-learn, Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **Machine Learning**: Hugging Face Transformers, PyTorch, Datasets library
- **Browser Extension**: Manifest V3, Service Workers, Content Scripts
- **Other**: Flask (for static files), Plotly (for visualizations), Requests, TLD library

## Installation

### Prerequisites

- Python 3.8+
- Node.js (for extension development, optional)
- Chrome or Firefox browser

### Backend Setup

1. Navigate to the `backend/` directory:
   ```
   cd backend
   ```

2. Install Python dependencies:
   ```
   pip install -r ../requirements.txt
   ```

3. Ensure trained models are present in `../models/trainer_runs/`.

4. Run the server:
   ```
   uvicorn app:app --host 0.0.0.0 --port 6500 --reload
   ```

### Extension Setup

1. Open your browser's extension management page (e.g., `chrome://extensions/` for Chrome).

2. Enable "Developer mode".

3. Click "Load unpacked" and select the `extension/` directory.

4. The extension should now be installed and active.

### Landing Page

The landing page is automatically served by the backend at `http://localhost:6500/learn/` when the server is running.

## Usage

1. **Install the Extension**: Follow the extension setup steps above.

2. **Access Email Clients**: Open Gmail or Outlook in your browser. The extension will automatically inject detection scripts.

3. **View Predictions**: The extension analyzes email content and provides indicators for potential phishing attempts.

4. **Access Popup**: Click the extension icon to open the popup interface for additional controls and information.

5. **Educational Resources**: Visit the landing page via the extension for phishing awareness materials and take the interactive quiz to test your knowledge.

## API Endpoints

- `POST /api/predict`: Accepts text input and returns phishing probability scores.
  - Request body: `{"text": "email content"}` or `{"texts": ["email1", "email2"]}`
  - Response: Classification results with confidence scores.

## Development

### Training Models

Use the Jupyter notebook in `notebooks/Pishing.ipynb` to train and evaluate models. Ensure datasets are placed in the `data/` directory.

### Extension Development

Modify files in `extension/` as needed. Reload the extension in the browser after changes.

### Backend Development

The FastAPI app in `backend/app.py` can be extended with additional endpoints or features.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test thoroughly.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, please open an issue in the repository.