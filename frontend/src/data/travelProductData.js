// Commercial AI Travel Platform Product Dataset

export const FEATURED_DESTINATIONS = [
  {
    id: "IND_QUTUB_MINAR",
    name: "Qutub Minar",
    tagline: "World's Tallest Brick Minaret",
    state: "Delhi",
    city: "New Delhi",
    category: "Heritage Monument",
    rating: 4.8,
    reviews_count: 119322,
    price_per_person: "₹40 - ₹600",
    image_url: "https://images.unsplash.com/photo-1597040663442-9972c3d0b284?q=80&w=1000&auto=format&fit=crop",
    description: "A 73-metre UNESCO World Heritage minaret constructed in 1192, featuring intricate red sandstone carvings and Islamic calligraphy.",
    best_time: "Oct – Mar",
    duration: "2-3 Hours",
    highlights: ["Iron Pillar of Delhi", "Alai Darwaza", "Qutb Complex Gardens"]
  },
  {
    id: "IND_TAJ_MAHAL",
    name: "Taj Mahal",
    tagline: "Iconic Monument of Eternal Love",
    state: "Uttar Pradesh",
    city: "Agra",
    category: "World Wonder",
    rating: 4.9,
    reviews_count: 245100,
    price_per_person: "₹50 - ₹1,100",
    image_url: "https://images.unsplash.com/photo-1564507592333-c60657eea523?q=80&w=1000&auto=format&fit=crop",
    description: "An architectural masterpiece in white marble built by Shah Jahan in memory of his beloved wife Mumtaz Mahal.",
    best_time: "Nov – Feb",
    duration: "3-4 Hours",
    highlights: ["Sunrise Marble Reflections", "Mehtab Bagh Views", "Yamuna Riverfront"]
  },
  {
    id: "IND_HAWA_MAHAL",
    name: "Hawa Mahal",
    tagline: "Palace of 953 Honeycomb Windows",
    state: "Rajasthan",
    city: "Jaipur",
    category: "Royal Architecture",
    rating: 4.6,
    reviews_count: 87400,
    price_per_person: "₹50 - ₹200",
    image_url: "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?q=80&w=1000&auto=format&fit=crop",
    description: "Constructed in 1799 from pink sandstone, designed to allow royal ladies to observe street festivals undetected.",
    best_time: "Oct – Mar",
    duration: "1-2 Hours",
    highlights: ["Tattoo Cafe Viewpoint", "Inner Courtyard", "Jharokha Architecture"]
  },
  {
    id: "IND_INDIA_GATE",
    name: "India Gate",
    tagline: "National Memorial & Boulevard",
    state: "Delhi",
    city: "New Delhi",
    category: "War Memorial",
    rating: 4.7,
    reviews_count: 189200,
    price_per_person: "Free Entry",
    image_url: "https://images.unsplash.com/photo-1587474260584-136574528ed5?q=80&w=1000&auto=format&fit=crop",
    description: "A majestic 42-metre war memorial standing at the heart of Rajpath, illuminated beautifully at dusk.",
    best_time: "Evening All Year",
    duration: "1-2 Hours",
    highlights: ["Kartavya Path Promenade", "Amar Jawan Jyoti", "Boating Lawns"]
  },
  {
    id: "IND_CHARMINAR",
    name: "Charminar",
    tagline: "Heart of Historic Hyderabad",
    state: "Telangana",
    city: "Hyderabad",
    category: "Heritage Mosque",
    rating: 4.5,
    reviews_count: 98100,
    price_per_person: "₹25 - ₹300",
    image_url: "https://images.unsplash.com/photo-1605649487212-47bdab064df7?q=80&w=1000&auto=format&fit=crop",
    description: "Built in 1591, this quadrangle structure with four grand minarets overlooks the bustling Laad Bazaar.",
    best_time: "Oct – Mar",
    duration: "2 Hours",
    highlights: ["Laad Bazaar Pearl Shopping", "Irani Chai Spot", "Upper Mosque Terrace"]
  },
  {
    id: "IND_GATEWAY_OF_INDIA",
    name: "Gateway of India",
    tagline: "Waterfront Arch of Mumbai",
    state: "Maharashtra",
    city: "Mumbai",
    category: "Coastal Landmark",
    rating: 4.7,
    reviews_count: 215000,
    price_per_person: "Free Entry",
    image_url: "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?q=80&w=1000&auto=format&fit=crop",
    description: "Built to commemorate the visit of King George V, offering ferry rides to Elephanta Caves.",
    best_time: "Nov – Feb",
    duration: "1-2 Hours",
    highlights: ["Harbor Ferries", "Taj Mahal Palace View", "Arabian Sea Sunset"]
  }
];

export const LUXURY_HOTELS = [
  {
    id: "HOTEL_RAMBAGH_PALACE",
    name: "Rambagh Palace, Jaipur",
    tagline: "The Jewel of Jaipur — Former Royal Residence",
    city: "Jaipur",
    state: "Rajasthan",
    rating: 4.9,
    reviews: 4210,
    price_per_night: "₹45,000",
    image_url: "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1000&auto=format&fit=crop",
    amenities: ["Palace Gardens", "Royal Spa", "Fine Dining", "Indoor Pool"],
    distance_to_monument: "4.2 km to Hawa Mahal"
  },
  {
    id: "HOTEL_AMARVILAS",
    name: "The Oberoi Amarvilas, Agra",
    tagline: "Uninterrupted Taj Mahal Views From Every Room",
    city: "Agra",
    state: "Uttar Pradesh",
    rating: 4.95,
    reviews: 6180,
    price_per_night: "₹52,000",
    image_url: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1000&auto=format&fit=crop",
    amenities: ["Private Balcony Views", "Tiered Pool", "Butler Service", "Buggy Transfers"],
    distance_to_monument: "600m to Taj Mahal"
  },
  {
    id: "HOTEL_TAJ_PALACE_MUMBAI",
    name: "The Taj Mahal Palace, Mumbai",
    tagline: "Legendary Waterfront Grand Hotel",
    city: "Mumbai",
    state: "Maharashtra",
    rating: 4.85,
    reviews: 12400,
    price_per_night: "₹38,000",
    image_url: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1000&auto=format&fit=crop",
    amenities: ["Sea Views", "11 Restaurants", "Jiva Spa", "Art Collection"],
    distance_to_monument: "Adjacent to Gateway of India"
  }
];

export const CURATED_TRIPS = [
  {
    id: "TRIP_GOLDEN_TRIANGLE",
    title: "Golden Triangle Heritage Express",
    days: "5 Days / 4 Nights",
    cities: ["Delhi", "Agra", "Jaipur"],
    image_url: "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?q=80&w=1000&auto=format&fit=crop",
    highlights: ["Qutub Minar Guided Walk", "Sunrise at Taj Mahal", "Pink City Amber Fort Tour"],
    price_start: "₹28,500 / person",
    rating: 4.9
  },
  {
    id: "TRIP_ROYAL_RAJASTHAN",
    title: "Royal Forts & Palaces Luxury Trail",
    days: "7 Days / 6 Nights",
    cities: ["Jaipur", "Udaipur", "Jodhpur"],
    image_url: "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?q=80&w=1000&auto=format&fit=crop",
    highlights: ["Hawa Mahal Rooftop Tea", "Lake Pichola Sunset Boat Cruise", "Mehrangarh Fort Zip Line"],
    price_start: "₹45,000 / person",
    rating: 4.95
  }
];

export const TRAVEL_ARTICLES = [
  {
    id: "BLOG_TAJ_PHOTOGRAPHY",
    title: "The Ultimate Photography Guide to Capturing Taj Mahal at Sunrise",
    author: "Elena Rostova",
    read_time: "5 min read",
    date: "Aug 28, 2026",
    category: "Photography & Tips",
    image_url: "https://images.unsplash.com/photo-1564507592333-c60657eea523?q=80&w=1000&auto=format&fit=crop",
    snippet: "Best lens choices, hidden angles from Mehtab Bagh, and timing secrets to avoid crowds while shooting Agra's marble wonder."
  },
  {
    id: "BLOG_DELHI_FOOD",
    title: "10 Historic Culinary Spots Near Qutub Minar & Mehrauli Archeological Park",
    author: "Kabir Mehta",
    read_time: "7 min read",
    date: "Aug 15, 2026",
    category: "Culture & Cuisine",
    image_url: "https://images.unsplash.com/photo-1597040663442-9972c3d0b284?q=80&w=1000&auto=format&fit=crop",
    snippet: "From Mughlai kebabs to rooftop cafe views, explore the culinary heritage surrounding Delhi's 12th-century minaret."
  }
];

export const AI_SUGGESTION_PROMPTS = [
  "Plan a 5-day luxury Golden Triangle trip for a couple",
  "Find boutique heritage hotels near Taj Mahal with pool",
  "What is the best time to visit Hawa Mahal for photography?",
  "Recommend a 3-day cultural itinerary in Delhi with historical dining"
];
