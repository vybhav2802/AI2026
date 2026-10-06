import os, sys, json, datetime, pathlib, urllib.request
import feedparser
sys.excepthook = lambda t, v, tb: (print("ERROR:", t.__name__, "-", v), print("Hint: 400/403 = bad API key, 404 = bad model name, 429 = rate limit, wait and retry"), print(v.read().decode()[:500]) if hasattr(v, "read") else None)
FEEDS = ["https://huggingface.co/blog/feed.xml", "https://techcrunch.com/category/artificial-intelligence/feed/", "https://blog.google/technology/ai/rss/", "https://www.technologyreview.com/topic/artificial-intelligence/feed"]
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
key = os.environ.get("GEMINI_API_KEY", "").strip()
if not key: sys.exit("ERROR: GEMINI_API_KEY is empty. Add it in Settings > Secrets and variables > Actions (exact name).")
print("API key found.")
feeds = [feedparser.parse(u, agent="Mozilla/5.0 AI-Lesson-Bot") for u in FEEDS]
for u, f in zip(FEEDS, feeds): print(u, "->", len(f.entries), "items")
items = [f"- {e.get('title', '')}: {e.get('summary', '')[:300]}" for f in feeds for e in f.entries[:5]]
if not items: sys.exit("ERROR: No feed items fetched. All RSS feeds failed.")
prompt = "You are a friendly AI teacher. Using these recent AI news items, write one short beginner-friendly lesson. Reply ONLY with JSON in this shape: " + '{"title": "...", "summary": "...", "key_points": ["...", "..."], "example": "...", "quiz": [{"question": "...", "answer": "..."}]}' + "\n\n" + "\n".join(items[:20])
body = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}).encode()
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent", data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
print("Asking Gemini (" + MODEL + ")...")
data = json.loads(urllib.request.urlopen(req, timeout=90).read())
fence = "`" * 3
text = data["candidates"][0]["content"]["parts"][0]["text"].strip().removeprefix(fence + "json").removeprefix(fence).removesuffix(fence).strip()
lesson = json.loads(text)
if isinstance(lesson, list): lesson = lesson[0]
today = datetime.date.today().isoformat()
lesson["date"] = today
pathlib.Path("lessons").mkdir(exist_ok=True)
for name in ("latest.json", f"{today}.json"): pathlib.Path("lessons", name).write_text(json.dumps(lesson, indent=2, ensure_ascii=False), encoding="utf-8")
print("Saved lessons/latest.json and lessons/" + today + ".json")
