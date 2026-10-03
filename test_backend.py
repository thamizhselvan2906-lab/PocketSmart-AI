import os
import sys
import json

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set stdout to utf-8 if possible
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app import app
from backend.database import init_db

def run_tests():
    print("[INFO] Running PocketSmart AI Backend Verification Tests...")
    init_db()
    client = app.test_client()

    # 1. Test Static Index
    print("\n[1] Testing Static Index Route (GET /)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert b"PocketSmart" in res.data, "PocketSmart brand not in index.html"
    print("  [PASS] Index page loaded successfully")

    # 2. Test System Status
    print("\n[2] Testing System Status (GET /api/system/status)...")
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data and data["status"] == "healthy"
    print(f"  [PASS] Status healthy, engine mode: {data.get('engine_mode')}")

    # 3. Test Home Interior Planner
    print("\n[3] Testing Home Interior Planner (POST /api/planners/home-interior)...")
    home_payload = {
        "budget": 1000,
        "currency": "$",
        "room": "Living Room",
        "style": "Modern Minimalist",
        "items": [
            {"name": "Sofa", "qty": 1},
            {"name": "Coffee Table", "qty": 1}
        ],
        "notes": "Testing home planner"
    }
    res = client.post("/api/planners/home-interior", json=home_payload)
    assert res.status_code == 200, f"Got error: {res.data}"
    home_plan = res.get_json()
    assert "recommendations" in home_plan and len(home_plan["recommendations"]) > 0
    assert home_plan["estimated_spending"] <= home_plan["total_budget"], "Exceeded budget!"
    print(f"  [PASS] Generated {len(home_plan['recommendations'])} items. Budget: {home_plan['total_budget']}, Spent: {home_plan['estimated_spending']}, Remaining: {home_plan['remaining_budget']}")

    # 4. Test Party Planner
    print("\n[4] Testing Party Planner (POST /api/planners/party)...")
    party_payload = {
        "budget": 2500,
        "currency": "$",
        "event_type": "Birthday",
        "guest_count": 40,
        "requirements": ["Venue", "Catering", "Decoration", "Entertainment"],
        "notes": "Testing party planner"
    }
    res = client.post("/api/planners/party", json=party_payload)
    assert res.status_code == 200
    party_plan = res.get_json()
    assert "allocations" in party_plan and len(party_plan["allocations"]) > 0
    assert party_plan["estimated_spending"] <= party_plan["total_budget"]
    print(f"  [PASS] Generated party plan with {len(party_plan['allocations'])} category allocations")

    # 5. Test Jewelry Planner
    print("\n[5] Testing Jewelry Planner (POST /api/planners/jewelry)...")
    jewelry_payload = {
        "budget": 300,
        "currency": "$",
        "occasion": "Cocktail",
        "style": "Contemporary",
        "material": "Rose Gold",
        "notes": "Testing jewelry planner"
    }
    res = client.post("/api/planners/jewelry", json=jewelry_payload)
    assert res.status_code == 200
    jewelry_plan = res.get_json()
    assert "recommendations" in jewelry_plan
    assert jewelry_plan["estimated_spending"] <= jewelry_plan["total_budget"]
    print(f"  [PASS] Generated jewelry ensemble with {len(jewelry_plan['recommendations'])} pieces")

    # 6. Test Plan Save to Database
    print("\n[6] Testing Plan Save to SQLite (POST /api/plans/save)...")
    save_payload = {
        "title": home_plan["title"],
        "planner_type": "home",
        "currency": "$",
        "total_budget": home_plan["total_budget"],
        "estimated_spending": home_plan["estimated_spending"],
        "remaining_budget": home_plan["remaining_budget"],
        "ai_summary": home_plan["ai_summary"],
        "user_inputs": home_payload,
        "recommendations": home_plan["recommendations"],
        "allocations": home_plan.get("allocations", [])
    }
    res = client.post("/api/plans/save", json=save_payload)
    assert res.status_code == 201, f"Failed saving plan: {res.data}"
    saved_plan = res.get_json()["plan"]
    plan_id = saved_plan["id"]
    print(f"  [PASS] Plan persisted with ID {plan_id}")

    # 7. Test Plan Retrieval
    print(f"\n[7] Testing Plan Retrieval (GET /api/plans/{plan_id})...")
    res = client.get(f"/api/plans/{plan_id}")
    assert res.status_code == 200
    fetched = res.get_json()
    assert fetched["id"] == plan_id
    assert len(fetched["recommendations"]) == len(home_plan["recommendations"])
    print(f"  [PASS] Plan fetched accurately with {len(fetched['recommendations'])} items")

    # 8. Test Dynamic Item Toggle & Spending Recalculation
    print("\n[8] Testing Dynamic Item Toggle (PATCH /api/plans/<id>/items/<id>)...")
    first_item = fetched["recommendations"][0]
    initial_spending = fetched["estimated_spending"]
    item_cost = first_item["estimated_price"] * first_item["quantity"]

    res = client.patch(
        f"/api/plans/{plan_id}/items/{first_item['id']}",
        json={"is_selected": False}
    )
    assert res.status_code == 200
    patch_result = res.get_json()
    expected_spending = round(initial_spending - item_cost, 2)
    assert patch_result["estimated_spending"] == expected_spending, f"Expected {expected_spending}, got {patch_result['estimated_spending']}"
    print(f"  [PASS] Item excluded successfully. Spending reduced from ${initial_spending} to ${patch_result['estimated_spending']}")

    # 9. Test Dashboard Statistics
    print("\n[9] Testing Dashboard Stats (GET /api/dashboard/stats)...")
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.get_json()
    assert stats["total_plans"] >= 1
    assert stats["total_recommendations"] >= len(fetched["recommendations"])
    print(f"  [PASS] Dashboard aggregated: {stats['total_plans']} plans, {stats['total_recommendations']} recommendations, Total Budget: ${stats['total_budget']}")

    print("\n[SUCCESS] ALL TESTS PASSED FLINT-CLEAN! PocketSmart AI is 100% operational.")

if __name__ == "__main__":
    run_tests()
