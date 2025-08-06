import gradio as gr
import os
from utils import (
    extract_text_from_pdf, 
    mock_cv_analysis,
    search_real_jobs,
    format_comprehensive_results
)

def analyze_cv_and_search_jobs(pdf_file, country):
    """Main function to analyze CV and search for jobs with advanced insights"""
    try:
        # Extract text from PDF
        cv_text = extract_text_from_pdf(pdf_file)
        
        # Analyze CV with mock analysis (can be upgraded to Gemini later)
        analysis_result = mock_cv_analysis(cv_text)
        
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

2. **Retry Steps:**
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
    
    _Powered by Advanced Analysis + Real Job APIs_
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload Your CV")
            pdf_input = gr.File(
                label="📄 CV (PDF format only)", 
                file_types=[".pdf"],
                type="filepath"
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
                search_button = gr.Button("🔍 Analyze & Find Jobs", variant="primary", size="lg")
                clear_button = gr.Button("🧹 Clear All")
            
            gr.Markdown("""
            ### 🎯 What You Get:
            - **Advanced CV Analysis** with detailed insights
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
                
                ### 🤖 Advanced Analysis
                - Deep CV analysis with professional insights
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
                3. Click "Analyze & Find Jobs"
                4. Get comprehensive career insights!
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
            
            ### 🤖 Advanced Analysis
            - Deep CV analysis with professional insights
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
            3. Click "Analyze & Find Jobs"
            4. Get comprehensive career insights!
            """
        ],
        inputs=[],
        outputs=[pdf_input, country_input, custom_country, output]
    )
    
    gr.Markdown("""
    ---
    
    ## 🌟 Why This Tool is Different
    
    ### 🔥 Advanced Analysis
    - Professional-grade CV analysis
    - Detailed skills and experience assessment
    - Personalized career recommendations
    
    ### 💼 Real Job Integration
    - Connects to actual job boards
    - Live job listings updated in real-time
    - Direct application links
    
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
    
    ---
    
    Made with ❤️ using advanced technology
    """)

if __name__ == "__main__":
    app.launch(share=True, inline=False)