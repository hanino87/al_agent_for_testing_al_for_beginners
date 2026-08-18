import streamlit as st

from chatbot.bot import ask_bot
from testing.hallucination import (
    check_hallucination,
    evaluate_hallucination_guess,
)


# ============================================================
# SIDINSTÄLLNINGAR
# ============================================================

st.set_page_config(
    page_title="Hallucinationer - VM AI-Testbot",
    page_icon="⚠️",
    layout="centered",
)


# ============================================================
# SESSION STATE
# ============================================================

if "hallucination_messages" not in st.session_state:
    st.session_state.hallucination_messages = []

if "hallucination_result" not in st.session_state:
    st.session_state.hallucination_result = None

if "hallucination_evaluation" not in st.session_state:
    st.session_state.hallucination_evaluation = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚽ VM AI-Testbot")

    st.divider()

    st.subheader("Testområde")

    st.warning("⚠️ Hallucinationer")

    st.caption(
        "Kontrollera om AI:n hittar på personer, "
        "händelser, resultat eller andra detaljer."
    )

    st.divider()

    if st.button(
        "🆕 Ny hallucinationstest",
        use_container_width=True
    ):

        st.session_state.hallucination_messages = []
        st.session_state.hallucination_result = None
        st.session_state.hallucination_evaluation = None

        st.rerun()


# ============================================================
# RUBRIK
# ============================================================

st.title("⚠️ Hallucinationer")

st.write(
    "Ställ en fråga och kontrollera om AI:n hittar "
    "på information som inte finns."
)


# ============================================================
# VÄLKOMST
# ============================================================

if len(st.session_state.hallucination_messages) == 0:

     st.info(
            "👋 Exempel på frågor:\n\n"
            "- Vem vann VM 1950?\n"
            "- Vem mötte Frankrike i finalen 1998?\n"
            "- Vilka vann VM 2018?\n"
            "- Var spelades VM 2022?"
        )


# ============================================================
# CHATTHISTORIK
# ============================================================

for message in st.session_state.hallucination_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# FRÅGA
# ============================================================

question = st.chat_input(
    "Ställ en fråga som kan avslöja en hallucination..."
)


if question:

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.hallucination_messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------------------
    # AI-SVAR
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("AI:n tänker..."):

            answer = ask_bot(
                question=question,
                conversation=(
                    st.session_state.hallucination_messages[:-1]
                ),
            )

        st.markdown(answer)


    st.session_state.hallucination_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # --------------------------------------------------------
    # HALLUCINATIONSKONTROLL
    # --------------------------------------------------------

    with st.spinner(
        "Kontrollerar om AI:n hallucinerade..."
    ):

        result = check_hallucination(
            question=question,
            answer=answer,
        )


    st.session_state.hallucination_result = result
    st.session_state.hallucination_evaluation = None

    st.rerun()


# ============================================================
# GISSNING
# ============================================================

if st.session_state.hallucination_result is not None:

    st.divider()

    st.subheader("🔎 Hallucinerade AI:n?")

    st.write(
        "Gissa om AI:n hittade på information i sitt svar."
    )


    with st.form("hallucination_guess_form"):

        user_guess = st.radio(
            "Din gissning:",
            [
                "AI:n hallucinerade",
                "AI:n hallucinerade inte",
            ],
        )


        submitted = st.form_submit_button(
            "Kontrollera min gissning",
            use_container_width=True,
        )


        if submitted:

            user_believes_hallucination = (
                user_guess == "AI:n hallucinerade"
            )


            result = evaluate_hallucination_guess(
                actual_result=(
                    st.session_state.hallucination_result
                ),
                user_believes_hallucination=(
                    user_believes_hallucination
                ),
            )


            st.session_state.hallucination_evaluation = result

            st.rerun()


# ============================================================
# RESULTAT
# ============================================================

if st.session_state.hallucination_evaluation is not None:

    result = st.session_state.hallucination_evaluation

    st.divider()

    st.subheader("📊 Resultat")


    if result["hallucination"] is None:

        st.warning(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )

    elif result["title"].startswith("🎉"):

        st.success(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )

    else:

        st.error(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )


    st.info(
        f'💡 {result["explanation"]}'
    )