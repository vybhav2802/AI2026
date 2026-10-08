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
You are an expert AI teacher and practical mentor. Using the news items below, write ONE detailed, beginner-friendly lesson of about 1000 to 1500 words. Teach the main idea behind the news, not just the headline. Be practical and show the learner what they can actually do today. Only recommend real, well-known AI tools that exist, and say whether each one is free, freemium, or paid. Return ONLY valid JSON with these keys: title (string), summary (2 to 3 sentences), why_it_matters (one paragraph), explanation (list of 4 to 6 paragraphs teaching the concept step by step in simple words), key_points (list of 6 short points), tools (list of 3 to 5 objects, each with keys name, what_it_does, price, how_to_start), hands_on_task (list of 5 to 8 steps the learner can finish in 15 to 30 minutes using one of the tools), example (one real-world example paragraph), common_mistakes (list of 3 points), glossary (list of objects with keys term and meaning), quiz (list of 5 objects with keys question and answer), next_step (one sentence on what to learn tomorrow).body = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}).encode()
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
