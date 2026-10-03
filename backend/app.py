import os
import json
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from backend.config import Config
from backend.database import db_session, init_db
from backend.models import Plan, RecommendationItem, BudgetAllocation
from backend.gemini_service import gemini_service

app = Flask(
    __name__,
    static_folder=str(Config.FRONTEND_DIR / "static"),
    static_url_path="/static"
)
app.config.from_object(Config)
CORS(app)

# Initialize database schema
init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# -------------------------------------------------------------
# Static Frontend Serving
# -------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(Config.FRONTEND_DIR, "index.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


# -------------------------------------------------------------
# System & Health APIs
# -------------------------------------------------------------
@app.route("/api/system/status", methods=["GET"])
def system_status():
    has_key = gemini_service.is_api_configured()
    return jsonify({
        "status": "healthy",
        "has_gemini_key": has_key,
        "engine_mode": "Gemini Live AI" if has_key else "Smart Demo Engine",
        "database": "SQLite Connected"
    })


@app.route("/api/system/key", methods=["POST"])
def update_api_key():
    data = request.get_json() or {}
    key = data.get("api_key", "").strip()
    if not key:
        return jsonify({"error": "API key cannot be empty"}), 400

    gemini_service.set_api_key(key)
    return jsonify({
        "success": True,
        "message": "Gemini API key updated successfully",
        "engine_mode": "Gemini Live AI"
    })


# -------------------------------------------------------------
# Planner Endpoints
# -------------------------------------------------------------
@app.route("/api/planners/home-interior", methods=["POST"])
def plan_home_interior():
    try:
        data = request.get_json() or {}
        budget = float(data.get("budget", 0))
        if budget <= 0:
            return jsonify({"error": "Budget must be greater than 0"}), 400

        currency = data.get("currency", "$")
        room = data.get("room", "Living Room")
        items = data.get("items", [])
        style = data.get("style", "Modern Minimalist")
        notes = data.get("notes", "")

        result = gemini_service.plan_home_interior(
            budget=budget,
            currency=currency,
            room=room,
            items=items,
            style=style,
            notes=notes
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to generate interior plan: {str(e)}"}), 500


@app.route("/api/planners/party", methods=["POST"])
def plan_party():
    try:
        data = request.get_json() or {}
        budget = float(data.get("budget", 0))
        if budget <= 0:
            return jsonify({"error": "Budget must be greater than 0"}), 400

        currency = data.get("currency", "$")
        event_type = data.get("event_type", "Birthday")
        guest_count = int(data.get("guest_count", 25))
        requirements = data.get("requirements", ["Venue", "Catering", "Decoration", "Entertainment"])
        notes = data.get("notes", "")

        result = gemini_service.plan_party(
            budget=budget,
            currency=currency,
            event_type=event_type,
            guest_count=guest_count,
            requirements=requirements,
            notes=notes
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to generate party plan: {str(e)}"}), 500


@app.route("/api/planners/jewelry", methods=["POST"])
def plan_jewelry():
    try:
        # Check if multipart or JSON
        if request.content_type and "multipart/form-data" in request.content_type:
            budget = float(request.form.get("budget", 0))
            currency = request.form.get("currency", "$")
            occasion = request.form.get("occasion", "Cocktail")
            style = request.form.get("style", "Contemporary")
            material = request.form.get("material", "Yellow Gold")
            notes = request.form.get("notes", "")
            
            image_path = None
            if "outfit_image" in request.files:
                file = request.files["outfit_image"]
                if file and file.filename:
                    ext = file.filename.rsplit(".", 1)[-1].lower()
                    if ext in Config.ALLOWED_EXTENSIONS:
                        safe_name = f"outfit_{uuid.uuid4().hex[:10]}.{ext}"
                        save_dest = Config.UPLOAD_FOLDER / safe_name
                        file.save(str(save_dest))
                        image_path = str(save_dest)
        else:
            data = request.get_json() or {}
            budget = float(data.get("budget", 0))
            currency = data.get("currency", "$")
            occasion = data.get("occasion", "Cocktail")
            style = data.get("style", "Contemporary")
            material = data.get("material", "Yellow Gold")
            notes = data.get("notes", "")
            image_path = None

        if budget <= 0:
            return jsonify({"error": "Budget must be greater than 0"}), 400

        result = gemini_service.plan_jewelry(
            budget=budget,
            currency=currency,
            occasion=occasion,
            style=style,
            material=material,
            image_path=image_path,
            notes=notes
        )

        if image_path:
            result["uploaded_image_url"] = f"/uploads/{Path(image_path).name}"

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to generate jewelry plan: {str(e)}"}), 500


# -------------------------------------------------------------
# Plan CRUD & State Management
# -------------------------------------------------------------
@app.route("/api/plans", methods=["GET"])
def get_plans():
    try:
        planner_type = request.args.get("type")
        query = db_session.query(Plan)
        if planner_type:
            query = query.filter(Plan.planner_type == planner_type)

        plans = query.order_by(Plan.created_at.desc()).all()
        return jsonify([p.to_dict() for p in plans])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/plans/<int:plan_id>", methods=["GET"])
def get_plan(plan_id):
    plan = db_session.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan.to_dict())


@app.route("/api/plans/save", methods=["POST"])
def save_plan():
    try:
        data = request.get_json() or {}
        title = data.get("title", "My Budget Plan")
        planner_type = data.get("planner_type", "home")
        currency = data.get("currency", "$")
        total_budget = float(data.get("total_budget", 0))
        estimated_spending = float(data.get("estimated_spending", 0))
        remaining_budget = float(data.get("remaining_budget", 0))
        user_inputs = json.dumps(data.get("user_inputs", {}))
        ai_summary = data.get("ai_summary", "")
        image_path = data.get("image_path")

        plan = Plan(
            title=title,
            planner_type=planner_type,
            currency=currency,
            total_budget=total_budget,
            estimated_spending=estimated_spending,
            remaining_budget=remaining_budget,
            user_inputs=user_inputs,
            ai_summary=ai_summary,
            image_path=image_path
        )
        db_session.add(plan)
        db_session.flush()

        # Add recommendation items
        for rec in data.get("recommendations", []):
            item = RecommendationItem(
                plan_id=plan.id,
                name=rec.get("name", "Product"),
                category=rec.get("category", "General"),
                estimated_price=float(rec.get("estimated_price", 0)),
                quantity=int(rec.get("quantity", 1)),
                why_recommended=rec.get("why_recommended", ""),
                platform_name=rec.get("platform_name", "Online"),
                shopping_link=rec.get("shopping_link", "#"),
                is_selected=bool(rec.get("is_selected", True))
            )
            db_session.add(item)

        # Add budget allocations
        for alloc in data.get("allocations", []):
            ba = BudgetAllocation(
                plan_id=plan.id,
                category_name=alloc.get("category_name", "Category"),
                allocated_amount=float(alloc.get("allocated_amount", 0)),
                spent_amount=float(alloc.get("spent_amount", 0)),
                percentage=float(alloc.get("percentage", 0))
            )
            db_session.add(ba)

        db_session.commit()
        return jsonify({"success": True, "plan": plan.to_dict()}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": f"Failed to save plan: {str(e)}"}), 500


@app.route("/api/plans/<int:plan_id>", methods=["DELETE"])
def delete_plan(plan_id):
    plan = db_session.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    try:
        db_session.delete(plan)
        db_session.commit()
        return jsonify({"success": True, "message": "Plan deleted successfully"})
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/plans/<int:plan_id>/items/<int:item_id>", methods=["PATCH"])
def toggle_item(plan_id, item_id):
    plan = db_session.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return jsonify({"error": "Plan not found"}), 404

    item = db_session.query(RecommendationItem).filter(
        RecommendationItem.id == item_id,
        RecommendationItem.plan_id == plan_id
    ).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}
    if "is_selected" in data:
        item.is_selected = bool(data["is_selected"])
    if "quantity" in data:
        item.quantity = max(1, int(data["quantity"]))

    # Recalculate spending and remaining budget
    total_spent = sum(
        (rec.estimated_price * rec.quantity)
        for rec in plan.recommendations
        if rec.is_selected
    )
    plan.estimated_spending = round(total_spent, 2)
    plan.remaining_budget = round(max(0.0, plan.total_budget - total_spent), 2)

    db_session.commit()
    return jsonify({
        "success": True,
        "item": item.to_dict(),
        "estimated_spending": plan.estimated_spending,
        "remaining_budget": plan.remaining_budget
    })


# -------------------------------------------------------------
# Dashboard Statistics
# -------------------------------------------------------------
@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    plans = db_session.query(Plan).all()
    
    total_budget_sum = sum(p.total_budget for p in plans)
    total_spending_sum = sum(p.estimated_spending for p in plans)
    total_remaining_sum = sum(p.remaining_budget for p in plans)
    
    total_recs = db_session.query(RecommendationItem).count()

    type_counts = {
        "home": 0,
        "party": 0,
        "jewelry": 0
    }
    for p in plans:
        if p.planner_type in type_counts:
            type_counts[p.planner_type] += 1

    recent_plans = (
        db_session.query(Plan)
        .order_by(Plan.created_at.desc())
        .limit(6)
        .all()
    )

    return jsonify({
        "total_plans": len(plans),
        "total_budget": round(total_budget_sum, 2),
        "total_spending": round(total_spending_sum, 2),
        "total_remaining": round(total_remaining_sum, 2),
        "total_recommendations": total_recs,
        "type_counts": type_counts,
        "recent_plans": [p.to_dict() for p in recent_plans]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
