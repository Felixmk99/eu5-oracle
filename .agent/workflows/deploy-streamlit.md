---
description: Deploying EU5 Oracle to Streamlit Community Cloud
---

Follow these steps to deploy your private Oracle so others can access it via your Groq API key:

### 1. Push your code to GitHub
Streamlit Community Cloud deploys directly from a GitHub repository.
1. Create a new **Public** or **Private** repository on [GitHub](https://github.com/new) named `eu5-oracle`.
2. In your terminal, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/eu5-oracle.git
   git push -u origin main
   ```

### 2. Connect to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"Connect to GitHub"**.
3. Once logged in, click **"Create app"**.
4. Select your `eu5-oracle` repository and set the Main file path to `src/ui.py`.

### 3. Add your Secrets (CRITICAL for Groq)
Before the app starts, you must give it your API key securely:
1. In the Streamlit deployment dashboard, click **"Advanced settings..."** before clicking Deploy (or go to **Settings > Secrets** after deploying).
2. Paste the following into the Secrets box:
   ```toml
   GROQ_API_KEY = "your-gsk-api-key-here"
   ```
3. Click **Save**.

### 4. Deploy!
Click **"Deploy!"**. Streamlit will install the requirements from `requirements.txt` and your Oracle will be live at a custom URL.

// turbo-all
