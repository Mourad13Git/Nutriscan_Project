from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import plotly.express as px


def macro_distribution_chart(nutriments: Dict[str, Any]):
    """Camembert de répartition approximative glucides / protéines / lipides."""
    carbs = nutriments.get("carbohydrates_100g") or nutriments.get("carbohydrates", 0)
    sugars = nutriments.get("sugars_100g") or nutriments.get("sugars", 0)
    proteins = nutriments.get("proteins_100g") or nutriments.get("proteins", 0)
    fat = nutriments.get("fat_100g") or nutriments.get("fat", 0)

    # On considère "carbs nets" = glucides, dont sucres est un sous-ensemble
    data = pd.DataFrame(
        {
            "macro": ["Glucides", "Lipides", "Protéines"],
            "value": [carbs, fat, proteins],
        }
    )
    fig = px.pie(data, values="value", names="macro", title="Répartition approximative des macronutriments (g/100g)")
    return fig


def key_nutrients_bar_chart(nutriments: Dict[str, Any]):
    """Barres des nutriments clés (sucre, sel, graisses saturées, fibres)."""
    sugar = nutriments.get("sugars_100g") or 0
    salt = nutriments.get("salt_100g") or 0
    sat_fat = nutriments.get("saturated-fat_100g") or nutriments.get("saturated_fat_100g") or 0
    fiber = nutriments.get("fiber_100g") or 0

    data = pd.DataFrame(
        {
            "Nutriment": ["Sucres (g/100g)", "Sel (g/100g)", "Graisses saturées (g/100g)", "Fibres (g/100g)"],
            "Valeur": [sugar, salt, sat_fat, fiber],
        }
    )
    fig = px.bar(data, x="Nutriment", y="Valeur", title="Nutriments clés (pour 100g)")
    fig.update_layout(xaxis_title="", yaxis_title="g/100g")
    return fig


def compare_products_chart(products: List[Dict[str, Any]]):
    """Comparaison de quelques indicateurs clés entre plusieurs produits."""
    rows = []
    for p in products:
        nutriments = p.get("nutriments", {})
        rows.append(
            {
                "Produit": p.get("product_name", "Sans nom"),
                "Nutri-Score": (p.get("nutriscore_grade") or "?").upper(),
                "Sucre (g/100g)": nutriments.get("sugars_100g") or 0,
                "Sel (g/100g)": nutriments.get("salt_100g") or 0,
                "Graisses saturées (g/100g)": nutriments.get("saturated-fat_100g") or 0,
            }
        )

    df = pd.DataFrame(rows)
    df_long = df.melt(id_vars=["Produit", "Nutri-Score"], var_name="Indicateur", value_name="Valeur")

    fig = px.bar(
        df_long,
        x="Produit",
        y="Valeur",
        color="Indicateur",
        barmode="group",
        title="Comparaison nutritionnelle entre produits",
    )
    return fig



