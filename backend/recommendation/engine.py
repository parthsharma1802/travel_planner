"""
SmartTrip Recommendation Engine
================================
Candidate → Scoring → Ranking pipeline.
Ranks destinations/attractions/stops from the Tourism Knowledge Layer based on
the user's structured trip context. Extensible for future hotel/booking/FAISS sources.
"""

import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("smart_travel.recommendation_engine")

# ---------------------------------------------------------------------------
# Experience → category keyword mapping (dataset-aligned)
# ---------------------------------------------------------------------------
EXPERIENCE_CATEGORY_MAP: Dict[str, List[str]] = {
    "nature & scenic places": ["park", "national park", "nature preserve", "lake", "waterfall",
                                "viewpoint", "beach", "island", "river", "hill", "garden", "forest"],
    "history, heritage & culture": ["historical", "fortress", "fort", "museum", "heritage",
                                     "monument", "palace", "archaeological", "ruins"],
    "spiritual & pilgrimage":      ["hindu temple", "temple", "mosque", "church", "gurudwara",
                                     "buddhist temple", "jain temple", "pilgrimage", "shrine",
                                     "dargah", "monastery", "ghat"],
    "food & local experiences":    ["food", "market", "local", "bazaar", "cuisine", "restaurant"],
    "adventure & outdoor activities": ["adventure", "trek", "hiking", "rafting", "camping",
                                        "national park", "wildlife", "safari"],
    "beaches & relaxation":        ["beach", "island", "resort", "coastal", "sea"],
    "wildlife & national parks":   ["national park", "wildlife", "zoo", "sanctuary",
                                     "nature preserve", "tiger reserve", "bird"],
    "shopping & local markets":    ["market", "bazaar", "shopping", "handicraft"],
    "festivals & local experiences": ["festival", "fair", "cultural", "local"],
}

# Traveler type → preferred category signals
TRAVELER_CATEGORY_MAP: Dict[str, List[str]] = {
    "family":       ["park", "garden", "zoo", "museum", "national park", "historical", "lake"],
    "friends":      ["beach", "adventure", "island", "market", "historical", "national park"],
    "couple":       ["lake", "beach", "garden", "fort", "palace", "viewpoint", "island"],
    "solo":         ["historical", "museum", "national park", "heritage", "trek"],
    "business":     ["tourist attraction", "historical landmark"],
    "spiritual":    ["hindu temple", "temple", "pilgrimage", "shrine", "monastery",
                     "buddhist temple", "jain temple", "gurudwara", "dargah", "ghat"],
    "group":        ["tourist attraction", "national park", "beach", "historical"],
}

# Budget tier → rough scoring modifier
BUDGET_TIER_SCORE: Dict[str, float] = {
    "budget":   0.0,
    "mid":      0.1,
    "luxury":   0.2,
    "unknown":  0.0,
}

# Road-trip major intermediate cities (for route-aware stops on long legs)
# key = (origin_state_hint, destination_state_hint) → list of useful stops
ROUTE_INTERMEDIATE_HINTS: Dict[tuple, List[str]] = {
    ("delhi", "goa"):       ["Udaipur", "Ahmedabad", "Mumbai", "Pune"],
    ("delhi", "mumbai"):    ["Jaipur", "Udaipur", "Ahmedabad", "Surat"],
    ("delhi", "bangalore"): ["Agra", "Bhopal", "Hyderabad"],
    ("delhi", "chennai"):   ["Agra", "Bhopal", "Nagpur", "Hyderabad"],
    ("mumbai", "goa"):      ["Pune", "Kolhapur"],
    ("bangalore", "goa"):   ["Hubli", "Gokarna"],
    ("delhi", "kolkata"):   ["Agra", "Varanasi", "Patna"],
    ("delhi", "varanasi"):  ["Agra", "Allahabad"],
    ("mumbai", "bangalore"):["Pune", "Belgaum"],
}


def _parse_budget_tier(budget_text: Optional[str]) -> str:
    """Convert free-text budget to internal tier."""
    if not budget_text:
        return "unknown"
    t = budget_text.lower().replace(",", "").replace(" ", "")
    # Extract numeric value
    import re
    nums = re.findall(r"[\d.]+", t)
    if not nums:
        return "unknown"
    val = float(nums[0])
    # Normalize lakhs/k
    if "lakh" in t or "lac" in t:
        val *= 100000
    elif "k" in t:
        val *= 1000
    # Per person per day rough guess:
    # <10k total → budget, 10k-50k → mid, >50k → luxury
    if val < 10000:
        return "budget"
    elif val < 75000:
        return "mid"
    else:
        return "luxury"


def _category_experience_score(category: str, experiences: List[str]) -> float:
    """Score how well a destination's category matches user experience preferences."""
    if not experiences or not category:
        return 0.0
    cat_lower = category.lower()
    score = 0.0
    for exp in experiences:
        keywords = EXPERIENCE_CATEGORY_MAP.get(exp.lower(), [])
        if any(kw in cat_lower for kw in keywords):
            score += 1.0
    # Normalize by number of preferences
    return min(score / max(len(experiences), 1), 1.0)


def _category_traveler_score(category: str, traveler_type: Optional[str]) -> float:
    """Score how well a category suits the traveler type."""
    if not traveler_type or not category:
        return 0.0
    cat_lower = category.lower()
    # Detect traveler type keyword
    t_lower = traveler_type.lower()
    t_key = "unknown"
    for key in TRAVELER_CATEGORY_MAP:
        if key in t_lower:
            t_key = key
            break
    if t_key == "unknown":
        return 0.0
    keywords = TRAVELER_CATEGORY_MAP.get(t_key, [])
    return 1.0 if any(kw in cat_lower for kw in keywords) else 0.0


def _quality_score(rating: Optional[float], reviews: Optional[float]) -> float:
    """Normalize rating (0-5) to 0-1 score, boosted by review volume."""
    base = (rating / 5.0) if rating else 0.4  # default middling score when no rating
    # Slight boost for high review volume (>1000 reviews)
    review_boost = min((reviews or 0) / 5000.0, 0.15) if reviews else 0.0
    return min(base + review_boost, 1.0)


def _route_fit_score(
    candidate: Dict[str, Any],
    destination: Optional[str],
    intermediate_stops: Optional[List[str]] = None,
) -> float:
    """
    Score how well this place fits the destination/route.
    Simple heuristic: name/state/district match to destination or known intermediate stops.
    """
    if not destination:
        return 0.5  # neutral when no destination context

    dest_lower = destination.lower()
    name_lower = (candidate.get("destination_name") or "").lower()
    state_lower = (candidate.get("state") or "").lower()
    district_lower = (candidate.get("city_district") or "").lower()

    # Direct destination match → high score
    if dest_lower in name_lower or dest_lower in state_lower or dest_lower in district_lower:
        return 1.0

    # Check intermediate stops
    if intermediate_stops:
        for stop in intermediate_stops:
            s = stop.lower()
            if s in name_lower or s in state_lower or s in district_lower:
                return 0.7

    return 0.3  # not directly on route → penalize slightly


def _weather_fit_score(
    category: str,
    weather_condition: Optional[str],
    experiences: List[str],
) -> float:
    """Adjust score based on weather suitability. Returns 0.0 neutral if no data."""
    if not weather_condition:
        return 0.0  # no data → no adjustment
    cat_lower = category.lower()
    cond_lower = weather_condition.lower()
    outdoor_cats = ["beach", "park", "national park", "trek", "adventure", "waterfall", "island"]
    is_outdoor = any(kw in cat_lower for kw in outdoor_cats)
    is_bad_weather = any(w in cond_lower for w in ["rain", "storm", "thunder", "heavy", "flood"])
    is_hot = any(w in cond_lower for w in ["hot", "heat", "scorching"])
    is_pleasant = any(w in cond_lower for w in ["clear", "sunny", "pleasant", "cool", "mild"])

    if is_outdoor and is_bad_weather:
        return -0.2
    if is_outdoor and is_pleasant:
        return 0.15
    if is_outdoor and is_hot and "beach" in cat_lower:
        return 0.05  # beach is okay even in heat
    return 0.0


def score_candidate(
    candidate: Dict[str, Any],
    trip_context: Dict[str, Any],
    destination: Optional[str],
    intermediate_stops: Optional[List[str]],
    weather_condition: Optional[str],
) -> Dict[str, Any]:
    """
    Compute an overall score for one candidate destination/attraction.
    Returns the candidate dict enriched with score and reasoning metadata.
    """
    category = candidate.get("category") or "Tourist Attraction"
    rating = candidate.get("rating")
    reviews = candidate.get("reviews_count")
    experiences = trip_context.get("experiences") or []
    traveler_type = trip_context.get("travelers") or trip_context.get("traveler_type")
    budget_text = trip_context.get("budget")

    # --- User Exclusions (Hard Constraints §4, §21) ---
    exclusions = [str(e).lower().strip() for e in (trip_context.get("exclusions") or []) if e]
    c_name = (candidate.get("destination_name") or "").lower()
    c_state = (candidate.get("state") or "").lower()
    c_dist = (candidate.get("city_district") or "").lower()
    c_cat = (category or "").lower()

    for excl in exclusions:
        if excl in c_name or excl in c_state or excl in c_dist or excl in c_cat:
            return {
                **candidate,
                "_score": -1.0,
                "_reasons": [f"Excluded by user constraint: {excl}"],
                "_priority": "excluded",
                "_exp_score": 0.0,
                "_route_score": 0.0,
                "_quality_score": 0.0,
                "_traveler_score": 0.0,
                "_weather_score": 0.0,
            }

    # --- Component scores (all 0.0–1.0 unless noted) ---
    exp_score    = _category_experience_score(category, experiences)        # preference match
    traveler_sc  = _category_traveler_score(category, traveler_type)        # traveler fit
    quality_sc   = _quality_score(rating, reviews)                          # quality signal
    route_sc     = _route_fit_score(candidate, destination, intermediate_stops)
    weather_sc   = _weather_fit_score(category, weather_condition, experiences)
    budget_tier  = _parse_budget_tier(budget_text)
    budget_bonus = BUDGET_TIER_SCORE.get(budget_tier, 0.0)

    # Weighted composite
    overall = (
        exp_score    * 2.5 +   # strongest signal — what user wants to do
        route_sc     * 2.0 +   # must be on/near route
        quality_sc   * 1.5 +   # quality matters
        traveler_sc  * 1.5 +   # fits the group
        weather_sc   * 1.0 +   # weather bonus/penalty
        budget_bonus * 0.5     # minor boost for matching budget tier
    ) / 9.0  # normalize to ~0-1

    reasons = []

    # Visual Landmark Anchor bonus
    anchor_landmark = trip_context.get("anchor_landmark")
    anchor_city = trip_context.get("anchor_city") or trip_context.get("destination")
    anchor_boost = 0.0
    if anchor_landmark:
        c_name = (candidate.get("destination_name") or "").lower()
        if anchor_landmark.lower() in c_name or c_name in anchor_landmark.lower():
            anchor_boost = 0.35
            reasons.append(f"Visual Anchor: matches recognized photo ({anchor_landmark})")
        elif anchor_city and (
            anchor_city.lower() in (candidate.get("city_district") or "").lower()
            or anchor_city.lower() in (candidate.get("state") or "").lower()
        ):
            anchor_boost = 0.15
            reasons.append(f"Located near {anchor_landmark} in {anchor_city}")

    overall = min(overall + anchor_boost, 1.0)

    # Build reason list for explainability
    if exp_score > 0.5:
        reasons.append("strong match for your experience preferences")
    elif exp_score > 0:
        reasons.append("partial match for your interests")
    if route_sc >= 1.0:
        reasons.append(f"directly at your destination")
    elif route_sc >= 0.7:
        reasons.append("useful stop along the route")
    elif route_sc < 0.4:
        reasons.append("out of route — significant detour")
    if quality_sc >= 0.85:
        reasons.append("highly rated by visitors")
    elif quality_sc >= 0.7:
        reasons.append("well rated")
    if traveler_sc > 0:
        reasons.append(f"suitable for {traveler_type}")
    if weather_sc < 0:
        reasons.append("weather may not be ideal for outdoor activity here")
    elif weather_sc > 0.1:
        reasons.append("good weather conditions for this type of place")

    # Priority classification
    if overall >= 0.65:
        priority = "high"
    elif overall >= 0.4:
        priority = "medium"
    else:
        priority = "optional"

    return {
        **candidate,
        "_score": round(overall, 4),
        "_reasons": reasons,
        "_priority": priority,
        "_exp_score": round(exp_score, 3),
        "_route_score": round(route_sc, 3),
        "_quality_score": round(quality_sc, 3),
        "_traveler_score": round(traveler_sc, 3),
        "_weather_score": round(weather_sc, 3),
    }


def _get_intermediate_stops(origin: Optional[str], destination: Optional[str]) -> List[str]:
    """Look up known useful intermediate cities for a long road trip leg."""
    if not origin or not destination:
        return []
    o = origin.lower().strip()
    d = destination.lower().strip()
    # Try exact key match
    key = (o, d)
    if key in ROUTE_INTERMEDIATE_HINTS:
        return ROUTE_INTERMEDIATE_HINTS[key]
    # Try partial match
    for (ok, dk), stops in ROUTE_INTERMEDIATE_HINTS.items():
        if ok in o and dk in d:
            return stops
    return []


def classify_stop_type(candidate: Dict[str, Any], destination: Optional[str]) -> str:
    """Classify a recommendation as primary_destination / stop / overnight_stop / optional_detour."""
    route_score = candidate.get("_route_score", 0.5)
    priority = candidate.get("_priority", "optional")
    dest_lower = (destination or "").lower()
    name_lower = (candidate.get("destination_name") or "").lower()
    state_lower = (candidate.get("state") or "").lower()

    if dest_lower and (dest_lower in name_lower or dest_lower in state_lower):
        return "primary_destination"
    if route_score >= 0.7 and priority == "high":
        return "worthwhile_stop"
    if route_score >= 0.7 and priority == "medium":
        return "overnight_stop"
    if route_score < 0.4 and priority == "optional":
        return "optional_detour"
    return "stop"


class RecommendationEngine:
    """
    Candidate → Scoring → Ranking pipeline.

    Usage:
        engine = RecommendationEngine()
        results = await engine.recommend(trip_context, weather_condition=...)
    """

    def __init__(self):
        from backend.services.tourism_service import tourism_service
        self._tourism = tourism_service

    def _build_search_queries(self, trip_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Derive search queries from trip context.
        Returns a list of {query, state, category, min_rating, limit} dicts.
        """
        queries = []
        destination = trip_context.get("destination")
        origin = trip_context.get("starting_point")
        experiences = trip_context.get("experiences") or []
        travelers = trip_context.get("travelers") or ""

        # --- Query 1: By destination state/name ---
        if destination:
            queries.append({
                "query": destination,
                "state": None,
                "category": None,
                "min_rating": None,
                "limit": 25,
                "label": "destination"
            })

        # --- Query 1b: Visual Landmark Anchor ---
        anchor_landmark = trip_context.get("anchor_landmark")
        anchor_city = trip_context.get("anchor_city") or trip_context.get("destination")
        anchor_state = trip_context.get("anchor_state")
        if anchor_landmark:
            queries.append({
                "query": anchor_landmark,
                "state": anchor_state,
                "category": None,
                "min_rating": None,
                "limit": 10,
                "label": "anchor_landmark"
            })
        if anchor_city and anchor_city != destination:
            queries.append({
                "query": anchor_city,
                "state": anchor_state,
                "category": None,
                "min_rating": None,
                "limit": 20,
                "label": "anchor_city"
            })

        # --- Query 2: By experience-mapped categories ---
        for exp in experiences[:3]:  # max 3 experiences to keep latency low
            cat_keywords = EXPERIENCE_CATEGORY_MAP.get(exp.lower(), [])
            if cat_keywords:
                # Use first relevant keyword as category search
                queries.append({
                    "query": cat_keywords[0],
                    "state": destination,
                    "category": None,
                    "min_rating": 4.0,
                    "limit": 15,
                    "label": f"experience:{exp}"
                })

        # --- Query 3: Spiritual trip special handling ---
        t_lower = travelers.lower()
        if "spiritual" in t_lower or "pilgrimage" in t_lower:
            queries.append({
                "query": "temple",
                "state": destination,
                "category": None,
                "min_rating": 4.0,
                "limit": 15,
                "label": "spiritual"
            })

        # --- Query 4: Intermediate stops ONLY for long self-drive road trips ---
        transport = (trip_context.get("transport") or "").lower()
        is_road_trip = any(k in transport for k in ["car", "drive", "bike", "road"])
        intermediate_stops = _get_intermediate_stops(origin, destination) if is_road_trip else []
        for stop in intermediate_stops[:3]:
            queries.append({
                "query": stop,
                "state": None,
                "category": None,
                "min_rating": None,
                "limit": 8,
                "label": f"route_stop:{stop}"
            })

        # Fallback: if no queries at all, do a general destination search
        if not queries and destination:
            queries.append({
                "query": destination,
                "state": None,
                "category": None,
                "min_rating": None,
                "limit": 20,
                "label": "fallback"
            })

        return queries

    def _retrieve_candidates(self, trip_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all search queries and deduplicate by destination_id."""
        queries = self._build_search_queries(trip_context)
        seen_ids = set()
        candidates = []

        for q in queries:
            try:
                results = self._tourism.search_destinations(
                    query=q.get("query"),
                    state=q.get("state"),
                    category=q.get("category"),
                    min_rating=q.get("min_rating"),
                    limit=q.get("limit", 15),
                )
                for r in results:
                    rid = r.get("destination_id")
                    if rid and rid not in seen_ids:
                        seen_ids.add(rid)
                        candidates.append(r)
            except Exception as e:
                logger.warning(f"Search query failed ({q.get('label')}): {e}")

        logger.info(f"Retrieved {len(candidates)} unique candidates from {len(queries)} queries")
        return candidates

    def recommend(
        self,
        trip_context: Dict[str, Any],
        weather_condition: Optional[str] = None,
        top_n: int = 12,
    ) -> Dict[str, Any]:
        """
        Main entry point. Returns ranked recommendations + metadata.

        Args:
            trip_context: Structured preferences dict from Groq
            weather_condition: Current weather description string (optional)
            top_n: Max number of results to return

        Returns:
            {
              "recommendations": [...],
              "intermediate_stops": [...],
              "context_summary": "...",
              "total_candidates": N
            }
        """
        destination = trip_context.get("destination")
        origin = trip_context.get("starting_point")
        experiences = trip_context.get("experiences") or []
        travelers = trip_context.get("travelers") or ""

        transport = (trip_context.get("transport") or "").lower()
        is_road_trip = any(k in transport for k in ["car", "drive", "bike", "road"])
        intermediate_stops = _get_intermediate_stops(origin, destination) if is_road_trip else []

        # 1. Retrieve candidates
        candidates = self._retrieve_candidates(trip_context)
        if not candidates:
            return {
                "recommendations": [],
                "intermediate_stops": intermediate_stops,
                "context_summary": "No matching destinations found in dataset.",
                "total_candidates": 0
            }

        # 2. Score all candidates
        scored = []
        for c in candidates:
            scored_c = score_candidate(
                candidate=c,
                trip_context=trip_context,
                destination=destination,
                intermediate_stops=intermediate_stops,
                weather_condition=weather_condition,
            )
            scored.append(scored_c)

        # 3. Sort by overall score descending (filter out excluded items)
        valid_scored = [c for c in scored if c.get("_score", 0) > 0.0]
        valid_scored.sort(key=lambda x: x["_score"], reverse=True)

        # 4. Build clean output (strip internal _ fields for return)
        recommendations = []
        for item in valid_scored[:top_n]:
            stop_type = classify_stop_type(item, destination)
            recommendations.append({
                "name": item.get("destination_name"),
                "state": item.get("state"),
                "district": item.get("city_district"),
                "category": item.get("category"),
                "rating": item.get("rating"),
                "type": stop_type,
                "score": item["_score"],
                "priority": item["_priority"],
                "reasons": item["_reasons"],
                "lat": item.get("latitude"),
                "lng": item.get("longitude"),
                "description": item.get("description"),
                "seasonality": item.get("ideal_seasonality"),
            })

        # 5. Build a concise context string for Groq (NOT raw JSON)
        context_lines = []
        anchor_landmark = trip_context.get("anchor_landmark")
        anchor_city = trip_context.get("anchor_city") or destination
        if anchor_landmark:
            context_lines.append(f"Visual Recommendation Anchor: {anchor_landmark} ({anchor_city or 'Heritage Site'})")
        if destination:
            context_lines.append(f"Destination: {destination}")
        if origin:
            context_lines.append(f"Origin: {origin}")
        if experiences:
            context_lines.append(f"Experiences: {', '.join(experiences)}")
        if intermediate_stops:
            context_lines.append(f"Key intermediate stops on this route: {', '.join(intermediate_stops)}")
        context_lines.append(f"Top {min(top_n, len(recommendations))} ranked recommendations:")
        for i, r in enumerate(recommendations[:8], 1):
            context_lines.append(
                f"  {i}. {r['name']} ({r['category']}, {r['state']}) "
                f"— {r['priority']} priority | {'; '.join(r['reasons'][:2])}"
            )

        return {
            "anchor": anchor_landmark,
            "destination": destination or anchor_city,
            "recommendations": recommendations,
            "intermediate_stops": intermediate_stops,
            "context_summary": "\n".join(context_lines),
            "total_candidates": len(candidates),
        }


# Global singleton
recommendation_engine = RecommendationEngine()
