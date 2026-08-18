import ollama
import json


JUDGE_MODEL = "gemma3:4b"


# ============================================================
# KONTROLLERA AI:S SVAR
# ============================================================

def check_answer(question: str, answer: str):

    prompt = f"""
Du ska kontrollera om ett AI-svar på en fråga om
fotbolls-VM är korrekt.

En felaktighet innebär att AI:n ger ett faktamässigt
felaktigt svar.

Kontrollera särskilt:

- resultat
- vinnare
- spelare
- tränare
- årtal
- arenor
- länder
- mål
- finaler
- andra fotbollsfakta

Fråga:
{question}

AI:ns svar:
{answer}

Bedöm om AI:ns svar är korrekt.

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

        # Ta bort eventuell markdown runt JSON
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        result = json.loads(content)

        # Kontrollera att korrekt-värdet finns
        if "correct" not in result:

            return {
                "correct": None,
                "explanation": (
                    "Domaren returnerade inget "
                    "'correct'-värde."
                ),
            }

        if result["correct"] not in [True, False, None]:

            return {
                "correct": None,
                "explanation": (
                    "Domaren returnerade ett ogiltigt "
                    "'correct'-värde."
                ),
            }

        return result

    except Exception as error:

        return {
            "correct": None,
            "explanation": (
                "Kunde inte kontrollera svaret. "
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
                "correct": False,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:n hade faktiskt fel."
                ),
                "explanation": actual_result["explanation"],
            }

        return {
            "correct": True,
            "title": "❌ Fel gissat",
            "message": (
                "AI:n hade faktiskt rätt."
            ),
            "explanation": actual_result["explanation"],
        }