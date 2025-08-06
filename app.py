import gradio as gr
import fitz  # PyMuPDF for PDF processing
import requests
import json
import os
from typing import List, Dict, Tuple
import re
from datetime import datetime
import time

# Configuration des API gratuites
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # L'utilisateur devra fournir sa clé
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")  # Clé API pour la recherche web

class CVAnalyzer:
    """Analyse les CV en utilisant Groq (API LLM gratuite)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrait le texte d'un PDF"""
        try:
            pdf_document = fitz.open(pdf_path)
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text += page.get_text()
            pdf_document.close()
            return text
        except Exception as e:
            return f"Erreur lors de la lecture du PDF: {str(e)}"
    
    def analyze_cv(self, cv_text: str) -> Dict:
        """Analyse le CV et extrait les informations clés"""
        prompt = f"""Analyse ce CV et extrais les informations suivantes en format JSON:
        - skills: liste des compétences techniques et soft skills
        - experience_level: junior/mid/senior
        - job_titles: titres de postes pertinents pour cette personne
        - industries: secteurs d'activité pertinents
        - languages: langues parlées
        - education_level: niveau d'études
        
        CV:
        {cv_text[:3000]}  # Limite pour éviter de dépasser les tokens
        
        Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "Tu es un expert en analyse de CV. Réponds toujours en JSON valide."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Nettoyer et parser le JSON
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            return json.loads(content)
        except Exception as e:
            return {
                "error": f"Erreur d'analyse: {str(e)}",
                "skills": [],
                "job_titles": ["Professionnel"],
                "experience_level": "mid",
                "industries": [],
                "languages": [],
                "education_level": "bachelor"
            }

class JobSearcher:
    """Recherche d'emplois en utilisant Serper API (gratuit jusqu'à 2500 requêtes/mois)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        
    def search_jobs(self, query: str, country: str, num_results: int = 10) -> List[Dict]:
        """Recherche des offres d'emploi"""
        # Utilisation de l'API Serper pour la recherche
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Adapter la requête selon le pays
        country_domains = {
            "France": "site:indeed.fr OR site:linkedin.com/jobs OR site:welcometothejungle.com",
            "USA": "site:indeed.com OR site:linkedin.com/jobs OR site:glassdoor.com",
            "UK": "site:indeed.co.uk OR site:linkedin.com/jobs OR site:reed.co.uk",
            "Canada": "site:indeed.ca OR site:linkedin.com/jobs OR site:workopolis.com",
            "Germany": "site:indeed.de OR site:linkedin.com/jobs OR site:stepstone.de",
            "Spain": "site:indeed.es OR site:linkedin.com/jobs OR site:infojobs.net"
        }
        
        search_query = f"{query} job offer {country_domains.get(country, 'site:linkedin.com/jobs')}"
        
        data = {
            "q": search_query,
            "gl": country.lower()[:2],
            "num": num_results
        }
        
        try:
            response = requests.post(
                "https://serpapi.com/search.json",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            results = response.json()
            
            jobs = []
            for result in results.get('organic', []):
                job = {
                    "title": result.get('title', ''),
                    "company": result.get('source', ''),
                    "link": result.get('link', ''),
                    "snippet": result.get('snippet', ''),
                    "date": result.get('date', '')
                }
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            # Si Serper échoue, utiliser une approche alternative avec DuckDuckGo
            return self.search_jobs_duckduckgo(query, country, num_results)
    
    def search_jobs_duckduckgo(self, query: str, country: str, num_results: int = 10) -> List[Dict]:
        """Recherche alternative avec DuckDuckGo (sans API key)"""
        try:
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            
            # Adapter la requête pour cibler les offres d'emploi
            search_query = f"{query} job offer vacancy hiring {country}"
            
            results = ddgs.text(
                search_query,
                region=country.lower()[:2] + "-" + country.lower()[:2],
                max_results=num_results
            )
            
            jobs = []
            for r in results:
                job = {
                    "title": r.get('title', ''),
                    "company": r.get('source', 'N/A'),
                    "link": r.get('link', ''),
                    "snippet": r.get('body', ''),
                    "date": "Recent"
                }
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            return [{
                "title": "Erreur de recherche",
                "company": "N/A",
                "link": "#",
                "snippet": f"Erreur: {str(e)}. Veuillez vérifier votre connexion internet.",
                "date": "N/A"
            }]

class CVJobMatcher:
    """Classe principale pour l'application"""
    
    def __init__(self):
        self.cv_analyzer = None
        self.job_searcher = None
        
    def setup_apis(self, groq_key: str, serper_key: str):
        """Configure les APIs avec les clés fournies"""
        self.cv_analyzer = CVAnalyzer(groq_key)
        self.job_searcher = JobSearcher(serper_key)
        
    def generate_search_queries(self, cv_analysis: Dict) -> List[str]:
        """Génère des requêtes de recherche optimisées basées sur l'analyse du CV"""
        queries = []
        
        # Requêtes basées sur les titres de postes
        for title in cv_analysis.get('job_titles', [])[:3]:
            queries.append(f'"{title}"')
        
        # Requêtes combinant compétences et niveau d'expérience
        skills = cv_analysis.get('skills', [])[:5]
        exp_level = cv_analysis.get('experience_level', 'mid')
        
        if skills:
            skill_query = f"{exp_level} {' '.join(skills[:3])}"
            queries.append(skill_query)
        
        # Requête par industrie
        for industry in cv_analysis.get('industries', [])[:2]:
            queries.append(f"{industry} jobs")
        
        return queries[:5]  # Limiter à 5 requêtes
    
    def process_cv_and_search(self, pdf_file, country: str, groq_key: str, serper_key: str) -> Tuple[str, str]:
        """Traite le CV et recherche des emplois"""
        try:
            # Vérifier les clés API
            if not groq_key:
                return "❌ Erreur: Clé API Groq manquante", ""
            
            # Configurer les APIs
            self.setup_apis(groq_key, serper_key)
            
            # Extraire le texte du CV
            cv_text = self.cv_analyzer.extract_text_from_pdf(pdf_file.name)
            if "Erreur" in cv_text:
                return cv_text, ""
            
            # Analyser le CV
            analysis_result = self.cv_analyzer.analyze_cv(cv_text)
            
            if "error" in analysis_result:
                return f"❌ {analysis_result['error']}", ""
            
            # Générer l'analyse formatée
            analysis_output = f"""📊 **Analyse du CV**

**Niveau d'expérience:** {analysis_result.get('experience_level', 'N/A')}
**Niveau d'études:** {analysis_result.get('education_level', 'N/A')}

**Compétences identifiées:**
{chr(10).join(['• ' + skill for skill in analysis_result.get('skills', [])])}

**Titres de postes suggérés:**
{chr(10).join(['• ' + title for title in analysis_result.get('job_titles', [])])}

**Secteurs d'activité:**
{chr(10).join(['• ' + industry for industry in analysis_result.get('industries', [])])}

**Langues:**
{chr(10).join(['• ' + lang for lang in analysis_result.get('languages', [])])}
"""
            
            # Générer les requêtes de recherche
            search_queries = self.generate_search_queries(analysis_result)
            
            # Rechercher des emplois
            all_jobs = []
            for query in search_queries:
                jobs = self.job_searcher.search_jobs(query, country, num_results=5)
                all_jobs.extend(jobs)
                time.sleep(0.5)  # Éviter le rate limiting
            
            # Dédupliquer par URL
            unique_jobs = {job['link']: job for job in all_jobs}.values()
            
            # Formater les résultats
            jobs_output = f"""🔍 **Offres d'emploi trouvées ({len(unique_jobs)} résultats)**

**Pays de recherche:** {country}
**Requêtes utilisées:** {', '.join(search_queries)}

---

"""
            
            for i, job in enumerate(list(unique_jobs)[:20], 1):
                jobs_output += f"""**{i}. {job['title']}**
🏢 {job['company']}
📅 {job['date']}
📝 {job['snippet'][:200]}...
🔗 [Voir l'offre]({job['link']})

---

"""
            
            return analysis_output, jobs_output
            
        except Exception as e:
            return f"❌ Erreur inattendue: {str(e)}", ""

# Créer l'application Gradio
def create_app():
    matcher = CVJobMatcher()
    
    with gr.Blocks(title="CV Job Matcher - Analyseur de CV et Recherche d'Emploi") as app:
        gr.Markdown("""
        # 🎯 CV Job Matcher
        
        Cette application analyse votre CV et trouve des offres d'emploi correspondantes.
        
        ## 🔧 Configuration requise:
        1. **Clé API Groq** (gratuite): [Obtenir une clé](https://console.groq.com/keys)
        2. **Clé API Serper** (optionnelle): [Obtenir une clé](https://serper.dev/) - 2500 recherches gratuites/mois
        
        Sans clé Serper, l'app utilisera DuckDuckGo (moins précis mais gratuit).
        """)
        
        with gr.Row():
            with gr.Column():
                groq_key = gr.Textbox(
                    label="Clé API Groq (obligatoire)",
                    placeholder="gsk_...",
                    type="password"
                )
                serper_key = gr.Textbox(
                    label="Clé API Serper (optionnelle)",
                    placeholder="Laissez vide pour utiliser DuckDuckGo",
                    type="password"
                )
        
        with gr.Row():
            with gr.Column():
                cv_file = gr.File(
                    label="📄 Téléchargez votre CV (PDF)",
                    file_types=[".pdf"]
                )
                country = gr.Dropdown(
                    label="🌍 Pays de recherche",
                    choices=["France", "USA", "UK", "Canada", "Germany", "Spain"],
                    value="France"
                )
                search_btn = gr.Button("🚀 Analyser et Rechercher", variant="primary")
        
        with gr.Row():
            with gr.Column():
                analysis_output = gr.Markdown(label="Analyse du CV")
            with gr.Column():
                jobs_output = gr.Markdown(label="Offres d'emploi")
        
        search_btn.click(
            fn=matcher.process_cv_and_search,
            inputs=[cv_file, country, groq_key, serper_key],
            outputs=[analysis_output, jobs_output]
        )
        
        gr.Markdown("""
        ---
        
        ## 📝 Notes:
        - L'analyse est limitée aux 3000 premiers caractères du CV pour économiser les tokens
        - Les résultats de recherche dépendent de la qualité des APIs utilisées
        - Pour de meilleurs résultats, utilisez un CV bien structuré en PDF
        
        ## 🔒 Confidentialité:
        - Vos données ne sont pas stockées
        - Les clés API restent dans votre navigateur
        - Le CV est traité uniquement pendant la session
        """)
    
    return app

# Point d'entrée principal
if __name__ == "__main__":
    app = create_app()
    app.launch(share=True, server_name="0.0.0.0")