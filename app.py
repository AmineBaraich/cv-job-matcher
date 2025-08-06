import gradio as gr
import os
from utils import (
    extract_text_from_pdf, 
    analyze_cv_with_gemini,
    search_real_jobs,
    format_comprehensive_results
)

def analyze_cv_and_search_jobs(pdf_file, country):
    """Main function to analyze CV and search for jobs with advanced insights"""
    try:
        # Extract text from PDF
        cv_text = extract_text_from_pdf(pdf_file.name)
        
        # Analyze CV with Gemini (completely free API)
        analysis_result = analyze_cv_with_gemini(cv_text)
        
        # Generate search query from analysis
        skills = analysis_result.get("skills_analysis", {}).get("technical_skills", [])
        titles = analysis_result.get("job_recommendations", [])
        
        search_terms = []
        if skills:
            search_terms.extend(skills[:5])
        if titles:
            search_terms.extend([t.get('role', '') for t in titles[:3]])
        
        search_query = " ".join(search_terms) if search_terms else "software developer"
        
        # Search for real jobs
        jobs = search_real_jobs(search_query, country)
        
        # Format comprehensive results
        formatted_results = format_comprehensive_results(analysis_result, jobs, country)
        
        return formatted_results
        
    except Exception as e:
        return f"""
# ❌ Error Processing Request

**Error Message:** {str(e)}

## 🛠 Troubleshooting Tips:

1. **File Issues:**
   - Ensure your CV is in PDF format
   - Check that the file is not corrupted
   - Try a different CV file
   - Keep file size under 10MB

2. **API Issues:**
   - Gemini API is completely free - get your key at: https://ai.google.dev/
   - Set your API key in the environment variables
   - Check internet connectivity

3. **Retry Steps:**
   - Refresh the page
   - Clear browser cache
   - Try a different browser
   - Wait a few minutes and try again

## 📞 Support

If problems persist, please:
- Check the browser console for detailed errors
- Ensure you're using the latest version of this tool
- Contact support with the error details above

*This tool works completely free with no hidden costs!*
"""

# Create Gradio interface
with gr.Blocks(title="Advanced CV Job Matcher - AI Powered") as app:
    gr.Markdown("""
    # 🚀 Advanced CV Job Matcher (AI Powered)
    
    ## The Most Advanced Free Job Matching Tool
    
    Upload your CV and get **AI-powered insights**, **real job opportunities**, and **personalized career advice**!
    
    _Powered by Gemini AI (completely free) + Real Job APIs_
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload Your CV")
            pdf_input = gr.File(
                label="📄 CV (PDF format only)", 
                file_types=[".pdf"],
                type="file"
            )
            
            gr.Markdown("### 🌍 Location Preferences")
            country_input = gr.Dropdown(
                choices=["", "Remote", "USA", "UK", "Canada", "Germany", "France", "Australia", "India", "Brazil", "Other"],
                value="",
                label="Preferred Location (Optional)"
            )
            
            custom_country = gr.Textbox(
                label="Custom Location (if Other selected)",
                placeholder="e.g., Netherlands, Singapore, etc."
            )
            
            with gr.Row():
                search_button = gr.Button("🔍 AI Analyze & Find Jobs", variant="primary", size="lg")
                clear_button = gr.Button("🧹 Clear All")
            
            gr.Markdown("""
            ### 🎯 What You Get:
            - **AI-Powered CV Analysis** with detailed insights
            - **Real Job Opportunities** from actual job boards
            - **Personalized Career Advice** tailored to your profile
            - **CV Improvement Suggestions** to boost your chances
            - **Market Trends** and salary benchmarks
            """)
        
        with gr.Column(scale=2):
            output = gr.Markdown(
                label="📊 Comprehensive Results",
                value="""
                # 🚀 Ready for Advanced Job Matching?
                
                ## What This Tool Provides:
                
                ### 🤖 AI-Powered Analysis
                - Deep CV analysis with Gemini AI
                - Skills assessment and gap identification
                - Experience evaluation and career progression insights
                
                ### 💼 Real Job Opportunities
                - Live job listings from actual job boards
                - Direct links to apply
                - Salary information and job details
                
                ### 📝 Personalized Recommendations
                - Tailored career advice
                - CV improvement suggestions
                - Market trends and opportunities
                
                ### 🎯 How to Get Started:
                1. Upload your CV (PDF format)
                2. Select your preferred location (optional)
                3. Click "AI Analyze & Find Jobs"
                4. Get comprehensive career insights!
                
                ---
                
                **Note:** This tool uses completely free APIs. For the best experience, get a free Gemini API key from [Google AI Studio](https://ai.google.dev/).
                """
            )
    
    def process_location(country, custom_country):
        if country == "Other" and custom_country:
            return custom_country
        return country if country else ""
    
    search_button.click(
        fn=lambda pdf, country, custom: analyze_cv_and_search_jobs(pdf, process_location(country, custom)),
        inputs=[pdf_input, country_input, custom_country],
        outputs=output
    )
    
    clear_button.click(
        fn=lambda: [
            None, 
            "", 
            "",
            """
            # 🚀 Ready for Advanced Job Matching?
            
            ## What This Tool Provides:
            
            ### 🤖 AI-Powered Analysis
            - Deep CV analysis with Gemini AI
            - Skills assessment and gap identification
            - Experience evaluation and career progression insights
            
            ### 💼 Real Job Opportunities
            - Live job listings from actual job boards
            - Direct links to apply
            - Salary information and job details
            
            ### 📝 Personalized Recommendations
            - Tailored career advice
            - CV improvement suggestions
            - Market trends and opportunities
            
            ### 🎯 How to Get Started:
            1. Upload your CV (PDF format)
            2. Select your preferred location (optional)
            3. Click "AI Analyze & Find Jobs"
            4. Get comprehensive career insights!
            
            ---
            
            **Note:** This tool uses completely free APIs. For the best experience, get a free Gemini API key from [Google AI Studio](https://ai.google.dev/).
            """
        ],
        inputs=[],
        outputs=[pdf_input, country_input, custom_country, output]
    )
    
    gr.Markdown("""
    ---
    
    ## 🌟 Why This Tool is Different
    
    ### 🔥 Advanced AI Analysis
    - **Gemini AI** (completely free with generous limits)
    - Professional-grade CV analysis
    - Detailed skills and experience assessment
    - Personalized career recommendations
    
    ### 💼 Real Job Integration
    - Connects to actual job boards
    - Live job listings updated in real-time
    - Direct application links
    - Location-based filtering
    
    ### 📊 Comprehensive Insights
    - Market trends and salary benchmarks
    - CV improvement suggestions with priorities
    - Career progression analysis
    - Personalized advice and strategies
    
    ### 🆓 100% Free & Privacy-Focused
    - **No subscription fees**
    - **No hidden costs**
    - **No data storage**
    - **Privacy-first design**
    
    ## 🚀 Get Your Free Gemini API Key
    
    1. Go to [Google AI Studio](https://ai.google.dev/)
    2. Sign in with your Google account
    3. Get your free API key (no credit card required)
    4. Set it as `GEMINI_API_KEY` in your environment
    
    **Free Tier Includes:**
    - 60 requests per minute
    - 2 million tokens per day
    - Access to Gemini Pro model
    - No expiration
    
    ---
    
    Made with ❤️ using cutting-edge AI technology
    """)
    
    # Add custom CSS for better styling
    app.style = """
        .gradio-container {
            max-width: 1200px !important;
        }
        h1 {
            color: #1f2937;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 10px;
        }
        .markdown {
            line-height: 1.6;
        }
        button.primary {
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
            border: none;
            color: white;
            font-weight: bold;
        }
    """

# For Colab deployment
def create_colab_app():
    """Create app specifically for Colab deployment"""
    return app

if __name__ == "__main__":
    # Check if running in Colab
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
    
    if IN_COLAB:
        # In Colab, provide instructions for API key
        import os
        if not os.getenv('GEMINI_API_KEY'):
            print("⚠️  No Gemini API key found.")
            print("To use advanced AI analysis:")
            print("1. Get your FREE API key from: https://ai.google.dev/")
            print("2. In Colab, go to Runtime > Run All")
            print("3. When prompted, enter your API key")
            print("\nUsing mock analysis for now...")
        
        app.launch(share=True, inline=False)
    else:
        app.launch(share=True, inline=False)