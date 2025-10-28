import joblib
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

#  vectorisation
def vectorise(stemmed_text: str):
    cv = joblib.load("AI/development/cv/count_vectorizer3.joblib")
    return cv.transform([stemmed_text])

# combined preprocessing pipeline
def preprocess(input_text: str):
    clean_text = str(input_text).strip()
    no_stopwords = remove_stopwords(clean_text)
    stemmed = stem(no_stopwords)
    return vectorise(stemmed)