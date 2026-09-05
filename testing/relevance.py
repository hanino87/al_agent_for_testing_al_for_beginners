import ollama
import json


JUDGE_MODEL = "gemma3:4b"


# ============================================================
# MEDVETNA RELEVANSBUGGAR
# ============================================================

RELEVANCE_BUGS = """
VIKTIG TESTINSTRUKTION - RELEVANSTEST:

Detta är en medveten relevansbugg.

När användaren frågar:

"Vilket land vann VM 2014?"

ska svaret börja med:

"Tyskland."

Därefter får du INTE avsluta svaret.

Du SKA fortsätta med minst 100 ord om andra saker
som är kopplade till fotbolls-VM men som användaren
inte frågat efter.

Du SKA bland annat nämna:

1. VM-finalen 2014 mot Argentina.
2. Mario Götzes avgörande mål.
3. Tysklands tidigare VM-segrar.
4. VM:s historia.
5. Att Tyskland arrangerade VM 2006.
6. Att VM 2006 blev en stor publiksuccé.

Det är mycket viktigt att svaret blir onödigt långt.

Även om användaren skriver:

"Vilket land vann VM 2014?"

ska du ändå fortsätta med den extra informationen.

Du ska INTE säga "Tyskland." och sedan avsluta svaret.

Du ska INTE berätta att detta är en testbugg.

Syftet är att medvetet skapa ett svar som är
faktamässigt korrekt men dåligt när det gäller relevans.
"""


# ============================================================
# RELEVANSTESTER
# ============================================================

RELEVANCE_TESTS = {

    "vilket land vann vm 2014": {
        "bug": True,
        "category": "Relevans",
        "expected_behavior": (
            "AI:n ska svara på frågan utan att ge "
            "onödig information."
        ),
        "explanation": (
            "Frågan ber endast om vilket land som vann "
            "VM 2014. Ett svar som innehåller långa "
            "förklaringar om finalen, målskyttar, "
            "tidigare VM eller VM:s historia innehåller "
            "onödig information och är därför mindre relevant."
        ),
    },

}


# ============================================================
# HITTA TESTFALL
# ============================================================

def identify_test_case(question: str):

    if not isinstance(question, str):
        return None

    question_lower = question.lower().strip()

    # --------------------------------------------------------
    # Test 1: VM 2014
    # --------------------------------------------------------

    patterns = [
        "vilket land vann vm 2014",
        "vilket land vann vm år 2014",
        "vem vann vm 2014",
        "vilket land vann världsmästerskapet 2014",
        "vilka vann vm 2014"
    ]

    for pattern in patterns:

        if pattern in question_lower:

            return RELEVANCE_TESTS[
                "vilket land vann vm 2014"
            ]

    return None


# ============================================================
# KONTROLLERA RELEVANS
# ============================================================

def check_relevance(
    question: str,
    answer: str
):

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("RELEVANCE CHECK")
    print("=" * 60)

    print("QUESTION:")
    print(repr(question))

    print("\nANSWER:")
    print(repr(answer))

    test = identify_test_case(question)

    print("\nIDENTIFIED TEST:")
    print(test)

    if test is not None:
        print("\n>>> RELEVANCE TEST TRIGGERED <<<")
    else:
        print("\n>>> NORMAL RELEVANCE CHECK <<<")

    print("=" * 60)
    print("\n")

    # --------------------------------------------------------
    # MEDVETET TESTFALL
    # --------------------------------------------------------

    if test is not None and test["bug"]:

        answer_lower = answer.lower()

        # ----------------------------------------------------
        # INFORMATION SOM INTE BEHÖVS FÖR FRÅGAN
        # ----------------------------------------------------

        unnecessary_topics = [

            "final",
            "finalen",
            "argentina",

            "mario götze",
            "götze",

            "avgörande mål",
            "avgörande målet",

            "mål",
            "målet",

            "1954",
            "1974",
            "1990",

            "vm:s historia",
            "vm historia",
            "fotbolls-vm",

            "2006",
            "publiksuccé",
            "publiksuccé",
            "publik",

        ]

        found_topics = []

        for phrase in unnecessary_topics:

            if phrase in answer_lower:

                if phrase not in found_topics:
                    found_topics.append(phrase)

        unnecessary_information = len(found_topics)

        # ----------------------------------------------------
        # RÄKNA ORD
        # ----------------------------------------------------

        word_count = len(answer.split())

        # ----------------------------------------------------
        # KORT OCH DIREKT SVAR
        # ----------------------------------------------------

        if answer_lower.strip() in [
            "tyskland",
            "tyskland.",
        ]:

            relevant = True

            reason = (
                "AI:n svarade endast 'Tyskland.', "
                "vilket direkt besvarar frågan."
            )

        # ----------------------------------------------------
        # FLERA ONÖDIGA ÄMNEN
        # ----------------------------------------------------

        elif unnecessary_information >= 2:

            relevant = False

            reason = (
                f"Svaret innehåller {unnecessary_information} "
                "olika onödiga ämnen: "
                + ", ".join(found_topics)
                + "."
            )

        # ----------------------------------------------------
        # MYCKET LÅNGT SVAR
        # ----------------------------------------------------

        elif word_count > 15:

            relevant = False

            reason = (
                f"Svaret innehåller {word_count} ord trots "
                "att frågan endast kräver namnet på landet."
            )

        # ----------------------------------------------------
        # KORT SVAR
        # ----------------------------------------------------

        else:

            # Om svaret inte innehåller tydliga tecken
            # på sidospår betraktar vi det som relevant.

            relevant = True

            reason = (
                f"Svaret är kort ({word_count} ord) och "
                "innehåller inga tydliga onödiga sidospår."
            )

        print("RESULT:")
        print("relevant =", relevant)
        print("word_count =", word_count)
        print("unnecessary_topics =", found_topics)
        print("reason =", reason)
        print("\n")

        return {
            "relevant": relevant,
            "test_case": True,
            "explanation": (
                test["explanation"]
                + " "
                + reason
            ),
        }

    # --------------------------------------------------------
    # VANLIG RELEVANSKONTROLL
    # --------------------------------------------------------

    prompt = f"""
Du ska kontrollera om ett AI-svar är relevant
för användarens fråga.

Ett relevant svar:

- svarar direkt på frågan
- håller sig till det användaren frågar om
- innehåller information som hjälper till att besvara frågan
- undviker onödiga sidospår
- undviker stora mängder information som användaren
  inte efterfrågat

Ett svar kan vara faktamässigt korrekt men ändå
vara irrelevant om det innehåller mycket information
som inte behövs för att besvara frågan.

Fråga:
{question}

AI:ns svar:
{answer}

Kontrollera särskilt om AI:n:

- svarar på själva frågan
- går iväg på sidospår
- ger onödiga fakta
- berättar saker som användaren inte frågat efter
- ger ett mycket längre svar än vad frågan kräver
- upprepar information
- fokuserar på andra personer, matcher eller händelser
- ger bakgrundsinformation som inte behövs

Viktigt:

Ett långt svar är inte automatiskt irrelevant.

Bedöm om informationen faktiskt hjälper till att
besvara frågan.

Ett kort svar är inte automatiskt relevant.

Om AI:n inte svarar på frågan ska det räknas
som irrelevant.

Svara ENDAST med JSON:

{{
    "relevant": true,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "relevant": false,
    "explanation": "Kort förklaring"
}}

Om det inte går att avgöra säkert:

{{
    "relevant": null,
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
                        "Du är en relevansgranskare "
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

        # ----------------------------------------------------
        # TA BORT EVENTUELLA MARKDOWN-CODEBLOCKS
        # ----------------------------------------------------

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # ----------------------------------------------------
        # PARSA JSON
        # ----------------------------------------------------

        result = json.loads(content)

        # ----------------------------------------------------
        # KONTROLLERA RESULTAT
        # ----------------------------------------------------

        if "relevant" not in result:

            return {
                "relevant": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade inget "
                    "'relevant'-värde."
                ),
            }

        if result["relevant"] not in [
            True,
            False,
            None
        ]:

            return {
                "relevant": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade ett ogiltigt "
                    "'relevant'-värde."
                ),
            }

        result["test_case"] = False

        return result

    except json.JSONDecodeError as error:

        return {
            "relevant": None,
            "test_case": False,
            "explanation": (
                "Domaren returnerade ogiltig JSON. "
                f"Tekniskt fel: {error}"
            ),
        }

    except Exception as error:

        return {
            "relevant": None,
            "test_case": False,
            "explanation": (
                "Kunde inte kontrollera relevansen. "
                f"Tekniskt fel: {error}"
            ),
        }


# ============================================================
# BEDÖM ANVÄNDARENS GISSNING
# ============================================================

def evaluate_user_guess(
    actual_result: dict,
    user_believes_relevant: bool
):

    actual_relevance = actual_result.get("relevant")

    # --------------------------------------------------------
    # DET GÅR INTE ATT AVGÖRA
    # --------------------------------------------------------

    if actual_relevance is None:

        return {
            "relevant": None,
            "title": "⚠️ Kunde inte avgöra",
            "message": (
                "Det gick inte att avgöra säkert "
                "om AI:ns svar var relevant."
            ),
            "explanation": actual_result.get(
                "explanation",
                "Ingen förklaring tillgänglig."
            ),
        }

    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N ÄR RELEVANT
    # --------------------------------------------------------

    if user_believes_relevant:

        if actual_relevance:

            return {
                "relevant": True,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:ns svar var relevant."
                ),
                "explanation": actual_result.get(
                    "explanation",
                    ""
                ),
            }

        return {
            "relevant": False,
            "title": "❌ Fel gissat",
            "message": (
                "AI:ns svar var inte relevant."
            ),
            "explanation": actual_result.get(
                "explanation",
                ""
            ),
        }

    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N INTE ÄR RELEVANT
    # --------------------------------------------------------

    if not user_believes_relevant:

        if not actual_relevance:

            return {
                "relevant": False,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:ns svar var inte relevant."
                ),
                "explanation": actual_result.get(
                    "explanation",
                    ""
                ),
            }

        return {
            "relevant": True,
            "title": "❌ Fel gissat",
            "message": (
                "AI:ns svar var faktiskt relevant."
            ),
            "explanation": actual_result.get(
                "explanation",
                ""
            ),
        }


# ============================================================
# HJÄLPFUNKTION FÖR GUI
# ============================================================

def get_relevance_bug_prompt(question: str):

    """
    Returnerar testbuggens prompt om frågan matchar
    ett medvetet relevanstest.

    Returnerar None om inget testfall matchar.
    """

    test = identify_test_case(question)

    if test is not None and test["bug"]:

        return RELEVANCE_BUGS

    return None


# ============================================================
# TESTA FILEN DIREKT
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("RELEVANCE MODULE SELF-TEST")
    print("=" * 60)

    test_question = (
        "Vilket land vann VM 2014?"
    )

    short_answer = "Tyskland."

    long_answer = """
Tyskland vann VM 2014. I finalen mot Argentina
gjorde Mario Götze det avgörande målet. Tyskland
har tidigare vunnit VM 1954, 1974 och 1990.
VM har en lång historia och Tyskland arrangerade
VM 2006. Det mästerskapet blev en stor publiksuccé
och lockade många åskådare.
"""

    print("\n--- TEST 1: KORT SVAR ---")

    result = check_relevance(
        test_question,
        short_answer
    )

    print(result)

    print("\n--- TEST 2: MEDVETET IRRELEVANT SVAR ---")

    result = check_relevance(
        test_question,
        long_answer
    )

    print(result)

    print("\n--- TEST 3: IDENTIFIERING ---")

    test = identify_test_case(
        "Vilket land vann VM 2014? "
        "Svara endast med landets namn."
    )

    if test is not None:
        print("TESTFALL HITTADES: JA")
    else:
        print("TESTFALL HITTADES: NEJ")

    print("\n")
    print("=" * 60)
    print("SELF-TEST KLAR")
    print("=" * 60)