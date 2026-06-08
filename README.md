# Local Business Lead Finder

Find small businesses near you that need a website — powered by Google Places API.

## Setup (one time)

1. Make sure Python is installed — open terminal and run:
   ```
   python --version
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## How to run (Streamlit - Recommended)

1. Open terminal in this folder
2. Run:
   ```
   streamlit run app.py
   ```
3. Browser opens automatically at `http://localhost:8501`

## How to use

1. Paste your Google Places API key in the sidebar
2. Enter area name (e.g. "Indiranagar, Bangalore")
3. Pick business category
4. Click **Find Leads**
5. Filter by **📞 + No Website** to see best leads
6. Click **⬇️ Download CSV** for your outreach list

## Deploy to Streamlit Cloud (Free & Easy)

1. Push your code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repo, branch, and `app.py`
5. Deploy — get a shareable URL instantly

Your app runs for free on Streamlit Cloud!

## Alternative: Run with Flask (Original)

```bash
python server.py
```
Then visit `http://localhost:5000`

## Stop the server

Press `Ctrl+C` in the terminal.
