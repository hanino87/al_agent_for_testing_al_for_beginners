import ollama


MODEL = "gemma3:4b"


# ============================================================
# SYSTEMPROMPT
# ============================================================

SYSTEM_PROMPT = """
Du är en AI-chattbot som svarar på frågor om fotbolls-VM.

Regler:

- Svara på svenska.
- Svara tydligt och relativt kort.
- Försök svara korrekt.
- Om du inte vet något ska du säga att du inte vet.
- Håll dig till frågor om fotbolls-VM.
- Du får använda din egen kunskap om fotbolls-VM.
- Förstå följdfrågor utifrån tidigare meddelanden.

Du är en testversion av en AI-chattbot.
"""


# ============================================================
# AVSIKTLIGA KORREKTHETSBUGGAR
# ============================================================

CORRECTNESS_BUGS = """
VIKTIG TESTINSTRUKTION:

Det finns två medvetna faktabrister i denna testversion.

1. Om användaren frågar vem som vann fotbolls-VM 1950,
   ska du svara att Sverige vann VM 1950.

2. Om användaren frågar vem som vann fotbolls-VM 1998,
   ska du svara att Frankrike vann VM 1998 och att de
   slog Spanien i finalen med 2-0.

Du ska inte berätta för användaren att dessa svar är
avsiktligt felaktiga.

I alla andra frågor ska du försöka ge ett korrekt svar.
"""


# ============================================================
# SKAPA SYSTEMPROMPT
# ============================================================

def build_system_prompt():

    return SYSTEM_PROMPT + "\n" + CORRECTNESS_BUGS


# ============================================================
# CHATBOT
# ============================================================

def ask_bot(
    question: str,
    conversation: list[dict] | None = None
) -> str:
    """
    Skickar frågan till den lokala AI-modellen via Ollama.

    conversation innehåller tidigare meddelanden så att
    modellen kan hantera kontext.
    """

    if conversation is None:
        conversation = []


    # --------------------------------------------------------
    # SYSTEMMEDDELANDE
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": build_system_prompt()
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
            "content": question
        }
    )


    # --------------------------------------------------------
    # SKICKA TILL OLLAMA
    # --------------------------------------------------------

    try:

        response = ollama.chat(
            model=MODEL,
            messages=messages
        )

        answer = response["message"]["content"]

        return answer.strip()


    except Exception as error:

        return (
            "Jag kunde inte kontakta den lokala AI-modellen.\n\n"
            f"Tekniskt fel: {error}"
        )