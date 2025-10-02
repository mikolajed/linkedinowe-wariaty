# LinkedInowe Wariaty

## Overview

This app tracks and visualizes puzzle game scores shared by players from LinkedIn posts.  
Supported games:

- **Zip** – time and backtracks  
- **Mini Sudoku** – time  
- **Tango** – time  
- **Pinpoint** – guesses and accuracy  
- **Crossclimb** – time  
- **Queens** – time  

All numeric metrics are stored regardless of language in the posts. Non-numeric parts like "flawless" or emojis are ignored for analytics.

Scores are visualized in two tabs:

1. **All Scores** – table of all processed scores.  
2. **Progress** – line charts of player progress over game numbers.

---

## Setup

### 1. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Configure secrets
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Edit `.streamlit/secrets.toml` with your LinkedIn OAuth and AWS credentials.

### 4. Run locally
```bash
streamlit run app.py
```
---

## Database Schema

### 1. `raw_game_posts`
Stores the full user-submitted post for reference.

| Column | Type | Description |
|--------|------|-------------|
| user_id | string | Partition key |
| timestamp | string | Submission timestamp (ISO UTC) |
| raw_post | string | Full post text |
| game | string | Optional: extracted game type |
| game_number | number | Optional: extracted game number |

> **Note:** Only the original post is stored here; do not parse numeric metrics.

### 2. `game_scores`
Stores processed numeric metrics for plotting and analysis.

| Column | Type | Description |
|--------|------|-------------|
| user_id | string | Partition key |
| game | string | e.g., Zip, Mini Sudoku |
| game_number | number | From #number in post |
| score | number | Primary metric (time in seconds or guesses) |
| metric | string | "seconds", "guesses", "backtracks", "accuracy" |
| secondary_metric | number | Optional: backtracks or accuracy |
| game_date | string | Derived from submission timestamp |
| timestamp | string | UTC timestamp of saving |

### Metric Mapping

| Game | Primary Metric | Secondary Metric |
|------|----------------|-------------------|
| Zip | time (seconds) | backtracks |
| Mini Sudoku | time (seconds) | — |
| Tango | time (seconds) | — |
| Pinpoint | guesses | accuracy (%) |
| Crossclimb | time (seconds) | — |
| Queens | time (seconds) | — |

### Notes

- `game_scores` contains numeric metrics only, suitable for plotting in the All Scores and Progress tabs.
- `raw_game_posts` preserves the original input for auditing or additional parsing.
- Tables use `user_id` as partition key; optionally, `timestamp` or `game_number` can be the sort key to allow multiple entries per user.
- All plots use `game_number` as the X-axis to show progress over time.

## Example Data Flow

**Raw Post:**  
"Just played Mini Sudoku #52 | 6:29 and flawless ✏️"

**Processed Data:**
```json
{
  "user_id": "user123",
  "game": "Mini Sudoku",
  "game_number": 52,
  "score": 389,  // 6:29 in seconds
  "metric": "seconds",
  "game_date": "2025-10-02",
  "timestamp": "2025-10-02T14:30:00Z"
}
````
