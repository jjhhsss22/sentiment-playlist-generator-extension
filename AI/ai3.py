# import necessary modules
import pandas as pd
import neattext.functions as nt
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
import joblib
from sklearn.model_selection import train_test_split
import tensorflow as tf

from matplotlib import pyplot as plt


# Structuring
dataset = pd.read_csv("Dataset/one/emotion_sentimen_dataset.csv")  # Read dataset
dataset = dataset.drop(columns=["ID"])  # remove the ID column completely as we do not need them


# Stopwords removal
dataset['text'] = dataset['text'].apply(nt.remove_stopwords)  # replace the record with the string with stopwords removed


# Stemming
ps = PorterStemmer() # porter stemmer instantiation

def stem_text(text):  # function to apply stemming
    words = word_tokenize(text)
    stemmed_words = [ps.stem(word) for word in words]

    return ' '.join(stemmed_words)

dataset['Filtered_text'] = dataset['text'].apply(stem_text) # Apply the preprocessing function to the text column


# Additional
Filtered_text = dataset['Filtered_text']
Emotion = dataset['Emotion']
Emotion = pd.get_dummies(Emotion) # Convert labels to one-hot encoded format


# vectorisation
count_vectorizer = CountVectorizer()  # count vectorizer instantiation

Filtered_text = count_vectorizer.fit_transform(Filtered_text)  # a count_vectorizer will be made specific to our dataset

joblib.dump(count_vectorizer, "cv/count_vectorizer3.joblib")  # save our count vectorizer


# Splitting
Filtered_text_train, Filtered_text_test, Emotion_train, Emotion_test = train_test_split(Filtered_text, Emotion, test_size=0.2)
                                                                                        # split the dataset into training and testing


# Define the model using the architecture mentioned in the design section
model = tf.keras.Sequential([
    tf.keras.Input(shape=(Filtered_text_train.shape[1],)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(13, activation='softmax')
])


# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])


# Train the model
results = model.fit(Filtered_text_train, Emotion_train, epochs=15, batch_size=16, validation_split=0.2)


# Evaluation
loss, accuracy = model.evaluate(Filtered_text_test, Emotion_test)
print("Accuracy: ", accuracy)
print("Loss: ", loss)


plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(results.history['loss'], label='Train Loss')
plt.plot(results.history['val_loss'], label='Validation Loss')
plt.title('model train vs validation loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper right')

plt.subplot(1, 2, 2)
plt.plot(results.history['accuracy'], label='Train Accuracy')
plt.plot(results.history['val_accuracy'], label='Validation Accuracy')
plt.title('model train vs validation accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper right')

plt.show()


# Save the model
model.save("sentiment_model3.keras")