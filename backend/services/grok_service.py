import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx
from dotenv import load_dotenv
from backend.services.weather_service import weather_service
from backend.services.tourism_service import tourism_service
from backend.services.map_service import map_service
from backend.recommendation.engine import recommendation_engine

load_dotenv()

logger = logging.getLogger("smart_travel.grok_service")

KNOWN_INDIAN_CITIES = [
    "delhi", "new delhi", "goa", "jaipur", "mumbai", "udaipur", "agra", "bengaluru",
    "bangalore", "chennai", "kolkata", "hyderabad", "ahmedabad", "pune", "varanasi",
    "ayodhya", "haridwar", "rishikesh", "amritsar", "manali", "shimla", "chandigarh",
    "surat", "lucknow", "prayagraj", "kullu", "dharamshala", "leh", "ladakh", "gokarna",
    "munnar", "kochi", "alleppey", "ooty", "kodaikanal", "pondicherry", "hampi", "mysore",
    "sonamarg", "gulmarg", "srinagar", "jodhpur", "jaisalmer", "pushkar", "nainital",
    "mussoorie", "kasol", "spiti", "darjeeling", "gangtok", "shillong", "kaziranga"
]

DORA_AI_SYSTEM_PROMPT = """You are Dora AI — an intelligent, unified AI travel planning assistant.
You orchestrate route mapping, live weather, landmark computer vision, tourism datasets, live train schedules, flight fares, and hotel pricing into a single, cohesive travel plan.

CORE ORCHESTRATION & PRESENTATION RULES:

1. CLEAN CHAT RESPONSE STRUCTURE:
   - Every response must be polished, readable, and visually organized.
   - Use clear markdown headings (##, ###), short paragraphs, bullet points (• or -), numbered steps, and spacing where appropriate.
   - NEVER dump raw JSON, Python-like dictionaries, API payloads, escaped characters, internal tool names, or debugging output into the conversational chat. The user must see a finished, human-ready answer.

2. TABLE FORMATTING:
   - Whenever comparing options or presenting structured data, ALWAYS format it as a valid Markdown table with standard pipes:
     * Flight comparison: | Airline | Departure | Arrival | Stops | Price |
     * Train comparison: | Train | Departure | Arrival | Duration | Fare |
     * Hotel stays: | Hotel / Property | Area / Location | Price/Night | Rating | Distance / Type |
     * Budget breakdown: | Category | Estimated Cost (₹) |
     * Multi-day summary: | Day | Location | Key Activities | Stay / Notes |
   - Use proper columns, alignment, and readable text. Never use raw text dumps or broken JSON for comparisons.

3. ITINERARY PRESENTATION:
   - When presenting daily itineraries, format them cleanly and consistently:
     ### Day X: [Destination / Title]
     • **Route / Destination**: [Clear path or city area]
     • **Morning**: [Key sights, monuments, and timing]
     • **Afternoon**: [Lunch spots, cultural exploration]
     • **Evening**: [Sunset views, local markets, dinner]
     • **Stay**: [Recommended hotel or budget stay range]
     • **Estimated Cost**: [Estimated daily expenditure]
   - Keep the itinerary concise, logical, and easy to scan without repeating information unnecessarily.

4. HOTEL RECOMMENDATIONS — BUDGET FIRST (HARD CONSTRAINT):
   - Treat the user's budget as a strict, non-negotiable constraint.
   - Always prioritize affordable, clean, and realistic accommodations (guesthouses, homestays, 2/3-star verified stays) before any premium or luxury options.
   - Do NOT repeatedly suggest expensive 5-star hotels when cheaper suitable alternatives exist.
   - If exact pricing is unavailable or hotel rates exceed the budget, clearly provide an estimated price range instead of inventing an exact price.
     Example: "Budget-friendly stays: approximately ₹1,500–₹2,500/night."

5. WEATHER INTEGRATION:
   - Always incorporate available weather insights (temperature, sky condition, rain probability, season) whenever destination or date details are known.
   - Provide practical, weather-specific travel advice (e.g. carry sunscreen/hydration, best morning hours for monuments, monsoon road tips).

6. SMART TRANSPORT & ROAD TRIPS:
   - For road trips (such as "Delhi to Goa by car"), use the verified route distance and driving time upfront.
   - Do NOT force multiple tourist cities into the itinerary. Suggest at most 1–2 sensible highway rest/overnight stops only for driver safety and endurance.
   - Clearly mark these stops as optional rest breaks.

7. IMAGE FLOW:
   - When the user uploads a travel or monument image, first identify the landmark and location accurately using the computer vision result.
   - Then recommend verified nearby places, attractions, and cultural experiences around that landmark.
"""

ITINERARY_TRIGGER_PHRASES = [
    "create my final itinerary", "create final itinerary", "create my itinerary", "create itinerary",
    "make the complete plan", "make complete plan", "finalize this trip", "finalize trip",
    "make the plan", "final plan", "give me the final plan", "plan my trip", "plan the trip",
    "give me the itinerary", "make my itinerary", "now plan it", "that's everything", "thats everything",
    "generate itinerary", "complete itinerary", "full itinerary", "build the itinerary", "plan it now",
    "okay plan", "ok plan", "ab plan karo", "plan banao", "itinerary banao", "plan kar do",
    "final itinerary", "make final", "plan a trip around this", "plan trip around this", "plan around this"
]

EXPLICIT_ROUTE_TRIGGER_PHRASES = [
    "show route", "route dikhao", "road route", "road distance", "driving distance",
    "directions", "show map", "map dikhao", "fastest route", "driving time",
    "kitna time", "how far", "kitne km", "distance between"
]

EXPLICIT_WEATHER_TRIGGER_PHRASES = [
    "weather", "mausam", "temperature", "kitni garmi", "barish", "rain",
    "will it rain", "climate", "temp today", "forecast", "kaisa rahega"
]


class GrokService:
    def __init__(self):
        self.api_key = (
            os.getenv("XAI_API_KEY") or
            os.getenv("GROK_API_KEY") or
            os.getenv("GROQ_API_KEY")
        )
        if self.api_key and self.api_key.startswith("gsk_"):
            self.base_url = os.getenv("XAI_BASE_URL", "https://api.groq.com/openai/v1")
            self.default_model = os.getenv("XAI_MODEL", "openai/gpt-oss-120b")
        else:
            self.base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
            self.default_model = os.getenv("XAI_MODEL", "grok-2-latest")

    def validate_environment(self):
        if not self.api_key or self.api_key.startswith("your_"):
            raise ValueError("XAI_API_KEY / GROK_API_KEY is not configured in .env file.")

    def _classify_message_intent(self, text: str) -> Dict[str, bool]:
        """Pre-classify user message to guide tool usage decisions."""
        t = text.lower().strip()
        
        has_itinerary_word = any(w in t for w in ["itinerary", "day-by-day", "day by day", "full plan", "final plan"])
        has_plan_or_trip = any(w in t for w in ["plan", "trip", "tour", "vacation", "journey"])
        has_duration = bool(re.search(r'\b\d+\s*[-–]?\s*(?:days?|nights?)\b|a week|1 week|weekend', t))
        has_destination = any(c in t for c in KNOWN_INDIAN_CITIES + [
            "uttarakhand", "himachal", "himachal pradesh", "rajasthan", "kashmir", "kerala", "goa", "golden triangle"
        ])

        is_itinerary_trigger = (
            any(p in t for p in ITINERARY_TRIGGER_PHRASES)
            or t.startswith("my trip choices:")
            or has_itinerary_word
            or (has_plan_or_trip and has_duration and (has_destination or "from" in t or "to" in t or "around" in t or "this" in t or "here" in t))
            or bool(re.search(r'\bplan\b.*?\b(?:trip|itinerary|tour)\b.*?\baround\b', t))
        )
        
        # Explicit route inquiry check
        is_route_request = any(re.search(r'\b' + re.escape(p) + r'\b', t) for p in EXPLICIT_ROUTE_TRIGGER_PHRASES)
        if not is_route_request and ("distance" in t or "route" in t) and ("to" in t or "se" in t):
            if not any(w in t for w in ["plan", "itinerary", "recommend", "suggest", "hotel", "stay"]):
                is_route_request = True
                
        is_weather_request = any(re.search(r'\b' + re.escape(p) + r'\b', t) for p in EXPLICIT_WEATHER_TRIGGER_PHRASES)
        is_train_request = any(re.search(r'\b' + re.escape(kw) + r'\b', t) for kw in [
            "train", "trains", "rail", "railway", "shatabdi", "rajdhani", "vande bharat",
            "train batao", "train schedule", "train timings", "train options", "train route"
        ])
        is_flight_request = any(re.search(r'\b' + re.escape(kw) + r'\b', t) for kw in [
            "flight", "flights", "airline", "airways", "plane", "hawai jahaj",
            "indigo", "air india", "spicejet", "vistara", "akasa", "flight ticket",
            "flights dikhao", "flight timings", "flight search", "flight rate", "airfare"
        ])
        is_hotel_request = any(re.search(r'\b' + re.escape(kw) + r'\b', t) for kw in [
            "hotel", "hotels", "stay", "stays", "resort", "resorts", "room", "rooms",
            "accommodation", "homestay", "hotel rate", "hotel price", "booking.com",
            "hotels.com", "priceline", "agoda", "hotel dikhao", "hotel batao", "hostel", "guesthouse"
        ])
        is_transport_comparison = any(kw in t for kw in [
            "compare", "flight vs train", "train vs flight", "car vs train", "flight vs car",
            "how to reach", "how to go", "how should i travel", "best way to reach", "best way to travel",
            "transport options", "travel options", "car or train", "flight or train", "train or flight"
        ])

        return {
            "is_itinerary_trigger": is_itinerary_trigger,
            "is_route_request": is_route_request,
            "is_weather_request": is_weather_request,
            "is_train_request": is_train_request,
            "is_flight_request": is_flight_request,
            "is_hotel_request": is_hotel_request,
            "is_transport_comparison": is_transport_comparison,
        }

    def _extract_and_merge_trip_context(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract structured trip context across conversation."""
        state = {
            "starting_point": None,
            "destination": None,
            "dates": None,
            "duration": None,
            "budget": None,
            "travelers": None,
            "transport": None,
            "spiritual_focus": None,
            "interests": [],
            "exclusions": [],
            "direct_only": False,
            "travel_style": None
        }

        budget_pat = r'(?:₹\s*[\d,kK]+(?:\s*lakhs?|\s*lac|\s*total|\s*per\s*person)*|(?:around|approx|budget\s*(?:is|of)?)\s*(?:₹|rs\.?|inr)?\s*[\d,kK]+(?:\s*lakhs?|\s*lac|\s*thousand|\s*total|\s*per\s*person)*|\d+\s*(?:lakhs?|lac|k)(?:\s*total|\s*per\s*person)?)'
        date_pat = r'\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\s+(?:to|-)\s+(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+)?\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?|\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(?:to|-)\s+\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s+\d{4})?|\d{1,2}(?:st|nd|rd|th)?\s+(?:to|-)\s+\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s+\d{4})?|(?:diwali|holi|new year|christmas|eid)\s+weekend)\b'

        INDIAN_STATES_AND_REGIONS = [
            "uttarakhand", "himachal pradesh", "himachal", "rajasthan", "kashmir",
            "kerala", "goa", "ladakh", "sikkim", "meghalaya", "karnataka", "tamil nadu"
        ]
        all_dest_candidates = sorted(KNOWN_INDIAN_CITIES + INDIAN_STATES_AND_REGIONS, key=len, reverse=True)

        for msg in messages:
            if msg.get("role") != "user":
                continue
            text = msg.get("content", "").strip()
            t_lower = text.lower()

            # 1. Exclusions
            excl_set = set(state.get('exclusions', []))
            for c in KNOWN_INDIAN_CITIES:
                if re.search(r'\b(?:no|not|nahi|excluding|skip|without)\s+' + re.escape(c) + r'\b', t_lower) or \
                   re.search(r'\b' + re.escape(c) + r'\s+(?:nahi jaana|nahi jana|mat dikhana|skip karo|nahi)\b', t_lower):
                    excl_set.add(c.title())
            if 'no temple' in t_lower or 'temple nahi' in t_lower or 'no spiritual' in t_lower:
                excl_set.add('temple')
            if 'no trek' in t_lower or 'trekking nahi' in t_lower or 'no adventure' in t_lower:
                excl_set.add('trek')
            if 'no beach' in t_lower or 'beach nahi' in t_lower:
                excl_set.add('beach')
            state['exclusions'] = list(excl_set)

            # Direct Trip Constraint
            if any(kw in t_lower for kw in ['direct', 'direct trip', 'only', 'sirf', 'no stops', 'don\'t add stops', 'dont add stops', 'bina ruke']):
                state['direct_only'] = True

            # 2. Origin (supports "from Delhi", "Delhi se", "Delhi to Goa", "Delhi -> Goa")
            for c in sorted(KNOWN_INDIAN_CITIES, key=len, reverse=True):
                if c.title() in state['exclusions']:
                    continue
                if re.search(r'\b(?:from|live in|starting from|start from|leaving|i\'m from)\s+' + re.escape(c) + r'\b', t_lower) or \
                   re.search(r'\b' + re.escape(c) + r'\s+(?:se|se lekar)\b', t_lower) or \
                   re.search(r'\b' + re.escape(c) + r'\s+(?:to|->|towards)\s+[a-z]+', t_lower):
                    state['starting_point'] = c.title()
                    break

            # 3. Destination
            for c in all_dest_candidates:
                if c.title() == state.get('starting_point') or c.title() in state['exclusions']:
                    continue
                if re.search(r'\b(?:drive to|going to|go to|trip to|travel to|visit|explore|towards|places in|to|se|in)\s+' + re.escape(c) + r'\b', t_lower) or \
                   re.search(r'\b' + re.escape(c) + r'\s+(?:trip|tour|jaana|jana|ghoomna|ka plan|plan|chalo)\b', t_lower):
                    state['destination'] = c.title()
                    break

            if not state['destination']:
                for c in all_dest_candidates:
                    if c.title() != state.get('starting_point') and c.title() not in state['exclusions'] and re.search(r'\b' + re.escape(c) + r'\b', t_lower):
                        state['destination'] = c.title()
                        break

            # If still not found, check pair "City to City"
            if not state['destination'] or not state['starting_point']:
                m_pair = re.search(r'\b([A-Za-z]+)\s+(?:to|->|se)\s+([A-Za-z]+)\b', text)
                if m_pair:
                    c1, c2 = m_pair.group(1).title(), m_pair.group(2).title()
                    if c2.lower() in KNOWN_INDIAN_CITIES or any(s in c2.lower() for s in INDIAN_STATES_AND_REGIONS):
                        if not state['destination']:
                            state['destination'] = c2
                        if not state['starting_point']:
                            state['starting_point'] = c1

            # Travelers
            m_trav = re.search(r'\b(\d+)\s*(?:friends|people|persons|of us|pax|travelers|guys)\b', t_lower)
            if m_trav:
                state['travelers'] = f"{m_trav.group(1)} friends" if "friend" in t_lower else f"{m_trav.group(1)} travelers"
            elif 'parent' in t_lower or 'mom' in t_lower or 'dad' in t_lower:
                state['travelers'] = 'Family (with Parents)'
            elif 'couple' in t_lower:
                state['travelers'] = 'Couple'
            elif 'family' in t_lower:
                state['travelers'] = 'Family'
            elif 'solo' in t_lower:
                state['travelers'] = 'Solo'

            # Transport
            if any(kw in t_lower for kw in ['my car', 'own car', 'by car', 'self-drive', 'self drive', 'driving', 'drive']):
                state['transport'] = 'Car (Self-drive)'
            elif 'bike' in t_lower or 'motorcycle' in t_lower:
                state['transport'] = 'Bike'
            elif 'train' in t_lower or 'rail' in t_lower:
                state['transport'] = 'Train'
            elif 'flight' in t_lower or 'fly' in t_lower or 'air' in t_lower:
                state['transport'] = 'Flight'

            # Duration
            m_dur = re.search(r'\b(\d+)\s*[-–]?\s*(?:days?|nights?)\b', t_lower)
            if m_dur:
                state['duration'] = f"{m_dur.group(1)} days"
            elif 'a week' in t_lower or 'one week' in t_lower or '1 week' in t_lower:
                state['duration'] = '7 days'
            elif 'weekend' in t_lower:
                state['duration'] = '3 days'

            # Travel Style
            if any(kw in t_lower for kw in ['relaxed', 'slow pace', 'comfortable', 'easy pace', 'peaceful']):
                state['travel_style'] = 'Relaxed Pace'
            elif any(kw in t_lower for kw in ['fast-paced', 'cover more', 'packed', 'active']):
                state['travel_style'] = 'Fast-Paced'
            elif any(kw in t_lower for kw in ['luxury', 'premium', '5-star', '5 star']):
                state['travel_style'] = 'Luxury'
            elif any(kw in t_lower for kw in ['budget', 'cheap', 'backpacker', 'limited budget', 'low budget']):
                state['travel_style'] = 'Budget-Friendly'

            # Budget
            m_budg = re.search(budget_pat, text, re.I)
            if m_budg and any(b_kw in t_lower for b_kw in ['₹', 'rs', 'budget', '50k', '20k', '30k', '70k', '10k', '15k', 'lakh', 'total']):
                state['budget'] = m_budg.group(0).strip()

            # Dates
            m_date = re.search(date_pat, t_lower)
            if m_date:
                state['dates'] = m_date.group(0).title()

            # Interests
            exp_set = set(state.get('interests', []))
            if 'beach' in t_lower: exp_set.add('Beaches & Relaxation')
            if 'nightlife' in t_lower or 'party' in t_lower or 'club' in t_lower: exp_set.add('Nightlife & Parties')
            if 'food' in t_lower or 'cuisine' in t_lower: exp_set.add('Food & Local Experiences')
            if 'temple' in t_lower or 'spiritual' in t_lower or 'pilgrimage' in t_lower: exp_set.add('Spiritual & Pilgrimage')
            if 'heritage' in t_lower or 'fort' in t_lower or 'history' in t_lower: exp_set.add('History, Heritage & Culture')
            if 'nature' in t_lower or 'wildlife' in t_lower or 'waterfall' in t_lower: exp_set.add('Nature & Scenic Places')
            state['interests'] = list(exp_set)

            # Visual Landmark Anchor
            m_lm = re.search(r'identified (?:it|this) as ([^,\n\]]+)(?:,\s*([^,\n\]]+))?', text, re.I)
            if not m_lm:
                m_lm = re.search(r'detected ([^,\n\]]+)(?:,\s*([^,\n\]]+))?', text, re.I)
            if not m_lm:
                m_lm = re.search(r'\[User attached (?:image|a photo)(?: of landmark)?:\s*([^,\n\]]+)(?:,\s*([^,\n\]]+))?\]', text, re.I)
            if m_lm:
                state['anchor_landmark'] = m_lm.group(1).strip()
                if m_lm.group(2):
                    loc_parts = [p.strip() for p in m_lm.group(2).split(",") if p.strip()]
                    if loc_parts:
                        state['anchor_city'] = loc_parts[0]
                        if len(loc_parts) > 1:
                            state['anchor_state'] = loc_parts[1]
                        if not state.get('destination'):
                            state['destination'] = loc_parts[0]

        return state

    def _parse_dynamic_route_locations(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Extract clean origin and stops using city recognition."""
        t_lower = text.lower()
        origin, dest = None, None
        for c in sorted(KNOWN_INDIAN_CITIES, key=len, reverse=True):
            if re.search(r'\b(?:from|in|starting from|start from|leaving|i\'m from)\s+' + re.escape(c) + r'\b', t_lower):
                origin = c.title()
                break
        for c in sorted(KNOWN_INDIAN_CITIES, key=len, reverse=True):
            if re.search(r'\b(?:drive to|going to|go to|trip to|travel to|visit|explore|towards|to|se)\s+' + re.escape(c) + r'\b', t_lower):
                if c.title() != origin:
                    dest = c.title()
                    break

        if origin and dest:
            return origin, [dest]

        # Simple pattern: City to City
        m = re.search(r'\b([A-Za-z]+)\s+(?:to|->|se)\s+([A-Za-z]+)\b', text)
        if m:
            c1, c2 = m.group(1).title(), m.group(2).title()
            if c1.lower() in KNOWN_INDIAN_CITIES or c2.lower() in KNOWN_INDIAN_CITIES:
                return c1, [c2]

        return None, []

    async def _try_get_route(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Call OSRM to get real driving route."""
        if not messages:
            return None
        last_msg = messages[-1].get("content", "")
        origin, stops = self._parse_dynamic_route_locations(last_msg)
        if not origin and len(messages) > 1:
            text = " ".join([m.get("content", "") for m in messages[-2:]])
            origin, stops = self._parse_dynamic_route_locations(text)
        if origin and stops:
            try:
                return await map_service.plan_route(origin, stops)
            except Exception as e:
                logger.warning(f"OSRM route failed for {origin} -> {stops}: {e}")
        return None

    def _sanitize_text_formatting(self, text: str) -> str:
        """Sanitize text formatting for user-facing markdown, preserving tables and bullets."""
        if not text:
            return ""
        s = text.strip()
        
        # Remove surrounding code block markers if the whole content is wrapped in one
        if s.startswith("```json"):
            s = s[7:]
            if s.endswith("```"):
                s = s[:-3]
            s = s.strip()
        elif s.startswith("```") and s.endswith("```"):
            inner = s[3:-3].strip()
            if inner.startswith("{") and inner.endswith("}"):
                s = inner

        # If s looks like raw JSON, extract user-facing message
        if s.startswith("{") or s.startswith("[") or '"message":' in s:
            try:
                p = json.loads(s)
                if isinstance(p, list) and len(p) > 0 and isinstance(p[0], dict):
                    p = p[0]
                if isinstance(p, dict):
                    if p.get("message"):
                        s = str(p["message"])
                    elif p.get("summary"):
                        s = str(p["summary"])
                    elif p.get("itinerary") and isinstance(p["itinerary"], dict) and p["itinerary"].get("days"):
                        days_md = []
                        for d in p["itinerary"]["days"]:
                            days_md.append(f"### Day {d.get('day', '')}: {d.get('title', '')}\n• **Morning**: {d.get('morning', '—')}\n• **Afternoon**: {d.get('afternoon', '—')}\n• **Evening**: {d.get('evening', '—')}\n• **Stay**: {d.get('stay', '—')}")
                        s = "## Travel Itinerary\n\n" + "\n\n".join(days_md)
            except Exception:
                m_msg = re.search(r'"message"\s*:\s*"((?:\\.|[^"\\])*)"', s, re.DOTALL)
                if m_msg:
                    try:
                        s = json.loads(f'"{m_msg.group(1)}"')
                    except Exception:
                        s = m_msg.group(1).replace("\\n", "\n").replace('\\"', '"')
                else:
                    # Strip leading json braces if accidentally prepended
                    s = re.sub(r'^\s*[\{\[]\s*["\w\s]+:\s*', '', s)

        # Unescape literal backslash escapes
        if "\\n" in s:
            s = s.replace("\\n", "\n")
        if '\\"' in s:
            s = s.replace('\\"', '"')

        # Clean non-breaking spaces
        s = s.replace('\u202f', ' ').replace('\u00a0', ' ')
        
        # Remove any internal tool debugging traces if present
        s = re.sub(r'^\[(?:DEBUG|TRACE|TOOL CALL|AGENT)\][^\n]*\n?', '', s, flags=re.MULTILINE)
        
        return s.strip()

    def _extract_itinerary_from_text(self, text: str, destination: str = "India", origin: str = "") -> Optional[Dict[str, Any]]:
        """Synthesize structured itinerary dictionary from conversational markdown when JSON mode was omitted."""
        if not text or not re.search(r'\bday\s*\d+\b', text, re.I):
            return None

        # Look for Day headings e.g. "### Day 1: Amber Fort", "**Day 1: ...**", or "Day 1:"
        day_matches = list(re.finditer(r'(?:^|\n)(?:[#*•-]*\s*)?(?:###?\s*)?Day\s*(\d+)[:\s–—*]+([^\n]+)', text, re.I))
        if not day_matches:
            return None

        days = []
        for i, match in enumerate(day_matches):
            day_num = int(match.group(1))
            day_title = match.group(2).strip().replace("**", "").replace("*", "")
            start_pos = match.end()
            end_pos = day_matches[i + 1].start() if i + 1 < len(day_matches) else len(text)
            day_body = text[start_pos:end_pos].strip()

            m_morning = re.search(r'(?:morning|am)[:\s–—*]+([^\n•\*\#]+)', day_body, re.I)
            m_afternoon = re.search(r'(?:afternoon|noon|pm)[:\s–—*]+([^\n•\*\#]+)', day_body, re.I)
            m_evening = re.search(r'(?:evening|night)[:\s–—*]+([^\n•\*\#]+)', day_body, re.I)
            m_stay = re.search(r'(?:stay|hotel|accommodation)[:\s–—*]+([^\n•\*\#]+)', day_body, re.I)
            m_cost = re.search(r'(?:estimated daily cost|estimated cost|cost|budget)[:\s–—*]+([^\n•\*\#]+)', day_body, re.I)

            days.append({
                "day": day_num,
                "title": day_title if day_title else f"Day {day_num} in {destination}",
                "morning": m_morning.group(1).strip() if m_morning else "Morning exploration & key landmarks",
                "afternoon": m_afternoon.group(1).strip() if m_afternoon else "Afternoon cultural sightseeing & dining",
                "evening": m_evening.group(1).strip() if m_evening else "Evening leisure & local markets",
                "stay": m_stay.group(1).strip() if m_stay else "Recommended Stays",
                "estimated_cost": m_cost.group(1).strip() if m_cost else "Included in budget"
            })

        if not days:
            return None

        return {
            "overview": {
                "title": f"{len(days)}-Day Itinerary for {destination}",
                "destination": destination,
                "origin": origin or "Delhi",
                "duration": f"{len(days)} Days",
                "budget": "Standard Budget",
                "total_estimated_cost": f"₹{len(days) * 4000:,}"
            },
            "days": days,
            "budget_breakdown": {
                "transport": "Transit / Fuel",
                "accommodation": "Stays & Hotels",
                "food": "Dining",
                "activities": "Sightseeing",
                "total": f"₹{len(days) * 4000:,}"
            }
        }

    def _extract_target_location(self, messages: List[Dict[str, str]], route_info: Optional[Dict], context: Dict[str, Any]) -> Optional[str]:
        """Extract destination for tourism/weather lookups."""
        if context.get("destination"):
            return context["destination"]
        if context.get("anchor_city"):
            return context["anchor_city"]
        if context.get("anchor_landmark"):
            return context["anchor_landmark"]
        if route_info and route_info.get("stops"):
            return route_info["stops"][-1]["name"]
        
        all_text = " ".join([m.get("content", "") for m in messages[-3:]]).lower()
        for loc in KNOWN_INDIAN_CITIES:
            if loc != (context.get("starting_point") or "").lower() and loc in all_text:
                return loc.title()
        return None

    async def generate_smart_trip_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        landmark_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.validate_environment()
        target_model = model or self.default_model

        # Extract structured trip context from messages
        extracted_context = self._extract_and_merge_trip_context(messages)

        # Merge landmark context if passed in current turn
        if landmark_context and landmark_context.get("landmark_name"):
            extracted_context["anchor_landmark"] = landmark_context["landmark_name"]
            loc = landmark_context.get("location")
            if loc:
                loc_parts = [p.strip() for p in loc.split(",") if p.strip()]
                if loc_parts:
                    extracted_context["anchor_city"] = loc_parts[0]
                    if len(loc_parts) > 1:
                        extracted_context["anchor_state"] = loc_parts[1]
                    if not extracted_context.get("destination"):
                        extracted_context["destination"] = loc_parts[0]

        last_user_msg = messages[-1].get("content", "").strip() if messages else ""
        msg_intent = self._classify_message_intent(last_user_msg)
        is_quiz_submission = last_user_msg.lower().startswith("my trip choices:")
        
        # Determine tool needs
        needs_route = (
            msg_intent["is_route_request"]
            or msg_intent["is_itinerary_trigger"]
            or msg_intent["is_transport_comparison"]
            or (extracted_context.get("starting_point") and extracted_context.get("destination"))
        )
        needs_weather = msg_intent["is_weather_request"]

        # Fetch route data via OSRM
        route_info = None
        if needs_route:
            route_info = await self._try_get_route(messages)
            if not route_info and extracted_context.get("starting_point") and extracted_context.get("destination"):
                try:
                    route_info = await map_service.plan_route(
                        extracted_context["starting_point"],
                        [extracted_context["destination"]]
                    )
                except Exception as r_err:
                    logger.warning(f"Fallback OSRM route failed: {r_err}")

        target_loc = self._extract_target_location(messages, route_info, extracted_context)

        # Initialize context blocks
        landmark_context_str = ""
        dataset_context_str = ""
        weather_context_str = ""
        route_context_str = ""
        recommendation_context_str = ""
        train_context_str = ""
        flight_context_str = ""
        hotel_context_str = ""
        budget_context_str = ""
        engine_recommendations = []
        train_results = None
        flight_results = None
        hotel_results = None

        # 1. IMAGE FLOW: Landmark recognition + nearby recommendations
        if landmark_context:
            l_name = landmark_context.get("landmark_name")
            l_loc = landmark_context.get("location")
            l_tour = landmark_context.get("tourism_info") or {}
            
            nearby_places = []
            if extracted_context.get("anchor_city"):
                nearby_places = tourism_service.search_destinations(query=extracted_context["anchor_city"], limit=5)

            landmark_context_str = (
                f"\n\n[IMAGE & LANDMARK IDENTIFICATION CONTEXT]:\n"
                f"- Identified Landmark: {l_name or 'Scenic Travel Photo'}\n"
                f"- Verified Location: {l_loc or 'India'}\n"
            )
            if l_tour.get("description"):
                landmark_context_str += f"- Overview: {l_tour['description']}\n"
            if nearby_places:
                nb_list = [f"{p['destination_name']} ({p.get('category', 'Attraction')})" for p in nearby_places]
                landmark_context_str += f"- Verified Nearby Attractions in {extracted_context.get('anchor_city')}: {', '.join(nb_list)}\n"
            
            landmark_context_str += (
                "ORCHESTRATION INSTRUCTION: First identify the landmark and its location clearly to the user. "
                "Then use the verified nearby attractions above to suggest relevant places to visit and things to do around it.\n"
            )

        # 2. BUDGET CONSTRAINT CONTEXT
        if extracted_context.get("budget"):
            budget_context_str = (
                f"\n\n[USER BUDGET CONSTRAINT]:\n"
                f"- Stated Budget: {extracted_context['budget']}\n"
                f"- HARD CONSTRAINT: Never recommend stays, flights, or packages that exceed this budget. "
                f"If luxury hotels are returned in context that exceed this amount, provide realistic budget/homestay price ranges (e.g. ₹1,200–₹2,500/night) and practical cost-saving tips.\n"
            )

        # 3. WEATHER CONTEXT
        weather_cond = None
        dates_ctx = extracted_context.get("dates") or (last_user_msg if any(m in last_user_msg.lower() for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "monsoon", "winter", "summer", "diwali"]) else None)
        weather_target = target_loc or extracted_context.get("destination") or extracted_context.get("anchor_city")
        
        if weather_target:
            try:
                weather_eval = await weather_service.evaluate_travel_weather(
                    destination=weather_target,
                    dates_text=dates_ctx
                )
                if weather_eval:
                    live_w = weather_eval.get("live_weather") or {}
                    weather_cond = live_w.get("weather_condition")
                    weather_context_str = (
                        f"\n\n[VERIFIED WEATHER & SEASONAL CLIMATE -- {weather_eval['destination'].upper()}]:\n"
                        f"- Season: {weather_eval.get('season_name')}\n"
                        f"- Overview: {weather_eval.get('climate_summary')}\n"
                        f"- Sightseeing Nuances: {weather_eval.get('outdoor_nuances')}\n"
                    )
                    if live_w.get("current_temperature_c") is not None:
                        weather_context_str += f"- Temperature: {live_w.get('current_temperature_c')}°C ({live_w.get('weather_condition', 'Pleasant')})\n"
                    if live_w.get("precipitation_probability_pct") is not None:
                        weather_context_str += f"- Rain Probability: {live_w.get('precipitation_probability_pct')}%\n"
                    weather_context_str += (
                        "WEATHER INSTRUCTION: Actively integrate this verified weather information (temperature, condition, rain probability) "
                        "into the travel response with practical clothing, hydration, and outdoor timing advice.\n"
                    )
            except Exception as w_err:
                logger.warning(f"Weather evaluation failed: {w_err}")

        # 4. RECOMMENDATIONS CONTEXT
        needs_recommendations = (
            msg_intent["is_itinerary_trigger"]
            or any(kw in last_user_msg.lower() for kw in [
                "recommend", "suggest", "best places", "where to go", "what to see",
                "places in", "places to visit", "things to do", "attractions", "itinerary"
            ])
        )
        if needs_recommendations and (target_loc or extracted_context.get("anchor_landmark")):
            rec_dest = target_loc or extracted_context.get("anchor_city") or extracted_context.get("anchor_landmark")
            engine_trip_ctx = {
                "destination": rec_dest,
                "anchor_landmark": extracted_context.get("anchor_landmark"),
                "anchor_city": extracted_context.get("anchor_city"),
                "anchor_state": extracted_context.get("anchor_state"),
                "starting_point": extracted_context.get("starting_point"),
                "experiences": extracted_context.get("interests", []),
                "exclusions": extracted_context.get("exclusions", []),
                "travelers": extracted_context.get("travelers"),
                "budget": extracted_context.get("budget"),
                "transport": extracted_context.get("transport"),
                "travel_style": extracted_context.get("travel_style"),
                "duration": extracted_context.get("duration"),
            }
            engine_result = recommendation_engine.recommend(
                trip_context=engine_trip_ctx,
                weather_condition=weather_cond,
                top_n=6,
            )
            engine_recommendations = engine_result.get("recommendations", [])
            if engine_recommendations:
                recommendation_context_str = (
                    "\n\n[VERIFIED DESTINATION ATTRACTIONS & RECOMMENDATIONS]:\n"
                    + engine_result["context_summary"]
                )
        elif target_loc:
            retrieved = tourism_service.search_destinations(query=target_loc, limit=4)
            if retrieved:
                dataset_context_str = "\n\n[TOURISM DATASET CONTEXT]:\n"
                for idx, r in enumerate(retrieved, 1):
                    dataset_context_str += f"{idx}. {r['destination_name']} ({r.get('category', 'Sightseeing')}, {r.get('state', '')})\n"

        # 5. ROUTE CONTEXT & SMART TRANSPORT (OSRM)
        if route_info:
            route_context_str = (
                f"\n\n[VERIFIED OSRM ROAD ROUTE]:\n"
                f"Origin: {route_info['origin']['name']} -> Destination: {route_info['stops'][-1]['name']}\n"
                f"Total Distance: {route_info['total_distance_km']} km | Driving Duration: {route_info['total_duration_text']}\n"
                f"SMART TRANSPORT INSTRUCTION: State the real driving distance and duration upfront. "
                f"Do NOT force multiple tourist cities into the itinerary. Suggest at most 1–2 sensible rest/overnight points (e.g., Udaipur/Pune for Delhi-Goa) "
                f"strictly for driver endurance and safety, clearly marking them as optional rest breaks.\n"
            )

        # 6. TRAIN SEARCH (RAILKIT)
        needs_trains = (
            msg_intent.get("is_train_request")
            or msg_intent.get("is_transport_comparison")
            or (extracted_context.get("transport") == "Train" and extracted_context.get("starting_point") and target_loc)
        )
        if needs_trains:
            t_orig = extracted_context.get("starting_point")
            t_dest = target_loc or extracted_context.get("destination")
            if t_orig and t_dest and t_orig.lower() != t_dest.lower():
                try:
                    from backend.services.train_service import train_service
                    train_res = await train_service.search_trains(source=t_orig, destination=t_dest, limit=5)
                    if train_res.get("status") == "success" and train_res.get("trains"):
                        train_results = train_res
                        train_context_str = (
                            f"\n\n[VERIFIED RAILKIT TRAIN SCHEDULES]:\n"
                            f"Route: {train_res['source'].get('station_name', t_orig)} -> {train_res['destination'].get('station_name', t_dest)}\n"
                            f"Total Available Trains: {train_res['total_trains']}\n"
                        )
                        for tr in train_res["trains"][:4]:
                            train_context_str += (
                                f"- {tr['train_number']} {tr['train_name']}: Dep {tr['departure_time']} ({tr['from_station_name']}) -> "
                                f"Arr {tr['arrival_time']} ({tr['to_station_name']}), Duration: {tr['duration']}\n"
                            )
                except Exception as t_err:
                    logger.warning(f"Train search failed: {t_err}")

        # 7. FLIGHT SEARCH (SERPAPI GOOGLE FLIGHTS)
        needs_flights = (
            msg_intent.get("is_flight_request")
            or msg_intent.get("is_transport_comparison")
            or (extracted_context.get("transport") == "Flight" and extracted_context.get("starting_point") and target_loc)
        )
        if needs_flights:
            f_orig = extracted_context.get("starting_point")
            f_dest = target_loc or extracted_context.get("destination")
            if f_orig and f_dest and f_orig.lower() != f_dest.lower():
                try:
                    from backend.services.flight_service import flight_service
                    flight_res = await flight_service.search_flights(origin=f_orig, destination=f_dest, limit=5)
                    if flight_res.get("status") == "success" and flight_res.get("flights"):
                        flight_results = flight_res
                        flight_context_str = (
                            f"\n\n[VERIFIED GOOGLE FLIGHT SCHEDULES & FARES]:\n"
                            f"Route: {flight_res['origin'].get('airport_code', f_orig)} -> {flight_res['destination'].get('airport_code', f_dest)}\n"
                        )
                        for fl in flight_res["flights"][:4]:
                            stop_str = "Non-stop" if fl["is_non_stop"] else f"{fl['stops']} stop"
                            flight_context_str += (
                                f"- {fl['airline']} {fl['flight_number']}: Dep {fl['departure_time']} -> Arr {fl['arrival_time']}, "
                                f"Duration: {fl['duration']}, {stop_str}, Fare: ₹{fl['price']:,}\n"
                            )
                except Exception as f_err:
                    logger.warning(f"Flight search failed: {f_err}")

        # 8. HOTEL SEARCH (MAKCORPS)
        needs_hotels = (
            msg_intent.get("is_hotel_request")
            or msg_intent.get("is_itinerary_trigger")
            or (extracted_context.get("budget") and (target_loc or extracted_context.get("destination")))
            or any(kw in last_user_msg.lower() for kw in ["hotel", "stay", "where to stay", "resort", "hostel"])
        )
        if needs_hotels:
            h_city = target_loc or extracted_context.get("destination") or extracted_context.get("anchor_city")
            if h_city:
                try:
                    from backend.services.hotel_service import hotel_service
                    hotel_res = await hotel_service.search_hotels(city=h_city, limit=4)
                    if hotel_res.get("status") == "success" and hotel_res.get("hotels"):
                        hotel_results = hotel_res
                        hotel_context_str = (
                            f"\n\n[VERIFIED HOTEL REFERENCE RATES (Makcorps)]:\n"
                            f"City: {hotel_res.get('city')}\n"
                            f"HOTEL RECOMMENDATION INSTRUCTION: Budget is a hard constraint. "
                            f"Prioritize affordable, realistic accommodation (clean homestays/budget stays) before luxury resorts. "
                            f"If exact pricing is unavailable or hotels exceed budget, clearly provide an estimated price range (e.g. 'Budget-friendly stays: approximately ₹1,500–₹2,500/night'). "
                            f"Format hotel comparisons as a clean Markdown table: | Hotel / Property | Area / Location | Price/Night | Rating | Distance / Type |\n"
                        )
                        for h in hotel_res["hotels"][:4]:
                            hotel_context_str += (
                                f"- {h['hotel_name']}: Indicative Lowest ₹{h['lowest_price_inr']:,}/night on {h['best_vendor']} (Rating: {h['rating']})\n"
                            )
                except Exception as h_err:
                    logger.warning(f"Hotel search failed: {h_err}")

        # MULTI-MODAL COMPARISON INSTRUCTION
        comparison_context_str = ""
        if msg_intent.get("is_transport_comparison"):
            comparison_context_str = (
                "\n\n[MULTI-MODAL TRANSPORT COMPARISON TASK]:\n"
                "Compare Flight vs Train vs Car using clear, readable Markdown tables:\n"
                "- Flight Table: | Airline | Departure | Arrival | Stops | Price |\n"
                "- Train Table: | Train | Departure | Arrival | Duration | Fare |\n"
                "Compare Total Cost, Travel Time, and Comfort, aligned with user budget.\n"
                "Conclude with a clear, reasoned recommendation for the best travel mode.\n"
            )

        # Assemble full active prompt
        active_system_prompt = (
            (system_prompt or DORA_AI_SYSTEM_PROMPT)
            + budget_context_str
            + landmark_context_str
            + dataset_context_str
            + recommendation_context_str
            + route_context_str
            + train_context_str
            + flight_context_str
            + hotel_context_str
            + weather_context_str
            + comparison_context_str
        )

        if msg_intent["is_itinerary_trigger"] or is_quiz_submission:
            active_system_prompt += (
                "\n\n[JSON OUTPUT MANDATE]:\n"
                "You MUST return a valid JSON object with EXACTLY this structure:\n"
                "{\n"
                '  "message": "<Polished final markdown response. Include clear headings, day-by-day sections with bullet points (• Route, • Morning, • Afternoon, • Evening, • Stay, • Estimated Cost), budget breakdown table, weather notes, and practical tips. NEVER dump raw JSON or backend data here.>",\n'
                '  "intent": "plan_itinerary",\n'
                '  "preferences": {\n'
                '    "destination": "...",\n'
                '    "starting_point": "...",\n'
                '    "duration": "...",\n'
                '    "budget": "...",\n'
                '    "travelers": "...",\n'
                '    "transport": "..."\n'
                "  },\n"
                '  "itinerary": {\n'
                '    "overview": {\n'
                '      "title": "...",\n'
                '      "destination": "...",\n'
                '      "origin": "...",\n'
                '      "dates": "...",\n'
                '      "duration": "...",\n'
                '      "transport": "...",\n'
                '      "budget": "...",\n'
                '      "total_estimated_cost": "..."\n'
                "    },\n"
                '    "days": [\n'
                '      {\n'
                '        "day": 1,\n'
                '        "title": "...",\n'
                '        "morning": "...",\n'
                '        "afternoon": "...",\n'
                '        "evening": "...",\n'
                '        "stay": "...",\n'
                '        "estimated_cost": "...",\n'
                '        "weather_note": "..."\n'
                "      }\n"
                "    ],\n"
                '    "budget_breakdown": {\n'
                '      "transport": "...",\n'
                '      "accommodation": "...",\n'
                '      "food": "...",\n'
                '      "activities": "...",\n'
                '      "other": "...",\n'
                '      "total": "..."\n'
                "    },\n"
                '    "closing_note": "..."\n'
                "  }\n"
                "}\n"
            )

        formatted_messages = [{"role": "system", "content": active_system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 3000,
        }
        if msg_intent["is_itinerary_trigger"] or is_quiz_submission:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DoraAI/1.0"
        }
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"

        models_to_try = [
            target_model,
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b"
        ]
        seen_m = set()
        deduped_models = []
        for m in models_to_try:
            if m not in seen_m:
                seen_m.add(m)
                deduped_models.append(m)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                data = None
                for cycle in range(3):
                    for attempt, m_name in enumerate(deduped_models):
                        payload["model"] = m_name
                        response = await client.post(endpoint, json=payload, headers=headers)
                        if response.status_code == 400 and "response_format" in payload:
                            del payload["response_format"]
                            response = await client.post(endpoint, json=payload, headers=headers)
                        if response.status_code == 429:
                            logger.warning(f"Groq API 429 on {m_name}. Switching to next fallback model...")
                            import asyncio
                            await asyncio.sleep(3.0)
                            continue
                        if response.status_code != 200:
                            logger.warning(f"Groq API returned {response.status_code} for {m_name}. Trying next fallback...")
                            continue
                        data = response.json()
                        break
                    if data:
                        break
                    if cycle == 0:
                        import asyncio
                        await asyncio.sleep(3.0)

                if not data:
                    raise Exception("All Groq models exhausted rate limits.")

                choices = data.get("choices", [])
                if not choices:
                    raise Exception("No completion choices returned.")

                raw_content = choices[0].get("message", {}).get("content", "").strip()
                if "</think>" in raw_content:
                    raw_content = raw_content.split("</think>")[-1].strip()
                elif "<think>" in raw_content:
                    raw_content = raw_content.split("<think>")[-1].strip()

                cleaned_json = raw_content
                if "```json" in cleaned_json:
                    cleaned_json = cleaned_json.split("```json")[-1].split("```")[0].strip()
                elif "```" in cleaned_json:
                    cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

                try:
                    parsed = json.loads(cleaned_json)
                    response_text = parsed.get("message")
                    itinerary_data = parsed.get("itinerary") or None
                    if not response_text:
                        if parsed.get("summary"):
                            response_text = parsed.get("summary")
                        elif parsed.get("overview"):
                            response_text = parsed.get("overview")
                        elif itinerary_data and isinstance(itinerary_data, dict) and itinerary_data.get("days"):
                            days_md = []
                            for d in itinerary_data["days"]:
                                days_md.append(f"### Day {d.get('day', '')}: {d.get('title', '')}\n• **Morning**: {d.get('morning', '—')}\n• **Afternoon**: {d.get('afternoon', '—')}\n• **Evening**: {d.get('evening', '—')}\n• **Stay**: {d.get('stay', '—')}")
                            response_text = "## Verified Travel Itinerary\n\n" + "\n\n".join(days_md)
                        else:
                            response_text = raw_content

                    raw_intent = parsed.get("intent")
                    if msg_intent["is_itinerary_trigger"] or is_quiz_submission:
                        intent = "plan_itinerary"
                    elif msg_intent["is_route_request"]:
                        intent = "route_planning"
                    elif msg_intent["is_weather_request"]:
                        intent = "weather_inquiry"
                    elif msg_intent["is_transport_comparison"]:
                        intent = "transport_inquiry"
                    else:
                        intent = raw_intent or "general_question"

                    preferences = parsed.get("preferences") or {}
                    quiz_data = parsed.get("quiz") or None
                except Exception:
                    response_text = raw_content
                    if msg_intent["is_route_request"]:
                        intent = "route_planning"
                    elif msg_intent["is_weather_request"]:
                        intent = "weather_inquiry"
                    elif msg_intent["is_transport_comparison"]:
                        intent = "transport_inquiry"
                    elif is_quiz_submission or msg_intent["is_itinerary_trigger"]:
                        intent = "plan_itinerary"
                    else:
                        intent = "general_question"
                    preferences = {}
                    quiz_data = None
                    itinerary_data = None

                sanitized_message = self._sanitize_text_formatting(response_text)

                if isinstance(itinerary_data, list):
                    itinerary_data = {"days": itinerary_data}
                elif not itinerary_data and (intent == "plan_itinerary" or re.search(r'\bday\s*1\b', sanitized_message, re.I)):
                    itinerary_data = self._extract_itinerary_from_text(
                        sanitized_message,
                        destination=preferences.get("destination") or target_loc or "India",
                        origin=preferences.get("starting_point") or extracted_context.get("starting_point") or "Delhi"
                    )

                final_preferences = {
                    "starting_point": preferences.get("starting_point") or extracted_context.get("starting_point"),
                    "destination": preferences.get("destination") or extracted_context.get("destination") or target_loc,
                    "dates": preferences.get("dates") or extracted_context.get("dates"),
                    "duration": preferences.get("duration") or extracted_context.get("duration"),
                    "budget": preferences.get("budget") or extracted_context.get("budget"),
                    "travelers": preferences.get("travelers") or extracted_context.get("travelers"),
                    "transport": preferences.get("transport") or extracted_context.get("transport"),
                    "spiritual_focus": preferences.get("spiritual_focus"),
                    "interests": preferences.get("interests") or extracted_context.get("interests") or [],
                    "travel_style": preferences.get("travel_style") or extracted_context.get("travel_style")
                }

                result_dict = {
                    "message": sanitized_message,
                    "intent": intent,
                    "quiz": quiz_data if (quiz_data and quiz_data.get("active") and quiz_data.get("questions")) else None,
                    "itinerary": itinerary_data,
                    "preferences": final_preferences,
                    "recommendations": engine_recommendations if engine_recommendations else None,
                    "landmark_context": landmark_context,
                    "model": data.get("model", target_model),
                    "usage": data.get("usage", {}),
                    "status": "success"
                }

                if route_info:
                    result_dict["route_data"] = route_info
                if train_results:
                    result_dict["train_data"] = train_results
                if flight_results:
                    result_dict["flight_data"] = flight_results
                if hotel_results:
                    result_dict["hotel_data"] = hotel_results

                return result_dict

            except httpx.HTTPStatusError as exc:
                logger.error(f"API HTTP error: {exc.response.status_code} - {exc.response.text}")
                raise Exception(f"API request failed ({exc.response.status_code}): {exc.response.text}")
            except Exception as exc:
                logger.error(f"API error: {str(exc)}")
                raise Exception(f"API service error: {str(exc)}")


grok_service = GrokService()
