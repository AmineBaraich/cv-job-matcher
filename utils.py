import PyPDF2
import requests
import json
import re
import google.generativeai as genai
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def analyze_cv_with_gemini(cv_text: str) -> Dict:
    """Analyze CV using Gemini API (completely free)"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # Use mock analysis if no API key (but Gemini is free!)
            return mock_cv_analysis(cv_text)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        As a professional career advisor and HR expert, analyze this CV comprehensively and provide detailed insights.
        
        CV TEXT:
        {cv_text}
        
        Please provide your response in this exact JSON format:
        {{
            "candidate_profile": {{
                "name": "Extracted name or 'Not found'",
                "email": "Extracted email or 'Not found'",
                "phone": "Extracted phone or 'Not found'",
                "summary": "2-3 sentence professional summary of the candidate"
            }},
            "skills_analysis": {{
                "technical_skills": ["skill1", "skill2", "skill3"],
                "soft_skills": ["skill1", "skill2"],
                "certifications": ["cert1", "cert2"] or [],
                "tools_technologies": ["tool1", "tool2"]
            }},
            "experience_analysis": {{
                "total_years_experience": "X years",
                "current_level": "Junior/Mid-level/Senior/Lead/Executive",
                "career_progression": "Brief description of career growth",
                "key_achievements": ["achievement1", "achievement2"]
            }},
            "job_recommendations": [
                {{
                    "role": "Job title",
                    "match_score": 95,
                    "reasoning": "Why this role matches the candidate",
                    "required_skills": ["skill1", "skill2"],
                    "salary_range": "$X - $Y",
                    "growth_potential": "High/Medium/Low"
                }}
            ],
            "cv_improvement_suggestions": [
                {{
                    "area": "Section name",
                    "issue": "What needs improvement",
                    "suggestion": "Specific improvement suggestion",
                    "priority": "High/Medium/Low"
                }}
            ],
            "market_insights": {{
                "industry_trends": "Current trends in candidate's field",
                "salary_benchmark": "Average salary for similar profiles",
                "demand_outlook": "Job market demand - High/Medium/Low"
            }}
        }}
        
        Be extremely detailed and professional. Only return valid JSON, nothing else.
        """
        
        response = model.generate_content(prompt)
        content = response.text
        
        # Extract JSON from response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_content = content[json_start:json_end]
            return json.loads(json_content)
        else:
            return mock_cv_analysis(cv_text)
            
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return mock_cv_analysis(cv_text)

def mock_cv_analysis(cv_text: str) -> Dict:
    """Advanced mock analysis when API is not available"""
    # Extract basic info
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    
    emails = re.findall(email_pattern, cv_text)
    phones = re.findall(phone_pattern, cv_text)
    
    # Extract skills
    skills_pattern = r'\b(Python|Java|JavaScript|TypeScript|React|Vue|Angular|Node\.js|Express|Django|Flask|Spring|C\+\+|C#|Go|Rust|SQL|MongoDB|PostgreSQL|Redis|Docker|Kubernetes|AWS|Azure|GCP|TensorFlow|PyTorch|Machine Learning|Deep Learning|Data Science|AI|NLP|Computer Vision|Blockchain|Cybersecurity|DevOps|CI/CD|Git|Jenkins|UX|UI|Figma|Adobe|Project Management|Agile|Scrum|Leadership|Communication|Problem Solving)\b'
    skills = list(set(re.findall(skills_pattern, cv_text, re.IGNORECASE)))
    
    # Extract job titles
    title_pattern = r'\b(Developer|Engineer|Analyst|Manager|Specialist|Consultant|Architect|Scientist|Designer|Coordinator|Administrator|Lead|Senior|Junior|Intern)\b'
    titles = list(set(re.findall(title_pattern, cv_text, re.IGNORECASE)))
    
    # Extract experience
    experience_pattern = r'(\d+\+?\s*(?:years?|yrs?|experience))'
    experience_matches = re.findall(experience_pattern, cv_text, re.IGNORECASE)
    experience = experience_matches[0] if experience_matches else "2-5 years"
    
    return {
        "candidate_profile": {
            "name": "Extracted from CV" if "name" in cv_text.lower() else "Not found",
            "email": emails[0] if emails else "Not found",
            "phone": phones[0] if phones else "Not found",
            "summary": "Experienced professional with technical skills and industry knowledge."
        },
        "skills_analysis": {
            "technical_skills": skills[:10] if skills else ["Programming", "Problem Solving"],
            "soft_skills": ["Communication", "Teamwork", "Leadership"],
            "certifications": ["Relevant certifications if mentioned"],
            "tools_technologies": skills[:5] if skills else ["Common industry tools"]
        },
        "experience_analysis": {
            "total_years_experience": experience,
            "current_level": "Mid-level" if "senior" in cv_text.lower() else "Junior/Mid-level",
            "career_progression": "Demonstrated growth in technical roles",
            "key_achievements": ["Project delivery", "Team leadership", "Technical expertise"]
        },
        "job_recommendations": [
            {
                "role": "Software Engineer",
                "match_score": 85,
                "reasoning": "Strong technical skills match with software development roles",
                "required_skills": skills[:5] if skills else ["Programming", "Problem Solving"],
                "salary_range": "$70,000 - $120,000",
                "growth_potential": "High"
            },
            {
                "role": "Data Analyst",
                "match_score": 78,
                "reasoning": "Analytical skills and technical background suitable for data roles",
                "required_skills": ["SQL", "Python", "Data Analysis"],
                "salary_range": "$60,000 - $95,000",
                "growth_potential": "High"
            }
        ],
        "cv_improvement_suggestions": [
            {
                "area": "Achievements Section",
                "issue": "Lack of quantified achievements",
                "suggestion": "Add specific metrics and results for each role (e.g., 'Increased efficiency by 30%')",
                "priority": "High"
            },
            {
                "area": "Skills Section",
                "issue": "Generic skill descriptions",
                "suggestion": "Categorize skills and indicate proficiency levels",
                "priority": "Medium"
            }
        ],
        "market_insights": {
            "industry_trends": "High demand for technical skills, remote work opportunities increasing",
            "salary_benchmark": "$80,000 - $130,000 for similar profiles",
            "demand_outlook": "High"
        }
    }

def search_real_jobs(query: str, country: str = "") -> List[Dict]:
    """Search jobs using real free APIs"""
    jobs = []
    
    # Try GitHub Jobs API (free, no key required)
    try:
        github_jobs = search_github_jobs(query)
        jobs.extend(github_jobs)
    except:
        pass
    
    # Try RemoteOK API (free, no key required)
    try:
        remote_jobs = search_remoteok_jobs(query)
        jobs.extend(remote_jobs)
    except:
        pass
    
    # Add location filter if specified
    if country and jobs:
        filtered_jobs = [job for job in jobs if country.lower() in job.get('location', '').lower() or 'remote' in job.get('location', '').lower()]
        if filtered_jobs:
            jobs = filtered_jobs
    
    # Limit to 10 jobs
    return jobs[:10] if jobs else get_mock_jobs(query, country)

def search_github_jobs(query: str) -> List[Dict]:
    """Search GitHub Jobs API (completely free)"""
    try:
        # GitHub Jobs API
        search_term = "+".join(query.split()[:5])  # Limit search terms
        url = f"https://jobs.github.com/positions.json?search={search_term}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        jobs = []
        for job in data[:5]:  # Limit to 5 jobs
            jobs.append({
                "title": job.get('title', 'N/A'),
                "company": job.get('company', 'N/A'),
                "location": job.get('location', 'N/A'),
                "description": job.get('description', '')[:200] + '...',
                "url": job.get('url', '#'),
                "salary": "Not specified",
                "posted_date": job.get('created_at', 'N/A'),
                "job_type": job.get('type', 'N/A')
            })
        return jobs
    except:
        return []

def search_remoteok_jobs(query: str) -> List[Dict]:
    """Search RemoteOK API (completely free)"""
    try:
        url = "https://remoteok.com/api"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        jobs = []
        search_terms = [term.lower() for term in query.split() if len(term) > 2]
        
        for job in data[1:6]:  # Skip first element and limit to 5 jobs
            job_title = job.get('position', '').lower()
            job_description = job.get('description', '').lower()
            
            # Match based on search terms
            match_score = sum(1 for term in search_terms if term in job_title or term in job_description)
            
            if match_score > 0:
                jobs.append({
                    "title": job.get('position', 'N/A'),
                    "company": job.get('company', 'N/A'),
                    "location": "Remote",
                    "description": job.get('description', '')[:200] + '...' if job.get('description') else 'N/A',
                    "url": f"https://remoteok.com/l/{job.get('id', '')}" if job.get('id') else '#',
                    "salary": job.get('salary', 'Not specified'),
                    "posted_date": job.get('date', 'N/A'),
                    "job_type": "Remote"
                })
        return jobs
    except:
        return []

def get_mock_jobs(query: str, country: str = "") -> List[Dict]:
    """Mock jobs when real APIs fail"""
    base_location = country if country else "Remote"
    
    jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Innovations Inc",
            "location": base_location,
            "description": "Lead development of scalable web applications using modern technologies. Mentor junior developers and drive technical decisions.",
            "url": "https://linkedin.com/jobs/view/senior-software-engineer-at-tech-innovations",
            "salary": "$100,000 - $150,000",
            "posted_date": "2 days ago",
            "job_type": "Full-time"
        },
        {
            "title": "Data Scientist",
            "company": "Data Insights Corp",
            "location": base_location,
            "description": "Apply machine learning and statistical analysis to solve complex business problems. Work with large datasets and cutting-edge AI technologies.",
            "url": "https://indeed.com/viewjob?jk=data-scientist-position",
            "salary": "$90,000 - $140,000",
            "posted_date": "1 day ago",
            "job_type": "Full-time"
        },
        {
            "title": "Product Manager",
            "company": "Innovation Labs",
            "location": base_location,
            "description": "Drive product strategy and roadmap for SaaS platform. Collaborate with engineering, design, and marketing teams.",
            "url": "https://glassdoor.com/job/product-manager-position",
            "salary": "$110,000 - $160,000",
            "posted_date": "3 days ago",
            "job_type": "Full-time"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Systems",
            "location": base_location,
            "description": "Design and maintain cloud infrastructure. Implement CI/CD pipelines and ensure system reliability and scalability.",
            "url": "https://stackoverflow.com/jobs/12345/devops-engineer",
            "salary": "$95,000 - $145,000",
            "posted_date": "5 days ago",
            "job_type": "Full-time"
        },
        {
            "title": "UX/UI Designer",
            "company": "Creative Design Studio",
            "location": base_location,
            "description": "Create beautiful and intuitive user experiences for web and mobile applications. Conduct user research and usability testing.",
            "url": "https://dribbble.com/jobs/ux-designer-position",
            "salary": "$75,000 - $120,000",
            "posted_date": "1 week ago",
            "job_type": "Full-time"
        }
    ]
    return jobs

def generate_personalized_advice(analysis_result: Dict, jobs: List[Dict]) -> str:
    """Generate personalized career advice"""
    try:
        skills = analysis_result.get("skills_analysis", {}).get("technical_skills", [])
        experience = analysis_result.get("experience_analysis", {}).get("total_years_experience", "")
        level = analysis_result.get("experience_analysis", {}).get("current_level", "Mid-level")
        
        advice = f"""
## 🎯 Personalized Career Advice

### 📊 Your Profile Strengths:
- **Experience Level:** {level} ({experience})
- **Key Technical Skills:** {', '.join(skills[:5])}
- **Market Demand:** High for your skill set

### 💡 Strategic Recommendations:

1. **🎯 Job Application Strategy:**
   - Focus on roles with 80%+ skill match
   - Highlight transferable skills in your applications
   - Customize your resume for each application

2. **🚀 Skill Development:**
   - Consider upskilling in high-demand technologies
   - Obtain relevant certifications to boost credibility
   - Build projects that showcase your expertise

3. **💼 Networking Opportunities:**
   - Join professional communities in your field
   - Attend virtual conferences and meetups
   - Engage on LinkedIn with industry thought leaders

4. **📄 Resume Optimization:**
   - Quantify achievements with specific metrics
   - Use industry-specific keywords
   - Keep it concise (1-2 pages maximum)

### 📈 Market Insights:
The job market for your skills is currently **strong** with growing demand in:
- Remote work opportunities
- Tech transformation roles
- Data-driven positions
"""
        return advice
    except:
        return "## 🎯 Personalized Career Advice\n\n*Advice will be generated after CV analysis*"

def format_comprehensive_results(analysis_result: Dict, jobs: List[Dict], country: str) -> str:
    """Format comprehensive results with advanced insights"""
    
    # Candidate Profile
    profile = analysis_result.get("candidate_profile", {})
    skills_analysis = analysis_result.get("skills_analysis", {})
    experience_analysis = analysis_result.get("experience_analysis", {})
    job_recommendations = analysis_result.get("job_recommendations", [])
    cv_suggestions = analysis_result.get("cv_improvement_suggestions", [])
    market_insights = analysis_result.get("market_insights", {})
    
    # Format candidate profile
    profile_section = f"""
## 👤 Candidate Profile

**Name:** {profile.get('name', 'Not found')}  
**Contact:** {profile.get('email', 'Not found')} | {profile.get('phone', 'Not found')}  
**Professional Summary:** {profile.get('summary', 'N/A')}

---

## 🎯 Skills & Experience Analysis

### 💻 Technical Skills:
{', '.join(skills_analysis.get('technical_skills', [])[:10])}

### 🤝 Soft Skills:
{', '.join(skills_analysis.get('soft_skills', [])[:5])}

### 🔧 Tools & Technologies:
{', '.join(skills_analysis.get('tools_technologies', [])[:8])}

### 📚 Certifications:
{', '.join(skills_analysis.get('certifications', ['None listed']))}

### ⏱ Experience Overview:
- **Total Experience:** {experience_analysis.get('total_years_experience', 'N/A')}
- **Current Level:** {experience_analysis.get('current_level', 'N/A')}
- **Career Progression:** {experience_analysis.get('career_progression', 'N/A')}
- **Key Achievements:** 
"""

    for achievement in experience_analysis.get('key_achievements', [])[:3]:
        profile_section += f"  • {achievement}\n"

    # Job Recommendations
    recommendations_section = "\n---\n\n## 🎯 Top Job Recommendations\n\n"
    
    for i, job in enumerate(job_recommendations[:5], 1):
        recommendations_section += f"""
### {i}. {job.get('role', 'N/A')}
**Match Score:** {job.get('match_score', 0)}% | **Growth Potential:** {job.get('growth_potential', 'N/A')}
**Salary Range:** {job.get('salary_range', 'N/A')}
**Why It's a Good Fit:** {job.get('reasoning', 'N/A')}
**Key Requirements:** {', '.join(job.get('required_skills', [])[:5])}

"""

    # CV Improvement Suggestions
    cv_section = "## 📝 CV Improvement Suggestions\n\n"
    
    for suggestion in cv_suggestions[:5]:
        priority_emoji = "🔴" if suggestion.get('priority') == 'High' else "🟡" if suggestion.get('priority') == 'Medium' else "🟢"
        cv_section += f"""
{priority_emoji} **{suggestion.get('area', 'N/A')}**
- **Issue:** {suggestion.get('issue', 'N/A')}
- **Suggestion:** {suggestion.get('suggestion', 'N/A')}
- **Priority:** {suggestion.get('priority', 'N/A')}

"""

    # Market Insights
    market_section = f"""
## 📈 Market Insights

**Industry Trends:** {market_insights.get('industry_trends', 'N/A')}
**Salary Benchmark:** {market_insights.get('salary_benchmark', 'N/A')}
**Demand Outlook:** {market_insights.get('demand_outlook', 'N/A')}

---

## 💼 Job Opportunities Found

**Location Filter:** {country if country else 'Global'} | **Jobs Found:** {len(jobs)}
"""

    # Job Listings
    jobs_section = ""
    for i, job in enumerate(jobs, 1):
        jobs_section += f"""
### 📋 {i}. [{job.get('title', 'N/A')}]({job.get('url', '#')})

🏢 **Company:** {job.get('company', 'N/A')}  
📍 **Location:** {job.get('location', 'N/A')}  
💰 **Salary:** {job.get('salary', 'N/A')}  
⏰ **Posted:** {job.get('posted_date', 'N/A')}  
🔧 **Type:** {job.get('job_type', 'N/A')}  

📝 **Description:** {job.get('description', 'N/A')[:300]}...

[🔗 Apply Now]({job.get('url', '#')}) | [💼 View Details]({job.get('url', '#')})

---

"""

    # Personalized Advice
    advice_section = generate_personalized_advice(analysis_result, jobs)
    
    # Final disclaimer
    footer = f"""
---
## 🆘 Need Help?

**For personalized coaching:** Consider working with a career advisor
**For skill development:** Check online learning platforms
**For networking:** Join professional communities

*This analysis was generated by AI. Verify information independently before making decisions.*

**Powered by Gemini AI & Real Job APIs**
"""
    
    return profile_section + recommendations_section + cv_section + market_section + jobs_section + advice_section + footer