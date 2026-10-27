import math
from uuid import uuid4
from datetime import datetime, timezone
from app.schemas.contracts import ClothingRead, OutfitRead, SimilarItem
from app.repositories.wardrobe import category_counts, items, similar

CATEGORIES = ['Tops', 'Bottoms', 'Shoes', 'Outerwear', 'Accessories']
TARGETS = {'Tops': 3, 'Bottoms': 2, 'Shoes': 2, 'Outerwear': 1, 'Accessories': 1}
NEUTRALS = {'black', 'white', 'gray', 'grey', 'cream', 'beige', 'navy', 'brown', 'neutral'}
PAIRABLE = {'Tops': {'Bottoms', 'Shoes', 'Outerwear', 'Accessories'},
            'Bottoms': {'Tops', 'Shoes', 'Outerwear', 'Accessories'},
            'Shoes': {'Tops', 'Bottoms', 'Outerwear'},
            'Outerwear': {'Tops', 'Bottoms', 'Shoes'},
            'Accessories': {'Tops', 'Bottoms', 'Shoes'}}


def cosine(a, b):
    if a is None or b is None:
        return 0.0
    return sum(float(x) * float(y) for x, y in zip(a, b)) / ((math.sqrt(sum(float(x)**2 for x in a)) * math.sqrt(sum(float(y)**2 for y in b))) or 1)


def classification(score):
    if score >= .90: return 'likely_duplicate'
    if score >= .72: return 'similar'
    if score >= .48: return 'related'
    return 'different'


def similar_items(db, user_id, product):
    ranked = sorted(((item, round(max(0, cosine(item.embedding, product.embedding)), 3))
                     for item in similar(db, user_id, product)), key=lambda x: x[1], reverse=True)
    return [SimilarItem(item=ClothingRead.model_validate(item), similarity_score=score,
                        classification=classification(score)) for item, score in ranked[:5]]


def compatibility(a, b):
    if a.category.lower() == b.category.lower(): return 0
    if b.category not in PAIRABLE.get(a.category, set()): return 0
    score = 40
    ca, cb = a.color.lower(), b.color.lower()
    score += 20 if ca in NEUTRALS or cb in NEUTRALS or ca == cb else 5
    score += 15 if not a.style or not b.style or a.style.lower() == b.style.lower() else 0
    score += 10 if not a.occasion or not b.occasion or a.occasion.lower() == b.occasion.lower() else 0
    score += 10 if not a.season or not b.season or 'all' in a.season.lower() or 'all' in b.season.lower() or a.season.lower() == b.season.lower() else 0
    score += 5 if abs(a.formality - b.formality) <= 1 else 0
    return min(score, 100)


def compatible(db, user_id, anchor):
    return sorted(((item, compatibility(anchor, item)) for item in items(db, user_id, limit=1000)
                   if item.id != getattr(anchor, 'id', None)), key=lambda pair: pair[1], reverse=True)


def generate(db, user_id, anchor, limit=3):
    ranked = [(item, score) for item, score in compatible(db, user_id, anchor) if score >= 55]
    results = []
    seen = set()
    for first, score in ranked:
        selected = [first]
        for other, other_score in ranked:
            if other.category != first.category and other.id != first.id and other_score >= 60 and compatibility(first, other) >= 50:
                selected.append(other)
                break
        ids = [x.id for x in selected]
        if getattr(anchor, 'id', None) and anchor.__class__.__name__ == 'WardrobeItem':
            ids.insert(0, anchor.id)
        key = tuple(sorted(ids))
        if key in seen: continue
        seen.add(key)
        results.append(OutfitRead(id=str(uuid4()), name=f'{anchor.name} outfit {len(results)+1}', item_ids=ids,
                                  occasion=anchor.occasion or 'Everyday', description=f'Pairs {anchor.name} with {", ".join(x.name for x in selected)}.',
                                  saved=False, created_at=datetime.now(timezone.utc)))
        if len(results) >= limit: break
    return results


def gaps(db, user_id):
    counts = category_counts(db, user_id)
    output = []
    for category, target in TARGETS.items():
        count = counts.get(category, 0)
        if count < target:
            priority = 'High' if count == 0 else 'Medium'
            output.append({'id': category.lower(), 'category': category, 'title': f'Add {category.lower()}',
                           'description': f'{count} of {target} suggested {category.lower()} owned.',
                           'priority': priority, 'image_url': '', 'pairs_with': [c for c in CATEGORIES if counts.get(c, 0) and c != category],
                           'count': count, 'target': target})
    return output
