from __future__ import annotations

TRANSLATIONS = {
    "es": {
        "generating": "⏳ Generando tu sitio web...",
        "deploying": "🚀 Desplegando tu sitio web...",
        "live": "✅ Tu sitio web está en vivo:",
        "failed": "❌ No se pudo generar el sitio web. Inténtalo de nuevo.",
    },
    "fr": {
        "generating": "⏳ Génération de votre site web...",
        "deploying": "🚀 Déploiement de votre site web...",
        "live": "✅ Votre site web est en ligne :",
        "failed": "❌ Échec de la génération du site web. Veuillez réessayer.",
    },
    "en": {
        "generating": "⏳ Generating your website...",
        "deploying": "🚀 Deploying your website...",
        "live": "✅ Your website is live:",
        "failed": "❌ Failed to generate website. Please retry.",
    },
}


def t(key: str, language: str = "en") -> str:
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"][key])
