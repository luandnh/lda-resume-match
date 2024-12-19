from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from wordcloud import WordCloud
import io
import pandas as pd
import uvicorn
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data from CSV
jobs_df = pd.read_json(
    "./data/processed/job_data_processed.json", orient="records", lines=True
)

resumes_df = pd.read_json(
    "./data/processed/resume_data_full.json", orient="records", lines=True
)


# api get list of jobs
@app.get("/api/v1/jobs")
async def read_jobs(limit: int = 10, offset: int = 0, industry: str = ""):
    data = jobs_df
    if industry:
        data = jobs_df[jobs_df["industry"] == industry]

    return {
        "data": data[offset : offset + limit].to_dict(orient="records"),
        "total": len(data),
    }


# api get detail of a job
@app.get("/api/v1/jobs/{job_id}")
async def read_job(job_id: int):
    job = jobs_df[jobs_df["job_id"] == job_id]
    if len(job) == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "data": job.to_dict(orient="records")[0],
    }


# api stats of top n companies by job postings
@app.get("/api/v1/stats/top_companies/postings")
async def read_top_companies(top: int = 10):
    # get top n companies by job postings (value count)
    # Get top 10 most frequent companies and their counts
    top_companies = jobs_df["company_name"].value_counts().head(top).reset_index()
    top_companies.columns = ["company_name", "count"]
    return {
        "data": top_companies.to_dict(orient="records"),
    }


# api stats of top n companies of industry
@app.get("/api/v1/stats/top_companies/industry")
async def read_top_companies(top: int = 10):
    # get top n companies by industry (value count)
    # Get top 10 most frequent companies and their counts
    top_companies = jobs_df["industry"].value_counts().head(top).reset_index()
    top_companies.columns = ["industry", "count"]
    return {
        "data": top_companies.to_dict(orient="records"),
    }


# api get list of resumes
@app.get("/api/v1/resumes")
async def read_resumes(limit: int = 10, offset: int = 0, category: str = ""):
    data = resumes_df
    if category:
        data = resumes_df[resumes_df["category"] == category]

    return {
        "data": data[offset : offset + limit].to_dict(orient="records"),
        "total": len(data),
    }


# api get detail of a resume
@app.get("/api/v1/resumes/{resume_id}")
async def read_resume(resume_id: int):
    resume = resumes_df[resumes_df["ID"] == resume_id]
    if len(resume) == 0:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "data": resume.to_dict(orient="records")[0],
    }


# api stats of top n categories by resumes
@app.get("/api/v1/stats/top_categories/resumes")
async def read_top_categories(top: int = 10):
    # get top n categories by resumes (value count)
    # Get top 10 most frequent categories and their counts
    top_categories = resumes_df["Category"].value_counts().head(top).reset_index()
    top_categories.columns = ["Category", "count"]
    return {
        "data": top_categories.to_dict(orient="records"),
    }


# api get wordcloud of resume category
@app.get("/api/v1/resume/skills/wordcloud")
async def read_resume_wordcloud(category: str = ""):
    data = resumes_df
    if category:
        data = resumes_df[resumes_df["Category"] == category]
    # Replace spaces in multi-word terms with underscores
    data["Skills"] = data["Skills"].apply(
        lambda x: [skill.replace(" ", "_") for skill in x]
    )

    # Flatten the list of skills
    all_skills = [skill for sublist in data["Skills"] for skill in sublist]

    # Combine all skills into a single string
    skills_text = " ".join(all_skills)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        skills_text
    )

    # Save the WordCloud to a BytesIO buffer
    buffer = io.BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)

    # Return the image as a response
    return StreamingResponse(buffer, media_type="image/png")


# api get list of skills
@app.get("/api/v1/skills")
async def read_skills(category: str = ""):
    data = resumes_df
    if category:
        data = resumes_df[resumes_df["Category"] == category]
    # Count the occurrences of each skill
    skill_counts = Counter(
        skill for skills_list in data["Skills"] for skill in skills_list
    )

    # Sort skills by their counts (most frequent first)
    sorted_skills = [skill for skill, count in skill_counts.most_common()]
    return {
        "data": sorted_skills,
    }


# api get list of categories
@app.get("/api/v1/categories")
async def read_categories():
    return {
        "data": resumes_df["Category"].unique().tolist(),
    }


# api get list of industries
@app.get("/api/v1/industries")
async def read_industries():
    return {
        "data": jobs_df["industry"].unique().tolist(),
    }


# api find top matches for a job description
@app.get("/api/v1/jobs/{job_id}/matches")
async def read_matches(job_id: int, top: int = 5):
    job = jobs_df[jobs_df["job_id"] == job_id]
    if len(job) == 0:
        raise HTTPException(status_code=404, detail="Job not found")

    # Step 1: Vectorize the text data
    vectorizer = CountVectorizer(stop_words="english")
    all_text = list(resumes_df["Feature"]) + list(job["jdFeatures"])
    vectorized_text = vectorizer.fit_transform(all_text)

    # Step 2: Fit LDA
    lda = LatentDirichletAllocation(
        n_components=10, random_state=42
    )  # Assuming 3 topics for simplicity
    lda_matrix = lda.fit_transform(vectorized_text)

    # Step 3: Separate LDA outputs for resumes and job descriptions
    resume_topics = lda_matrix[: len(resumes_df)]
    job_topics = lda_matrix[len(resumes_df) :]

    # Step 4: Compute cosine similarity
    lda_similarity_matrix = cosine_similarity(job_topics, resume_topics)

    # Step 5: Find top matches for job description
    similarity_scores = lda_similarity_matrix[0].argsort()[::-1][:top]
    top_matches = []
    for resume_idx in similarity_scores:
        similarity = lda_similarity_matrix[0, resume_idx]
        resume = resumes_df.iloc[resume_idx]
        top_matches.append(
            {"resume": resume.to_dict(), "similarity": float(similarity)}
        )

    top_matches = sorted(top_matches, key=lambda x: x["similarity"], reverse=True)

    return {
        "data": top_matches,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
