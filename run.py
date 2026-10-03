import os
import sys

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Reconfigure stdout for unicode safe printing on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("PocketSmart AI - AI-Powered Budget & Recommendation Platform")
    print(f"Server running at: http://127.0.0.1:{port}")
    print("Planners: Home Interior | Party Planner | Jewelry & Outfit Vision")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=True)
