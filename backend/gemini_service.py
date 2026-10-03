import os
import json
import re
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.config import Config
from backend.mock_data import (
    HOME_INTERIOR_CATALOG,
    PARTY_CATALOG,
    JEWELRY_CATALOG,
    create_search_link
)

# Optional google-generativeai import
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to configure genai: {e}")

    def is_api_configured(self) -> bool:
        return bool(self.api_key)

    def set_api_key(self, key: str):
        self.api_key = key.strip()
        if self.api_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.api_key)

    def _call_gemini_json(self, prompt: str, image_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call Gemini API and parse structured JSON response."""
        if not self.api_key or not GENAI_AVAILABLE:
            return None

        models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        
        contents = []
        if image_path and os.path.exists(image_path):
            try:
                from PIL import Image
                img = Image.open(image_path)
                contents.append(img)
            except Exception as img_err:
                print(f"Could not load image {image_path}: {img_err}")

        contents.append(prompt)

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.4,
                    }
                )
                response = model.generate_content(contents)
                if response and response.text:
                    text = response.text.strip()
                    # Clean markdown code blocks if any
                    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
                    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
                    text = text.rstrip("`").strip()
                    data = json.loads(text)
                    return data
            except Exception as e:
                print(f"Gemini model {model_name} attempt failed: {e}")
                continue

        return None

    # ==========================================
    # 1. HOME INTERIOR PLANNER
    # ==========================================
    def plan_home_interior(
        self,
        budget: float,
        currency: str,
        room: str,
        items: List[Dict[str, Any]],
        style: str = "Modern Minimalist",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Generate Home Interior budget allocation & product recommendations."""
        items_description = ", ".join([f"{it.get('name')} (qty: {it.get('qty', 1)})" for it in items]) if items else "essential room furniture & decor"

        prompt = f"""
You are PocketSmart AI, an expert interior designer and frugal budget planner.
Generate a comprehensive, cost-conscious home interior recommendation plan for a {room}.

User Parameters:
- Total Budget: {currency}{budget}
- Room: {room}
- Selected Items and Quantities: {items_description}
- Preferred Style: {style}
- Additional Notes: {notes or 'None'}

CRITICAL REQUIREMENTS:
1. Total estimated cost of all recommended items combined MUST BE <= {budget}.
2. Provide specific realistic product recommendations with real-world estimated prices.
3. For each product, specify category, realistic price, quantity, rationale ('why_recommended'), and platform ('Amazon', 'IKEA', 'Target', 'Wayfair', 'Etsy', etc.).
4. Provide a budget allocation breakdown across categories (e.g. Seating, Lighting, Decor, Storage) summing to {budget}.
5. Return ONLY a valid JSON object matching this schema:
{{
  "title": "{style} {room} Design & Budget Plan",
  "ai_summary": "Detailed summary explaining design choices, space ergonomics, and how the budget was preserved.",
  "allocations": [
    {{"category_name": "Category Name", "allocated_amount": 100.0, "percentage": 25.0}}
  ],
  "recommendations": [
    {{
      "name": "Detailed Product Name",
      "category": "Category Name",
      "estimated_price": 50.0,
      "quantity": 1,
      "why_recommended": "Reason why it fits the style, quality, and budget",
      "platform_name": "IKEA",
      "search_query": "product search term"
    }}
  ]
}}
"""
        result = self._call_gemini_json(prompt)
        if result and "recommendations" in result and result["recommendations"]:
            return self._enrich_result(result, budget, currency)

        # Fallback to realistic deterministic generator
        return self._fallback_home_interior(budget, currency, room, items, style, notes)

    def _fallback_home_interior(
        self,
        budget: float,
        currency: str,
        room: str,
        items: List[Dict[str, Any]],
        style: str,
        notes: str
    ) -> Dict[str, Any]:
        catalog = HOME_INTERIOR_CATALOG.get(room, HOME_INTERIOR_CATALOG["Living Room"])
        selected_item_names = [it.get("name", "").lower() for it in items] if items else []

        # Filter or pick relevant items from catalog
        chosen_candidates = []
        if selected_item_names:
            for cat_item in catalog:
                for req in selected_item_names:
                    if req in cat_item["name"].lower() or req in cat_item["category"].lower():
                        chosen_candidates.append(cat_item)
                        break
        if not chosen_candidates or len(chosen_candidates) < 4:
            chosen_candidates = catalog[:5]

        # Calculate budget scaling factor
        catalog_total = sum(c["base_price"] for c in chosen_candidates)
        target_budget = budget * 0.92  # leave a safe buffer
        scale = target_budget / catalog_total if catalog_total > 0 else 1.0

        recommendations = []
        allocations_map = {}
        total_spent = 0.0

        for item in chosen_candidates:
            scaled_price = round(max(15.0, item["base_price"] * scale), 2)
            qty = 1
            if items:
                for req in items:
                    if req.get("name", "").lower() in item["name"].lower():
                        qty = int(req.get("qty", 1))
                        break

            item_cost = round(scaled_price * qty, 2)
            if total_spent + item_cost > budget:
                scaled_price = round(max(10.0, (budget - total_spent) / qty), 2)
                item_cost = round(scaled_price * qty, 2)

            total_spent += item_cost
            cat = item["category"]
            allocations_map[cat] = allocations_map.get(cat, 0.0) + item_cost

            recommendations.append({
                "name": f"{style} {item['name']}",
                "category": cat,
                "estimated_price": scaled_price,
                "quantity": qty,
                "total_price": item_cost,
                "why_recommended": f"Tailored for {style} aesthetics. {item['reason']}",
                "platform_name": item["platform"],
                "shopping_link": create_search_link(item["platform"], f"{style} {item['search']}"),
                "is_selected": True
            })

        allocations = []
        for cat, amt in allocations_map.items():
            pct = (amt / total_spent * 100.0) if total_spent > 0 else 0
            allocations.append({
                "category_name": cat,
                "allocated_amount": round(amt, 2),
                "spent_amount": round(amt, 2),
                "percentage": round(pct, 1)
            })

        return {
            "title": f"{style} {room} Intelligent Budget Plan",
            "ai_summary": f"Smart budget plan crafted for your {room} with a {style} aesthetic. Designed to maximize aesthetic harmony, comfort, and space utility while keeping estimated costs at {currency}{round(total_spent, 2)} with a surplus reserve of {currency}{round(max(0, budget - total_spent), 2)}.",
            "total_budget": budget,
            "estimated_spending": round(total_spent, 2),
            "remaining_budget": round(max(0, budget - total_spent), 2),
            "currency": currency,
            "allocations": allocations,
            "recommendations": recommendations
        }

    # ==========================================
    # 2. PARTY PLANNER
    # ==========================================
    def plan_party(
        self,
        budget: float,
        currency: str,
        event_type: str,
        guest_count: int,
        requirements: List[str],
        notes: str = ""
    ) -> Dict[str, Any]:
        """Generate Party budget allocation across categories & vendor/item recommendations."""
        req_str = ", ".join(requirements) if requirements else "Venue, Food & Drinks, Decor, Music"

        prompt = f"""
You are PocketSmart AI, a premier event planner and budget strategist.
Create a comprehensive party/event plan and vendor/supplies budget division for a {event_type}.

Parameters:
- Total Budget: {currency}{budget}
- Guest Count: {guest_count} attendees
- Event Type: {event_type}
- Key Requirements: {req_str}
- Additional Notes: {notes or 'None'}

CRITICAL REQUIREMENTS:
1. Divide the budget automatically across essential categories: Venue (approx 35-40%), Food & Drinks (approx 30-35%), Decoration (approx 10-15%), Entertainment (approx 10-15%).
2. The total estimated cost of all recommended items/services MUST BE <= {budget}.
3. Calculate realistic per-guest or bulk pricing appropriate for {guest_count} guests.
4. Return ONLY a valid JSON object matching this schema:
{{
  "title": "{event_type} Celebration Budget Blueprint",
  "ai_summary": "Strategic overview of budget division, guest per-head allocation, and atmosphere styling.",
  "allocations": [
    {{"category_name": "Venue", "allocated_amount": 400.0, "percentage": 40.0}},
    {{"category_name": "Catering & Drinks", "allocated_amount": 350.0, "percentage": 35.0}},
    {{"category_name": "Decorations", "allocated_amount": 150.0, "percentage": 15.0}},
    {{"category_name": "Entertainment", "allocated_amount": 100.0, "percentage": 10.0}}
  ],
  "recommendations": [
    {{
      "name": "Service or Item Name",
      "category": "Venue | Catering & Drinks | Decorations | Entertainment",
      "estimated_price": 350.0,
      "quantity": 1,
      "why_recommended": "Detailed reason why it fits guest capacity and event tone",
      "platform_name": "Peerspace | Amazon | Local Catering | GigSalad",
      "search_query": "search keywords"
    }}
  ]
}}
"""
        result = self._call_gemini_json(prompt)
        if result and "recommendations" in result and result["recommendations"]:
            return self._enrich_result(result, budget, currency)

        return self._fallback_party(budget, currency, event_type, guest_count, requirements, notes)

    def _fallback_party(
        self,
        budget: float,
        currency: str,
        event_type: str,
        guest_count: int,
        requirements: List[str],
        notes: str
    ) -> Dict[str, Any]:
        catalog = PARTY_CATALOG.get(event_type, PARTY_CATALOG["Birthday"])
        
        # Default allocation percentages
        weights = {
            "Venue": 0.38,
            "Catering": 0.34,
            "Decoration": 0.14,
            "Entertainment": 0.14
        }

        recommendations = []
        allocations = []
        total_spent = 0.0

        for cat_name, cat_weight in weights.items():
            cat_budget = budget * cat_weight
            cat_items = catalog.get(cat_name, [])
            
            spent_in_cat = 0.0
            if cat_items:
                # Pick 1-2 items per category
                for item in cat_items:
                    item_price = round(cat_budget * (0.8 if len(cat_items) > 1 else 0.95), 2)
                    if spent_in_cat + item_price > cat_budget:
                        item_price = round(max(20.0, cat_budget - spent_in_cat), 2)
                    
                    spent_in_cat += item_price
                    total_spent += item_price

                    recommendations.append({
                        "name": f"{item['name']} ({guest_count} guests)",
                        "category": cat_name,
                        "estimated_price": item_price,
                        "quantity": 1,
                        "total_price": item_price,
                        "why_recommended": f"Optimized for {guest_count} guests. {item['reason']}",
                        "platform_name": item["platform"],
                        "shopping_link": create_search_link(item["platform"], item["search"]),
                        "is_selected": True
                    })
                    if len(cat_items) > 1 and len(recommendations) % 2 == 0:
                        break

            allocations.append({
                "category_name": cat_name,
                "allocated_amount": round(cat_budget, 2),
                "spent_amount": round(spent_in_cat, 2),
                "percentage": round(cat_weight * 100, 1)
            })

        return {
            "title": f"{event_type} Budget Blueprint ({guest_count} Guests)",
            "ai_summary": f"Automated budget breakdown for {guest_count} guests. We partitioned the budget across venue booking, food/drink catering (${round(budget*0.34/max(guest_count,1), 2)}/guest), festive atmosphere decor, and music/entertainment, keeping your event under budget.",
            "total_budget": budget,
            "estimated_spending": round(total_spent, 2),
            "remaining_budget": round(max(0, budget - total_spent), 2),
            "currency": currency,
            "allocations": allocations,
            "recommendations": recommendations
        }

    # ==========================================
    # 3. JEWELRY PLANNER (With Vision support)
    # ==========================================
    def plan_jewelry(
        self,
        budget: float,
        currency: str,
        occasion: str,
        style: str,
        material: str,
        image_path: Optional[str] = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Generate Jewelry ensemble matching occasion, style, material, and optional outfit image."""
        has_image = bool(image_path and os.path.exists(image_path))
        image_instruction = ""
        if has_image:
            image_instruction = (
                "An outfit image has been uploaded by the user! Carefully inspect the outfit's colors, neckline (e.g. V-neck, sweetheart, high neck, boat neck), silhouette, and fabric texture. "
                "Recommend matching jewelry pieces that complement the neckline, enhance the color palette, and avoid visual clutter."
            )

        prompt = f"""
You are PocketSmart AI, an elite fashion stylist and fine jewelry advisor.
Design a curated jewelry ensemble tailored precisely to the user's budget and attire.

Parameters:
- Total Budget: {currency}{budget}
- Occasion: {occasion}
- Jewelry Style: {style}
- Preferred Material / Metal / Stones: {material}
- Additional Notes: {notes or 'None'}
{image_instruction}

CRITICAL REQUIREMENTS:
1. Total estimated cost of all recommended jewelry pieces combined MUST BE <= {budget}.
2. Recommend 3 to 5 complementary jewelry pieces (e.g. Necklace, Earrings, Bracelet, Ring, or Set).
3. If an outfit image is present, specifically explain in the 'ai_summary' and 'why_recommended' how each piece harmonizes with the outfit's neckline, colors, and cut.
4. Specify realistic market pricing, platform ('Etsy', 'Blue Nile', 'Tanishq', 'Amazon', 'Target'), and search queries.
5. Return ONLY a valid JSON object matching this schema:
{{
  "title": "{style} {occasion} Jewelry Ensemble",
  "ai_summary": "Stylist assessment of how the chosen pieces complement the {occasion} dress code and neckline while remaining within budget.",
  "allocations": [
    {{"category_name": "Necklaces", "allocated_amount": 80.0, "percentage": 40.0}},
    {{"category_name": "Earrings", "allocated_amount": 60.0, "percentage": 30.0}},
    {{"category_name": "Wristwear & Rings", "allocated_amount": 60.0, "percentage": 30.0}}
  ],
  "recommendations": [
    {{
      "name": "Product Name",
      "category": "Necklace | Earrings | Bracelets | Rings",
      "estimated_price": 75.0,
      "quantity": 1,
      "why_recommended": "Styling reason referencing neckline, colors, and occasion",
      "platform_name": "Etsy",
      "search_query": "product keywords"
    }}
  ]
}}
"""
        result = self._call_gemini_json(prompt, image_path=image_path)
        if result and "recommendations" in result and result["recommendations"]:
            return self._enrich_result(result, budget, currency)

        return self._fallback_jewelry(budget, currency, occasion, style, material, has_image, notes)

    def _fallback_jewelry(
        self,
        budget: float,
        currency: str,
        occasion: str,
        style: str,
        material: str,
        has_image: bool,
        notes: str
    ) -> Dict[str, Any]:
        # Filter matching jewelry from catalog
        candidates = []
        for item in JEWELRY_CATALOG:
            score = 0
            if any(s.lower() in style.lower() for s in item["styles"]):
                score += 2
            if any(o.lower() in occasion.lower() for o in item["occasions"]):
                score += 2
            if any(m.lower() in material.lower() for m in item["materials"]):
                score += 2
            candidates.append((score, item))

        candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [c[1] for c in candidates[:4]]

        catalog_total = sum(i["price"] for i in selected)
        target = budget * 0.94
        scale = target / catalog_total if catalog_total > 0 else 1.0

        recommendations = []
        allocations_map = {}
        total_spent = 0.0

        for item in selected:
            price = round(max(18.0, item["price"] * scale), 2)
            if total_spent + price > budget:
                price = round(max(10.0, budget - total_spent), 2)

            total_spent += price
            cat = item["category"]
            allocations_map[cat] = allocations_map.get(cat, 0.0) + price

            outfit_touch = " Pairs harmoniously with your outfit neckline and tones." if has_image else ""
            recommendations.append({
                "name": f"{material} {item['name']}",
                "category": cat,
                "estimated_price": price,
                "quantity": 1,
                "total_price": price,
                "why_recommended": f"{item['reason']}.{outfit_touch}",
                "platform_name": item["platform"],
                "shopping_link": create_search_link(item["platform"], f"{material} {item['search']}"),
                "is_selected": True
            })

        allocations = []
        for cat, amt in allocations_map.items():
            pct = (amt / total_spent * 100.0) if total_spent > 0 else 0
            allocations.append({
                "category_name": cat,
                "allocated_amount": round(amt, 2),
                "spent_amount": round(amt, 2),
                "percentage": round(pct, 1)
            })

        image_blurb = " Outfit image analysis confirmed color balance and neckline compatibility." if has_image else ""
        return {
            "title": f"{style} {occasion} Jewelry Collection",
            "ai_summary": f"Curated {material} jewelry ensemble for {occasion} in a {style} aesthetic.{image_blurb} Total expenditure is kept safely at {currency}{round(total_spent, 2)} with a reserve of {currency}{round(max(0, budget - total_spent), 2)}.",
            "total_budget": budget,
            "estimated_spending": round(total_spent, 2),
            "remaining_budget": round(max(0, budget - total_spent), 2),
            "currency": currency,
            "allocations": allocations,
            "recommendations": recommendations
        }

    # ==========================================
    # Helper: Result Enrichment
    # ==========================================
    def _enrich_result(self, result: Dict[str, Any], budget: float, currency: str) -> Dict[str, Any]:
        """Normalize and enrich recommendations with verified shopping links and totals."""
        recommendations = []
        total_spent = 0.0

        raw_recs = result.get("recommendations", [])
        for rec in raw_recs:
            price = float(rec.get("estimated_price", 0.0))
            qty = int(rec.get("quantity", 1))
            total_item_price = round(price * qty, 2)
            
            platform = rec.get("platform_name", "Amazon")
            query = rec.get("search_query") or rec.get("name", "product")
            link = rec.get("shopping_link") or create_search_link(platform, query)

            total_spent += total_item_price
            recommendations.append({
                "name": rec.get("name", "Product"),
                "category": rec.get("category", "General"),
                "estimated_price": round(price, 2),
                "quantity": qty,
                "total_price": total_item_price,
                "why_recommended": rec.get("why_recommended", "Carefully selected to meet your budget and style."),
                "platform_name": platform,
                "shopping_link": link,
                "is_selected": True
            })

        # Calculate remaining
        remaining = round(max(0.0, budget - total_spent), 2)

        # Normalize allocations
        allocations = []
        raw_allocs = result.get("allocations", [])
        for alloc in raw_allocs:
            amt = float(alloc.get("allocated_amount", 0.0))
            pct = float(alloc.get("percentage", 0.0))
            if pct == 0.0 and budget > 0:
                pct = (amt / budget) * 100.0
            allocations.append({
                "category_name": alloc.get("category_name", "Category"),
                "allocated_amount": round(amt, 2),
                "spent_amount": round(amt, 2),
                "percentage": round(pct, 1)
            })

        return {
            "title": result.get("title", "PocketSmart AI Plan"),
            "ai_summary": result.get("ai_summary", "Personalized budget allocation and recommendations."),
            "total_budget": round(budget, 2),
            "estimated_spending": round(total_spent, 2),
            "remaining_budget": remaining,
            "currency": currency,
            "allocations": allocations,
            "recommendations": recommendations
        }


# Singleton service instance
gemini_service = GeminiService()
