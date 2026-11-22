import os
import io
import urllib.request
import logging
from typing import Dict, Any, List, Optional, Union, BinaryIO
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms, models

logger = logging.getLogger("smart_travel.scene_service")

# Paths
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/places365"))
PRETRAINED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/pretrained"))

CHECKPOINT_FILENAME = "resnet18_places365.pth"
CATEGORIES_FILENAME = "categories_places365.txt"

PRIMARY_CHECKPOINT_PATH = os.path.join(MODELS_DIR, CHECKPOINT_FILENAME)
FALLBACK_CHECKPOINT_PATH = os.path.join(PRETRAINED_DIR, CHECKPOINT_FILENAME)
CATEGORIES_PATH = os.path.join(MODELS_DIR, CATEGORIES_FILENAME)

OFFICIAL_CHECKPOINT_URL = "http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar"
OFFICIAL_CATEGORIES_URL = "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"

# ImageNet normalization standard for Places365
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

SCENE_TRANSFORM = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])

# High-level travel scene category mappings
TRAVEL_SCENE_MAPPING = {
    "beach/coast": [
        "beach", "coast", "ocean", "seashore", "boardwalk", "beach_house", "harbor",
        "lagoon", "pier", "promenade", "swimming_pool", "water_park"
    ],
    "mountain/hills": [
        "mountain", "mountain_path", "mountain_snowy", "cliff", "valley", "volcano",
        "butte", "canyon", "ski_resort", "ski_slope", "snowfield"
    ],
    "forest/nature": [
        "forest", "forest_path", "rainforest", "bamboo_forest", "botanical_garden",
        "orchard", "tree_farm", "jungle", "national_park"
    ],
    "heritage/architecture": [
        "arch", "archaeological_excavation", "amphitheater", "aqueduct", "castle",
        "palace", "ruins", "monument", "mausoleum", "tomb", "fortress", "pyramid",
        "viaduct", "courtyard", "plaza", "fountain"
    ],
    "temple/spiritual": [
        "temple/south_asia", "temple/east_asia", "temple/asia", "church/outdoor",
        "church/indoor", "mosque/outdoor", "mosque/indoor", "pagoda", "monastery",
        "shrine", "synagogue/outdoor", "cathedral/outdoor", "abbey"
    ],
    "waterfall/river/waterbody": [
        "waterfall", "river", "lake/natural", "pond", "creek", "canal/natural",
        "canal/urban", "watering_hole", "dam"
    ],
    "city/urban": [
        "street", "downtown", "skyscraper", "cityscape", "crosswalk", "alley",
        "apartment_building/outdoor", "building_facade", "bazaar/outdoor",
        "market/outdoor", "shopping_mall/indoor", "tower"
    ],
    "scenic landscape/rural": [
        "field/wild", "field/cultivated", "pasture", "desert/sand", "desert/vegetation",
        "meadow", "rice_paddy", "farm", "vineyard", "hayfield"
    ]
}

# Curated Indian Tourism Alternatives mapped to scene experiences
INDIAN_SCENE_ALTERNATIVES = {
    "mountain/snow": {
        "theme": "Snowy Peaks & Alpine Slopes",
        "regions": ["Kashmir", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Ladakh"],
        "destinations": [
            {"name": "Gulmarg", "state": "Jammu & Kashmir", "vibe": "Snow-covered alpine meadows, world-class ski slopes, and the high-altitude Gulmarg Gondola"},
            {"name": "Manali & Solang Valley", "state": "Himachal Pradesh", "vibe": "Snowy Himalayan passes, skiing, paragliding, and mountain hot springs"},
            {"name": "Auli", "state": "Uttarakhand", "vibe": "Panoramic Nanda Devi views and premier ski slopes"},
            {"name": "Yumthang Valley & Lachung", "state": "Sikkim", "vibe": "Snow-fringed rhododendron valleys and majestic Eastern Himalayan vistas"}
        ]
    },
    "mountain/hills": {
        "theme": "Scenic Mountains & Serene Hill Stations",
        "regions": ["Himachal Pradesh", "Uttarakhand", "Western Ghats", "Northeast India"],
        "destinations": [
            {"name": "Mussoorie & Nainital", "state": "Uttarakhand", "vibe": "Lush green pine ridges, sunset points, and serene mountain lakes"},
            {"name": "Munnar", "state": "Kerala", "vibe": "Misty emerald tea estates and winding Western Ghats ridges"},
            {"name": "Coorg", "state": "Karnataka", "vibe": "Lush coffee plantations, waterfalls, and scenic hill trails"},
            {"name": "Shillong & Cherrapunji", "state": "Meghalaya", "vibe": "Rolling cloud-kissed hills, waterfalls, and living root bridges"}
        ]
    },
    "desert": {
        "theme": "Golden Sand Dunes & Desert Safaris",
        "regions": ["Rajasthan", "Gujarat"],
        "destinations": [
            {"name": "Jaisalmer (Sam Sand Dunes)", "state": "Rajasthan", "vibe": "Golden Thar sand dunes, sunset camel safaris, and stargazing camps"},
            {"name": "Rann of Kutch", "state": "Gujarat", "vibe": "Endless white salt desert, full-moon cultural camps, and folk music"},
            {"name": "Bikaner & Osian", "state": "Rajasthan", "vibe": "Historic desert forts and traditional camel country"}
        ]
    },
    "beach/coast": {
        "theme": "Tropical Coastlines & Pristine Beaches",
        "regions": ["Goa", "Andaman & Nicobar", "Kerala", "Karnataka", "Puducherry"],
        "destinations": [
            {"name": "Havelock Island (Radhanagar Beach)", "state": "Andaman & Nicobar", "vibe": "Turquoise waters, powder-white sand, and vibrant coral reefs"},
            {"name": "South Goa Beaches (Palolem & Agonda)", "state": "Goa", "vibe": "Tranquil crescent coves, palm-lined shores, and relaxed beach shacks"},
            {"name": "Varkala Cliff", "state": "Kerala", "vibe": "Dramatic red laterite cliffs towering over the Arabian Sea"},
            {"name": "Gokarna (Om Beach)", "state": "Karnataka", "vibe": "Secluded coastal trails, peaceful beaches, and spiritual ambience"}
        ]
    },
    "forest/nature": {
        "theme": "Dense Forests & Wildlife Reserves",
        "regions": ["Uttarakhand", "Madhya Pradesh", "Assam", "Kerala"],
        "destinations": [
            {"name": "Jim Corbett National Park", "state": "Uttarakhand", "vibe": "Dense Sal forests, foothills, and famous Bengal tiger safaris"},
            {"name": "Kaziranga National Park", "state": "Assam", "vibe": "Lush elephant grass grasslands and one-horned rhino territory"},
            {"name": "Wayanad Wildlife Sanctuary", "state": "Kerala", "vibe": "Verdant rainforests, spice hills, and wildlife trails"}
        ]
    },
    "waterfall/river/waterbody": {
        "theme": "Cascading Waterfalls & Serene Waterways",
        "regions": ["Meghalaya", "Kerala", "Karnataka", "Madhya Pradesh"],
        "destinations": [
            {"name": "Nohkalikai & Nohsngithiang Falls", "state": "Meghalaya", "vibe": "Spectacular cliff-edge waterfalls plunged into deep gorges"},
            {"name": "Alleppey Backwaters", "state": "Kerala", "vibe": "Tranquil palm-fringed lagoons and traditional houseboat cruises"},
            {"name": "Jog Falls", "state": "Karnataka", "vibe": "Towering segmented cataracts surrounded by Western Ghats greenery"}
        ]
    },
    "heritage/architecture": {
        "theme": "Grand Forts, Palaces & Monumental Architecture",
        "regions": ["Rajasthan", "Uttar Pradesh", "Karnataka", "Madhya Pradesh", "Gujarat"],
        "destinations": [
            {"name": "Jaipur & Udaipur", "state": "Rajasthan", "vibe": "Opulent palaces, hilltop forts, and intricate royal architecture"},
            {"name": "Hampi", "state": "Karnataka", "vibe": "UNESCO World Heritage Vijayanagara boulder-strewn ruins and grand stone chariot"},
            {"name": "Khajuraho", "state": "Madhya Pradesh", "vibe": "Exquisitely carved Nagara-style stone temples"},
            {"name": "Statue of Unity (Kevadia)", "state": "Gujarat", "vibe": "World's tallest monumental statue (182m) with panoramic Narmada views"}
        ]
    },
    "temple/spiritual": {
        "theme": "Sacred Temples & Spiritual Ghats",
        "regions": ["Uttar Pradesh", "Tamil Nadu", "Punjab", "Uttarakhand", "Odisha"],
        "destinations": [
            {"name": "Varanasi Ghats", "state": "Uttar Pradesh", "vibe": "Ancient Ganges riverfront, morning boat rides, and mesmerizing Ganga Aarti"},
            {"name": "Golden Temple (Amritsar)", "state": "Punjab", "vibe": "Gleaming sanctum surrounded by the sacred Amrit Sarovar"},
            {"name": "Madurai Meenakshi & Rameswaram", "state": "Tamil Nadu", "vibe": "Towering sculpted Dravidian gopurams and sacred ocean shrines"},
            {"name": "Rishikesh", "state": "Uttarakhand", "vibe": "Himalayan yoga retreat, serene river banks, and evening aarti"}
        ]
    }
}


def map_label_to_travel_category(label: str) -> str:
    """Map a fine-grained Places365 scene label to a high-level travel category."""
    label_lower = label.lower().replace(" ", "_")
    for travel_cat, keywords in TRAVEL_SCENE_MAPPING.items():
        for kw in keywords:
            if kw in label_lower:
                return travel_cat
    if "temple" in label_lower or "church" in label_lower or "mosque" in label_lower:
        return "temple/spiritual"
    if "water" in label_lower or "lake" in label_lower:
        return "waterfall/river/waterbody"
    if "forest" in label_lower or "park" in label_lower or "garden" in label_lower:
        return "forest/nature"
    if "mountain" in label_lower or "hill" in label_lower:
        return "mountain/hills"
    return "scenic landscape"


def get_indian_alternatives(travel_category: str, scene_label: str) -> Optional[Dict[str, Any]]:
    """Retrieve curated Indian travel alternatives matching a scene category."""
    label_lower = scene_label.lower().replace(" ", "_")
    if any(k in label_lower for k in ["snow", "ski", "ice", "glacier"]):
        return INDIAN_SCENE_ALTERNATIVES.get("mountain/snow")
    if any(k in label_lower for k in ["desert", "sand", "dune"]):
        return INDIAN_SCENE_ALTERNATIVES.get("desert")
    if travel_category in INDIAN_SCENE_ALTERNATIVES:
        return INDIAN_SCENE_ALTERNATIVES[travel_category]
    if "mountain" in travel_category or "hill" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("mountain/hills")
    if "beach" in travel_category or "coast" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("beach/coast")
    if "temple" in travel_category or "spiritual" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("temple/spiritual")
    if "heritage" in travel_category or "architecture" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("heritage/architecture")
    if "water" in travel_category or "river" in travel_category or "waterfall" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("waterfall/river/waterbody")
    if "forest" in travel_category or "nature" in travel_category:
        return INDIAN_SCENE_ALTERNATIVES.get("forest/nature")
    return None


def synthesize_scene_experience(top_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:

    """
    Synthesize multi-label Places365 predictions into a cohesive scene/vibe signal,
    and search Indian tourism data for relevant destinations matching that experience.
    """
    if not top_predictions:
        return {
            "vibe_summary": "scenic landscape",
            "experience_description": "beautiful scenic landscape",
            "relevant_regions": ["Uttarakhand", "Himachal Pradesh", "Kerala", "Sikkim"],
            "destinations": []
        }

    labels = [p.get("label", "").lower() for p in top_predictions]
    categories = [p.get("travel_category", "").lower() for p in top_predictions]

    # Detect multi-vibe signals
    has_mountain = any(k in l for l in labels for k in ["mountain", "cliff", "hill", "canyon", "ski", "snowfield"])
    has_valley = any("valley" in l for l in labels)
    has_rural = any(k in l for l in labels for k in ["village", "field", "pasture", "vineyard", "farm", "meadow", "rice_paddy", "hayfield"])
    has_snow = any(k in l for l in labels for k in ["snow", "ski", "ice", "glacier"])
    has_beach = any(k in l for l in labels for k in ["beach", "coast", "ocean", "seashore", "sand"])
    has_desert = any(k in l for l in labels for k in ["desert", "sand", "dune"])
    has_water = any(k in l for l in labels for k in ["waterfall", "river", "lake", "creek", "pond", "water"])
    has_forest = any(k in l for l in labels for k in ["forest", "jungle", "rainforest", "tree", "garden"])
    has_spiritual = any(k in l for l in labels for k in ["temple", "church", "mosque", "shrine", "monastery"])
    has_heritage = any(k in l for l in labels for k in ["palace", "fort", "castle", "monument", "ruins", "arch"])

    # 1. Compose Vibe Summary
    vibe_tokens = []
    if has_rural:
        vibe_tokens.append("scenic rural")
    if has_valley:
        vibe_tokens.append("valley")
    if has_mountain or "mountain/hills" in categories:
        vibe_tokens.append("mountain")
    if has_snow:
        vibe_tokens.append("snowy peaks")
    if has_beach:
        vibe_tokens.append("tropical coast")
    if has_desert:
        vibe_tokens.append("desert dunes")
    if has_water:
        vibe_tokens.append("waterfalls & lakes")
    if has_forest:
        vibe_tokens.append("dense forest")
    if has_spiritual:
        vibe_tokens.append("spiritual & sacred")
    if has_heritage:
        vibe_tokens.append("heritage & architecture")

    if not vibe_tokens:
        top_name = top_predictions[0].get("display_name", "Scenic Landscape").lower()
        vibe_tokens.append(top_name)

    vibe_summary = " + ".join(vibe_tokens)

    # 2. Compose natural experience description
    if has_valley and (has_mountain or has_rural):
        exp_desc = "beautiful valley and mountain landscape"
        if has_rural:
            exp_desc += " with scenic rural countryside"
    elif has_beach:
        exp_desc = "serene coastal shoreline and beach vibe"
    elif has_desert:
        exp_desc = "golden sand dunes and desert landscape"
    elif has_snow:
        exp_desc = "snowy alpine peaks and winter mountain scenery"
    elif has_forest or has_water:
        exp_desc = "lush green forests, waterfalls, and natural water bodies"
    elif has_spiritual:
        exp_desc = "sacred architecture and spiritual sanctuary"
    elif has_heritage:
        exp_desc = "historic forts, palaces, and monumental heritage"
    else:
        exp_desc = f"picturesque {top_predictions[0].get('display_name', 'landscape').lower()} scenery"

    # 3. Determine relevant Indian regions
    if has_mountain or has_valley or has_rural:
        if has_snow:
            relevant_regions = ["Kashmir", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Ladakh"]
        else:
            relevant_regions = ["Uttarakhand", "Himachal Pradesh", "Kashmir", "Sikkim", "Northeast India"]
    elif has_beach:
        relevant_regions = ["Goa", "Andaman & Nicobar", "Kerala", "Karnataka", "Puducherry"]
    elif has_desert:
        relevant_regions = ["Rajasthan", "Gujarat"]
    elif has_water:
        relevant_regions = ["Meghalaya", "Kerala", "Karnataka", "Uttarakhand"]
    elif has_forest:
        relevant_regions = ["Uttarakhand", "Madhya Pradesh", "Assam", "Kerala"]
    elif has_spiritual:
        relevant_regions = ["Uttar Pradesh", "Tamil Nadu", "Punjab", "Uttarakhand", "Odisha"]
    elif has_heritage:
        relevant_regions = ["Rajasthan", "Karnataka", "Madhya Pradesh", "Uttar Pradesh", "Gujarat"]
    else:
        relevant_regions = ["Uttarakhand", "Himachal Pradesh", "Kerala", "Rajasthan"]

    # 4. Search Indian Tourism Data from TourismService for real matching destinations
    matched_destinations = []
    try:
        from backend.services.tourism_service import tourism_service
        # Search query using primary vibe signals
        search_terms = []
        if has_valley:
            search_terms.append("valley")
        if has_mountain:
            search_terms.append("mountain")
            search_terms.append("hill")
        if has_rural:
            search_terms.append("meadow")
            search_terms.append("plantation")
        if has_water:
            search_terms.append("waterfall")
            search_terms.append("lake")
        if has_beach:
            search_terms.append("beach")
        if has_desert:
            search_terms.append("desert")

        seen_names = set()
        for term in search_terms:
            hits = tourism_service.search_destinations(query=term, limit=4)
            for h in hits:
                d_name = h.get("destination_name")
                if d_name and d_name not in seen_names:
                    seen_names.add(d_name)
                    matched_destinations.append({
                        "name": d_name,
                        "state": h.get("state"),
                        "city_district": h.get("city_district"),
                        "category": h.get("category"),
                        "rating": h.get("rating"),
                        "vibe": h.get("description") or f"Scenic {term} destination in {h.get('state')}"
                    })
                if len(matched_destinations) >= 6:
                    break
            if len(matched_destinations) >= 6:
                break
    except Exception as t_err:
        logger.debug(f"Tourism service lookup in synthesize_scene_experience skipped: {t_err}")

    return {
        "vibe_summary": vibe_summary,
        "experience_description": exp_desc,
        "relevant_regions": relevant_regions,
        "destinations": matched_destinations
    }


def format_display_name(label: str) -> str:
    """Format raw Places365 label (e.g. /t/temple/south_asia) into clean English."""
    cleaned = label.lstrip("/").replace("_", " ")
    parts = [p for p in cleaned.split("/") if p and len(p) > 1]
    if parts:
        return " ".join(parts).title()
    return cleaned.title()



class SceneService:
    """
    Pretrained Places365 Scene Recognition Inference Service.
    Loads ResNet-18 Places365 classifier once into memory.
    Supports Apple Silicon MPS, CUDA, and CPU inference.
    """

    def __init__(self):
        self.device = self._select_device()
        self.model: Optional[nn.Module] = None
        self.classes: List[str] = []
        self.is_loaded: bool = False
        self._ensure_resources()
        self._load_model()

    def _select_device(self) -> torch.device:
        """Select fastest available compute device (MPS > CUDA > CPU)."""
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("SceneService using Apple Silicon GPU (MPS).")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("SceneService using NVIDIA CUDA GPU.")
        else:
            device = torch.device("cpu")
            logger.info("SceneService using CPU.")
        return device

    def _ensure_resources(self):
        """Ensure categories and model checkpoint exist, downloading from official source if needed."""
        os.makedirs(MODELS_DIR, exist_ok=True)

        # 1. Categories file
        if not os.path.exists(CATEGORIES_PATH):
            logger.info(f"Places365 categories file not found locally. Downloading from {OFFICIAL_CATEGORIES_URL}...")
            try:
                urllib.request.urlretrieve(OFFICIAL_CATEGORIES_URL, CATEGORIES_PATH)
                logger.info(f"Downloaded categories to {CATEGORIES_PATH}")
            except Exception as e:
                logger.error(f"Failed to download Places365 categories: {e}")

        # 2. Checkpoint file
        if not os.path.exists(PRIMARY_CHECKPOINT_PATH) and not os.path.exists(FALLBACK_CHECKPOINT_PATH):
            logger.info(f"Places365 checkpoint not found locally. Downloading from {OFFICIAL_CHECKPOINT_URL}...")
            try:
                urllib.request.urlretrieve(OFFICIAL_CHECKPOINT_URL, PRIMARY_CHECKPOINT_PATH)
                logger.info(f"Downloaded checkpoint to {PRIMARY_CHECKPOINT_PATH}")
            except Exception as e:
                logger.error(f"Failed to download Places365 checkpoint: {e}")

    def _load_categories(self):
        """Parse categories_places365.txt into ordered class list."""
        if not os.path.exists(CATEGORIES_PATH):
            logger.warning(f"Categories file missing at {CATEGORIES_PATH}")
            self.classes = []
            return

        try:
            classes = []
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        raw_class = parts[0][3:] if len(parts[0]) > 3 else parts[0]
                        classes.append(raw_class)
            self.classes = classes
            logger.info(f"Loaded {len(self.classes)} Places365 scene categories.")
        except Exception as e:
            logger.error(f"Error reading categories file: {e}")
            self.classes = []

    def _load_model(self):
        """Load Places365 ResNet-18 weights into memory once."""
        if self.is_loaded:
            return

        self._load_categories()

        candidate_paths = [
            os.path.join(MODELS_DIR, "resnet18_places365.pth.tar"),
            os.path.join(MODELS_DIR, "resnet18_places365.pth"),
            os.path.join(PRETRAINED_DIR, "resnet18_places365.pth.tar"),
            os.path.join(PRETRAINED_DIR, "resnet18_places365.pth")
        ]
        ckpt_path = None
        for p in candidate_paths:
            if os.path.exists(p) and os.path.getsize(p) > 1000000:
                ckpt_path = p
                break

        if not ckpt_path:
            logger.error(f"Cannot load Places365 model: no valid checkpoint found in {candidate_paths}")
            return

        try:
            logger.info(f"Loading Places365 ResNet-18 model from {ckpt_path} onto {self.device}...")
            # Instantiate ResNet-18 with 365 classes
            model = models.resnet18(num_classes=365)

            checkpoint = torch.load(ckpt_path, map_location=self.device, weights_only=False)
            state_dict = checkpoint.get("state_dict", checkpoint)

            # Strip 'module.' prefix from DataParallel training
            cleaned_state_dict = {}
            for k, v in state_dict.items():
                clean_k = k.replace("module.", "")
                cleaned_state_dict[clean_k] = v

            model.load_state_dict(cleaned_state_dict)
            model.to(self.device)
            model.eval()

            # Freeze parameters for fast inference
            for p in model.parameters():
                p.requires_grad = False

            self.model = model
            self.is_loaded = True
            logger.info(f"Successfully loaded Places365 ResNet-18 on {self.device} in eval mode.")
        except Exception as e:
            logger.error(f"Failed to load Places365 model: {e}")
            self.model = None
            self.is_loaded = False

    def _prepare_image(self, image_input: Union[str, bytes, BinaryIO, Image.Image]) -> Image.Image:
        """Convert various input types to a PIL RGB Image."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        elif isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"Image path not found: {image_input}")
            return Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")
        elif hasattr(image_input, "read"):
            content = image_input.read()
            if isinstance(content, str):
                content = content.encode("latin1")
            return Image.open(io.BytesIO(content)).convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

    def recognize_scene(
        self,
        image_input: Union[str, bytes, BinaryIO, Image.Image],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Recognize scene type from an input image using pretrained Places365 ResNet-18.

        Args:
            image_input: File path, bytes, file-like object, or PIL Image.
            top_k: Number of top scene predictions to return (default: 5).

        Returns:
            Structured dictionary with scene prediction, confidence, travel category, and top predictions.
        """
        if not self.is_loaded or self.model is None:
            self._load_model()
            if not self.is_loaded or self.model is None:
                return {
                    "status": "error",
                    "error": "Places365 model is not available or failed to load.",
                    "scene": None,
                    "label": None,
                    "confidence": 0.0,
                    "top_predictions": []
                }

        try:
            image = self._prepare_image(image_input)
            tensor = SCENE_TRANSFORM(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                logits = self.model(tensor)
                probabilities = torch.softmax(logits, dim=1).squeeze(0)

            top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(self.classes) or 365))

            top_predictions = []
            for rank, (prob_tensor, idx_tensor) in enumerate(zip(top_probs, top_indices), 1):
                idx = int(idx_tensor.item())
                prob = float(prob_tensor.item())
                label = self.classes[idx] if idx < len(self.classes) else f"class_{idx}"
                display_name = format_display_name(label)
                travel_cat = map_label_to_travel_category(label)

                top_predictions.append({
                    "rank": rank,
                    "label": label,
                    "display_name": display_name,
                    "confidence": round(prob, 4),
                    "confidence_pct": round(prob * 100.0, 2),
                    "travel_category": travel_cat
                })

            top_1 = top_predictions[0] if top_predictions else {}
            top_scene_label = top_1.get("label", "unknown")
            top_travel_cat = top_1.get("travel_category", "scenic landscape")
            indian_alts = get_indian_alternatives(top_travel_cat, top_scene_label)
            scene_exp = synthesize_scene_experience(top_predictions)

            return {
                "status": "success",
                "scene": top_scene_label,
                "label": top_scene_label,
                "display_name": top_1.get("display_name", "Unknown"),
                "travel_category": top_travel_cat,
                "confidence": top_1.get("confidence", 0.0),
                "confidence_pct": top_1.get("confidence_pct", 0.0),
                "top_predictions": top_predictions,
                "suggested_indian_alternatives": indian_alts,
                "scene_experience": scene_exp,
                "device": str(self.device)
            }

        except Exception as e:
            logger.error(f"Scene recognition inference error: {e}")
            return {
                "status": "error",
                "error": f"Inference failed: {str(e)}",
                "scene": None,
                "label": None,
                "confidence": 0.0,
                "top_predictions": [],
                "scene_experience": None
            }


    def get_model_status(self) -> Dict[str, Any]:
        """Return diagnostic status of the Places365 scene service."""
        return {
            "model_loaded": self.is_loaded,
            "device": str(self.device),
            "categories_count": len(self.classes),
            "checkpoint_path": PRIMARY_CHECKPOINT_PATH if os.path.exists(PRIMARY_CHECKPOINT_PATH) else FALLBACK_CHECKPOINT_PATH
        }

# Singleton service instance
scene_service = SceneService()
