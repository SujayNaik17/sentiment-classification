# utils.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download once (if not already done)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = text.encode('ascii', 'ignore').decode('ascii')  # remove emojis
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)
