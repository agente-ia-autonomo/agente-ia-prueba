# Email AI Agent

Un bot que revisa tu Gmail cada 5 minutos, analiza los emails con IA y decide si responder automáticamente o marcarlos para que los veas tú. Corre gratis en GitHub Actions.

---

## Cómo funciona

```
Gmail (no leídos)
       ↓
  Lee el email
       ↓
  Groq / LLaMA 3.3 70B lo analiza
       ↓
 ┌─────┴──────┐
 │            │
responde    escala
 │            │
Envía reply  ⭐ Marca con estrella
Marca leído  (para revisión manual)
 │            │
 └─────┬──────┘
       ↓
  Etiqueta: bot-processed
```

---

## Qué hace exactamente

- Lee solo emails no leídos que no haya procesado antes
- Si la consulta es simple (FAQ, info general) → responde solo
- Si es una queja, tema complejo o hay dudas → lo escala y te lo marca con estrella
- Si la IA falla por algún motivo → escala automáticamente, nunca responde a ciegas
- Soporta tildes, emojis y caracteres especiales en el asunto sin romperse

---

## Setup

### 1. Clona el repo

```bash
git clone https://github.com/tu-usuario/email-agent.git
cd email-agent
```

### 2. Consigue las credenciales

**Groq API Key**
Entra en [console.groq.com](https://console.groq.com) y crea una API key. Es gratis.

**Gmail OAuth**
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto y activa la **Gmail API**
3. Crea credenciales OAuth 2.0 (tipo: app de escritorio)
4. Haz el flujo de autenticación para obtener el `refresh_token`
5. El JSON final tiene que tener esta forma:

```json
{
  "token": "ya29.xxx",
  "refresh_token": "1//xxx",
  "client_id": "xxx.apps.googleusercontent.com",
  "client_secret": "xxx"
}
```

### 3. Añade los secrets en GitHub

Settings → Secrets and variables → Actions:

| Secret | Qué es |
|--------|--------|
| `GROQ_API_KEY` | Tu API key de Groq |
| `GMAIL_CREDENTIALS_JSON` | El JSON completo de OAuth |
| `COMPANY_NAME` | El nombre de tu empresa (sale en las respuestas) |

### 4. Listo

Sube el código a `main` y el workflow empieza solo. Cada 5 minutos revisa el buzón.

Si quieres lanzarlo a mano, puedes desde la pestaña **Actions → Run workflow**.

---

## Estructura

```
email-agent/
├── email_agent.py
├── requirements.txt
└── .github/
    └── workflows/
        └── email_agent.yml
```

---

## Personalización

El comportamiento del bot lo controla el `SYSTEM_PROMPT` dentro de `email_agent.py`. Desde ahí puedes cambiar cuándo responde y cuándo escala, el tono de las respuestas, o añadir respuestas concretas para preguntas frecuentes.

---

## Stack

- Python 3.11
- Gmail API
- Groq — LLaMA 3.3 70B
- GitHub Actions

---

## Nota importante

No subas nunca el JSON de credenciales al repo. Los secrets van en GitHub Secrets, no en el código.
