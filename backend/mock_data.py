import urllib.parse

def create_search_link(platform: str, query: str) -> str:
    encoded_query = urllib.parse.quote_plus(query)
    platform_lower = platform.lower()
    if "amazon" in platform_lower:
        return f"https://www.amazon.com/s?k={encoded_query}"
    elif "ikea" in platform_lower:
        return f"https://www.ikea.com/us/en/search/?q={encoded_query}"
    elif "etsy" in platform_lower:
        return f"https://www.etsy.com/search?q={encoded_query}"
    elif "target" in platform_lower:
        return f"https://www.target.com/s?searchTerm={encoded_query}"
    elif "wayfair" in platform_lower:
        return f"https://www.wayfair.com/keyword.php?keyword={encoded_query}"
    elif "tanishq" in platform_lower:
        return f"https://www.tanishq.co.in/shop?q={encoded_query}"
    elif "blue nile" in platform_lower:
        return f"https://www.bluenile.com/search?q={encoded_query}"
    else:
        return f"https://www.google.com/search?tbm=shop&q={encoded_query}"

# Realistic Mock Catalog for Intelligent Offline/Fallback Planner Generation
HOME_INTERIOR_CATALOG = {
    "Living Room": [
        {"name": "Nordic Fabric 3-Seater Sofa", "category": "Seating", "base_price": 450, "platform": "IKEA", "search": "modern 3 seater sofa", "reason": "Durable textured fabric with ergonomic foam cushions for long-term comfort"},
        {"name": "Minimalist Solid Oak Coffee Table", "category": "Tables", "base_price": 120, "platform": "Target", "search": "solid oak coffee table modern", "reason": "Warm natural wood grain finish with rounded corners for child-safe space"},
        {"name": "Boho Geometric Handwoven Area Rug (5x7)", "category": "Textiles & Rugs", "base_price": 85, "platform": "Amazon", "search": "geometric handwoven area rug 5x7", "reason": "Soft pile with stain-resistant fibers, anchors the room visually"},
        {"name": "Adjustable Matte Black Floor Arc Lamp", "category": "Lighting", "base_price": 65, "platform": "Target", "search": "matte black floor arc lamp", "reason": "Provides direct and ambient warm illumination with dimmer switch"},
        {"name": "Floating Media Entertainment Console (60 inch)", "category": "Storage", "base_price": 160, "platform": "Wayfair", "search": "floating tv console 60 inch", "reason": "Sleek wall-mounted design with cable management channels"},
        {"name": "Velvet Accent Armchair", "category": "Seating", "base_price": 175, "platform": "Amazon", "search": "velvet accent armchair cozy", "reason": "Adds a pop of luxury texture and comfortable extra reading seating"},
        {"name": "Linen Blackout Curtains (Set of 2)", "category": "Window Treatments", "base_price": 45, "platform": "Amazon", "search": "linen blackout curtains set of 2", "reason": "Thermal insulated linen blend for sound dampening and light control"},
        {"name": "Ceramic Decorative Vase Trio", "category": "Decor", "base_price": 35, "platform": "Etsy", "search": "minimalist ceramic vase set", "reason": "Artisanal neutral tones to style the coffee table and media console"}
    ],
    "Bedroom": [
        {"name": "Solid Wood Queen Bed Frame with Headboard", "category": "Beds", "base_price": 380, "platform": "Wayfair", "search": "queen bed frame with headboard wood", "reason": "Sturdy noise-free wooden slats with warm mid-century modern aesthetic"},
        {"name": "10-Inch Cooling Gel Memory Foam Mattress", "category": "Mattresses", "base_price": 290, "platform": "Amazon", "search": "cooling gel memory foam mattress queen", "reason": "Pressure-relieving medium-firm support with breathable cooling cover"},
        {"name": "Twin Nightstand Pair with Drawer", "category": "Storage", "base_price": 110, "platform": "Target", "search": "modern nightstand set of 2 with drawers", "reason": "Compact bedside storage with built-in cable pass-throughs"},
        {"name": "100% Washed Cotton Duvet Cover Set", "category": "Bedding", "base_price": 55, "platform": "Amazon", "search": "100 washed cotton duvet cover set", "reason": "Breathable, pre-washed softness that gets softer with every wash"},
        {"name": "Dimmable Touch Bedside Lamps (Set of 2)", "category": "Lighting", "base_price": 42, "platform": "Amazon", "search": "touch bedside lamps with usb port set of 2", "reason": "3-way dimming with built-in USB-C fast charging ports"},
        {"name": "Full Length Arch Floor Mirror", "category": "Decor", "base_price": 95, "platform": "Target", "search": "arch full length floor mirror aluminum", "reason": "Expands natural light and gives the bedroom an open, airy feel"},
        {"name": "6-Drawer Double Dresser", "category": "Storage", "base_price": 240, "platform": "IKEA", "search": "6 drawer double dresser white wood", "reason": "Spacious smooth-gliding drawers for clothing and linens"}
    ],
    "Kitchen": [
        {"name": "Extendable Solid Birch Dining Table", "category": "Dining Tables", "base_price": 299, "platform": "IKEA", "search": "extendable dining table solid wood", "reason": "Accommodates 4 to 8 guests seamlessly with easy pull-out leaf"},
        {"name": "Modern Ergonomic Dining Chairs (Set of 4)", "category": "Dining Seating", "base_price": 160, "platform": "Wayfair", "search": "dining chairs set of 4 modern wood legs", "reason": "Wipe-clean curved molded shells with solid beech wood legs"},
        {"name": "Pendant Glass & Brass Island Lights (Set of 2)", "category": "Lighting", "base_price": 75, "platform": "Amazon", "search": "glass pendant lights kitchen island set of 2", "reason": "Warm industrial brass fixtures with seeded glass shades"},
        {"name": "Bamboo Kitchen Baker's Rack & Microwave Cart", "category": "Storage", "base_price": 89, "platform": "Target", "search": "kitchen bakers rack microwave stand bamboo", "reason": "Multi-tier utility storage with side hooks for utensils"},
        {"name": "Non-Slip Anti-Fatigue Cushioned Kitchen Mat Set", "category": "Comfort & Rugs", "base_price": 38, "platform": "Amazon", "search": "anti fatigue kitchen mats set of 2 cushioned", "reason": "Ergonomic high-density foam alleviates joint pressure during cooking"}
    ]
}

PARTY_CATALOG = {
    "Birthday": {
        "Venue": [
            {"name": "Private Loft or Garden Event Space Rental (4 hrs)", "base_pct": 0.35, "platform": "Peerspace", "search": "birthday party venue rental", "reason": "Flexible party space with sound system and ambient lighting"},
            {"name": "Cozy Community Hall / Park Pavilion Reservation", "base_pct": 0.20, "platform": "Local Municipal", "search": "park pavilion community event hall", "reason": "Spacious and highly budget-friendly with outdoor/indoor flex"}
        ],
        "Catering": [
            {"name": "Gourmet Finger Foods & Sliders Buffet", "base_pct": 0.30, "platform": "Local Catering", "search": "party catering finger foods sliders platter", "reason": "Crowd-pleasing varieties with vegetarian and gluten-free choices"},
            {"name": "Custom 2-Tier Celebration Cake & Dessert Board", "base_pct": 0.10, "platform": "Etsy Bakery", "search": "custom artisan birthday cake", "reason": "Photogenic centerpiece dessert tailored to party theme"}
        ],
        "Decoration": [
            {"name": "Custom Balloon Arch & Shimmer Backdrop Kit", "base_pct": 0.10, "platform": "Amazon", "search": "diy balloon arch kit metallic backdrop", "reason": "Vibrant Instagram-worthy photo zone with matching banner"},
            {"name": "Ambient LED Fairy String & Uplighting Pack", "base_pct": 0.05, "platform": "Amazon", "search": "led uplighting battery string lights party", "reason": "Transforms any room vibe from daytime to evening party mode"}
        ],
        "Entertainment": [
            {"name": "Professional DJ & Portable Sound System (3 hrs)", "base_pct": 0.15, "platform": "GigSalad", "search": "party dj event sound lighting rental", "reason": "Keeps the crowd engaged with curated playlists and microphones"},
            {"name": "DIY Bluetooth Party Speaker & Karaoke Mic Duo", "base_pct": 0.06, "platform": "Target", "search": "portable party speaker with wireless mic bluetooth", "reason": "Fun interactive karaoke setup within a strict budget"}
        ]
    },
    "Wedding": {
        "Venue": [
            {"name": "Charming Rustic Barn or Vineyard Venue", "base_pct": 0.40, "platform": "WeddingWire", "search": "rustic barn wedding venue rental", "reason": "Picturesque setting providing ceremony and reception spaces"}
        ],
        "Catering": [
            {"name": "3-Course Plated Dinner & Cocktail Hors d'oeuvres", "base_pct": 0.32, "platform": "Local Catering", "search": "wedding catering plated dinner packages", "reason": "High-end dining experience with champagne toast"}
        ],
        "Decoration": [
            {"name": "Silk Floral Arch & Table Centerpieces Ensemble", "base_pct": 0.14, "platform": "Etsy", "search": "wedding floral arch arrangements centerpieces", "reason": "Lush romantic botanical styling without exorbitant fresh flower markup"}
        ],
        "Entertainment": [
            {"name": "Live Acoustic Duo & Reception DJ Package", "base_pct": 0.14, "platform": "The Knot", "search": "wedding live musician dj package", "reason": "Romantic live ceremony music followed by energetic dance reception"}
        ]
    },
    "Corporate": {
        "Venue": [
            {"name": "Executive Conference Hall / Rooftop Lounge", "base_pct": 0.40, "platform": "Peerspace", "search": "corporate mixer rooftop venue rental", "reason": "Professional AV capabilities and panoramic networking space"}
        ],
        "Catering": [
            {"name": "Artisanal Canapés & Premium Barista Station", "base_pct": 0.35, "platform": "Local Catering", "search": "corporate event canapes charcuterie catering", "reason": "Clean easy-to-eat bites while mingling and networking"}
        ],
        "Decoration": [
            {"name": "Branded Step-and-Repeat Backdrop & Modern Podium", "base_pct": 0.12, "platform": "Amazon", "search": "custom step and repeat backdrop banner stand", "reason": "Polished corporate presence for press and employee social shares"}
        ],
        "Entertainment": [
            {"name": "Guest Keynote Speaker / Team Trivia Facilitator", "base_pct": 0.13, "platform": "Local Agency", "search": "corporate trivia host event emcee", "reason": "Engaging team bonding without awkward corporate downtime"}
        ]
    }
}

JEWELRY_CATALOG = [
    {
        "name": "18K Gold Plated Paperclip Chain Link Necklace",
        "category": "Necklace",
        "styles": ["Minimalist", "Contemporary", "Casual"],
        "occasions": ["Casual", "Office", "Cocktail"],
        "materials": ["Yellow Gold"],
        "price": 48.0,
        "platform": "Etsy",
        "search": "18k gold plated paperclip chain necklace",
        "reason": "Trendy yet timeless layering staple that elevates both crisp blouses and evening tops"
    },
    {
        "name": "Sparkling Moissanite Solitaire Drop Earrings",
        "category": "Earrings",
        "styles": ["Classic", "Minimalist", "Statement"],
        "occasions": ["Wedding", "Cocktail", "Festive"],
        "materials": ["White Gold / Silver", "Diamond"],
        "price": 85.0,
        "platform": "Blue Nile",
        "search": "moissanite drop earrings sterling silver",
        "reason": "Brilliant fire and sparkle rivaling mined diamonds at an accessible price"
    },
    {
        "name": "Art Deco Emerald Green Crystal Cocktail Ring",
        "category": "Rings",
        "styles": ["Vintage", "Statement"],
        "occasions": ["Cocktail", "Wedding", "Festive"],
        "materials": ["Rose Gold", "Gemstones"],
        "price": 62.0,
        "platform": "Etsy",
        "search": "emerald cut green crystal art deco ring",
        "reason": "Bold focal jewelry that draws eyes to your gestures with rich jewel-tone depth"
    },
    {
        "name": "Traditional Kundan & Pearl Choker Set with Maang Tikka",
        "category": "Jewelry Set",
        "styles": ["Traditional", "Statement"],
        "occasions": ["Wedding", "Festive"],
        "materials": ["Yellow Gold", "Gemstones"],
        "price": 140.0,
        "platform": "Tanishq",
        "search": "kundan choker necklace earrings maang tikka set",
        "reason": "Opulent traditional craftsmanship ideal for matching intricate silk sarees or lehengas"
    },
    {
        "name": "Solid Sterling Silver Twisted Cable Bangle",
        "category": "Bracelets",
        "styles": ["Minimalist", "Contemporary"],
        "occasions": ["Office", "Casual", "Cocktail"],
        "materials": ["White Gold / Silver", "Platinum"],
        "price": 54.0,
        "platform": "Amazon",
        "search": "925 sterling silver twisted cable bangle bracelet",
        "reason": "Sleek architectural wristwear that stacks effortlessly with watches"
    },
    {
        "name": "Freshwater Baroque Pearl Pendant Necklace",
        "category": "Necklace",
        "styles": ["Contemporary", "Vintage", "Minimalist"],
        "occasions": ["Office", "Wedding", "Cocktail"],
        "materials": ["Yellow Gold", "Rose Gold"],
        "price": 72.0,
        "platform": "Target",
        "search": "baroque freshwater pearl pendant necklace gold",
        "reason": "Organic irregular pearl form that gives modern sophistication to any neckline"
    },
    {
        "name": "Diamond-Accented Huggie Hoop Earrings",
        "category": "Earrings",
        "styles": ["Minimalist", "Contemporary"],
        "occasions": ["Office", "Casual", "Cocktail", "Wedding"],
        "materials": ["Yellow Gold", "Rose Gold", "White Gold / Silver"],
        "price": 58.0,
        "platform": "Amazon",
        "search": "pave cz huggie hoop earrings 14k gold plated",
        "reason": "Comfortable for all-day wear with snug secure latch and discreet sparkle"
    },
    {
        "name": "Sapphire Blue Teardrop Crystal Tennis Bracelet",
        "category": "Bracelets",
        "styles": ["Classic", "Statement"],
        "occasions": ["Cocktail", "Wedding", "Festive"],
        "materials": ["White Gold / Silver", "Gemstones"],
        "price": 89.0,
        "platform": "Blue Nile",
        "search": "sapphire blue crystal tennis bracelet white gold plated",
        "reason": "Graceful wrist shimmer complementing monochromatic and deep navy/black gowns"
    }
]
