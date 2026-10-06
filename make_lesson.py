import os, json, datetime, urllib.request
from zoneinfo import ZoneInfo
import feedparser

# Sources to read every morning (you can add or remove later)
FEEDS = [
 "https://rss.arxiv.org/rss/cs.AI",
 "https://huggingface.co/blog/feed.xml",
 "https://simonwillison.net/atom/everything/",
]

MODEL = "gemini-flash-latest"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# 1. Collect fresh items
items = []
for url in FEEDS:
 try:
 feed = feedparser.parse(url)
 for e in feed.entries[:5]:
 items.append({
 "source": feed.feed.get("title", url),
 "title": e.get("title", ""),
 "link": e.get("link", ""),
 "summary": e.get("summary", "")[:500],
 })
 except Exception as ex:
 print("Feed failed:", url, ex)

if not items:
 raise SystemExit("No feed items fetched. Check the feed links.")

# 2. Ask Gemini to write a lesson + quiz
prompt = f"""You are a friendly AI teacher. From the news items below, pick the
single most useful topic for a beginner learning AI in 2026.
Return ONLY JSON in this exact shape:
{{
 "title": "...",
 "summary": "2-3 sentence overview",
 "lesson": "300-400 word plain-English lesson with one real-world example",
 "key_terms": [{{"term": "...", "meaning": "..."}}],
 "quiz": [{{"question": "...", "options": ["A","B","C","D"], "answer": "exact correct option", "why": "..."}}],
 "source_links": ["links of the items you used"]
}}
Include exactly 3 quiz questions.

News items:
{json.dumps(items, ensure_ascii=False)}
"""

body = {
 "contents": [{"parts": [{"text": prompt}]}],
 "generationConfig": {"responseMimeType": "application/json"},
}
req = urllib.request.Request(
 API_URL,
 data=json.dumps(body).encode(),
 headers={"Content-Type": "application/json",
 "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
)
with urllib.request.urlopen(req, timeout=120) as r:
 data = json.load(r)

lesson = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])

# 3. Save it with today's India date
today = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
lesson["date"] = today
os.makedirs("lessons", exist_ok=True)
for path in (f"lessons/{today}.json", "lessons/latest.json"):
 with open(path, "w", encoding="utf-8") as f:
 json.dump(lesson, f, ensure_ascii=False, indent=2)

print("Saved lesson:", lesson.get("title"))
