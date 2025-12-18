from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from litellm import completion
from litellm.exceptions import BadRequestError


load_dotenv()


def _get_model_primary() -> str:
    return os.getenv("LITELLM_MODEL_PRIMARY", "groq/llama-3.1-8b-instant")


def _get_model_secondary() -> str:
    # Modèle secondaire : utilise llama-3.3-70b-versatile si disponible, sinon fallback sur le primaire
    # Si llama-3.3-70b-versatile n'est pas disponible, utiliser groq/llama-3.1-8b-instant ou groq/mixtral-8x7b-32768
    return os.getenv("LITELLM_MODEL_SECONDARY", "groq/llama-3.1-8b-instant")


def _base_messages(system_prompt: str, extra_messages: List[Dict[str, str]] | None = None) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]
    if extra_messages:
        messages.extend(extra_messages)
    return messages


def _call_llm(model: str, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
    """Appel générique au LLM via LiteLLM (Groq)."""
    # LiteLLM lit la clé GROQ_API_KEY dans l'environnement si le modèle est de type groq/*
    response = completion(
        model=model,
        messages=messages,
        temperature=0.4,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]  # type: ignore[index]


def analyze_product(product: Dict[str, Any]) -> str:
    """Analyse IA du produit à partir des champs OpenFoodFacts."""
    name = product.get("product_name", "Produit sans nom")
    brands = product.get("brands", "Marque inconnue")
    nutri_score = (product.get("nutriscore_grade") or "?").upper()
    nova = product.get("nova_group")
    nutriments = product.get("nutriments", {})
    ingredients = product.get("ingredients_text", "")
    additives = product.get("additives_original_tags", []) or []

    user_content = (
        f"Produit: {name} - Marque: {brands}\n"
        f"Nutri-Score: {nutri_score}\n"
        f"NOVA: {nova}\n"
        f"Nutriments (g/100g): {nutriments}\n"
        f"Ingrédients: {ingredients}\n"
        f"Additifs: {additives}\n\n"
        "Donne une analyse claire et pédagogique de la qualité nutritionnelle de ce produit pour un adulte moyen, "
        "avec :\n"
        "- points positifs\n"
        "- points de vigilance (sucre, sel, graisses saturées, ultra-transformation)\n"
        "- une conclusion globale (à consommer souvent / occasionnellement / rarement).\n"
        "Réponse en français, en 2-3 paragraphes maximum."
    )

    messages = _base_messages(
        "Tu es un expert en nutrition. Tu expliques de manière simple, factuelle et non alarmiste.",
        extra_messages=[{"role": "user", "content": user_content}],
    )
    return _call_llm(_get_model_primary(), messages)


def chat_with_user(user_message: str, chat_history: List[Dict[str, str]]) -> str:
    """Chatbot général nutrition + questions sur les produits."""
    messages = _base_messages(
        (
            "Tu es un assistant en nutrition. Tu donnes des explications générales basées sur des principes de santé "
            "publique (type PNNS), sans poser de diagnostic médical et sans donner de conseils médicaux personnalisés. "
            "Si une question relève de la médecine (symptômes graves, traitement), recommande de consulter un "
            "professionnel de santé."
        )
    )
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    return _call_llm(_get_model_primary(), messages)


def recommend_alternatives(product: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
    """Génère une courte recommandation d'alternatives plus saines parmi une liste de produits."""
    product_name = product.get("product_name", "Produit")
    product_nutri = (product.get("nutriscore_grade") or "?").upper()
    product_nova = product.get("nova_group")
    
    # Formater les candidats de manière lisible
    candidates_text = ""
    for i, cand in enumerate(candidates[:5], 1):
        name = cand.get("product_name", "Produit sans nom")
        brand = cand.get("brands", "Marque inconnue")
        nutri = (cand.get("nutriscore_grade") or "?").upper()
        nova = cand.get("nova_group")
        sugar = cand.get("nutriments", {}).get("sugars_100g", "?")
        fat = cand.get("nutriments", {}).get("saturated-fat_100g", "?")
        
        candidates_text += (
            f"{i}. {name} ({brand})\n"
            f"   Nutri-Score: {nutri} | NOVA: {nova if nova is not None else '?'}\n"
            f"   Sucre: {sugar}g/100g | Graisses saturées: {fat}g/100g\n\n"
        )
    
    user_content = (
        f"Produit actuel: {product_name}\n"
        f"Nutri-Score: {product_nutri} | NOVA: {product_nova if product_nova is not None else '?'}\n\n"
        f"Alternatives possibles:\n{candidates_text}\n"
        "Compare ces alternatives au produit actuel et recommande les 3-5 meilleures options "
        "en expliquant brièvement pourquoi elles sont meilleures (meilleur Nutri-Score, moins de sucre, "
        "moins de graisses saturées, moins ultra-transformé, etc.).\n"
        "Réponse en français, sous forme de liste à puces avec le nom du produit et une explication courte (1-2 phrases)."
    )

    messages = _base_messages(
        "Tu es un expert en nutrition qui aide à choisir des produits plus sains dans la même catégorie. "
        "Tu donnes des explications claires et factuelles.",
        extra_messages=[{"role": "user", "content": user_content}],
    )
    
    # Utiliser le modèle primaire (plus fiable) avec fallback en cas d'erreur
    model_primary = _get_model_primary()
    
    try:
        return _call_llm(model_primary, messages, max_tokens=800)
    except Exception:
        # En cas d'échec (quota, erreur API, etc.), retourner une recommandation basique
        return _generate_fallback_recommendation(product, candidates)


def _nutriscore_to_value(grade: str | None) -> int:
    """Convertit un Nutri-Score en valeur numérique pour comparaison (A=1, B=2, ..., E=5)."""
    if not grade:
        return 99
    grade_upper = str(grade).upper().strip()
    mapping = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    return mapping.get(grade_upper, 99)


def _generate_fallback_recommendation(product: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
    """Génère une recommandation basique sans IA en cas d'échec des modèles."""
    if not candidates:
        return "Aucune alternative trouvée pour ce produit."
    
    product_nutri = _nutriscore_to_value(product.get("nutriscore_grade"))
    
    recommendations = []
    for cand in candidates[:5]:
        name = cand.get("product_name", "Produit sans nom")
        brand = cand.get("brands", "Marque inconnue")
        nutri = (cand.get("nutriscore_grade") or "?").upper()
        nutri_val = _nutriscore_to_value(cand.get("nutriscore_grade"))
        
        if nutri_val < product_nutri:
            recommendations.append(f"• **{name}** ({brand}) — Nutri-Score: {nutri} — Meilleur score nutritionnel que le produit actuel.")
    
    if recommendations:
        return "**Alternatives recommandées :**\n\n" + "\n\n".join(recommendations)
    else:
        return "Aucune alternative avec un meilleur Nutri-Score trouvée dans cette catégorie."


