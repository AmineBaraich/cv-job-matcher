import os
import re
import json
import fitz  # PyMuPDF
import google.generativeai as genai
from duckduckgo_search import DDGS
from typing import Dict, List

# --- Configuration ---
# API keys can be set via environment variables or passed directly
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- PDF Processing ---
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")

# --- Mock Analysis (Fallback) ---
def mock_cv_analysis(cv_text: str) -> Dict:
    """Provides a basic mock analysis if no API key is available."""
    # Simple skill extraction
    skills_pattern = r'\b(Python|Java|JavaScript|React|Node\.js|Django|Flask|SQL|MongoDB|AWS|Docker|Kubernetes|Git|Machine Learning|Data Science|Web Development|DevOps|Cloud|AI|UX|UI|Project Management)\b'
    skills = list(set(re.findall(skills_pattern, cv_text, re.IGNORECASE)))

    # Simple title extraction
    title_pattern = r'\b(Developer|Engineer|Analyst|Manager|Specialist|Consultant|Architect|Scientist|Designer|Coordinator|Administrator)\b'
    titles = list(set(re.findall(title_pattern, cv_text, re.IGNORECASE)))

    return {
        "candidate_profile": {
            "name": "Name not found",
            "email": "Email not found",
            "phone": "Phone not found",
            "summary": "Analysis based on provided CV text."
        },
        "skills_analysis": {
            "technical_skills": skills if skills else ["General skills identified"],
            "soft_skills": ["Communication", "Teamwork"],
            "certifications": [],
            "tools_technologies": skills[:5] if skills else ["Common tools"]
        },
        "experience_analysis": {
            "total_years_experience": "Years not quantified",
            "current_level": "Level not determined",
            "career_progression": "Progression identified in text",
            "key_achievements": ["Achievements mentioned in CV"]
        },
        "job_recommendations": [
            {
                "role": title if titles else "Software Professional",
                "match_score": 80,
                "reasoning": "Based on skills found in CV.",
                "required_skills": skills[:3] if skills else ["Core skills"],
                "salary_range": "Not specified",
                "growth_potential": "Medium"
            }
        ],
        "cv_improvement_suggestions": [
            {
                "area": "Quantify Achievements",
                "issue": "Lack of metrics",
                "suggestion": "Add numbers and results to experience.",
                "priority": "High"
            }
        ],
        "market_insights": {
            "industry_trends": "Relevant skills are in demand.",
            "salary_benchmark": "Varies by role and location.",
            "demand_outlook": "Stable"
        }
    }

# --- AI Analysis (Qwen/Gemini) ---
def analyze_cv_with_gemini(cv_text: str) -> Dict:
    """Analyzes CV using the Qwen/Gemini API."""
    if not GEMINI_API_KEY:
        return mock_cv_analysis(cv_text)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        As a professional career advisor, analyze this CV and provide detailed insights.
        CV TEXT:
        {cv_text}

        Please provide your response in this EXACT JSON format:
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

        Be extremely detailed and professional. Return ONLY the valid JSON, nothing else.
        """

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=4000,
                temperature=0.2 # Lower temperature for more consistent JSON
            )
        )
        content = response.text.strip()

        # Attempt to extract JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_content = content[json_start:json_end]
            # Sanitize potential issues in JSON string representation
            json_content = json_content.replace('\n', '').replace('\r', '')
            return json.loads(json_content)
        else:
            print("Could not find valid JSON in Gemini response.")
            return mock_cv_analysis(cv_text)
    except json.JSONDecodeError as je:
        print(f"Gemini API JSON parsing error: {je}")
        # Log problematic content for debugging (be careful with sensitive data)
        # print(f"Problematic content: {content[:500]}...")
        return mock_cv_analysis(cv_text)
    except Exception as e:
        print(f"Gemini API general error: {e}")
        return mock_cv_analysis(cv_text)

# --- Job Search ---
def search_jobs_duckduckgo(query: str, max_results: int = 5) -> List[Dict]:
    """Searches for jobs using DuckDuckGo."""
    jobs = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(f"job {query}", max_results=max_results)
            for r in results:
                 # Basic filtering to try and get job-related results
                if any(keyword in r['title'].lower() or keyword in r['body'].lower() for keyword in ['job', 'hiring', 'position', 'opening', 'career']):
                    jobs.append({
                        "title": r.get('title', 'N/A'),
                        "company": "Company not specified", # DDGS text search doesn't reliably extract company
                        "location": "Location not specified", # DDGS text search doesn't reliably extract location
                        "description": r.get('body', 'N/A')[:200] + '...',
                        "url": r.get('href', '#'),
                        "salary": "Not specified",
                        "posted_date": "N/A",
                        "job_type": "N/A"
                    })
        return jobs
    except Exception as e:
        print(f"Error searching jobs with DuckDuckGo: {e}")
        return []

# --- Results Formatting ---
def format_comprehensive_results(analysis_result: Dict, jobs: List[Dict], country: str) -> str:
    """Formats the analysis and job results into a Markdown string."""
    if not analysis_result:
        return "# Error: Could not analyze CV."

    profile = analysis_result.get("candidate_profile", {})
    skills_analysis = analysis_result.get("skills_analysis", {})
    experience_analysis = analysis_result.get("experience_analysis", {})
    job_recommendations = analysis_result.get("job_recommendations", [])
    cv_suggestions = analysis_result.get("cv_improvement_suggestions", [])
    market_insights = analysis_result.get("market_insights", {})

    profile_section = f"""
## 👤 Candidate Profile
**Name:** {profile.get('name', 'Not found')}  
**Contact:** {profile.get('email', 'Not found')} | {profile.get('phone', 'Not found')}  
**Summary:** {profile.get('summary', 'N/A')}
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

    recommendations_section = "\n---\n## 🎯 Top Job Recommendations\n"
    for i, job in enumerate(job_recommendations[:5], 1):
        recommendations_section += f"""
### {i}. {job.get('role', 'N/A')}
**Match Score:** {job.get('match_score', 0)}% | **Growth Potential:** {job.get('growth_potential', 'N/A')}  
**Salary Range:** {job.get('salary_range', 'N/A')}  
**Why It's a Good Fit:** {job.get('reasoning', 'N/A')}  
**Key Requirements:** {', '.join(job.get('required_skills', [])[:5])}
"""

    cv_section = "\n---\n## 📝 CV Improvement Suggestions\n"
    for suggestion in cv_suggestions[:5]:
        priority_emoji = "🔴" if suggestion.get('priority') == 'High' else "🟡" if suggestion.get('priority') == 'Medium' else "🟢"
        cv_section += f"""
{priority_emoji} **{suggestion.get('area', 'N/A')}**
- **Issue:** {suggestion.get('issue', 'N/A')}
- **Suggestion:** {suggestion.get('suggestion', 'N/A')}
- **Priority:** {suggestion.get('priority', 'N/A')}
"""

    market_section = f"""
---\n## 📈 Market Insights
**Industry Trends:** {market_insights.get('industry_trends', 'N/A')}  
**Salary Benchmark:** {market_insights.get('salary_benchmark', 'N/A')}  
**Demand Outlook:** {market_insights.get('demand_outlook', 'N/A')}
---
## 💼 Job Opportunities Found
**Location Filter:** {country if country else 'Global'} | **Jobs Found:** {len(jobs)}
"""

    jobs_section = ""
    for i, job in enumerate(jobs, 1):
        jobs_section += f"""
### 📋 [{job.get('title', 'N/A')}]({job.get('url', '#')})
🏢 **Company:** {job.get('company', 'N/A')}  
📍 **Location:** {job.get('location', 'N/A')}  
💰 **Salary:** {job.get('salary', 'N/A')}  
⏰ **Posted:** {job.get('posted_date', 'N/A')}  
🔧 **Type:** {job.get('job_type', 'N/A')}  
📝 **Description:** {job.get('description', 'N/A')}
[🔗 Apply Now]({job.get('url', '#')})
---
"""

    footer = "\n*Analysis generated by AI. Verify information independently.*"
    return profile_section + recommendations_section + cv_section + market_section + jobs_section + footer
