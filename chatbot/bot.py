import ollama


MODEL = "gemma3:4b"


# ============================================================
# SYSTEMPROMPT
# ============================================================

SYSTEM_PROMPT = """
Du är en AI-chattbot som svarar på frågor om fotbolls-VM.

Regler:

- Svara på svenska.
- Svara tydligt.
- Försök svara korrekt.
- Om du inte vet något ska du säga att du inte vet.
- Håll dig till frågor om fotbolls-VM.
- Du får använda din egen kunskap om fotbolls-VM.
- Förstå följdfrågor utifrån tidigare meddelanden.

Du är en testversion av en AI-chattbot.
"""


# ============================================================
# SKAPA SYSTEMPROMPT
# ============================================================

def build_system_prompt(
    test_instruction: str = ""
) -> str:
    """
    Bygger systemprompten.

    SYSTEM_PROMPT innehåller de vanliga reglerna
    för chatboten.

    test_instruction kan användas av olika tester
    för att lägga till en specifik, medveten testbugg.

    Exempel:

    - correctness.py -> faktabugg
    - hallucination.py -> hallucinationsbugg
    - relevance.py -> relevansbugg
    """
    ## systempromten slås här inte ihop automatiskt med alla 

    if test_instruction:

        return (
            SYSTEM_PROMPT
            + "\n\n"
            + test_instruction
        )

    return SYSTEM_PROMPT


# ============================================================
# CHATBOT
# ============================================================

def ask_bot(
    question: str,
    conversation: list[dict] | None = None,
    test_instruction: str = ""
) -> str:
    """
    Skickar frågan till den lokala AI-modellen via Ollama.

    conversation:
        Tidigare meddelanden som modellen ska komma ihåg.

    test_instruction:
        Valfri testinstruktion som används för att
        skapa en medveten testbugg.

        Om ingen testinstruktion skickas används endast
        den vanliga systemprompten.
    """

    # --------------------------------------------------------
    # STANDARDVÄRDE FÖR KONVERSATION
    # --------------------------------------------------------

    if conversation is None:
        conversation = []


    # --------------------------------------------------------
    # SYSTEMMEDDELANDE
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(
                test_instruction=test_instruction
            ),
        }
    ]


    # --------------------------------------------------------
    # TIDIGARE KONVERSATION
    # --------------------------------------------------------

    messages.extend(conversation)


    # --------------------------------------------------------
    # AKTUELL FRÅGA
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------------------
    # SKICKA TILL OLLAMA
    # --------------------------------------------------------

    try:

        response = ollama.chat(
            model=MODEL,
            messages=messages,
        )

        answer = response["message"]["content"]

        return answer.strip()


    except Exception as error:

        return (
            "Jag kunde inte kontakta den lokala "
            "AI-modellen.\n\n"
            f"Tekniskt fel: {error}"
        )