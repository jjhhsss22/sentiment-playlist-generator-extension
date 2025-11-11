import joblib
import os
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import neattext.functions as nt

#  stopwords removal
def remove_stopwords(text: str) -> str:
    return nt.remove_stopwords(text)

# stemming
def stem(text: str) -> str:
    ps = PorterStemmer()

    words = word_tokenize(text)
    stemmed = [ps.stem(word) for word in words]
    return ' '.join(stemmed)

#  vectorisation "cv/count_vectorizer3.joblib"
def vectorise(stemmed_text: str):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path of current file
    cv_path = os.path.join(BASE_DIR, "..", "cv", "count_vectorizer3.joblib")
    cv_path = os.path.abspath(cv_path)
    cv = joblib.load(cv_path)
    return cv.transform([stemmed_text])

# combined preprocessing pipeline
def preprocess(input_text: str):
    clean_text = str(input_text).strip()
    no_stopwords = remove_stopwords(clean_text)
    stemmed = stem(no_stopwords)
    return vectorise(stemmed)