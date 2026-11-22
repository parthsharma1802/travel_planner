// Phase 5 Realistic Mock Dataset for Indian Monuments & Travel Destinations

export const CANONICAL_LANDMARKS = [
  {
    id: "IND_QUTUB_MINAR",
    name: "Qutub Minar",
    class_id: 19,
    state: "Delhi",
    city: "New Delhi",
    category: "Historical Minaret",
    rating: 4.5,
    reviews_count: 119322,
    image_url: "https://images.unsplash.com/photo-1597040663442-9972c3d0b284?q=80&w=1000&auto=format&fit=crop",
    description: "A 73-metre high minaret constructed in 1192 by Qutab-ud-din Aibak, part of the UNESCO World Heritage Site Qutb Complex.",
    price_info: "₹40 (Indians) | ₹600 (Foreigners)",
    ideal_season: "October to March",
    similarity_score: 0.9967,
    top_3_classes: [
      { name: "Qutub Minar", confidence: 99.67 },
      { name: "Iron Pillar", confidence: 0.16 },
      { name: "Gateway of India", confidence: 0.04 }
    ]
  },
  {
    id: "IND_TAJ_MAHAL",
    name: "Taj Mahal",
    class_id: 22,
    state: "Uttar Pradesh",
    city: "Agra",
    category: "Mughal Architecture",
    rating: 4.8,
    reviews_count: 245100,
    image_url: "https://images.unsplash.com/photo-1564507592333-c60657eea523?q=80&w=1000&auto=format&fit=crop",
    description: "An immense mausoleum of white marble, built in Agra between 1631 and 1648 by order of the Mughal emperor Shah Jahan.",
    price_info: "₹50 (Indians) | ₹1,100 (Foreigners)",
    ideal_season: "November to February",
    similarity_score: 0.9845,
    top_3_classes: [
      { name: "Taj Mahal", confidence: 98.45 },
      { name: "Humayun's Tomb", confidence: 1.12 },
      { name: "Fatehpur Sikri", confidence: 0.35 }
    ]
  },
  {
    id: "IND_HAWA_MAHAL",
    name: "Hawa Mahal",
    class_id: 11,
    state: "Rajasthan",
    city: "Jaipur",
    category: "Palace",
    rating: 4.4,
    reviews_count: 87400,
    image_url: "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?q=80&w=1000&auto=format&fit=crop",
    description: "The Palace of Breeze, constructed in 1799 from red and pink sandstone with 953 intricate small windows called Jharokhas.",
    price_info: "₹50 (Indians) | ₹200 (Foreigners)",
    ideal_season: "October to March",
    similarity_score: 0.9712,
    top_3_classes: [
      { name: "Hawa Mahal", confidence: 97.12 },
      { name: "Amer Fort", confidence: 2.10 },
      { name: "City Palace", confidence: 0.65 }
    ]
  },
  {
    id: "IND_INDIA_GATE",
    name: "India Gate",
    class_id: 13,
    state: "Delhi",
    city: "New Delhi",
    category: "War Memorial",
    rating: 4.6,
    reviews_count: 189200,
    image_url: "https://images.unsplash.com/photo-1587474260584-136574528ed5?q=80&w=1000&auto=format&fit=crop",
    description: "A prominent war memorial located astride the Rajpath, standing as a tribute to 84,000 soldiers of the British Indian Army.",
    price_info: "Free Entry",
    ideal_season: "October to March",
    similarity_score: 0.9650,
    top_3_classes: [
      { name: "India Gate", confidence: 96.50 },
      { name: "Gateway of India", confidence: 2.80 },
      { name: "Red Fort", confidence: 0.50 }
    ]
  },
  {
    id: "IND_CHARMINAR",
    name: "Charminar",
    class_id: 4,
    state: "Telangana",
    city: "Hyderabad",
    category: "Historic Mosque",
    rating: 4.5,
    reviews_count: 98100,
    image_url: "https://images.unsplash.com/photo-1605649487212-47bdab064df7?q=80&w=1000&auto=format&fit=crop",
    description: "Built in 1591, Charminar is a landmark monument and mosque with four grand arches and minarets located in the heart of Hyderabad.",
    price_info: "₹25 (Indians) | ₹300 (Foreigners)",
    ideal_season: "October to March",
    similarity_score: 0.9580,
    top_3_classes: [
      { name: "Charminar", confidence: 95.80 },
      { name: "Golconda Fort", confidence: 3.10 },
      { name: "Qutub Shahi Tombs", confidence: 0.95 }
    ]
  },
  {
    id: "IND_GATEWAY_OF_INDIA",
    name: "Gateway of India",
    class_id: 9,
    state: "Maharashtra",
    city: "Mumbai",
    category: "Arch Monument",
    rating: 4.6,
    reviews_count: 215000,
    image_url: "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?q=80&w=1000&auto=format&fit=crop",
    description: "An 26-metre high arch monument built in the early 20th century in Mumbai to commemorate the landing of King-Emperor George V.",
    price_info: "Free Entry",
    ideal_season: "November to February",
    similarity_score: 0.9520,
    top_3_classes: [
      { name: "Gateway of India", confidence: 95.20 },
      { name: "India Gate", confidence: 3.50 },
      { name: "Taj Mahal Palace", confidence: 1.10 }
    ]
  }
];

export const MOCK_FILTER_CATEGORIES = [
  "All Monuments",
  "UNESCO World Heritage",
  "Mughal Architecture",
  "Palaces & Forts",
  "War Memorials",
  "South Indian Temples"
];
