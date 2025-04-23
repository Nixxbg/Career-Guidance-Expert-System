from flask import Flask, render_template, request, redirect, url_for
import json
import os
from models.job_matcher import JobMatcher
from models.rule_matcher import RuleMatcher

app = Flask(__name__)

# Load job database
def load_jobs():
    with open('data/jobs_database.json', 'r') as f:
        return json.load(f)

# Initialize matchers
job_matcher = None
rule_matcher = None

@app.route('/')
def index():
    # Get available skills from the job database
    jobs = load_jobs()
    all_skills = set()
    for job in jobs:
        for skill in job['required_skills']:
            all_skills.add(skill)
    
    # Sort skills alphabetically
    skills_list = sorted(list(all_skills))
    
    # Get available job categories
    job_categories = sorted(set(job['category'] for job in jobs))
    
    return render_template('index.html', skills=skills_list, categories=job_categories)

@app.route('/match', methods=['POST'])
def match_jobs():
    # Get user inputs
    selected_skills = request.form.getlist('skills')
    years_experience = int(request.form.get('experience', 0))
    interests = request.form.get('interests', '')
    preferred_categories = request.form.getlist('categories')
    
    # Load jobs
    jobs = load_jobs()
    
    # Initialize matchers if not done yet
    global job_matcher, rule_matcher
    if job_matcher is None:
        job_matcher = JobMatcher(jobs)
    if rule_matcher is None:
        rule_matcher = RuleMatcher()
    
    # Get job matches using cosine similarity
    user_profile = {
        'skills': selected_skills,
        'experience': years_experience,
        'interests': interests,
        'preferred_categories': preferred_categories
    }
    
    # Get similarity matches
    similarity_matches = job_matcher.match(user_profile)
    
    # Apply rule-based filtering
    final_matches = rule_matcher.filter_matches(similarity_matches, user_profile)
    
    # Identify skill gaps
    for match in final_matches:
        match['skill_gaps'] = rule_matcher.identify_skill_gaps(match, user_profile)
    
    return render_template('results.html', matches=final_matches, user_profile=user_profile)

if __name__ == '__main__':
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    # Check if job database exists, if not create a sample one
    if not os.path.exists('data/jobs_database.json'):
        sample_jobs = [
            {
                "id": 1,
                "title": "Software Developer",
                "category": "Technology",
                "description": "Develop and maintain software applications",
                "required_skills": ["Python", "JavaScript", "SQL", "Git"],
                "min_experience": 1,
                "salary_range": "$70,000 - $90,000"
            },
            {
                "id": 2,
                "title": "Data Scientist",
                "category": "Data Science",
                "description": "Analyze and interpret complex data",
                "required_skills": ["Python", "R", "SQL", "Machine Learning", "Statistics"],
                "min_experience": 2,
                "salary_range": "$80,000 - $110,000"
            },
            {
                "id": 3,
                "title": "UX Designer",
                "category": "Design",
                "description": "Create user-friendly interfaces",
                "required_skills": ["UI Design", "User Research", "Wireframing", "Prototyping"],
                "min_experience": 1,
                "salary_range": "$65,000 - $85,000"
            }
        ]
        with open('data/jobs_database.json', 'w') as f:
            json.dump(sample_jobs, f, indent=2)
    
    app.run(debug=True)
