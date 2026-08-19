import streamlit as st


# ============================================================
# SIDINSTÄLLNINGAR
# ============================================================

st.set_page_config(
    page_title="VM AI-Testbot",
    page_icon="⚽",
    layout="centered",
)


# ============================================================
# HUVUDSIDA
# ============================================================

st.title("⚽ VM AI-Testbot")

st.write(
    "Välkommen till VM AI-Testbot."
)

st.write(
    "Här kan du testa olika typer av AI-fel "
    "i frågor om fotbolls-VM."
)


# ============================================================
# TESTOMRÅDEN
# ============================================================

st.subheader("🧪 Testområden")

st.info(
    """
    Använd menyn till vänster för att välja ett testområde.

    ✓  **Korrekthet**
    
    Kontrollera om AI:n ger faktamässigt korrekta svar.

    ⚠️ **Hallucinationer**
    
    Kontrollera om AI:n hittar på personer, händelser,
    resultat eller andra detaljer som inte finns.
    
    🎯 **Relevans**
    
    Kontrollera om AI:n ger ett relevant svar på frågan och inte, 
    leder in användaren på fel sidospår eller ger onödig information som användaren inte 
    har efterfrågat.
    
    """
    
)


# ============================================================
# INFORMATION
# ============================================================

st.divider()

st.subheader("📋 Så fungerar testningen")

st.write(
    "1. Välj ett testområde i menyn."
)

st.write(
    "2. Ställ en fråga till AI:n."
)

st.write(
    "3. Läs AI:ns svar."
)

st.write(
    "4. Gör din egen gissning."
)

st.write(
    "5. Systemet kontrollerar om din gissning var rätt."
)