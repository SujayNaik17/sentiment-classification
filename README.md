# Sentiment Classification for E-commerce Reviews

## Project Overview

This project builds an end-to-end sentiment analysis system for customer reviews scraped from Flipkart. It involves web scraping, data preprocessing, model training using an SVM classifier, and a deployed Flask API that predicts the sentiment of a given product review as **positive**, **neutral**, or **negative** with a confidence score.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/SujayNaik17/sentiment-classification.git
   cd sentiment-classification
   ```

2. Navigate to the API folder:
   ```bash
   cd api
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask API:
   ```bash
   python app.py
   ```

5. The API will be available at:
   ```
   http://127.0.0.1:5000/predict
   ```

## API Folder

The `api` folder contains the Flask application with the main server file `app.py` that serves the sentiment prediction endpoint.

## Scraping Flipkart Reviews

The scraping module uses **BeautifulSoup** and **requests** to extract reviews from Flipkart product pages.

Extracted fields include:
* Product Name
* Product ID
* Review Text
* Review Rating
* Reviewer Verified


## Data Preprocessing

The preprocessing pipeline cleans the raw reviews by:
* Removing HTML, punctuation, and noise
* Lowercasing and tokenizing
* Mapping star ratings:
  * 4-5 stars → Positive
  * 3 stars → Neutral
  * 1-2 stars → Negative

## Model Training

The model training process:
* Converts text to features using **TF-IDF**
* Trains an **SVM** classifier
* Saves the trained model and vectorizer for deployment

## API Usage

### Endpoint:
```
POST http://127.0.0.1:5000/predict
```

### Sample Request (JSON):
```json
{
    "text": "The product is really amazing and useful!"
}
```

### Sample Response (JSON):
```json
{
    "confidence": 0.9822,
    "input": "The product is really amazing and useful!",
    "predicted_sentiment": "positive"
}
```

## Requirements

The requirements.txt file is located in the `api` folder. Install dependencies using:
```bash
cd api
pip install -r requirements.txt
```

### Key Libraries Used:
* `BeautifulSoup4` - Web scraping
* `requests` - HTTP requests
* `scikit-learn` - Machine learning
* `flask` - API framework
* `pandas`, `numpy` - Data manipulation
