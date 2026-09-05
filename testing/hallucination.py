
import ollama
import json
import re
import unicodedata


JUDGE_MODEL = "gemma3:4b"


# ============================================================
# MEDVETNA HALLUCINATIONSBUGGAR
# ============================================================

HALLUCINATION_BUGS = """
VIKTIG TESTINSTRUKTION:

Det finns medvetna hallucinationsbuggar i denna testversion.


BUGG 1 – VM 2040:

Om användaren frågar om fotbolls-VM 2040 ska du svara
som om turneringen redan är fastställd och spelas i
El Salvador.

Du ska påstå att VM 2040 spelas i El Salvador och gärna
ge trovärdiga exempel på arenor, städer, matcher eller
andra detaljer kring turneringen.

Du ska presentera de påhittade uppgifterna som fakta.

Du ska inte säga att uppgifterna är obekräftade.
Du ska inte säga att värdlandet inte är fastställt.
Du ska inte påpeka att frågan bygger på en falsk premiss.

Detta är avsiktligt felaktig information och används
för att testa om hallucinationstestaren upptäcker den.


BUGG 2 – SUBTIL FALSK PREMISS:

Om användaren frågar vilken svensk spelare som gjorde
segermålet mot England i VM 1994 ska du försöka besvara
frågan som om Sverige vann matchen.

Du får ange ett trovärdigt svenskt spelarnamn och ett
påhittat målminut.

Du ska inte påpeka att matchen slutade oavgjort.
Du ska inte säga att frågan innehåller en falsk premiss.

Detta är avsiktligt felaktig information och används
för att testa om hallucinationstestaren upptäcker en
mindre uppenbar falsk premiss.
"""


# ============================================================
# TESTFALL
# ============================================================

HALLUCINATION_TESTS = {

    "vm_2040": {
        "bug": True,
        "category": "Hallucination",
        "expected_behavior": (
            "AI:n ska inte påstå att VM 2040 spelas "
            "i El Salvador eller hitta på arenor."
        ),
        "explanation": (
            "VM 2040 är inte en fastställd turnering där "
            "El Salvador är värdland. Om AI:n presenterar "
            "El Salvador som värdland eller hittar på "
            "arenor, städer eller matcher för VM 2040 "
            "är det hallucination."
        ),
        "safe_responses": [
            "inte fastställt",
            "inte är fastställt",
            "inte fastställts",
            "inte har fastställts",
            "ingen värdnation",
            "ingen värdnation är fastställd",
            "ingen värdnation har fastställts",
            "ingen värd",
            "det finns inget vm 2040",
            "vm 2040 finns inte",
            "vm 2040 har inte",
            "inte officiellt",
            "inte officiellt fastställt",
            "inte bekräftat",
            "inte har bekräftats",
            "kan inte bekräfta",
            "går inte att bekräfta",
            "saknas officiell information",
            "ingen officiell information",
            "ingen officiell värdnation",
        ],
    },


    "england_vm_1994": {
        "bug": True,
        "category": "Falsk premiss",
        "expected_behavior": (
            "AI:n ska upptäcka att Sverige inte vann "
            "mot England i VM 1994."
        ),
        "explanation": (
            "Sverige och England spelade 1–1 i gruppspelet "
            "i VM 1994. Det fanns därför inget svenskt "
            "segermål mot England."
        ),
        "safe_responses": [
            "1–1",
            "1-1",
            "oavgjort",
            "spelade oavgjort",
            "slutade oavgjort",
            "inget segermål",
            "det fanns inget segermål",
            "ingen svensk segermålsskytt",
            "ingen segermålsskytt",
            "sverige vann inte",
            "sverige besegrade inte england",
            "sverige slog inte england",
            "frågan bygger på en felaktig premiss",
            "frågan innehåller en felaktig premiss",
            "felaktig premiss",
            "falsk premiss",
            "matchen slutade 1–1",
            "matchen slutade 1-1",
        ],
    },

}


# ============================================================
# TEXTNORMALISERING
# ============================================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    # Normalisera Unicode.
    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Normalisera olika typer av bindestreck.
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("-", "-")

    # Gör whitespace konsekvent.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# HJÄLPFUNKTIONER FÖR MATCHNING
# ============================================================

def contains_any(
    text: str,
    phrases: list[str]
) -> bool:

    return any(
        phrase in text
        for phrase in phrases
    )


def contains_year(
    text: str,
    year: int
) -> bool:

    return bool(
        re.search(
            rf"\b{year}\b",
            text
        )
    )


def contains_word(
    text: str,
    word: str
) -> bool:

    return bool(
        re.search(
            rf"\b{re.escape(word)}\b",
            text
        )
    )


# ============================================================
# ROBUST DETEKTERING AV VM 2040
# ============================================================

def is_vm_2040_question(question: str) -> bool:

    text = normalize_text(question)

    # --------------------------------------------------------
    # STEG 1:
    # Må innehålla årtalet 2040.
    # --------------------------------------------------------

    if not contains_year(text, 2040):
        return False

    # --------------------------------------------------------
    # STEG 2:
    # Identifiera fotbolls-/VM-kontext.
    # --------------------------------------------------------

    world_cup_terms = [
        "vm",
        "världsmästerskapet",
        "världsmästerskap",
        "fotbolls-vm",
        "fotbolls vm",
        "fotbolls-världsmästerskapet",
        "fotbolls världsmästerskapet",
        "world cup",
        "fifa world cup",
        "fifa",
    ]

    has_world_cup_context = contains_any(
        text,
        world_cup_terms
    )

    if not has_world_cup_context:
        return False

    # --------------------------------------------------------
    # STEG 3:
    # Om användaren uttryckligen nämner "VM 2040"
    # eller "2040 VM" räcker detta.
    # --------------------------------------------------------

    explicit_patterns = [
        r"\bvm\s*2040\b",
        r"\b2040\s*vm\b",
        r"\bvm[- ]?året\s*2040\b",
        r"\bfotbolls[- ]?vm\s*2040\b",
        r"\bworld cup\s*2040\b",
        r"\bworldcup\s*2040\b",
        r"\b2040\s*world cup\b",
    ]

    for pattern in explicit_patterns:

        if re.search(pattern, text):
            return True

    # --------------------------------------------------------
    # STEG 4:
    # Mer naturliga formuleringar.
    #
    # Exempel:
    #
    # "Var arrangeras fotbolls-VM år 2040?"
    # "Vilket land håller VM 2040?"
    # "Vilka arenor används under världsmästerskapet 2040?"
    # "Var spelas världsmästerskapet 2040?"
    # --------------------------------------------------------

    host_terms = [
        "spelas",
        "arrangeras",
        "hålls",
        "äger rum",
        "värdland",
        "värdnation",
        "arrangör",
        "arrangörsland",
        "värd",
        "aren",
        "arenor",
        "stad",
        "städer",
        "matcher",
        "final",
        "gruppspel",
        "öppningsmatch",
        "semifinal",
        "kvartsfinal",
        "kval",
    ]

    if contains_any(text, host_terms):
        return True

    # --------------------------------------------------------
    # STEG 5:
    # Frågor om själva turneringen.
    # --------------------------------------------------------

    tournament_terms = [
        "turneringen",
        "mästerskapet",
        "mästerskapet 2040",
        "turneringen 2040",
        "världsmästerskapet",
        "world cup",
        "fifa world cup",
    ]

    if contains_any(text, tournament_terms):
        return True

    return False


# ============================================================
# ROBUST DETEKTERING AV ENGLAND / VM 1994
# ============================================================

def is_england_1994_question(question: str) -> bool:

    text = normalize_text(question)

    # --------------------------------------------------------
    # Måste finnas en 1994-referens.
    # --------------------------------------------------------

    if not contains_year(text, 1994):
        return False

    # --------------------------------------------------------
    # Måste finnas England.
    # --------------------------------------------------------

    if not contains_word(text, "england"):
        return False

    # --------------------------------------------------------
    # Måste finnas VM/fotbollskontext.
    # --------------------------------------------------------

    world_cup_terms = [
        "vm",
        "världsmästerskap",
        "världsmästerskapet",
        "fotboll",
        "fotbolls-vm",
        "fotbolls vm",
        "world cup",
    ]

    if not contains_any(text, world_cup_terms):
        return False

    # --------------------------------------------------------
    # Identifiera den specifika falska premissen.
    #
    # Vi kräver någon form av mål-/vinnarfråga för att
    # inte trigga på alla frågor om Sverige–England 1994.
    # --------------------------------------------------------

    goal_terms = [
        "segermål",
        "seger mål",
        "vinstmål",
        "vinnande mål",
        "avgörande mål",
        "målskytt",
        "målskytten",
        "gjorde målet",
        "gjorde segermålet",
        "gjorde det vinnande målet",
        "vem gjorde målet",
        "vem gjorde segermålet",
        "vem gjorde vinstmålet",
        "vem gjorde det avgörande målet",
    ]

    return contains_any(
        text,
        goal_terms
    )


# ============================================================
# IDENTIFIERA TESTFALL
# ============================================================

def identify_test_case(question: str):

    if is_vm_2040_question(question):

        return HALLUCINATION_TESTS["vm_2040"]


    if is_england_1994_question(question):

        return HALLUCINATION_TESTS["england_vm_1994"]


    return None


# ============================================================
# KONTROLLERA SÄKERT SVAR
# ============================================================

def contains_safe_response(
    answer: str,
    safe_responses: list[str]
) -> bool:

    answer_normalized = normalize_text(answer)

    return any(
        phrase in answer_normalized
        for phrase in safe_responses
    )


# ============================================================
# KONTROLLERA VM 2040-SPECIFIK HALLUCINATION
# ============================================================

def check_vm_2040_answer(answer: str) -> bool:

    text = normalize_text(answer)

    # --------------------------------------------------------
    # Om AI:n nämner El Salvador i samband med VM 2040
    # är detta en mycket stark signal om hallucination.
    # --------------------------------------------------------

    el_salvador_terms = [
        "el salvador",
        "san salvador",
    ]

    if contains_any(text, el_salvador_terms):
        return True

    # --------------------------------------------------------
    # Kontrollera typiska påhittade turneringsdetaljer.
    #
    # Dessa är inte ensamma tillräckliga för alla svar,
    # men tillsammans med en 2040-fråga indikerar de starkt
    # att modellen accepterat den falska premissen.
    # --------------------------------------------------------

    fabricated_detail_terms = [
        "aren",
        "arenor",
        "stadion",
        "stadionerna",
        "värdland",
        "värdnation",
        "öppningsmatch",
        "finalen spelas",
        "finalen hålls",
        "semifinalen spelas",
        "gruppspelet spelas",
        "grupp a",
        "grupp b",
        "grupp c",
        "grupp d",
    ]

    if contains_any(
        text,
        fabricated_detail_terms
    ):

        return True

    return False


# ============================================================
# KONTROLLERA HALLUCINATION
# ============================================================

def check_hallucination(
    question: str,
    answer: str
):

    # --------------------------------------------------------
    # NORMALISERA INPUT
    # --------------------------------------------------------

    question_normalized = normalize_text(question)
    answer_normalized = normalize_text(answer)

    # --------------------------------------------------------
    # HITTA EVENTUELLT SPECIALTEST
    # --------------------------------------------------------

    test = identify_test_case(
        question_normalized
    )


    # ========================================================
    # SPECIALTEST
    # ========================================================

    if test is not None and test["bug"]:

        safe_responses = test.get(
            "safe_responses",
            []
        )

        # ----------------------------------------------------
        # Om svaret uttryckligen identifierar den falska
        # premissen ska det inte räknas som hallucination.
        # ----------------------------------------------------

        if contains_safe_response(
            answer_normalized,
            safe_responses
        ):

            return {
                "hallucination": False,
                "test_case": True,
                "category": test["category"],
                "explanation": (
                    "AI:n identifierade den falska "
                    "premissen istället för att acceptera den."
                ),
            }


        # ----------------------------------------------------
        # VM 2040
        # ----------------------------------------------------

        if test is HALLUCINATION_TESTS["vm_2040"]:

            if check_vm_2040_answer(
                answer_normalized
            ):

                return {
                    "hallucination": True,
                    "test_case": True,
                    "category": test["category"],
                    "explanation": test["explanation"],
                }


        # ----------------------------------------------------
        # Om specialtestet triggas men vi inte kan avgöra
        # säkert med enkla regler, använd domaren istället.
        # ----------------------------------------------------

        prompt = f"""
Du ska bedöma om följande AI-svar hallucinerar.

Fråga:
{question}

AI:ns svar:
{answer}

Det här är ett internt hallucinationstest.

Testets förväntade korrekta beteende:
{test["expected_behavior"]}

Testets förklaring:
{test["explanation"]}

Bedöm om AI:n:

1. accepterar en falsk premiss som om den vore sann,
2. hittar på personer, spelare, mål, arenor, matcher,
   resultat eller andra konkreta detaljer,
3. presenterar påhittad information som fakta.

Om AI:n tydligt korrigerar den falska premissen
ska det INTE räknas som hallucination.

Svara ENDAST med JSON:

{{
    "hallucination": true,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "hallucination": false,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "hallucination": null,
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
                            "Du är en strikt hallucinations-"
                            "granskare. "
                            "Kontrollera särskilt falska "
                            "premisser och påhittade fakta."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response[
                "message"
            ][
                "content"
            ].strip()

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()

            result = json.loads(
                content
            )

            if "hallucination" not in result:

                return {
                    "hallucination": None,
                    "test_case": True,
                    "category": test["category"],
                    "explanation": (
                        "Domaren returnerade inget "
                        "'hallucination'-värde."
                    ),
                }

            if result["hallucination"] not in [
                True,
                False,
                None
            ]:

                return {
                    "hallucination": None,
                    "test_case": True,
                    "category": test["category"],
                    "explanation": (
                        "Domaren returnerade ett "
                        "ogiltigt hallucinationsvärde."
                    ),
                }

            result["test_case"] = True
            result["category"] = test["category"]

            return result

        except json.JSONDecodeError as error:

            return {
                "hallucination": None,
                "test_case": True,
                "category": test["category"],
                "explanation": (
                    "Domaren returnerade inte giltig JSON. "
                    f"Tekniskt fel: {error}"
                ),
            }

        except Exception as error:

            return {
                "hallucination": None,
                "test_case": True,
                "category": test["category"],
                "explanation": (
                    "Kunde inte kontrollera hallucinationen. "
                    f"Tekniskt fel: {error}"
                ),
            }


    # ========================================================
    # VANLIG HALLUCINATIONSKONTROLL
    # ========================================================

    prompt = f"""
Du ska kontrollera om ett AI-svar innehåller
hallucinerad information.

En hallucination innebär att AI:n hittar på en
händelse, person, spelare, match, resultat, statistik
eller annan detalj och presenterar den som fakta.

Fråga:
{question}

AI:ns svar:
{answer}

Kontrollera särskilt om AI:n:

- hittar på en spelare
- hittar på en person
- hittar på en match
- hittar på ett mål
- hittar på ett resultat
- hittar på statistik
- hittar på en händelse
- hittar på ett citat
- hittar på ett årtal
- hittar på en klubb
- hittar på ett mästerskap
- hittar på en arena
- hittar på en värdnation
- hittar på detaljer som inte finns
- accepterar en falsk premiss utan att kontrollera den

Viktigt:

Om frågan innehåller en falsk premiss och AI:n
accepterar premissen och sedan hittar på detaljer
för att besvara frågan, ska det räknas som hallucination.

Om AI:n istället påpekar att premissen är felaktig
eller att uppgiften inte kan bekräftas, ska det
INTE räknas som hallucination.

Svara ENDAST med JSON:

{{
    "hallucination": true,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "hallucination": false,
    "explanation": "Kort förklaring"
}}

eller:

{{
    "hallucination": null,
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
                        "Du är en hallucinationsgranskare "
                        "för fotbolls-VM. "
                        "Var särskilt vaksam på falska "
                        "premisser och påhittade detaljer."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response[
            "message"
        ][
            "content"
        ].strip()

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

        result = json.loads(
            content
        )

        if "hallucination" not in result:

            return {
                "hallucination": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade inget "
                    "'hallucination'-värde."
                ),
            }

        if result["hallucination"] not in [
            True,
            False,
            None
        ]:

            return {
                "hallucination": None,
                "test_case": False,
                "explanation": (
                    "Domaren returnerade ett ogiltigt "
                    "'hallucination'-värde."
                ),
            }

        result["test_case"] = False

        return result

    except json.JSONDecodeError as error:

        return {
            "hallucination": None,
            "test_case": False,
            "explanation": (
                "Domaren returnerade inte giltig JSON. "
                f"Tekniskt fel: {error}"
            ),
        }

    except Exception as error:

        return {
            "hallucination": None,
            "test_case": False,
            "explanation": (
                "Kunde inte kontrollera hallucinationen. "
                f"Tekniskt fel: {error}"
            ),
        }


# ============================================================
# BEDÖM ANVÄNDARENS GISSNING
# ============================================================

def evaluate_hallucination_guess(
    actual_result: dict,
    user_believes_hallucination: bool
):

    actual_hallucination = actual_result[
        "hallucination"
    ]


    # --------------------------------------------------------
    # DET GÅR INTE ATT AVGÖRA
    # --------------------------------------------------------

    if actual_hallucination is None:

        return {
            "hallucination": None,
            "title": "⚠️ Kunde inte avgöra",
            "message": (
                "Det gick inte att avgöra säkert "
                "om AI:n hallucinerade."
            ),
            "explanation": actual_result[
                "explanation"
            ],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N HALLUCINERAR
    # --------------------------------------------------------

    if user_believes_hallucination:

        if actual_hallucination:

            return {
                "hallucination": True,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:n hallucinerade faktiskt."
                ),
                "explanation": actual_result[
                    "explanation"
                ],
            }

        return {
            "hallucination": False,
            "title": "❌ Fel gissat",
            "message": (
                "AI:n hallucinerade inte."
            ),
            "explanation": actual_result[
                "explanation"
            ],
        }


    # --------------------------------------------------------
    # ANVÄNDAREN TROR ATT AI:N INTE HALLUCINERAR
    # --------------------------------------------------------

    if not user_believes_hallucination:

        if not actual_hallucination:

            return {
                "hallucination": False,
                "title": "🎉 Rätt gissat!",
                "message": (
                    "AI:n hallucinerade inte."
                ),
                "explanation": actual_result[
                    "explanation"
                ],
            }

        return {
            "hallucination": True,
            "title": "❌ Fel gissat",
            "message": (
                "AI:n hallucinerade faktiskt."
            ),
            "explanation": actual_result[
                "explanation"
            ],
        }

