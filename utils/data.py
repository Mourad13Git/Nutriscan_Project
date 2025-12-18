from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

OPENFOODFACTS_API_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"
OPENFOODFACTS_API_PRODUCT = "https://world.openfoodfacts.org/api/v0/product"


def _build_search_params(query: str, page_size: int = 20) -> Dict[str, Any]:
    return {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }


def _apply_filters(product: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Filtre un produit selon les critères simples (vegan, sans gluten, bio, sucres, sel)."""
    nutriments = product.get("nutriments", {})
    labels = (product.get("labels", "") or "").lower()
    ingredients_text = (product.get("ingredients_text", "") or "").lower()

    if filters.get("vegan"):
        if "vegan" not in labels and "végétalien" not in labels:
            return False

    if filters.get("gluten_free"):
        if "sans gluten" not in labels and "gluten-free" not in labels:
            if "gluten" in ingredients_text:
                return False

    if filters.get("organic"):
        if "bio" not in labels and "organic" not in labels:
            return False

    sugar_100g = nutriments.get("sugars_100g") or nutriments.get("sugar_100g")
    if sugar_100g is not None and sugar_100g > filters.get("max_sugar", 50):
        return False

    salt_100g = nutriments.get("salt_100g")
    if salt_100g is not None and salt_100g > filters.get("max_salt", 10):
        return False

    return True


def _is_barcode(query: str) -> bool:
    """Détecte si la requête est un code-barres (numérique uniquement, 8-13 chiffres)."""
    query_clean = query.strip().replace(" ", "").replace("-", "")
    return query_clean.isdigit() and 8 <= len(query_clean) <= 13


def _get_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """Récupère un produit par son code-barres via l'API OpenFoodFacts."""
    barcode_clean = barcode.strip().replace(" ", "").replace("-", "")
    url = f"{OPENFOODFACTS_API_PRODUCT}/{barcode_clean}.json"
    
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") == 1 and data.get("product"):
            return data["product"]
        return None
    except requests.RequestException:
        return None


def search_products(query: str, filters: Optional[Dict[str, Any]] = None, page_size: int = 20) -> List[Dict[str, Any]]:
    """Recherche des produits dans l'API OpenFoodFacts.
    
    Gère à la fois la recherche par texte et par code-barres.
    """
    filters = filters or {}
    
    # Si c'est un code-barres, utiliser l'endpoint spécifique
    if _is_barcode(query):
        product = _get_product_by_barcode(query)
        if product:
            # Appliquer les filtres même pour un code-barres
            if _apply_filters(product, filters):
                return [product]
            return []
        return []
    
    # Sinon, recherche par texte classique
    params = _build_search_params(query=query, page_size=page_size)

    try:
        resp = requests.get(OPENFOODFACTS_API_SEARCH, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])

        filtered = [p for p in products if _apply_filters(p, filters)]
        return filtered
    except requests.RequestException:
        return []


def _nutriscore_to_value(grade: str | None) -> int:
    """Convertit un Nutri-Score en valeur numérique pour comparaison (A=1, B=2, ..., E=5)."""
    if not grade:
        return 99  # Valeur élevée pour les produits sans score
    grade_upper = str(grade).upper().strip()
    mapping = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    return mapping.get(grade_upper, 99)


def find_alternatives(product: Dict[str, Any], max_results: int = 10) -> List[Dict[str, Any]]:
    """Trouve des alternatives plus saines au produit donné.
    
    Recherche des produits similaires (même catégorie) avec un meilleur Nutri-Score.
    """
    # Extraire la catégorie principale du produit
    categories = product.get("categories", "") or ""
    categories_tags = product.get("categories_tags", []) or []
    
    # Utiliser la première catégorie significative
    search_term = ""
    if categories_tags:
        # Prendre la catégorie la plus spécifique (généralement la dernière)
        search_term = categories_tags[-1].replace("en:", "").replace("fr:", "")
    elif categories:
        # Extraire un mot-clé de la catégorie
        parts = categories.split(",")
        if parts:
            search_term = parts[0].strip().split()[-1]  # Prendre le dernier mot
    
    if not search_term:
        return []
    
    # Nutri-Score actuel du produit
    current_nutri = _nutriscore_to_value(product.get("nutriscore_grade"))
    
    # Rechercher des produits similaires
    params = _build_search_params(query=search_term, page_size=50)
    params["sort_by"] = "nutriscore_grade"
    
    try:
        resp = requests.get(OPENFOODFACTS_API_SEARCH, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("products", [])
        
        # Filtrer : meilleur Nutri-Score, exclure le produit actuel
        product_code = product.get("code") or product.get("_id")
        alternatives = []
        
        for candidate in candidates:
            candidate_code = candidate.get("code") or candidate.get("_id")
            # Exclure le produit actuel
            if candidate_code == product_code:
                continue
            
            # Vérifier que le produit a les infos minimales
            if not candidate.get("product_name") or not candidate.get("nutriscore_grade"):
                continue
            
            candidate_nutri = _nutriscore_to_value(candidate.get("nutriscore_grade"))
            
            # Garder seulement ceux avec un meilleur ou égal Nutri-Score
            if candidate_nutri < current_nutri:
                alternatives.append(candidate)
            
            if len(alternatives) >= max_results:
                break
        
        # Trier par Nutri-Score (meilleur en premier)
        alternatives.sort(key=lambda p: _nutriscore_to_value(p.get("nutriscore_grade")))
        
        return alternatives[:max_results]
    except requests.RequestException:
        return []



