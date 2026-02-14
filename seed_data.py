import django
import os
import random

# ------------------
# Django setup
# ------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Project.settings")
django.setup()

from Prolean.models import Training, City

# ------------------
# CITIES (30 Moroccan)
# ------------------
cities_list = [
    "Agadir", "Al Hoceïma", "Berkane", "Béni Mellal", "Casablanca", "Dakhla",
    "El Jadida", "Errachidia", "Essaouira", "Fès", "Ifrane", "Khenifra",
    "Khouribga", "Kénitra", "Laâyoune", "Marrakech", "Meknès", "Nador",
    "Ouarzazate", "Oujda", "Rabat", "Safi", "Salé", "Settat", "Sidi Slimane",
    "Tanger", "Taroudant", "Taza", "Tiznit", "Tétouan"
]

print("Creating cities...")
# City model might not exist if it was removed in favor of choices, 
# but views.py imports it. If it doesn't exist, we skip.
try:
    for name in cities_list:
        City.objects.get_or_create(name=name, defaults={"is_active": True})
    print("Cities created.")
except Exception as e:
    print(f"Skipping City creation (might not exist as model): {e}")

# ------------------
# CACES TRAININGS
# ------------------
caces_trainings = [
    ("CACES R485 – Chariots Élévateurs Télescopiques", 1900, "caces"),
    ("CACES R489 – Chariots Élévateurs", 2400, "caces"),
    ("CACES R482 – Engins de Chantier", 2500, "caces"),
    ("CACES R490 – Grues de Chargement", 2800, "caces"),
    ("Habilitation Électrique B1/B2", 1500, "electricite"),
    ("Soudage TIG/MIG", 3000, "soudage"),
    ("Management d'équipe", 4000, "management"),
]

print("Creating trainings...")

for title, price, category in caces_trainings:
    slug = title.lower().replace(" ", "-").replace("–", "-").replace("é", "e").replace("/", "-")
    
    # Determine category boolean fields
    cat_caces = category == "caces"
    cat_elec = category == "electricite"
    cat_soud = category == "soudage"
    cat_mgmt = category == "management"
    
    defaults = {
        "title": title,
        "short_description": f"Formation professionnelle certifiante : {title}",
        "detailed_description": f"Une formation complète pour maîtriser {title}. Programme incluant théorie et pratique.",
        "objectives": "Maîtriser les règles de sécurité\nObtenir la certification officielle\nAméliorer l'employabilité",
        "price_mad": price,
        "duration_days": 5,
        "badge": "promo" if price < 2500 else "popular",
        "is_active": True,
        "is_featured": True,
        "thumbnail": "https://via.placeholder.com/600x400",
        
        # Categories
        "category_caces": cat_caces,
        "category_electricite": cat_elec,
        "category_soudage": cat_soud,
        "category_management": cat_mgmt,
        "category_securite": True, # Always include security

        # Certificates
        "certificate_name_1": "Certificat Professionnel",
        "certificate_image_1": "https://via.placeholder.com/400x300",
        
        # License
        "license_recto_url": "https://via.placeholder.com/400x250",
        "license_verso_url": "https://via.placeholder.com/400x250",

        # Cities availability
        "available_casablanca": True,
        "available_rabat": True,
        "available_tanger": True,
        "available_marrakech": True,
    }

    try:
        training, created = Training.objects.update_or_create(
            slug=slug,
            defaults=defaults
        )
        print(f"{'Created' if created else 'Updated'}: {title}")
    except Exception as e:
        # Fallback if slug exists but with different uniqueness constrains or other errors
        # Try with a random suffix
        slug = f"{slug}-{random.randint(1000, 9999)}"
        try:
             Training.objects.create(slug=slug, **defaults)
             print(f"Created with new slug: {title}")
        except Exception as e2:
             print(f"Failed to create {title}: {e2}")

print("Seeding complete ✅")
