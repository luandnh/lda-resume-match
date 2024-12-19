import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import nltk
from PyPDF2 import PdfReader
from nltk import pos_tag, sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = "".join(page.extract_text() for page in reader.pages)
    return text

def preprocess_text(text):
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    sentences = sent_tokenize(text)
    features = {"feature": ""}
    stop_words = set(stopwords.words("english"))
    for sent in sentences:
        if any(criteria in sent for criteria in ["skills", "education"]):
            words = word_tokenize(sent)
            words = [word for word in words if word not in stop_words]
            tagged_words = pos_tag(words)
            filtered_words = [
                word
                for word, tag in tagged_words
                if tag not in ["DT", "IN", "TO", "PRP", "WP"]
            ]
            features["feature"] += " ".join(filtered_words)
    return features

def process_resume_data(df):
    id = df["ID"]
    category = df["Category"]
    print(f"Processing resume data/resume/data/data/{category}/{id}.pdf")
    text = extract_text_from_pdf(
        f"./data/resume/data/data/{category}/{id}.pdf"
    )
    features = preprocess_text(text)
    df["Feature"] = features["feature"]
    df["Skills"] = parse_skills_from_resume(features["feature"])
    return df

def parse_skills_from_resume(text):
    stop_words = set(stopwords.words("english"))
    if pd.isna(text):
        return ''
    words = word_tokenize(text.lower())
    words = [word for word in words if word not in stop_words]
    matched_skills = [skill for skill in skills_list if skill.lower() in words]
    return matched_skills

skills_df = pd.read_csv('./data/skills.csv')
skills_list = skills_df.columns

print("Reading resume data...")
resume_data = pd.read_csv('./data/resume/Resume/Resume.csv')

# resume_data = resume_data.drop(["Resume_html"], axis=1)

# remove the duplicates from the dataset
print("Removing Duplicates...")
resume_data = resume_data.drop_duplicates(subset=["Resume_str"], keep="first")

# preprocess the resume data
print("Preprocessing resume data...")
resume_data = resume_data.apply(process_resume_data, axis=1)
resume_data = resume_data.drop(columns=['Resume_str'])

# save the preprocessed resume data
print("Saving preprocessed resume data...")
resume_data.to_json('./data/processed/resume_data_full.json', orient='records', lines=True)