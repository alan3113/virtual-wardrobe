from uuid import uuid4
from app.repositories.wardrobe import category_counts
from app.schemas.contracts import ClothingRead, ProductAnalysis, ProductRead, ShoppingRead
from app.services.intelligence import compatible, generate, similar_items, TARGETS


def duplicate_risk(matches):
    if matches and matches[0].classification == 'likely_duplicate':
        return 'High'
    if matches and matches[0].classification == 'similar':
        return 'Medium'
    return 'Low'


def analyze_product(db, user_id, product):
    matches = similar_items(db, user_id, product)
    return ProductAnalysis(product=ProductRead.model_validate(product), similar_items=matches,
                           duplicate_risk=duplicate_risk(matches))


def analyze_shopping(db, user_id, product):
    matches = similar_items(db, user_id, product)
    ranked = [(item, score) for item, score in compatible(db, user_id, product) if score >= 55]
    outfit_options = generate(db, user_id, product)
    counts = category_counts(db, user_id)
    gap = counts.get(product.category, 0) < TARGETS.get(product.category, 1)
    risk = duplicate_risk(matches)
    score = round(sum(s for _, s in ranked[:5]) / min(5, len(ranked))) if ranked else 0
    explanation = (f'{len(matches)} similar item(s) found. {len(ranked)} wardrobe item(s) pair with this product. '
                   f'{"It fills a category gap." if gap else "The category is represented."} Duplicate risk is {risk.lower()}.')
    return ShoppingRead(id=str(uuid4()), product=ProductRead.model_validate(product), wardrobe_match=score,
                        similar_item_owned=len([m for m in matches if m.classification in {'likely_duplicate', 'similar'}]),
                        compatible_items=len(ranked), new_outfits=len(outfit_options), duplicate_risk=risk,
                        wardrobe_gap=gap, explanation=explanation, outfit_item_ids=[o.item_ids for o in outfit_options],
                        similar_items=matches, compatibility_score=score,
                        compatible_wardrobe_items=[ClothingRead.model_validate(i) for i, _ in ranked[:10]],
                        possible_new_outfits=outfit_options)
