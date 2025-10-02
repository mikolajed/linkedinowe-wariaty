# LinkedInowe Wariaty

A score tracker for LinkedIn games (Pinpoint, Queens, Crossclimb) for three friends.

## Quick Start (Local Testing)
```bash
# Clone and cd
git clone https://github.com/your-username/LinkedInoweWariaty.git
cd LinkedInoweWariaty

# Create and activate virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with LinkedIn OAuth and AWS credentials

# Run locally
streamlit run app.py