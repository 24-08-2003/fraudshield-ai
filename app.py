import streamlit as st
import requests

# Configuration de la page
st.set_page_config(page_title="FraudShield AI", page_icon="🛡️", layout="wide")

st.title("🛡️ FraudShield AI - Interface MLOps")
st.markdown("Testez les prédictions de fraude en temps réel via notre modèle hébergé sur FastAPI.")

st.sidebar.header(" Détails de la transaction")

# Création du formulaire de saisie dans la barre latérale
# Les valeurs par défaut correspondent à l'exemple de votre README
amount = st.sidebar.number_input("Montant de la transaction ($)", min_value=0.0, value=1547.99)
merchant_category = st.sidebar.selectbox("Catégorie du marchand", ["online_retail", "travel", "groceries", "electronics", "services"])
card_type = st.sidebar.selectbox("Type de carte", ["visa", "mastercard", "amex", "discover"])
entry_mode = st.sidebar.selectbox("Mode de saisie", ["online", "chip", "swipe", "contactless"])

col1, col2 = st.sidebar.columns(2)
hour_of_day = col1.number_input("Heure du jour (0-23)", min_value=0, max_value=23, value=2)
day_of_week = col2.number_input("Jour de la semaine (0-6)", min_value=0, max_value=6, value=4)

merchant_risk_score = st.sidebar.slider("Score de risque marchand", 0.0, 1.0, 0.82)
velocity_score = st.sidebar.slider("Score de vélocité", 0.0, 1.0, 0.71)
distance_from_home = st.sidebar.number_input("Distance du domicile (km)", min_value=0, value=3421)
transaction_count_1h = st.sidebar.number_input("Nombre de transactions (1h)", min_value=0, value=8)

# Bouton d'action
if st.sidebar.button(" Analyser la Transaction", use_container_width=True):
    
    # Préparation des données pour l'API (basé sur le schéma de votre API)
    payload = {
        "amount": amount,
        "merchant_category": merchant_category,
        "card_type": card_type,
        "entry_mode": entry_mode,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "merchant_risk_score": merchant_risk_score,
        "velocity_score": velocity_score,
        "distance_from_home": distance_from_home,
        "transaction_count_1h": transaction_count_1h
    }
    
    with st.spinner("Analyse en cours par le modèle ML..."):
        try:
            # Appel à votre backend FastAPI local (port 8000)
            API_URL = "http://localhost:8000/api/v1/predict/"
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Affichage des résultats
                st.markdown("---")
                st.subheader(" Résultat du Modèle")
                
                # Affichage visuel selon si c'est une fraude ou non
                if result.get("is_fraud"):
                    st.error(f" **ALERTE FRAUDE !** Cette transaction est hautement suspecte.")
                else:
                    st.success(f" **Transaction Légitime.** Aucun comportement anormal détecté.")
                
                # Création de métriques stylisées
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Probabilité de Fraude", f"{result.get('fraud_probability', 0)*100:.2f} %")
                m2.metric("Niveau de Risque", result.get("risk_level", "INCONNU"))
                m3.metric("Seuil Utilisé", result.get("threshold_used", 0.5))
                m4.metric("Temps d'inférence", f"{result.get('processing_time_ms', 0):.2f} ms")
                
                # Affichage du JSON brut pour le côté technique/MLOps
                with st.expander("Voir la réponse JSON brute de l'API"):
                    st.json(result)
                    
            else:
                st.warning(f"L'API a retourné une erreur {response.status_code}. Vérifiez les données envoyées.")
                
        except requests.exceptions.ConnectionError:
            st.error(" **Impossible de joindre le backend !**")
            st.info("Avez-vous bien lancé votre serveur FastAPI ? Tapez : `uvicorn backend.app.main:app --reload --port 8000` dans un autre terminal.")