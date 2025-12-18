import os

import streamlit as st
from dotenv import load_dotenv

from utils import data as data_utils
from utils import charts as charts_utils
from utils import chatbot as chatbot_utils


load_dotenv()  # Charge les variables d'environnement (.env)


st.set_page_config(
    page_title="NutriScan",
    page_icon="🥗",
    layout="wide",
)


def init_session_state() -> None:
    """Initialise les clés de session Streamlit."""
    if "history" not in st.session_state:
        st.session_state["history"] = []  # historique des produits consultés
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []  # historique du chatbot
    if "selected_products" not in st.session_state:
        st.session_state["selected_products"] = []  # pour le comparateur
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []  # résultats de recherche
    if "current_product" not in st.session_state:
        st.session_state["current_product"] = None  # produit actuellement affiché


def sidebar_filters():
    st.sidebar.header("Filtres nutritionnels")
    vegan = st.sidebar.checkbox("Végan uniquement")
    gluten_free = st.sidebar.checkbox("Sans gluten")
    organic = st.sidebar.checkbox("Bio")

    max_sugar = st.sidebar.slider("Sucre max (g/100g)", 0, 50, 30)
    max_salt = st.sidebar.slider("Sel max (g/100g)", 0, 10, 5)

    return {
        "vegan": vegan,
        "gluten_free": gluten_free,
        "organic": organic,
        "max_sugar": max_sugar,
        "max_salt": max_salt,
    }


def render_header():
    st.title("🥗 NutriScan")
    st.markdown(
        "Votre **assistant nutrition intelligent** basé sur les données ouvertes d'OpenFoodFacts et l'IA."
    )


def render_search_section(filters):
    st.subheader("🔍 Recherche de produit")

    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_input("Nom du produit ou code-barres", "")
    with col2:
        search_button = st.button("Rechercher")

    # Si nouvelle recherche, mettre à jour les résultats
    if search_button and query:
        with st.spinner("Recherche des produits..."):
            products = data_utils.search_products(query=query, filters=filters)
            st.session_state["search_results"] = products
            # Réinitialiser le produit courant si nouvelle recherche
            st.session_state["current_product"] = None

    # Utiliser les résultats stockés dans session_state
    products = st.session_state.get("search_results", [])

    if products:
        st.markdown("### Résultats")
        options = {
            f"{p['product_name']} — {p.get('brands', 'Marque inconnue')} (Nutri-Score: {p.get('nutriscore_grade', '?').upper()})": p
            for p in products
        }
        
        # Déterminer l'index par défaut
        default_index = 0
        if st.session_state.get("current_product"):
            # Trouver l'index du produit actuel dans la liste
            current_id = st.session_state["current_product"].get("_id") or st.session_state["current_product"].get("code")
            for idx, p in enumerate(products):
                if (p.get("_id") or p.get("code")) == current_id:
                    default_index = idx
                    break
        
        label = st.selectbox("Sélectionnez un produit", list(options.keys()), index=default_index)
        selected_product = options[label]

        # Mettre à jour le produit courant et l'historique
        if selected_product:
            product_id = selected_product.get("_id") or selected_product.get("code")
            current_id = None
            if st.session_state.get("current_product"):
                current_id = st.session_state["current_product"].get("_id") or st.session_state["current_product"].get("code")
            
            # Si le produit a changé, mettre à jour
            if product_id != current_id:
                st.session_state["current_product"] = selected_product
                if product_id not in st.session_state["history"]:
                    st.session_state["history"].append(product_id)
                if selected_product not in st.session_state["selected_products"]:
                    st.session_state["selected_products"].append(selected_product)
        
        # Retourner le produit sélectionné depuis le selectbox
        return selected_product

    elif search_button and query:
        st.warning("Aucun produit trouvé. Essayez un autre terme ou un code-barres.")
        return None

    # Si pas de résultats mais qu'on a un produit en session, le retourner
    return st.session_state.get("current_product")


def render_product_details(product):
    if not product:
        return

    st.subheader("🧾 Fiche produit")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        image_url = product.get("image_front_small_url") or product.get("image_url")
        if image_url:
            st.image(image_url, use_column_width=True)

        nutri_score = (product.get("nutriscore_grade") or "?").upper()
        nova_group = product.get("nova_group")

        st.markdown(f"**Nutri-Score :** {nutri_score}")
        st.markdown(f"**NOVA :** {nova_group if nova_group is not None else '?'}")

    with col_right:
        st.markdown(f"### {product.get('product_name', 'Produit sans nom')}")
        st.markdown(f"**Marque :** {product.get('brands', 'Inconnue')}")

        with st.spinner("Analyse IA du produit..."):
            analysis = chatbot_utils.analyze_product(product)
        st.markdown("#### 🤖 Analyse IA")
        st.write(analysis)

    # Visualisations nutritionnelles et alternatives
    col_comp, col_alt = st.columns([1, 1])
    
    with col_comp:
        st.subheader("📊 Composition nutritionnelle")
        nutriments = product.get("nutriments", {})
        fig_pie = charts_utils.macro_distribution_chart(nutriments)
        fig_bars = charts_utils.key_nutrients_bar_chart(nutriments)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.plotly_chart(fig_bars, use_container_width=True)
    
    with col_alt:
        st.subheader("🔄 Alternatives recommandées")
        with st.spinner("Recherche d'alternatives plus saines..."):
            alternatives = data_utils.find_alternatives(product, max_results=5)
        
        if alternatives:
            # Générer la recommandation IA
            with st.spinner("Analyse des alternatives par IA..."):
                recommendation_text = chatbot_utils.recommend_alternatives(product, alternatives)
            
            st.markdown("#### 🤖 Recommandations IA")
            st.write(recommendation_text)
            
            st.markdown("#### 📋 Produits suggérés")
            for alt in alternatives[:5]:
                alt_name = alt.get("product_name", "Produit sans nom")
                alt_brand = alt.get("brands", "Marque inconnue")
                alt_nutri = (alt.get("nutriscore_grade") or "?").upper()
                alt_nova = alt.get("nova_group")
                
                # Créer un bouton/cliquable pour sélectionner l'alternative
                with st.container():
                    st.markdown(f"**{alt_name}** — {alt_brand}")
                    st.markdown(f"Nutri-Score: **{alt_nutri}** | NOVA: {alt_nova if alt_nova is not None else '?'}")
                    
                    # Bouton pour ajouter au comparateur
                    if st.button(f"Voir détails", key=f"alt_{alt.get('code', alt.get('_id', ''))}"):
                        st.session_state["current_product"] = alt
                        st.rerun()
                    st.markdown("---")
        else:
            st.info("Aucune alternative trouvée pour ce produit. Essayez une recherche manuelle.")


def render_comparator():
    st.subheader("🔄 Comparateur de produits")
    products = st.session_state.get("selected_products", [])
    if len(products) < 2:
        st.info("Ajoutez au moins deux produits pour les comparer.")
        return

    fig = charts_utils.compare_products_chart(products)
    st.plotly_chart(fig, use_container_width=True)


def render_chatbot():
    st.subheader("💬 Chatbot nutrition")

    user_input = st.text_input("Posez une question", "")
    if st.button("Envoyer") and user_input:
        with st.spinner("Réflexion en cours..."):
            answer = chatbot_utils.chat_with_user(
                user_message=user_input,
                chat_history=st.session_state["chat_history"],
            )
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})

    if st.session_state["chat_history"]:
        with st.expander("Historique du chatbot"):
            for msg in st.session_state["chat_history"]:
                prefix = "🧑‍💻" if msg["role"] == "user" else "🤖"
                st.markdown(f"**{prefix}** {msg['content']}")


def main():
    init_session_state()
    filters = sidebar_filters()
    render_header()

    selected_product = render_search_section(filters)

    if selected_product:
        render_product_details(selected_product)

    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        render_comparator()
    with cols[1]:
        render_chatbot()


if __name__ == "__main__":
    main()


