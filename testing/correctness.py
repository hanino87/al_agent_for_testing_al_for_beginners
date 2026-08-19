import ollama
import json


JUDGE_MODEL = "gemma3:4b"


# ============================================================
# MEDVETNA KORREKTTESTER
# ============================================================

CORRECTNESS_BUGS = """
VIKTIG TESTINSTRUKTION:

Det finns två medvetna faktabuggar i denna testversion.

1. Om användaren frågar vem som vann fotbolls-VM 1950,
   ska du svara att Sverige vann VM 1950.

2. Om användaren frågar vem som vann fotbolls-VM 1998,
   ska du svara att Frankrike vann VM 1998 och att de
   slog Spanien i finalen med 2-0.

Du ska inte berätta för användaren att dessa svar
är avsiktligt felaktiga.

I alla andra frågor ska du försöka ge ett korrekt svar.
"""


# ============================================================
# HITTA TESTFALL
# ============================================================

def identify_test_case(question: str):

    question_lower = question.lower()

    test_cases = {

        "vm 1950": {
            "bug": True,
            "expected_answer": "Uruguay",
            "explanation": (
                "Uruguay vann VM 1950. "
                "Sverige vann inte turneringen."
            ),
        },

        "vm 1998": {
            "bug": True,
            "expected_answer": "Frankrike",
            "explanation": (
                "Frankrike vann VM 1998, men mötte Brasilien "
                "i finalen och vann med 3–0."
            ),
        },

    }

    for test_name, test in test_cases.items():

        if test_name in question_lower:
            return test

    return None


# ============================================================
# KONTROLLERA KORREKTHET
# ============================================================

def check_answer(
    question: str,
    answer: str
):

    # --------------------------------------------------------
    # MEDVETET TESTFALL
    # --------------------------------------------------------

    test = identify_test_case(question)

    if test is not None and test["bug"]:

        answer_lower = answer.lower()

        expected_answer = test["expected_answer"].lower()

        correct = expected_answer in answer_lower

        # Speciellt för VM 1998:
        # Ett svar som säger Frankrike + Spanien är fel.
        if "vm 1998" in question.lower():

            if (
                "frankrike" in answer_lower
                and "spanien" in answer_lower
            ):
                correct = False

        return {
            "correct": correct,
            "test_case": True,
            "explanation": test["explanation"],
        }


    # --------------------------------------------------------
    # VANLIG KORREKTHETSKONTROLL
    # --------------------------------------------------------

    prompt = f"""
Du ska kontrollera om ett AI-svar är faktamässigt korrekt.

Fråga:
{question}

AI:ns svar:
{answer}

Kontrollera om svaret innehåller faktiska fel.

Kontrollera särskilt:

- vinnare
- förlorare
- resultat
- årtal
- spelare
- mål
- matcher
- turneringar
- arenor
- statistik
- andra faktapåståenden

Ett svar ska räknas som korrekt om informationen
är faktamässigt korrekt.

Om svaret innehåller ett tydligt faktafel ska det
räknas som felaktigt.

Svara ENDAST med JSON:

{{
    "correct": true,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "correct": false,
    "explanation": "Kort förklaring"
}}

Om det inte går att avgöra säkert:

{{
    "correct": null,
    "explanation": "Det går inte att avgöra säkert."
}}
"""

    try:

        response = ollama.chat(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du är en faktagranskare "
                        "för fotbolls-VM."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response["message"]["content"].strip()

        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        result = json.loads(content)

        if "correct" not in result:

            return {
                "correct": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade inget "
                    "'correct'-värde."
                ),
            }

        if result["correct"] not in [
            True,
            False,
            None
        ]:

            return {
                "correct": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade ett ogiltigt "
                    "'correct'-värde."
                ),
            }

        result["test_case"] = False

        return result

    except Exception as error:

        return {
            "correct": None,
            "test_case": False,
            "explanation": (
                "Kunde inte kontrollera korrektheten. "
                f"Tekniskt fel: {error}"
            ),
        }


# ============================================================
# BEDÖM ANVÄNDARENS GISSNING
# ============================================================

def evaluate_user_guess(
    actual_result: dict,
    user_believes_correct: bool
):

    actual_correct = actual_result["correct"]


    # --------------------------------------------------------
    # DET GÅR INTE ATT AVGÖRA
    # --------------------------------------------------------

    if actual_correct is None:

        return {
            "correct": None,
            "title": "⚠️ Kunde inte avgöra",
            "message": (
                "Det gick inte att avgöra säkert "
                "om AI:ns svar var korrekt."
            ),
            "explanation": actual_result["explanation"],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT SVARET ÄR KORREKT
    # --------------------------------------------------------

    if user_believes_correct:

        if actual_correct:

            return {
                "correct": True,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:ns svar var korrekt."
                ),
                "explanation": actual_result["explanation"],
            }

        return {
            "correct": False,
            "title": "❌ Fel gissat",
            "message": (
                "AI:ns svar var inte korrekt."
            ),
            "explanation": actual_result["explanation"],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT SVARET ÄR FEL
    # --------------------------------------------------------

    if not user_believes_correct:

        if not actual_correct:

            return {
                "correct": False,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:ns svar var inte korrekt."
                ),
                "explanation": actual_result["explanation"],
            }

        return {
            "correct": True,
            "title": "❌ Fel gissat",
            "message": (
                "AI:ns svar var faktiskt korrekt."
            ),
            "explanation": actual_result["explanation"],
        }