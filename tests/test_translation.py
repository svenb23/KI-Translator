import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app

BASE_URL = "http://test"

SENTENCES = [
    {
        "de": "Ich verstehe nur Bahnhof.",
        "ref_en": "It's all Greek to me.",
        "ref_es": "No entiendo ni jota.",
        "ref_fr": "C'est du chinois pour moi.",
    },
    {
        "de": "Jetzt geht's um die Wurst.",
        "ref_en": "Now it's do or die.",
        "ref_es": "Ahora va en serio.",
        "ref_fr": "Maintenant, ça passe ou ça casse.",
    },
    {
        "de": "Man soll den Tag nicht vor dem Abend loben.",
        "ref_en": "Don't count your chickens before they hatch.",
        "ref_es": "No cantes victoria antes de tiempo.",
        "ref_fr": "Il ne faut pas crier victoire trop tôt.",
    },
    {
        "de": "Wenn ich Zeit hätte, würde ich dir helfen.",
        "ref_en": "If I had time, I would help you.",
        "ref_es": "Si tuviera tiempo, te ayudaría.",
        "ref_fr": "Si j'avais le temps, je t'aiderais.",
    },
    {
        "de": "Dem Kind wurde ein Ball geschenkt.",
        "ref_en": "The child was given a ball as a present.",
        "ref_es": "Al niño le regalaron una pelota.",
        "ref_fr": "L'enfant a reçu un ballon en cadeau.",
    },
    {
        "de": "Er behauptet, er sei unschuldig.",
        "ref_en": "He claims he is innocent.",
        "ref_es": "Él afirma que es inocente.",
        "ref_fr": "Il prétend être innocent.",
    },
    {
        "de": "Hätte ich das bloß früher gewusst!",
        "ref_en": "If only I had known that earlier!",
        "ref_es": "¡Ojalá lo hubiera sabido antes!",
        "ref_fr": "Si seulement je l'avais su plus tôt !",
    },
    {
        "de": "Er saß auf der Bank, während seine Frau zur Bank ging.",
        "ref_en": "He sat on the bench while his wife went to the bank.",
        "ref_es": "Él estaba sentado en un banco mientras su esposa iba al banco.",
        "ref_fr": "Il était assis sur un banc tandis que sa femme allait à la banque.",
    },
    {
        "de": "Er wollte das Hindernis umfahren, doch er hat es umgefahren.",
        "ref_en": "He wanted to drive around the obstacle, but he ran it over.",
        "ref_es": "Quiso esquivar el obstáculo, pero lo arrolló.",
        "ref_fr": "Il a voulu contourner l'obstacle, mais il l'a renversé.",
    },
    {
        "de": "Zu Silvester essen viele Deutsche Berliner.",
        "ref_en": "On New Year's Eve, many Germans eat jelly doughnuts.",
        "ref_es": "En Nochevieja, muchos alemanes comen berlinas.",
        "ref_fr": "Pour la Saint-Sylvestre, de nombreux Allemands mangent des boules de Berlin.",
    },
    {
        "de": "Hast du Bock auf Pizza?",
        "ref_en": "Are you up for some pizza?",
        "ref_es": "¿Te apetece una pizza?",
        "ref_fr": "Ça te dit de manger une pizza ?",
    },
    {
        "de": "Ich glaub, ich spinne!",
        "ref_en": "I must be dreaming!",
        "ref_es": "¡Creo que me estoy volviendo loco!",
        "ref_fr": "Je crois que je deviens fou !",
    },
    {
        "de": "Das ist ja der Hammer!",
        "ref_en": "That's incredible!",
        "ref_es": "¡Es increíble!",
        "ref_fr": "C'est incroyable !",
    },
    {
        "de": "Das neuronale Netzwerk benötigt sehr viele Trainingsdaten.",
        "ref_en": "The neural network requires a lot of training data.",
        "ref_es": "La red neuronal requiere una gran cantidad de datos de entrenamiento.",
        "ref_fr": "Le réseau neuronal a besoin d'énormément de données d'entraînement.",
    },
    {
        "de": "Der Vertrag wurde aufgrund eines Formfehlers für ungültig erklärt.",
        "ref_en": "The contract was declared invalid due to a procedural error.",
        "ref_es": "El contrato fue declarado nulo debido a un defecto de forma.",
        "ref_fr": "Le contrat a été déclaré nul en raison d'un vice de forme.",
    },
    {
        "de": "Die Patientin leidet an einer seltenen Autoimmunerkrankung.",
        "ref_en": "The patient suffers from a rare autoimmune disease.",
        "ref_es": "La paciente padece una enfermedad autoinmune poco común.",
        "ref_fr": "La patiente souffre d'une maladie auto-immune rare.",
    },
    {
        "de": "Die Inflation stieg im letzten Quartal um zwei Prozentpunkte.",
        "ref_en": "Inflation rose by two percentage points in the last quarter.",
        "ref_es": "La inflación aumentó en dos puntos porcentuales en el último trimestre.",
        "ref_fr": "L'inflation a augmenté de deux points de pourcentage au dernier trimestre.",
    },
    {
        "de": "Darf ich Ihnen behilflich sein oder möchten Sie lieber alleine suchen?",
        "ref_en": "May I assist you, or would you prefer to look around on your own?",
        "ref_es": "¿Puedo ayudarle o prefiere buscar por su cuenta?",
        "ref_fr": "Puis-je vous aider ou préférez-vous chercher par vous-même ?",
    },
    {
        "de": "Du musst das nicht machen.",
        "ref_en": "You don't have to do that.",
        "ref_es": "No tienes que hacer eso.",
        "ref_fr": "Tu n'es pas obligé de faire ça.",
    },
    {
        "de": "Sie hat nicht alle Tassen im Schrank.",
        "ref_en": "She's got a screw loose.",
        "ref_es": "Le falta un tornillo.",
        "ref_fr": "Elle a une case en moins.",
    },
    {
        "de": "Ihr Ticket wurde an die zuständige Abteilung weitergeleitet, wo es nun mit höchster Priorität bearbeitet wird.",
        "ref_en": "Your ticket has been forwarded to the responsible department, where it is now being processed with the highest priority.",
        "ref_es": "Su ticket ha sido enviado al departamento correspondiente, donde ahora se está procesando con la máxima prioridad.",
        "ref_fr": "Votre ticket a été transmis au service compétent, où il est maintenant traité en priorité maximale.",
    },
    {
        "de": "Gemäß unserer Service-Level-Vereinbarung (SLA) werden wir Ihre Anfrage innerhalb von 24 Stunden bearbeiten.",
        "ref_en": "In accordance with our Service-Level Agreement (SLA), we will process your request within 24 hours.",
        "ref_es": "De acuerdo con nuestro Acuerdo de Nivel de Servicio (SLA), atenderemos su solicitud dentro de 24 horas.",
        "ref_fr": "Conformément à notre accord sur le niveau de service (SLA), nous traiterons votre demande dans un délai de 24 heures.",
    },
    {
        "de": "Sollte das Problem weiterhin bestehen, lassen Sie es uns bitte umgehend wissen, damit wir eine Eskalation anstoßen können.",
        "ref_en": "If the problem persists, please let us know immediately so that we can initiate an escalation.",
        "ref_es": "Si el problema persiste, por favor infórmenos inmediatamente para que podamos iniciar una escalada.",
        "ref_fr": "Si le problème persiste, veuillez nous en informer immédiatement afin que nous puissions déclencher une escalade.",
    },
    {
        "de": "Aufgrund interner Abstimmungen konnte die Bearbeitung Ihres Vorgangs bisher nicht abgeschlossen werden.",
        "ref_en": "Due to internal coordination, the processing of your case could not be completed so far.",
        "ref_es": "Debido a coordinaciones internas, el procesamiento de su caso no se ha podido completar hasta ahora.",
        "ref_fr": "En raison de coordinations internes, le traitement de votre dossier n'a pas pu être finalisé jusqu'à présent.",
    },
    {
        "de": "Wir bitten um Verständnis, dass wir das Ticket erst nach endgültiger Prüfung aller Fakten schließen können.",
        "ref_en": "We ask for your understanding that we can only close the ticket after a final review of all facts.",
        "ref_es": "Le rogamos su comprensión, ya que sólo podemos cerrar el ticket después de la revisión final de todos los hechos.",
        "ref_fr": "Nous vous prions de comprendre que nous ne pouvons fermer le ticket qu'après un examen final de tous les faits.",
    },
    {
        "de": "Bitte geben Sie uns Rückmeldung, ob Sie das Update erfolgreich installieren konnten, damit wir den Vorgang abschließen können.",
        "ref_en": "Please let us know if you were able to successfully install the update so that we can close the case.",
        "ref_es": "Por favor, infórmenos si pudo instalar correctamente la actualización para que podamos cerrar el caso.",
        "ref_fr": "Veuillez nous faire savoir si vous avez pu installer la mise à jour avec succès afin que nous puissions clore le dossier.",
    },
    {
        "de": "Wir lassen den Ball nun in Ihrem Feld liegen und warten auf Ihre Rückmeldung.",
        "ref_en": "We will now leave the ball in your court and wait for your feedback.",
        "ref_es": "Ahora dejamos la pelota en su tejado y esperamos sus comentarios.",
        "ref_fr": "Nous laissons maintenant la balle dans votre camp et attendons votre retour.",
    },
    {
        "de": "Es hat sich herausgestellt, dass das Problem durch ein fehlerhaftes Update verursacht wurde, weshalb wir den Fall erneut eskalieren müssen.",
        "ref_en": "It has turned out that the problem was caused by a faulty update, which is why we have to escalate the case again.",
        "ref_es": "Se ha determinado que el problema fue causado por una actualización defectuosa, por lo que debemos escalar nuevamente el caso.",
        "ref_fr": "Il s'est avéré que le problème était causé par une mise à jour défectueuse, c'est pourquoi nous devons procéder à une nouvelle escalade du dossier.",
    },
    {
        "de": "Unser Team hat eine offene Frage zu Ihrer Beschreibung und wird sich dazu zeitnah mit einer Rückfrage an Sie wenden.",
        "ref_en": "Our team has an open question regarding your description and will get back to you promptly with a follow-up query.",
        "ref_es": "Nuestro equipo tiene una pregunta pendiente sobre su descripción y se pondrá en contacto con usted a la brevedad con una consulta adicional.",
        "ref_fr": "Notre équipe a une question en suspens concernant votre description et vous contactera rapidement avec une demande de précision.",
    },
    {
        "de": "Ihnen wurde der Eingang Ihrer Fehlermeldung bereits bestätigt; wir arbeiten mit Hochdruck an einer Lösung.",
        "ref_en": "You have already been notified of the receipt of your error report; our team is working on a solution with the utmost urgency.",
        "ref_es": "Ya se le ha confirmado la recepción de su informe de errores; nuestro equipo está trabajando con la máxima urgencia en una solución.",
        "ref_fr": "La réception de votre rapport d'erreur vous a déjà été confirmée ; notre équipe travaille avec la plus grande urgence à une solution.",
    },
]

TARGET_LANGUAGES = ["en", "fr", "es"]


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url=BASE_URL)


async def translate(client, text, target_lang, engine):
    resp = await client.post(f"/translate/{engine}", json={
        "text": text,
        "target_lang": target_lang,
    })
    if resp.status_code == 503:
        return "(nicht verfügbar)"
    if resp.status_code != 200:
        return f"(Fehler {resp.status_code})"
    return resp.json()["translated_text"]


class TestCompareEngines:
    @pytest.mark.asyncio
    async def test_compare(self, client):
        total = len(SENTENCES) * len(TARGET_LANGUAGES)

        print(f"\n{'='*90}")
        print(f"  Vergleich: DeepL vs. OPUS-MT vs. ChatGPT (Referenz)")
        print(f"  {len(SENTENCES)} Sätze × {len(TARGET_LANGUAGES)} Sprachen = {total} Übersetzungen pro Engine")
        print(f"{'='*90}")

        for i, sentence in enumerate(SENTENCES, 1):
            text = sentence["de"]
            print(f"\n  [{i:02d}] {text}")

            for lang in TARGET_LANGUAGES:
                ref = sentence[f"ref_{lang}"]
                deepl_result = await translate(client, text, lang, "deepl")
                opus_result = await translate(client, text, lang, "opus")

                print(f"\n       {lang.upper()} Referenz: {ref}")
                print(f"       {lang.upper()} DeepL:    {deepl_result}")
                print(f"       {lang.upper()} OPUS-MT:  {opus_result}")

        print(f"\n{'='*90}\n")

        assert len(SENTENCES) == 30
