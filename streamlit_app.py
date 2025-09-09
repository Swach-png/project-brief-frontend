import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
from typing import Dict, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="AI Project Brief Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .report-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .role-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .role-card:hover {
        transform: translateY(-5px);
    }
    .role-card h3 {
        color: white;
        margin-bottom: 1rem;
    }
    .role-card ul {
        text-align: left;
        margin: 1rem 0;
    }
    .role-card li {
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Import configuration
try:
    from config import API_BASE_URL, SUPPORTED_FORMATS, DEBUG, API_TIMEOUT
    print(f"✅ Configuration loaded from config.py")
except ImportError:
    # Try to load from Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            API_BASE_URL = st.secrets.get("backend", {}).get("url", "http://localhost:8000")
            print(f"✅ Configuration loaded from Streamlit secrets")
        else:
            API_BASE_URL = "http://localhost:8000"
            print(f"⚠️ No Streamlit secrets found, using default localhost")
    except:
        API_BASE_URL = "http://localhost:8000"
        print(f"⚠️ Fallback to default localhost")
    
    # Fallback configuration if config.py is not available
    SUPPORTED_FORMATS = ["pdf", "docx", "txt"]
    DEBUG = False
    API_TIMEOUT = 30

def main():
    """Main application function"""
    
    # Initialize session state for role selection
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    
    # Role selection page
    if st.session_state.user_role is None:
        show_role_selection_page()
    else:
        # Role-specific pages
        if st.session_state.user_role == "brand_manager":
            show_brand_manager_page()
        elif st.session_state.user_role == "content_writer":
            show_content_writer_page()

def show_role_selection_page():
    """Show the main role selection page"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Project Brief Analyzer</h1>
        <p>Choose your role to get started with AI-powered project analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection
    st.markdown("## 👥 Select Your Role")
    st.markdown("Choose how you want to use the system:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="role-card">
            <h3>🎯 Brand Manager</h3>
            <ul>
                <li>Upload project briefs</li>
                <li>Generate content writer reports</li>
                <li>Submit content for designer reports</li>
                <li>Manage the complete workflow</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Continue as Brand Manager", type="primary", use_container_width=True):
            st.session_state.user_role = "brand_manager"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="role-card">
            <h3>✍️ Content Writer</h3>
            <ul>
                <li>View your assigned project briefs</li>
                <li>Access AI-generated content reports</li>
                <li>Submit your completed content</li>
                <li>Track project progress</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✍️ Continue as Content Writer", type="primary", use_container_width=True):
            st.session_state.user_role = "content_writer"
            st.rerun()
    
    # Footer info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>🔗 Basecamp integration enabled • 🤖 Powered by Google Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

def show_brand_manager_page():
    """Show the brand manager page with project brief upload and management"""
    
    # Header with role info and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Brand Manager Dashboard</h1>
            <p>Upload project briefs and manage the complete workflow</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Change Role", type="secondary"):
            st.session_state.user_role = None
            st.rerun()
    
    # Sidebar for brand manager
    with st.sidebar:
        st.header("📋 Navigation")
        tab = st.radio("Choose a tab:", ["Upload & Analyze", "Analysis Results", "Projects", "Sample Brief"])
        
        st.header("⚙️ Settings")
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["comprehensive", "basic", "detailed"],
            help="Choose the level of analysis detail"
        )
        
        include_suggestions = st.checkbox(
            "Include AI Suggestions",
            value=True,
            help="Include AI-generated suggestions and recommendations"
        )
        
        st.header("🔗 Basecamp Integration")
        st.info("Configure Basecamp integration in your .env file to enable automatic report uploads and notifications.")
    
    # Main content based on selected tab
    if tab == "Upload & Analyze":
        upload_and_analyze_tab(analysis_type, include_suggestions)
    elif tab == "Analysis Results":
        analysis_results_tab()
    elif tab == "Projects":
        brand_manager_projects_tab()
    elif tab == "Sample Brief":
        sample_brief_tab()

def show_content_writer_page():
    """Show the content writer page with project brief access and content submission"""
    
    # Header with role info and logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>✍️ Content Writer Dashboard</h1>
            <p>Access your project briefs and submit completed content</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Change Role", type="secondary"):
            st.session_state.user_role = None
            st.rerun()
    
    # Sidebar for content writer
    with st.sidebar:
        st.header("📋 Navigation")
        tab = st.radio("Choose a tab:", ["My Projects", "Submit Content", "Content History"])
        
        st.header("🔗 Basecamp Integration")
        st.info("Your reports and notifications are automatically sent to Basecamp.")
    
    # Main content based on selected tab
    if tab == "My Projects":
        content_writer_projects_tab()
    elif tab == "Submit Content":
        content_writer_submit_tab()
    elif tab == "Content History":
        content_writer_history_tab()

def upload_and_analyze_tab(analysis_type: str, include_suggestions: bool):
    """Upload and analyze tab"""
    st.header("📤 Upload & Analyze Project Brief")
    
    # File upload section
    st.subheader("📁 Upload Document")

    # Project selection (fetch from backend projects endpoint)
    st.subheader("📋 Select Project")
    st.info("Choose which project this ad campaign belongs to. The system will automatically retrieve the project's Basecamp message board and document vault.")
    try:
        resp = requests.get(f"{API_BASE_URL}/projects", timeout=API_TIMEOUT)
        if resp.status_code == 200:
            pdata = resp.json()
            if pdata.get("success") and pdata.get("projects"):
                projects = pdata["projects"]
                options = ["Select a project..."] + [p.get("name", "Unnamed Project") for p in projects if p.get("status")=="active"]
                options.append("Other - Custom Project")
                selected_project = st.selectbox("🏗️ Project", options=options, help="Select the project this campaign belongs to from your Basecamp projects")
                if selected_project == "Select a project...":
                    st.warning("⚠️ Please select a project")
                    return
                if selected_project == "Other - Custom Project":
                    custom_name = st.text_input("✏️ Custom Project Name", placeholder="Enter your project name")
                    if not custom_name.strip():
                        st.warning("⚠️ Please provide a custom project name")
                        return
                    final_project_name = custom_name
                    st.session_state['selected_project_id'] = None
                    st.session_state['selected_project_name'] = final_project_name
                else:
                    final_project_name = selected_project
                    sel = next((p for p in projects if p.get("name")==selected_project), None)
                    if sel:
                        st.session_state['selected_project_id'] = sel.get('id')
                        st.session_state['selected_project_name'] = sel.get('name')
                        st.info(f"📋 **Project Details:** {sel.get('description','No description available')}")
            else:
                st.info("📤 No projects found. Using fallback options.")
                st.session_state['selected_project_id'] = None
                st.session_state['selected_project_name'] = None
        else:
            st.error(f"❌ Failed to fetch projects from backend: {resp.status_code}")
            st.session_state['selected_project_id'] = None
            st.session_state['selected_project_name'] = None
    except Exception as e:
        st.error(f"❌ Error fetching projects: {str(e)}")
        st.session_state['selected_project_id'] = None
        st.session_state['selected_project_name'] = None
    
    # User selection dropdowns for Basecamp notifications
    st.subheader("👥 Select Content Writer")
    st.info("Select the content writer who will receive the Stage 1 report and notification.")
    
    # Fetch available users from backend
    try:
        response = requests.get(f"{API_BASE_URL}/users", timeout=API_TIMEOUT)
        if response.status_code == 200:
            users_data = response.json()
            if users_data.get("success") and users_data.get("users"):
                available_users = users_data["users"]
                
                # Filter users by role (you can customize this logic)
                content_writers = [user for user in available_users if user.get("basecamp_user_id")]
                
                if content_writers:
                    content_writer_options = ["None"] + [f"{user['name']} ({user['email']})" for user in content_writers]
                    selected_content_writer = st.selectbox(
                        "Content Writer",
                        options=content_writer_options,
                        help="Select the content writer who will receive the Stage 1 report"
                    )
                    
                    content_writer_id = None
                    if selected_content_writer != "None":
                        selected_name = selected_content_writer.split(" (")[0]
                        selected_user = next((user for user in content_writers if user["name"] == selected_name), None)
                        if selected_user:
                            content_writer_id = selected_user["basecamp_user_id"]  # Use Basecamp ID directly
                            st.success(f"✅ Selected: {selected_user['name']} (Basecamp ID: {selected_user['basecamp_user_id']})")
                else:
                    st.warning("⚠️ No content writers available with Basecamp access")
                    content_writer_id = None
                
                if content_writer_id:
                    st.subheader("📋 Selected Team Member")
                    selected_cw = next((user for user in content_writers if user["basecamp_user_id"] == content_writer_id), None)
                    if selected_cw:
                        st.info(f"**Content Writer:** {selected_cw['name']} ({selected_cw['email']})")
                else:
                    st.warning("⚠️ Please select a content writer to receive the Stage 1 report")
                
            else:
                st.error("❌ Failed to fetch users from backend")
                content_writer_id = None
                designer_id = None
        else:
            st.error(f"❌ Backend error: {response.status_code}")
            content_writer_id = None
            designer_id = None
            
    except Exception as e:
        st.error(f"❌ Error connecting to backend: {str(e)}")
        st.info("💡 Make sure the backend server is running")
        content_writer_id = None
        designer_id = None
    
    uploaded_file = st.file_uploader(
        "Choose a project brief document",
        type=SUPPORTED_FORMATS,
        help=f"Supported formats: {', '.join(SUPPORTED_FORMATS).upper()}"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Analysis options
        st.subheader("🔍 Analysis Options")
        st.write(f"**Analysis Type:** {analysis_type}")
        st.write(f"**Include Suggestions:** {include_suggestions}")
        
        # Analyze button
        if st.button("🚀 Analyze Document (Stage 1)", type="primary"):
            if not content_writer_id:
                st.error("❌ Please select a content writer to receive the Stage 1 report")
                return
                
            with st.spinner("🤖 AI is analyzing your document..."):
                try:
                    # Prepare form data
                    files = {"file": uploaded_file}
                    data = {
                        "content_writer_id": content_writer_id,
                        "analysis_type": analysis_type,
                        "include_suggestions": include_suggestions,
                        "project_id": st.session_state.get('selected_project_id'),
                        "project_name": st.session_state.get('selected_project_name', None)
                    }
                    
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files,
                        data=data,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store results in session state
                        st.session_state.analysis_results = result
                        st.session_state.uploaded_file = uploaded_file.name
                        
                        st.success("🎉 Stage 1 Analysis completed successfully!")
                        
                        # Show Basecamp integration status
                        if result.get("basecamp_integration"):
                            basecamp_status = result["basecamp_integration"]
                            st.subheader("📤 Basecamp Integration Status")
                            
                            if basecamp_status.get("content_writer_uploaded"):
                                st.success("✅ Content Writer Report uploaded to Basecamp")
                            if basecamp_status.get("content_writer_notified"):
                                st.success("✅ Content Writer notification sent")
                            
                            if basecamp_status.get("errors"):
                                st.error(f"⚠️ Some errors occurred: {basecamp_status['errors']}")
                        
                        # Show summary
                        show_analysis_summary(result)
                        
                        # Store project brief ID for Stage 2
                        if result.get("report_data", {}).get("project_brief_id"):
                            st.session_state.project_brief_id = result["report_data"]["project_brief_id"]
                            st.session_state.content_writer_id = content_writer_id
                        
                        # Show Stage 2 section
                        st.subheader("🚀 Stage 2: Submit Content for Designer")
                        st.info("After the content writer completes their work, submit the content here to generate a designer report.")
                        
                        # Content submission form
                        with st.form("content_submission"):
                            content_text = st.text_area(
                                "Content Writer's Work",
                                placeholder="Paste the content that was created based on the project brief...",
                                height=200,
                                help="Submit the content that was written based on the project brief analysis"
                            )
                            
                            submit_content = st.form_submit_button("📤 Submit Content & Generate Designer Report", type="primary")
                            
                            if submit_content and content_text.strip():
                                st.info("💡 **Note:** Designer selection will be handled by the content writer in their dashboard.")
                                st.success("✅ Content submitted successfully! The content writer will now handle designer selection and report generation.")
                                
                                # Store content for content writer to process
                                st.session_state.submitted_content = content_text
                        
                        # Switch to results tab
                        st.info("📊 Switch to 'Analysis Results' tab to view detailed reports")
                        
                    else:
                        st.error(f"❌ Analysis failed: {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Analysis timed out. Please try again with a shorter document.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Connection error. Please check if the backend server is running.")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

def analysis_results_tab():
    """Analysis results tab"""
    st.header("📊 Analysis Results")
    
    if "analysis_results" not in st.session_state:
        st.info("📤 No analysis results available. Please upload and analyze a document first.")
        return
    
    results = st.session_state.analysis_results
    uploaded_file = st.session_state.get("uploaded_file", "Unknown")
    
    # File information
    st.subheader("📁 Document Information")
    st.write(f"**File:** {uploaded_file}")
    st.write(f"**Processing Time:** {results.get('processing_time', 0):.2f} seconds")
    if results.get('tokens_used'):
        st.write(f"**Tokens Used:** {results['tokens_used']}")
    
    # Project Brief Analysis
    if results.get("project_brief") and results["project_brief"].get("analysis_summary"):
        st.subheader("📋 Project Brief Analysis")
        st.write(results["project_brief"]["analysis_summary"])
    
    # Content Writer Report
    if results.get("content_writer_report"):
        st.subheader("✍️ Content Writer Report")
        display_content_writer_report(results["content_writer_report"])
    
    # Designer Report
    if results.get("designer_report"):
        st.subheader("🎨 Designer Report")
        display_designer_report(results["designer_report"])
    
    # Export options
    st.subheader("📤 Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Export as JSON"):
            export_results_json(results)
    
    with col2:
        if st.button("📊 Export Summary as CSV"):
            export_summary_csv(results)

def display_content_writer_report(report: Dict[str, Any]):
    """Display content writer report"""
    with st.expander("📖 Content Writer Report Details", expanded=True):
        if report.get('full_report'):
            st.write(report['full_report'])
        else:
            st.info("No content writer report was generated.")

def display_designer_report(report: Dict[str, Any]):
    """Display designer report"""
    with st.expander("🎨 Designer Report Details", expanded=True):
        if report.get('full_report'):
            st.write(report['full_report'])
        else:
            st.info("No designer report was generated.")

def sample_brief_tab():
    """Sample brief tab"""
    st.header("📝 Sample Project Brief")
    
    st.markdown("""
    ### Example Project Brief Structure
    
    **Project Name:** Brand Website Redesign
    
    **Brand Name:** TechCorp Solutions
    
    **Project Type:** Website Redesign
    
    **Target Audience:** Small to medium business owners, IT professionals
    
    **Objectives:**
    - Increase website conversion rate by 25%
    - Improve user experience and navigation
    - Establish brand authority in the tech solutions space
    
    **Key Messages:**
    - TechCorp provides reliable, cost-effective IT solutions
    - We understand small business technology needs
    - Our solutions scale with your business growth
    
    **Tone of Voice:** Professional, approachable, trustworthy
    
    **Deliverables:**
    - Homepage design
    - Service pages (5 pages)
    - About us page
    - Contact page
    - Blog section
    
    **Timeline:** 6 weeks
    
    **Budget:** $15,000
    
    **Additional Notes:** Focus on mobile-first design, include customer testimonials, emphasize local business support.
    """)

def show_analysis_summary(results: Dict[str, Any]):
    """Show quick analysis summary"""
    st.subheader("📊 Quick Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Processing Time", f"{results.get('processing_time', 0):.2f}s")
    
    with col2:
        st.metric("Analysis Type", results.get('analysis_type', 'Unknown'))
    
    with col3:
        st.metric("Status", "✅ Complete" if results.get('success') else "❌ Failed")
    
    # Show project brief ID if available
    if results.get("report_data", {}).get("project_brief_id"):
        st.info(f"**Project ID:** {results['report_data']['project_brief_id']}")

def content_writer_projects_tab():
    """Content writer projects tab - shows assigned project briefs"""
    st.header("📋 My Assigned Projects")
    
    if "analysis_results" not in st.session_state:
        st.info("📤 No projects assigned yet. Brand managers will upload project briefs and assign them to you.")
        return
    
    results = st.session_state.analysis_results
    
    # Show project information
    st.subheader("📁 Current Project")
    uploaded_file = st.session_state.get("uploaded_file", "Unknown")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Project File:** {uploaded_file}")
        if results.get("report_data", {}).get("project_brief_id"):
            st.info(f"**Project ID:** {results['report_data']['project_brief_id']}")
    
    with col2:
        st.info(f"**Processing Time:** {results.get('processing_time', 0):.2f} seconds")
        st.info(f"**Analysis Type:** {results.get('analysis_type', 'Unknown')}")
    
    # Show project brief analysis
    if results.get("report_data", {}).get("project_summary"):
        st.subheader("📋 Project Brief Analysis")
        with st.expander("📖 View Project Brief Analysis", expanded=True):
            st.write(results["report_data"]["project_summary"])
    
    # Show content writer report
    if results.get("report_data", {}).get("content_writer_report"):
        st.subheader("✍️ Your Content Writing Report")
        with st.expander("📖 View Content Writing Report", expanded=True):
            st.write(results["report_data"]["content_writer_report"])
    
    # Show next steps
    st.subheader("🚀 Next Steps")
    st.markdown("""
    1. **Review the project brief analysis** above
    2. **Study your content writing report** for guidance
    3. **Create your content** based on the project requirements
    4. **Submit your completed content** in the 'Submit Content' tab
    5. **Wait for designer report** to be generated
    """)
    
    # Quick navigation
    st.info("💡 **Tip:** Use the sidebar to navigate between tabs and submit your content when ready.")

def content_writer_submit_tab():
    """Content writer submit tab - for submitting completed content"""
    st.header("📤 Submit Completed Content")
    
    if "analysis_results" not in st.session_state:
        st.info("📤 No projects available. Please wait for a brand manager to assign you a project.")
        return
    
    results = st.session_state.analysis_results
    project_brief_id = results.get("report_data", {}).get("project_brief_id")
    
    if not project_brief_id:
        st.error("❌ No project ID found. Please contact the brand manager.")
        return
    
    st.info(f"**Project ID:** {project_brief_id}")
    
    # Content submission form
    with st.form("content_writer_submission"):
        st.subheader("✍️ Submit Your Content")
        
        # File upload for content document
        st.info("📁 Upload your completed content document (PDF, DOCX, or TXT)")
        content_file = st.file_uploader(
            "Choose your content document",
            type=SUPPORTED_FORMATS,
            help=f"Upload the document containing your completed content. Supported formats: {', '.join(SUPPORTED_FORMATS).upper()}"
        )
        
        # Also allow text input as backup
        content_text = st.text_area(
            "Content Text (Optional - if not uploading document)",
            placeholder="Paste or type your completed content here as backup...",
            height=200,
            help="You can also paste your content here if you prefer text input"
        )
        
        # Designer selection
        st.subheader("🎨 Select Designer for Report")
        st.info("Choose a designer who will receive the report based on your content.")
        
        try:
            response = requests.get(f"{API_BASE_URL}/users", timeout=API_TIMEOUT)
            if response.status_code == 200:
                users_data = response.json()
                if users_data.get("success") and users_data.get("users"):
                    available_users = users_data["users"]
                    designers = [user for user in available_users if user.get("basecamp_user_id")]
                    
                    if designers:
                        designer_options = ["None"] + [f"{user['name']} ({user['email']})" for user in designers]
                        selected_designer = st.selectbox(
                            "Designer",
                            options=designer_options,
                            help="Select the designer who will receive the report"
                        )
                        
                        designer_id = None
                        if selected_designer != "None":
                            selected_name = selected_designer.split(" (")[0]
                            selected_user = next((user for user in designers if user["name"] == selected_name), None)
                            if selected_user:
                                designer_id = selected_user["basecamp_user_id"]
                                st.success(f"✅ Selected: {selected_user['name']}")
                    else:
                        st.warning("⚠️ No designers available")
                        designer_id = None
                else:
                    st.error("❌ Failed to fetch designers")
                    designer_id = None
            else:
                st.error(f"❌ Backend error: {response.status_code}")
                designer_id = None
                
        except Exception as e:
            st.error(f"❌ Error connecting to backend: {str(e)}")
            designer_id = None
        
        submit_content = st.form_submit_button("📤 Submit Content & Generate Designer Report", type="primary")
        
        if submit_content:
            # Check if either file or text is provided
            if not content_file and not content_text.strip():
                st.error("❌ Please either upload a content document or enter content text")
                return
            
            if not designer_id:
                st.error("❌ Please select a designer to receive the report")
                return
            
            with st.spinner("🤖 Generating designer report from your content..."):
                try:
                    # Prepare content data
                    content_data = {
                        "project_brief_id": project_brief_id,
                        "designer_id": designer_id,
                        "content_writer_id": None  # Will be set by backend based on session
                    }
                    
                    # Add content text if provided
                    if content_text.strip():
                        content_data["content_text"] = content_text
                    
                    # Add file if uploaded
                    files = {}
                    if content_file:
                        files["content_file"] = content_file
                        content_data["has_file"] = True
                    
                    # Submit content to backend
                    if files:
                        content_response = requests.post(
                            f"{API_BASE_URL}/submit-content",
                            files=files,
                            data=content_data,
                            timeout=300
                        )
                    else:
                        content_response = requests.post(
                            f"{API_BASE_URL}/submit-content",
                            data=content_data,
                            timeout=300
                        )
                    
                    if content_response.status_code == 200:
                        content_result = content_response.json()
                        st.success("🎉 Content submitted successfully! Designer report generated and uploaded to Basecamp.")
                        
                        # Show Basecamp integration status
                        if content_result.get("basecamp_integration"):
                            designer_status = content_result["basecamp_integration"]
                            if designer_status.get("designer_uploaded"):
                                st.success("✅ Designer Report uploaded to Basecamp")
                            if designer_status.get("designer_notified"):
                                st.success("✅ Designer notification sent")
                        
                        # Store designer results
                        st.session_state.designer_results = content_result
                        
                    else:
                        st.error(f"❌ Content submission failed: {content_response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error submitting content: {str(e)}")

def content_writer_history_tab():
    """Content writer history tab - shows completed projects and reports"""
    st.header("📚 Content History")
    
    if "designer_results" not in st.session_state:
        st.info("📤 No completed content submissions yet. Submit your content to see history here.")
        return
    
    results = st.session_state.designer_results
    
    st.subheader("✅ Latest Submission")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Project ID:** {results.get('project_brief_id', 'Unknown')}")
        st.info(f"**Processing Time:** {results.get('processing_time', 0):.2f} seconds")
    
    with col2:
        st.info(f"**Status:** {results.get('stage', 'Unknown')}")
        st.info(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Show designer report if available
    if results.get("report_data", {}).get("designer_report"):
        st.subheader("🎨 Designer Report Generated")
        with st.expander("📖 View Designer Report", expanded=True):
            st.write(results["report_data"]["designer_report"])
    
    # Show Basecamp integration status
    if results.get("basecamp_integration"):
        st.subheader("📤 Basecamp Integration Status")
        basecamp_status = results["basecamp_integration"]
        
        if basecamp_status.get("designer_uploaded"):
            st.success("✅ Designer Report uploaded to Basecamp")
        if basecamp_status.get("designer_notified"):
            st.success("✅ Designer notification sent")
        
        if basecamp_status.get("errors"):
            st.error(f"⚠️ Some errors occurred: {basecamp_status['errors']}")
    
    st.info("💡 **Note:** Your content has been successfully processed and the designer report has been generated and uploaded to Basecamp.")

def brand_manager_projects_tab():
    """Brand manager projects tab - shows all projects and their status"""
    st.header("📋 Project Management")
    
    # Project overview
    st.subheader("📊 Project Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if "analysis_results" in st.session_state:
            st.metric("Active Projects", "1", help="Projects currently in progress")
        else:
            st.metric("Active Projects", "0", help="Projects currently in progress")
    
    with col2:
        if "designer_results" in st.session_state:
            st.metric("Completed Projects", "1", help="Projects that have completed all stages")
        else:
            st.metric("Completed Projects", "0", help="Projects that have completed all stages")
    
    with col3:
        total_projects = 0
        if "analysis_results" in st.session_state:
            total_projects += 1
        if "designer_results" in st.session_state:
            total_projects += 1
        st.metric("Total Projects", total_projects, help="All projects in the system")
    
    # Current project status
    if "analysis_results" in st.session_state:
        st.subheader("🚀 Current Project Status")
        
        results = st.session_state.analysis_results
        project_brief_id = results.get("report_data", {}).get("project_brief_id", "Unknown")
        uploaded_file = st.session_state.get("uploaded_file", "Unknown")
        
        # Project details
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Project ID:** {project_brief_id}")
            st.info(f"**File:** {uploaded_file}")
            st.info(f"**Stage:** Stage 1 - Content Writer Report Generated")
        
        with col2:
            st.info(f"**Content Writer:** {results.get('content_writer_id', 'Not assigned')}")
            st.info(f"**Analysis Type:** {results.get('analysis_type', 'Unknown')}")
            st.info(f"**Status:** ✅ Complete")
        
        # Stage 1 completion
        st.success("✅ **Stage 1 Complete:** Project brief analyzed and content writer report generated")
        
        # Stage 2 status
        if "submitted_content" in st.session_state:
            st.success("✅ **Stage 2 Complete:** Content submitted for designer report")
            st.info(f"**Content Length:** {len(st.session_state.submitted_content)} characters")
        else:
            st.warning("⏳ **Stage 2 Pending:** Waiting for content writer to submit content")
            st.info("💡 **Next Step:** Content writer needs to submit their completed content")
    
    # Completed projects
    if "designer_results" in st.session_state:
        st.subheader("🎉 Completed Projects")
        
        results = st.session_state.designer_results
        project_brief_id = results.get("project_brief_id", "Unknown")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Project ID:** {project_brief_id}")
            st.info(f"**Final Stage:** {results.get('stage', 'Unknown')}")
        
        with col2:
            st.info(f"**Processing Time:** {results.get('processing_time', 0):.2f} seconds")
            st.info(f"**Status:** ✅ Complete")
        
        # Show completion summary
        st.success("🎉 **Project Successfully Completed!**")
        st.info("""
        **Workflow Summary:**
        1. ✅ Project brief uploaded and analyzed
        2. ✅ Content writer report generated and sent
        3. ✅ Content writer submitted completed content
        4. ✅ Designer report generated and sent
        5. ✅ All reports uploaded to Basecamp
        """)
    
    # No projects message
    if "analysis_results" not in st.session_state and "designer_results" not in st.session_state:
        st.info("📤 No projects available yet. Start by uploading a project brief in the 'Upload & Analyze' tab.")
    
    with col1:
        project_name = results.get("project_brief", {}).get("project_name", "Unknown")
        brand_name = results.get("project_brief", {}).get("brand_name", "Unknown")
        st.metric("Project", project_name)
        st.metric("Brand", brand_name)
    
    with col2:
        project_type = results.get("project_brief", {}).get("project_type", "Unknown")
        processing_time = results.get("processing_time", 0)
        st.metric("Type", project_type)
        st.metric("Processing Time", f"{processing_time:.2f}s")
    
    with col3:
        basecamp_uploaded = results.get("basecamp_integration", {}).get("content_writer_uploaded", False) or results.get("basecamp_integration", {}).get("designer_uploaded", False)
        notifications_sent = results.get("basecamp_integration", {}).get("content_writer_notified", False) or results.get("basecamp_integration", {}).get("designer_notified", False)
        st.metric("Basecamp Upload", "✅" if basecamp_uploaded else "❌")
        st.metric("Notifications", "✅" if notifications_sent else "❌")

def export_results_json(results: Dict[str, Any]):
    """Export results as JSON"""
    json_str = json.dumps(results, indent=2, default=str)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"project_brief_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def export_summary_csv(results: Dict[str, Any]):
    """Export summary as CSV"""
    try:
        project_brief = results.get("project_brief", {})
        
        summary_data = {
            "Field": [
                "Project Name", "Brand Name", "Project Type", "Target Audience",
                "Timeline", "Budget", "Objectives Count", "Deliverables Count",
                "Processing Time", "Tokens Used", "Basecamp Uploaded", "Notifications Sent"
            ],
            "Value": [
                project_brief.get("project_name", "N/A"),
                project_brief.get("brand_name", "N/A"),
                project_brief.get("project_type", "N/A"),
                project_brief.get("target_audience", "N/A"),
                project_brief.get("timeline", "N/A"),
                project_brief.get("budget", "N/A"),
                len(project_brief.get("objectives", [])),
                len(project_brief.get("deliverables", [])),
                f"{results.get('processing_time', 0):.2f}s",
                results.get("tokens_used", "N/A"),
                "Yes" if results.get("basecamp_integration", {}).get("content_writer_uploaded") or results.get("basecamp_integration", {}).get("designer_uploaded") else "No",
                "Yes" if results.get("basecamp_integration", {}).get("content_writer_notified") or results.get("basecamp_integration", {}).get("designer_notified") else "No"
            ]
        }
        
        df = pd.DataFrame(summary_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV Summary",
            data=csv,
            file_name=f"project_brief_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error exporting CSV: {str(e)}")

if __name__ == "__main__":
    main()
