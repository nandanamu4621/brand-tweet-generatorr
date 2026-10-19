# BrandVoice — AI Tweet Generator

A small Flask web app that infers a brand voice from user-provided details and optional example posts, then generates exactly 10 tweet drafts.

## Features
- Brand, industry, campaign objective, product details and preferred tone form
- Optional example posts to guide voice matching
- Four-bullet voice snapshot
- Ten varied tweet drafts with content-type labels
- Copy-one and copy-all controls
- No automatic social media scraping; no social media login required

## Requirements
- Python 3.10+
- An OpenAI API key with API access/billing enabled

## Run locally (Windows PowerShell)
```powershell
cd brand_tweet_generator
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Open `.env` in VS Code and replace `your_api_key_here` with your API key. Do not commit `.env` or share your key.

Then run:
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
python app.py
```
Open http://127.0.0.1:5000

If you use `.env`, install `python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` near the top of `app.py`, or set the environment variables in the terminal as shown above. For a minimal setup, setting the environment variable in PowerShell is sufficient.

## Deployment
Deploy as a Python web service on a host that supports Flask (for example Render or another compatible service). Set the start command to:
```text
gunicorn app:app
```
Add `OPENAI_API_KEY`, `OPENAI_MODEL` (optional), and `FLASK_SECRET_KEY` in the host's environment-variable settings. Do not put secrets in source code. A live link is only available after deploying this project to an account.

## Prompt design / approach
1. **Input collection:** collect optional brand name, category, product/service details, objective, tone and sample posts.
2. **Voice inference:** the prompt asks the model to infer tone, audience, themes and writing style. When example posts are absent, it must treat its findings as inference rather than verified social listening.
3. **Generation:** request JSON with four voice bullets and exactly ten tweet objects. Require variety across conversational, promotional, witty and informative formats.
4. **Quality constraints:** keep tweets concise, specific to the provided details and non-repetitive. Instruct the model not to invent prices, offers, statistics, product features or guarantees.
5. **Review:** users should review drafts for accuracy, brand suitability, legal claims and current campaign details before publishing.

## Example testing ideas
- **Zomato (food delivery):** objective = engagement; products = food delivery and restaurant discovery; tone = witty and conversational.
- **Nike (sportswear):** objective = brand awareness; products = sportswear and athletic footwear; tone = bold and energetic.

These are test inputs, not claims that the generated outputs reflect a live analysis of the brands' current social posts.

## Limitations
- No live scraping of X, Instagram or LinkedIn.
- Voice matching depends on the information and sample posts the user supplies.
- AI-generated drafts may contain errors; review before publishing.
- Each generation uses an external AI API and may incur usage charges.
