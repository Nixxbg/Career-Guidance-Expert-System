class RuleMatcher:
    def __init__(self):
        # Configure any constants needed for rule-based matching
        self.min_similarity_threshold = 0.1  # Minimum similarity score to consider
    
    def filter_matches(self, similarity_matches, user_profile):
        filtered_matches = []
        
        for job in similarity_matches:
            # Skip jobs with similarity below threshold
            if job['similarity_score'] < self.min_similarity_threshold:
                continue
            
            # Check experience level requirement
            user_experience = user_profile['experience']
            if user_experience < job['min_experience']:
                # Mark as requiring more experience but still include
                job['experience_gap'] = job['min_experience'] - user_experience
            else:
                job['experience_gap'] = 0
            
            # Add match score percentage for display
            job['match_percentage'] = round(job['similarity_score'] * 100, 1)
            
            filtered_matches.append(job)
        
        return filtered_matches
    
    def identify_skill_gaps(self, job, user_profile):
        """Identify skills that the user is missing for this job"""
        user_skills = set(user_profile['skills'])
        required_skills = set(job['required_skills'])
        
        # Find missing skills
        missing_skills = required_skills - user_skills
        
        return list(missing_skills)
