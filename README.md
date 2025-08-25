# AI Project Brief Analyzer - Frontend

## Deployment Instructions

1. **Upload to GitHub:**
   - Create a new GitHub repository
   - Upload all files from this directory
   - Make sure `streamlit_app.py` is in the root

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy!"

3. **Environment Variables:**
   - In Streamlit Cloud, go to Settings > Secrets
   - Add your backend URL:
   ```toml
   [backend]
   url = "https://my-microservice-deployment-581806428620.us-central1.run.app/"
   ```

4. **Update Configuration:**
   - The app will automatically use the backend URL from Streamlit secrets
   - Or update `config.py` with your production backend URL

## File Structure
```
streamlit_app.py          # Main application
requirements.txt          # Python dependencies
.streamlit/config.toml   # Streamlit configuration
```

## Backend URL
Make sure your backend is accessible from Streamlit Cloud:
- Backend URL: https://my-microservice-deployment-581806428620.us-central1.run.app/
- Test the connection before deploying
