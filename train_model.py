# train_model.py

import pandas as pd
import numpy as np
import re
import os
import joblib

# Text preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ML
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

# Download NLTK resources (only first time)
nltk.download('stopwords')
nltk.download('wordnet')

# -------------------------------
# 1️⃣ Load Dataset
# -------------------------------

DATA_PATH = "fake_job_postings.csv"   # Make sure CSV is in same folder
df = pd.read_csv(DATA_PATH)

# Keep only necessary columns
df = df[['title', 'description', 'fraudulent']]

# Drop missing values
df = df.dropna()

# Combine title + description
df['text'] = df['title'] + " " + df['description']

print("\nClass Distribution:")
print(df['fraudulent'].value_counts())

# -------------------------------
# 2️⃣ Text Cleaning Function
# -------------------------------

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)   # Remove numbers & symbols
    words = text.split()
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words and len(word) > 2
    ]
    return " ".join(words)

print("\nCleaning text...")
df['clean_text'] = df['text'].apply(clean_text)

# -------------------------------
# 3️⃣ TF-IDF Vectorization
# -------------------------------

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),     # VERY IMPORTANT (detects phrases like "activation fee")
    min_df=5
)

X = vectorizer.fit_transform(df['clean_text'])
y = df['fraudulent']

# -------------------------------
# 4️⃣ Train-Test Split
# -------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y   # Important for imbalance
)

# -------------------------------
# 5️⃣ Train Model
# -------------------------------

model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced'   # Fix imbalance issue
)

print("\nTraining model...")
model.fit(X_train, y_train)

# -------------------------------
# 6️⃣ Evaluate Model
# -------------------------------

y_pred = model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# -------------------------------
# 7️⃣ Optional: Adjust Threshold
# -------------------------------

# Increase fake detection sensitivity
y_prob = model.predict_proba(X_test)
threshold = 0.45  # try 0.4 - 0.5
y_pred_custom = (y_prob[:, 1] > threshold).astype(int)

print("\nClassification Report (Custom Threshold = 0.45):")
print(classification_report(y_test, y_pred_custom))

# -------------------------------
# 8️⃣ Save Model & Vectorizer
# -------------------------------

MODEL_DIR = "saved_model"
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, os.path.join(MODEL_DIR, "model.pkl"))
joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.pkl"))

print("\nModel and Vectorizer saved successfully!")