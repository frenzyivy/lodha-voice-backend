"""
Run once to seed the 5 projects: python seed.py
Replace every value below with your real project data before going live —
the `name` field must exactly match whatever you use in the Vapi system prompt.
"""
from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

PROJECTS = [
    dict(
        name="Lodha Marq",                 # TODO: real name
        location="Tardeo, Mumbai",                 # TODO
        price_min=15000000, price_max=25000000,   # TODO (INR)
        configurations="2, 3 BHK",                 # TODO
        possession_date="Dec 2027",                 # TODO
        rera_number="P51700000001",                 # TODO
        amenities="Clubhouse, swimming pool, gym, landscaped gardens",  # TODO
        description="Placeholder description.",
    ),
    dict(
        name="Lodha cullinan",
        location="Mumbai",
        price_min=8000000, price_max=14000000,
        configurations="1, 2 BHK",
        possession_date="Jun 2026",
        rera_number="P51700000002",
        amenities="Clubhouse, jogging track, kids play area",
        description="Placeholder description.",
    ),
    dict(
        name="Lodha world crest",
        location="worli , Mumbai",
        price_min=30000000, price_max=60000000,
        configurations="3, 4 BHK",
        possession_date="Mar 2028",
        rera_number="P51700000003",
        amenities="Sky lounge, infinity pool, spa, concierge",
        description="Placeholder description.",
    ),
    dict(
        name="Lodha Vista",
        location="Lower Parel, Mumbai",
        price_min=6000000, price_max=11000000,
        configurations="1, 2 BHK",
        possession_date="Sep 2026",
        rera_number="P51700000004",
        amenities="Clubhouse, multipurpose court, garden",
        description="Placeholder description.",
    ),
    dict(
        name="Lodha Acenza",
        location="Andheri, Mumbai",
        price_min=45000000, price_max=90000000,
        configurations="3, 4, 5 BHK",
        possession_date="Dec 2028",
        rera_number="P51700000005",
        amenities="Rooftop pool, private theatre, valet parking",
        description="Placeholder description.",
    ),
]

for p in PROJECTS:
    exists = db.query(models.Project).filter(models.Project.name == p["name"]).first()
    if exists:
        print(f"Skipping (already exists): {p['name']}")
        continue
    db.add(models.Project(**p, status="active"))
    print(f"Added: {p['name']}")

db.commit()
db.close()
print("Done.")
