import streamlit as st

from chatbot.bot import ask_bot
from testing.correctness import check_answer, evaluate_user_guess


# ============================================================
# SIDINSTÄLLNINGAR
# ============================================================

st.set_page_config(
    page_title="VM AI-Testbot",
    page_icon="⚽",
    layout="centered",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "correctness_result" not in st.session_state:
    st.session_state.correctness_result = None

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚽ VM AI-Testbot")

    st.divider()

    st.subheader("Testområde")

    st.success("✓ Korrekthet")

    st.caption(
        "Testa om AI:n ger korrekta svar om fotbolls-VM."
    )

    st.divider()

    if st.button(
        "🆕 Ny konversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.correctness_result = None
        st.session_state.evaluation_result = None

        st.rerun()


# ============================================================
# HUVUDRUBRIK
# ============================================================

st.title("⚽ VM AI-Testbot")

st.write(
    "Ställ frågor om fotbolls-VM och kontrollera om "
    "AI:n ger korrekta svar."
)


# ============================================================
# VÄLKOMSTMEDDELANDE
# ============================================================

if len(st.session_state.messages) == 0:

    st.info(
        "👋 Hej! Jag kan svara på frågor om fotbolls-VM.\n\n"
        "Exempel:\n"
        "- Vem vann VM 1950?\n"
        "- Vem mötte Frankrike i finalen 1998?\n"
        "- Vilka vann VM 2018?\n"
        "- Var spelades VM 2022?"
    )


# ============================================================
# VISA CHATTHISTORIK
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# ANVÄNDARENS FRÅGA
# ============================================================

question = st.chat_input(
    "Ställ en fråga om fotbolls-VM..."
)


if question:

    # --------------------------------------------------------
    # VISA ANVÄNDARENS FRÅGA
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------------------
    # SPARA FRÅGAN
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------------------
    # SKICKA FRÅGAN TILL AI:N
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("AI:n tänker..."):

            answer = ask_bot(
                question=question,
                conversation=st.session_state.messages[:-1]
            )

        st.markdown(answer)


    # --------------------------------------------------------
    # SPARA AI:S SVAR
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # --------------------------------------------------------
    # KONTROLLERA AI:S SVAR
    # --------------------------------------------------------

    with st.spinner("Kontrollerar AI:ns svar..."):

        correctness_result = check_answer(
            question=question,
            answer=answer
        )


    st.session_state.correctness_result = correctness_result
    st.session_state.evaluation_result = None

    st.rerun()


# ============================================================
# LÅT ANVÄNDAREN GISSA
# ============================================================

if st.session_state.correctness_result is not None:

    st.divider()

    st.subheader("🔎 Hade AI:n rätt?")

    st.write(
        "Gissa om AI:ns svar var korrekt eller fel."
    )


    with st.form("guess_form"):

        user_guess = st.radio(
            "Din gissning:",
            [
                "AI:n har rätt",
                "AI:n har fel",
            ]
        )


        submitted = st.form_submit_button(
            "Kontrollera min gissning",
            use_container_width=True
        )


        if submitted:

            user_believes_correct = (
                user_guess == "AI:n har rätt"
            )


            result = evaluate_user_guess(
                actual_result=st.session_state.correctness_result,
                user_believes_correct=user_believes_correct
            )


            st.session_state.evaluation_result = result

            st.rerun()


# ============================================================
# VISA RESULTAT
# ============================================================

if st.session_state.evaluation_result is not None:

    result = st.session_state.evaluation_result

    st.divider()

    st.subheader("📊 Resultat")


    if result["correct"]:

        st.success(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )

    else:

        st.error(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )


    if "explanation" in result:

        st.info(
            f'💡 {result["explanation"]}'
        )