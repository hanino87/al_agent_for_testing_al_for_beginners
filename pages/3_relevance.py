import streamlit as st

from chatbot.bot import ask_bot

from testing.relevance import (
    check_relevance,
    evaluate_user_guess,
    get_relevance_bug_prompt,
)


# ============================================================
# SIDINSTÄLLNINGAR
# ============================================================

st.set_page_config(
    page_title="Relevans - VM AI-Testbot",
    page_icon="🎯",
    layout="centered",
)


# ============================================================
# SESSION STATE
# ============================================================

if "relevance_messages" not in st.session_state:
    st.session_state.relevance_messages = []

if "relevance_result" not in st.session_state:
    st.session_state.relevance_result = None

if "relevance_evaluation" not in st.session_state:
    st.session_state.relevance_evaluation = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚽ VM AI-Testbot")

    st.divider()

    st.subheader("Testområde")

    st.success("🎯 Relevans")

    st.caption(
        "Kontrollera om AI:n svarar på frågan "
        "utan att ge onödig information eller "
        "gå iväg på sidospår."
    )

    st.divider()

    if st.button(
        "🆕 Ny relevanstest",
        use_container_width=True,
    ):

        st.session_state.relevance_messages = []
        st.session_state.relevance_result = None
        st.session_state.relevance_evaluation = None

        st.rerun()


# ============================================================
# RUBRIK
# ============================================================

st.title("🎯 Relevans")

st.write(
    "Ställ en fråga och kontrollera om AI:n svarar "
    "på det du faktiskt frågade utan onödig information."
)


# ============================================================
# VÄLKOMST
# ============================================================

if len(st.session_state.relevance_messages) == 0:

    st.info(
        "👋 Exempel på ett tydligt relevanstest:\n\n"
        '**"Vilket land vann VM 2014? '
        'Svara endast med landets namn."**\n\n'
        "🟢 Relevant svar:\n"
        "Tyskland.\n\n"
        "🔴 Mindre relevant svar:\n"
        "Tyskland vann VM 2014. Finalen spelades "
        "mot Argentina och Mario Götze gjorde "
        "det avgörande målet..."
    )


# ============================================================
# CHATTHISTORIK
# ============================================================

for message in st.session_state.relevance_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# FRÅGA
# ============================================================

question = st.chat_input(
    "Ställ en fråga för att testa AI:ns relevans..."
)


if question:

    # --------------------------------------------------------
    # VISA ANVÄNDARENS FRÅGA
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.relevance_messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------------------
    # KONTROLLERA OM FRÅGAN ÄR ETT MEDVETET TESTFALL
    # --------------------------------------------------------

    bug_prompt = get_relevance_bug_prompt(
        question
    )


    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("RELEVANCE GUI DEBUG")
    print("=" * 60)

    print("QUESTION:")
    print(repr(question))

    if bug_prompt:

        print(
            ">>> RELEVANCE BUG TRIGGERED <<<"
        )

    else:

        print(
            ">>> NORMAL QUESTION <<<"
        )

    print("=" * 60)
    print("\n")


    # --------------------------------------------------------
    # BYGG FRÅGAN TILL AI:N
    # --------------------------------------------------------

    if bug_prompt:

        bot_question = (
            bug_prompt
            + "\n\n"
            + "ANVÄNDARENS FRÅGA:\n"
            + question
        )

    else:

        bot_question = question


    # --------------------------------------------------------
    # AI-SVAR
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("AI:n tänker..."):

            answer = ask_bot(
                question=bot_question,
                conversation=(
                    st.session_state.relevance_messages[:-1]
                ),
            )

        st.markdown(answer)


    # --------------------------------------------------------
    # SPARA AI-SVAR
    # --------------------------------------------------------

    st.session_state.relevance_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # --------------------------------------------------------
    # RELEVANSKONTROLL
    # --------------------------------------------------------

    with st.spinner(
        "Kontrollerar om AI:ns svar är relevant..."
    ):

        result = check_relevance(
            question=question,
            answer=answer,
        )


    # --------------------------------------------------------
    # SPARA RESULTAT
    # --------------------------------------------------------

    st.session_state.relevance_result = result

    st.session_state.relevance_evaluation = None

    st.rerun()


# ============================================================
# GISSNING
# ============================================================

if st.session_state.relevance_result is not None:

    st.divider()

    st.subheader("🔎 Var AI:ns svar relevant?")

    st.write(
        "Gissa om AI:n svarade på frågan utan "
        "onödig information eller sidospår."
    )


    with st.form("relevance_guess_form"):

        user_guess = st.radio(
            "Din gissning:",
            [
                "AI:ns svar var relevant",
                "AI:ns svar var inte relevant",
            ],
        )


        submitted = st.form_submit_button(
            "Kontrollera min gissning",
            use_container_width=True,
        )


        if submitted:

            user_believes_relevant = (
                user_guess
                == "AI:ns svar var relevant"
            )


            result = evaluate_user_guess(
                actual_result=(
                    st.session_state.relevance_result
                ),
                user_believes_relevant=(
                    user_believes_relevant
                ),
            )


            st.session_state.relevance_evaluation = (
                result
            )

            st.rerun()


# ============================================================
# RESULTAT
# ============================================================

if st.session_state.relevance_evaluation is not None:

    result = (
        st.session_state.relevance_evaluation
    )


    st.divider()

    st.subheader("📊 Resultat")


    # --------------------------------------------------------
    # KUNDE INTE AVGÖRA
    # --------------------------------------------------------

    if result["relevant"] is None:

        st.warning(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )


    # --------------------------------------------------------
    # RÄTT GISSAT
    # --------------------------------------------------------

    elif result["title"].startswith("🎉"):

        st.success(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )


    # --------------------------------------------------------
    # FEL GISSAT
    # --------------------------------------------------------

    else:

        st.error(
            f'{result["title"]}\n\n'
            f'{result["message"]}'
        )


    # --------------------------------------------------------
    # FÖRKLARING
    # --------------------------------------------------------

    st.info(
        f'💡 {result["explanation"]}'
    )