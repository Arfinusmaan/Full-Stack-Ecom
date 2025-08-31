import os
from django.utils.timezone import now
from shop.models import Product, Category

def run():
    base_path = os.path.join('static', 'uploads')

    # Create fallback category
    category, _ = Category.objects.get_or_create(
        name='Recovered',
        defaults={
            'description': 'Imported from static folder',
            'status': False,
            'created_at': now(),
        }
    )

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                continue  # skip non-image files

            rel_path = os.path.relpath(os.path.join(root, filename), 'static')

            Product.objects.create(
                category=category,
                name=os.path.splitext(filename)[0],
                vendor='Unknown',
                product_image=rel_path,
                quantity=10,
                original_price=1000,
                selling_price=900,
                description='Auto-imported from static folder',
                status=False,
                trending=False,
                created_at=now()
            )

            print(f"Imported: {rel_path}")
