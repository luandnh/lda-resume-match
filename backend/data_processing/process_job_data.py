import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import nltk
from nltk import pos_tag, sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng")


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


# Preprocessing the company_industries (used to filter out job descriptions from matching industries that validate our resume data)
print("Reading company industries data...")
company_industries = pd.read_csv("./data/linkedin/companies/company_industries.csv")
# company_industries.info()

desired_industries = [
    "IT Services and IT Consulting",
    "Financial Services",
    "Real Estate",
    "Banking",
    "Technology, Information and Internet",
    "Software Development",
    "Computer and Network Security",
    "Hospitals and Health Care",
    "Insurance",
    "Biotechnology Research",
    "Utilities",
    "Consumer Services",
    "Advertising Services"
]
print("Filtering company industries data...")
filtered_industries = company_industries[
    company_industries["industry"].isin(desired_industries)
]
# filtered_industries.info()

# Preprocessing Job Postings Dataset (Linkedin)
print("Reading job postings data...")
job_posts = pd.read_csv("./data/linkedin/postings.csv")
job_posts.head()

job_posts = job_posts[
    ["job_id", "company_id", "company_name", "title", "description", "skills_desc"]
]
job_posts.head()

if job_posts.empty:
    print("empty")

# print total number of job postings
print("Total number of job postings: " + str(len(job_posts)))

job_descriptions = job_posts[
    ["job_id", "company_id", "company_name", "title", "description", "skills_desc"]
]

# Removing empty descriptions
print("Removing empty descriptions...")
job_descriptions = job_descriptions.dropna()
job_descriptions.isnull().sum()

# Filtering job postings by industries
print("Filtering job postings by industries...")
job_descriptions_filtered = job_descriptions.merge(
    filtered_industries[["company_id", "industry"]], on="company_id", how="inner"
)
job_descriptions2 = job_descriptions_filtered.dropna()
job_descriptions2 = job_descriptions2[
    job_descriptions2["description"].apply(lambda x: isinstance(x, str))
]
job_descriptions2["jdFeatures"] = job_descriptions2["description"].apply(
    lambda x: preprocess_text(x)["feature"]
)
job_descriptions2["skillFeatures"] = job_descriptions2["skills_desc"].apply(
    lambda x: preprocess_text(x)["feature"]
)

# Replacing empty string with Null
print("Replacing empty string with Null...")
job_descriptions2["jdFeatures"] = job_descriptions2["jdFeatures"].replace(
    r"^\s*$", np.nan, regex=True
)
job_descriptions2["skillFeatures"] = job_descriptions2["skillFeatures"].replace(
    r"^\s*$", np.nan, regex=True
)
job_descriptions2 = job_descriptions2.drop(
    columns=["skills_desc", "skillFeatures"], axis=1
)
job_descriptions2 = job_descriptions2.dropna(subset=["jdFeatures"])
job_descriptions2.head()

# save the preprocessed job postings data
print("Saving preprocessed job postings data...")
job_descriptions2.to_json(
    "./data/processed/job_data_processed.json", orient="records", lines=True
)
