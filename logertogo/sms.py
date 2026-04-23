import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_termii_sms(phone_number, message):
    """
    Envoie un SMS via l'API Termii.
    :param phone_number: Numéro de téléphone au format international (sans le '+', ex: 22890000000)
    :param message: Le contenu du message
    :return: dict contenant la réponse de Termii, ou None si échec
    """
    # Nettoyage du numéro de téléphone (retirer le + si présent)
    clean_phone = phone_number.replace('+', '').replace(' ', '')
    
    url = "https://api.ng.termii.com/api/sms/send"
    
    payload = {
        "to": clean_phone,
        "from": getattr(settings, 'TERMII_SENDER_ID', 'LogerTogo'),
        "sms": message,
        "type": "plain",
        "channel": "generic",
        "api_key": getattr(settings, 'TERMII_API_KEY', '')
    }
    
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info(f"SMS envoyé avec succès via Termii à {clean_phone}: {result}")
        return result
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg = f"{e.response.status_code} - {e.response.text}"
        logger.error(f"Erreur lors de l'envoi du SMS Termii à {clean_phone}: {error_msg}")
        return None
