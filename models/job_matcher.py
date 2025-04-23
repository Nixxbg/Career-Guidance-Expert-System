import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobMatcher:
    def __init__(self, jobs):
        self.jobs = jobs
        self.vectorizer = TfidfVectorizer()
        
        # Prepare job descriptions and skills for vectorization
        job_texts = []
        for job in self.jobs:
            # Combine title, description, and skills for better matching
            job_text = f"{job['title']} {job['description']} {' '.join(job['required_skills'])}"
            job_texts.append(job_text)
        
        # Fit the vectorizer
        self.job_vectors = self.vectorizer.fit_transform(job_texts)
    
    def match(self, user_profile):
        # Create user vector
        user_text = f"{' '.join(user_profile['skills'])} {user_profile['interests']}"
        user_vector = self.vectorizer.transform([user_text])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_vector, self.job_vectors)[0]
        
        # Combine jobs with their similarity scores
        job_matches = []
        for i, score in enumerate(similarity_scores):
            job = self.jobs[i].copy()  # Create a copy to avoid modifying original
            job['similarity_score'] = float(score)
            job_matches.append(job)
        
        # Sort by similarity score (descending)
        job_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Filter by category if preferred categories are specified
        if user_profile['preferred_categories']:
            job_matches = [job for job in job_matches if job['category'] in user_profile['preferred_categories']]
        
        return job_matches
