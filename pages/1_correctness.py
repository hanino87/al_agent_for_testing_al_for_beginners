import streamlit as st

from chatbot.bot import ask_bot
from testing.correctness import (
    check_answer,
    evaluate_user_guess,
)


# ============================================================
# SIDINSTÄLLNINGAR
# ============================================================

st.set_page_config(
    page_title="Korrekthet - VM AI-Testbot",
    page_icon="✓",
    layout="centered",
)


# ============================================================
# SESSION STATE
# ============================================================

if "correctness_messages" not in st.session_state:
    st.session_state.correctness_messages = []

if "correctness_result" not in st.session_state:
    st.session_state.correctness_result = None

if "correctness_evaluation" not in st.session_state:
    st.session_state.correctness_evaluation = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚽ VM AI-Testbot")

    st.divider()

    st.subheader("Testområde")

    st.success("✓ Korrekthet")

    st.caption(
        "Kontrollera om AI:n ger faktamässigt korrekta "
        "svar om fotbolls-VM."
    )

    st.divider()

    if st.button(
        "🆕 Ny korrekthetstest",
        use_container_width=True
    ):

        st.session_state.correctness_messages = []
        st.session_state.correctness_result = None
        st.session_state.correctness_evaluation = None

        st.rerun()


# ============================================================
# RUBRIK
# ============================================================

st.title("✓ Korrekthet")

st.write(
    "Ställ en fråga om fotbolls-VM och bedöm om AI:n "
    "svarar korrekt d.v.s med rätt information."
)


# ============================================================
# VÄLKOMST
# ============================================================

if len(st.session_state.correctness_messages) == 0:

    st.info(
        "👋 Exempel på frågor:\n\n"
        "- Vem vann VM 1950?\n"
        "**Bra korrekt svar:**\n"
        "Uruguay.\n\n"
        "- Var spelades VM 2022?"
        "**Dåligt korrekt svar:**\n"
        "Vm 2022 spelades i Tonga (Dåligt svar stämmer inte då Tonga aldrig arrangerrat ett vm).\n\n"
    )


# ============================================================
# CHATTHISTORIK
# ============================================================

for message in st.session_state.correctness_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# FRÅGA
# ============================================================

question = st.chat_input(
    "Ställ en fråga om fotbolls-VM..."
)


if question:

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.correctness_messages.append(
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
                    st.session_state.correctness_messages[:-1]
                ),
            )

        st.markdown(answer)


    st.session_state.correctness_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # --------------------------------------------------------
    # KONTROLL
    # --------------------------------------------------------

    with st.spinner("Kontrollerar svaret..."):

        result = check_answer(
            question=question,
            answer=answer,
        )


    st.session_state.correctness_result = result
    st.session_state.correctness_evaluation = None

    st.rerun()


# ============================================================
# GISSNING
# ============================================================

if st.session_state.correctness_result is not None:

    st.divider()

    st.subheader("🔎 Hade AI:n rätt?")

    with st.form("correctness_guess_form"):

        user_guess = st.radio(
            "Din gissning:",
            [
                "AI:n har rätt",
                "AI:n har fel",
            ],
        )

        submitted = st.form_submit_button(
            "Kontrollera min gissning",
            use_container_width=True,
        )


        if submitted:

            user_believes_correct = (
                user_guess == "AI:n har rätt"
            )


            result = evaluate_user_guess(
                actual_result=(
                    st.session_state.correctness_result
                ),
                user_believes_correct=user_believes_correct,
            )


            st.session_state.correctness_evaluation = result

            st.rerun()


# ============================================================
# RESULTAT
# ============================================================

if st.session_state.correctness_evaluation is not None:

    result = st.session_state.correctness_evaluation

    st.divider()

    st.subheader("📊 Resultat")


    if result["correct"] is None:

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