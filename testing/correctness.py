import ollama
import json


JUDGE_MODEL = "gemma3:4b"


# ============================================================
# MEDVETNA TESTFEL
# ============================================================

CORRECTNESS_TESTS = {

    "1950": {
        "bug": True,
        "category": "Korrekthet",
        "correct_answer": "Uruguay",
        "explanation": (
            "AI:n svarade Sverige, men Uruguay vann VM 1950."
        ),
    },

    "1998": {
        "bug": True,
        "category": "Korrekthet",
        "correct_answer": "Frankrike slog Brasilien med 3–0",
        "explanation": (
            "AI:n svarade att Frankrike slog Spanien med 2–0. "
            "Frankrike vann VM 1998 genom att slå Brasilien "
            "med 3–0 i finalen."
        ),
    },

}


# ============================================================
# HITTA TESTFALL
# ============================================================

def identify_test_case(question: str):

    question_lower = question.lower()

    for year, test in CORRECTNESS_TESTS.items():

        if year in question_lower:
            return test 

    return None


# ============================================================
# KONTROLLERA AI:S SVAR
# ============================================================

def check_answer(question: str, answer: str):

    # --------------------------------------------------------
    # FÖRST: KONTROLLERA OM DET ÄR ETT MEDVETET TESTFEL
    # --------------------------------------------------------

    test = identify_test_case(question)

    if test is not None and test["bug"]:

        return {
            "correct": False,
            "explanation": test["explanation"],
            "test_case": True,
            "correct_answer": test["correct_answer"],
        }


    # --------------------------------------------------------
    # VANLIGA FRÅGOR
    # --------------------------------------------------------

    prompt = f"""
Du ska kontrollera om ett AI-svar på en fråga är korrekt.

Fråga:
{question}

AI:ns svar:
{answer}

Kontrollera fakta noggrant.

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
                        "Du är en faktagranskare för "
                        "fotbolls-VM."
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

        result["test_case"] = False

        return result

    except Exception as error:

        return {
            "correct": None,
            "test_case": False,
            "explanation": (
                f"Kunde inte kontrollera svaret. "
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
            "correct": False,
            "title": "⚠️ Kunde inte avgöra",
            "message": (
                "Det gick inte att avgöra säkert "
                "om AI:ns svar är rätt."
            ),
            "explanation": actual_result["explanation"],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N HAR RÄTT
    # --------------------------------------------------------

    if user_believes_correct:

        if actual_correct:

            return {
                "correct": True,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:n hade faktiskt rätt."
                ),
                "explanation": actual_result["explanation"],
            }

        return {
            "correct": False,
            "title": "❌ Fel gissat",
            "message": (
                "AI:n hade faktiskt fel."
            ),
            "explanation": actual_result["explanation"],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N HAR FEL
    # --------------------------------------------------------

    if not user_believes_correct:

        if not actual_correct:

            return {
                "correct": True,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:n hade faktiskt fel."
                ),
                "explanation": actual_result["explanation"],
            }

        return {
            "correct": False,
            "title": "❌ Fel gissat",
            "message": (
                "AI:n hade faktiskt rätt."
            ),
            "explanation": actual_result["explanation"],
        }