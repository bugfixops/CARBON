"""
LLM Provider Configuration — Switch between Gemini, OpenAI, Bedrock, Groq, etc.

Usage in .env:
    LLM_PROVIDER=gemini          # or openai, bedrock, groq, vertex, ollama
    LLM_API_KEY=your_key_here
    LLM_MODEL=gemini-2.5-pro     # optional, uses default if not set

Provider-specific credential fallbacks (only used when LLM_API_KEY / LLM_MODEL
are not set, so you can keep provider-named vars side by side in one .env):
    bedrock: BEDROCK_KEY, BEDROCK_BASE_URL, BEDROCK_MODEL
    openai:  OPENAI_API_KEY, OPENAI_BASE_URL

Amazon Bedrock exposes an OpenAI-compatible Chat Completions endpoint (either
bedrock-runtime or bedrock-mantle) — same request/response shape as OpenAI,
just a different base_url and bearer key. See:
https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html

Multi-account failover (carbon-retest-groq):
    Keys are read from LLM_API_KEY, LLM_API_KEY2, ... LLM_API_KEY19.
    mark_key_exhausted() records a key as dead -- permanently on auth failure
    (401), or for the rest of the calendar day on 429/5xx. State is persisted
    to REBL_KEY_STATE_FILE (JSON) so exhaustion survives across case processes
    in a batch: a dead account is not retried by every subsequent case.
    rotate_key() always skips exhausted keys and returns False when none are
    usable. Key VALUES are never printed; logs reference key indices only.

Vertex AI via ADC (carbon-retest-gemini):
    PROVIDER=vertex-adc authenticates with a short-lived OAuth2 Bearer token
    minted from GOOGLE_APPLICATION_CREDENTIALS (service-account JSON) -- no API
    key is configured or required (get_config() skips the API-key check for
    auth='adc'). Optional: GCP_PROJECT_ID, VERTEX_LOCATION (default us-central1).
"""

import datetime as _datetime
import json as _json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# ── Read from .env ───────────────────────────────────────────────────────────

PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()

# Per-provider fallback env vars, checked only when the generic LLM_* var is
# empty. This lets a single .env hold both LLM_API_KEY/OPENAI_BASE_URL (for
# LLM_PROVIDER=openai) and BEDROCK_KEY/BEDROCK_BASE_URL (for
# LLM_PROVIDER=bedrock) without either clobbering the other.
_PROVIDER_KEY_FALLBACKS = {
    'gemini': ['GEMINI_API_KEY'],
    'bedrock': ['BEDROCK_KEY', 'BEDROCK_API_KEY'],
    'openai': ['OPENAI_API_KEY'],
}
_PROVIDER_BASE_URL_FALLBACKS = {
    'bedrock': ['BEDROCK_BASE_URL'],
    'openai': ['OPENAI_BASE_URL'],
}
_PROVIDER_MODEL_FALLBACKS = {
    'bedrock': ['BEDROCK_MODEL'],
    'openai': ['OPENAI_MODEL'],
}


def _first_env(names, default=''):
    for name in names:
        val = os.getenv(name, '')
        if val:
            return val
    return default


API_KEY = os.getenv('LLM_API_KEY', '') or _first_env(_PROVIDER_KEY_FALLBACKS.get(PROVIDER, []))
MODEL = os.getenv('LLM_MODEL', '') or _first_env(_PROVIDER_MODEL_FALLBACKS.get(PROVIDER, []))
BASE_URL_OVERRIDE = os.getenv('LLM_BASE_URL', '') or _first_env(_PROVIDER_BASE_URL_FALLBACKS.get(PROVIDER, []))

# ── API Key Rotation ────────────────────────────────────────────────────────
# Load all available API keys for automatic rotation on quota exhaustion.
# Keys are read from LLM_API_KEY, LLM_API_KEY2, LLM_API_KEY3, etc.

API_KEYS = []
if API_KEY:
    API_KEYS.append(API_KEY)
for i in range(2, 20):
    k = os.getenv(f'LLM_API_KEY{i}', '')
    if k:
        API_KEYS.append(k)

_current_key_index = 0

# ── Key exhaustion tracking ─────────────────────────────────────────────────
# _EXHAUSTED_PERMANENT: indices dead for good (auth failure).
# _EXHAUSTED_DAY: index -> ISO date; dead until the calendar day rolls over.
# Persisted to REBL_KEY_STATE_FILE so sibling case-processes share the state.

_EXHAUSTED_PERMANENT = set()
_EXHAUSTED_DAY = {}
_KEY_STATE_FILE = os.getenv('REBL_KEY_STATE_FILE', '')


def _today():
    return _datetime.date.today().isoformat()


def _load_key_state():
    if not _KEY_STATE_FILE:
        return
    try:
        with open(_KEY_STATE_FILE, 'r', encoding='utf-8') as f:
            data = _json.load(f)
        for i in data.get('permanent', []):
            if isinstance(i, int) and 0 <= i < len(API_KEYS):
                _EXHAUSTED_PERMANENT.add(i)
        for k, day in (data.get('day') or {}).items():
            i = int(k)
            if 0 <= i < len(API_KEYS) and day >= _today():
                _EXHAUSTED_DAY[i] = day
    except Exception:
        pass


def _save_key_state():
    if not _KEY_STATE_FILE:
        return
    try:
        d = os.path.dirname(_KEY_STATE_FILE)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(_KEY_STATE_FILE, 'w', encoding='utf-8') as f:
            _json.dump({'permanent': sorted(_EXHAUSTED_PERMANENT),
                        'day': {str(k): v for k, v in _EXHAUSTED_DAY.items()}}, f)
    except Exception:
        pass


def _is_exhausted(i):
    if i in _EXHAUSTED_PERMANENT:
        return True
    day = _EXHAUSTED_DAY.get(i)
    if day and day >= _today():
        return True
    return False


_load_key_state()


def mark_key_exhausted(permanent=False, reason=''):
    """Mark the CURRENT key exhausted (permanent on auth failure, else for the
    day) and persist the state for sibling case processes."""
    i = _current_key_index
    if permanent:
        _EXHAUSTED_PERMANENT.add(i)
        _EXHAUSTED_DAY.pop(i, None)
        scope = 'permanently'
    else:
        _EXHAUSTED_DAY[i] = _today()
        scope = 'for today'
    _save_key_state()
    extra = f' ({reason})' if reason else ''
    print(f"[Key Rotation] Key {i + 1}/{len(API_KEYS)} marked exhausted {scope}{extra}.")


def keys_remaining():
    """Number of configured keys not currently exhausted."""
    return sum(1 for i in range(len(API_KEYS)) if not _is_exhausted(i))


# ── Provider configs ─────────────────────────────────────────────────────────

PROVIDERS = {
    'gemini': {
        'type': 'gemini',           # uses google-generativeai library
        'default_model': 'gemini-2.5-pro',
        'max_tokens': 128000,
        'supports_vision': True,
    },
    'openai': {
        'type': 'openai',           # uses openai library
        'base_url': 'https://api.openai.com/v1',
        'default_model': 'gpt-4o',
        'max_tokens': 128000,
        'supports_vision': True,
    },
    'bedrock': {
        'type': 'openai',           # Bedrock's Chat Completions endpoint is OpenAI-wire-compatible
        # Default is the bedrock-runtime OpenAI-compatible path; override via
        # BEDROCK_BASE_URL / LLM_BASE_URL for bedrock-mantle or a specific region.
        # e.g. https://bedrock-runtime.<region>.amazonaws.com/openai/v1
        'base_url': 'https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1',
        'default_model': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'max_tokens': 128000,
        'supports_vision': True,
    },
    'groq': {
        'type': 'openai',           # groq uses openai-compatible API
        'base_url': 'https://api.groq.com/openai/v1',
        'default_model': 'openai/gpt-oss-120b',
        'max_tokens': 32768,
        'tpm_limit': 8000,      # Groq free-tier tokens/minute cap per request:
                                # prompt_tokens + max_tokens above this -> HTTP 413
        'supports_vision': False,  # text-only: Groq free tier exposes no vision models (Sep 2026)
    },
    'gemini-openai': {
        'type': 'openai',           # gemini via openai-compatible endpoint
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
        'default_model': 'gemini-2.5-pro',
        'max_tokens': 128000,
        'supports_vision': True,
    },
    'vertex': {
        'type': 'vertex',           # Vertex AI REST API — bills Google Cloud credits
        'base_url': 'https://aiplatform.googleapis.com/v1/publishers/google/models',
        'default_model': 'gemini-2.5-pro',
        'max_tokens': 128000,
        'supports_vision': True,
    },
    'vertex-adc': {
        'type': 'vertex',           # Vertex AI REST API, ADC Bearer-token auth
        'auth': 'adc',              # no API key: token minted from GOOGLE_APPLICATION_CREDENTIALS
        'default_model': 'gemini-2.5-pro',
        'max_tokens': 128000,
        'supports_vision': True,    # vision back on (unlike Groq free tier)
    },
    'ollama': {
        'type': 'openai',           # ollama uses openai-compatible API
        'base_url': 'http://localhost:11434/v1',
        'default_model': 'llama3',
        'max_tokens': 8192,
        'supports_vision': False,
    },
}

# ── Resolve config ───────────────────────────────────────────────────────────

def get_config():
    """Get the active LLM configuration."""
    if PROVIDER not in PROVIDERS:
        raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}. Options: {list(PROVIDERS.keys())}")

    config = dict(PROVIDERS[PROVIDER])
    # If the default (first) key is already exhausted from a prior case,
    # start on the first usable one.
    global _current_key_index
    if API_KEYS and _is_exhausted(_current_key_index):
        for i in range(len(API_KEYS)):
            if not _is_exhausted(i):
                _current_key_index = i
                break
    config['api_key'] = API_KEYS[_current_key_index] if API_KEYS else API_KEY
    config['model'] = MODEL or config['default_model']
    config['provider'] = PROVIDER

    # Allow overriding base_url from .env for OpenAI-compatible endpoints
    # (Bedrock runtime/mantle, custom OpenAI gateways). BASE_URL_OVERRIDE
    # already resolved LLM_BASE_URL first, then the provider-specific
    # fallback (BEDROCK_BASE_URL for bedrock, OPENAI_BASE_URL for openai).
    if BASE_URL_OVERRIDE and config.get('type') == 'openai':
        config['base_url'] = BASE_URL_OVERRIDE

    # ADC providers (vertex-adc) authenticate with a Bearer token minted from
    # GOOGLE_APPLICATION_CREDENTIALS -- no API key exists to configure.
    if not config['api_key'] and config.get('auth') != 'adc':
        fallback_names = _PROVIDER_KEY_FALLBACKS.get(PROVIDER, [])
        expected = ['LLM_API_KEY'] + fallback_names
        raise ValueError(
            f"No API key found for provider '{PROVIDER}'. Set one of: {', '.join(expected)}"
        )

    return config


def rotate_key():
    """Rotate to the next non-exhausted API key.
    Returns True if rotated, False if no usable keys remain."""
    global _current_key_index
    if len(API_KEYS) <= 1:
        return False
    old_idx = _current_key_index
    for step in range(1, len(API_KEYS) + 1):
        nxt = (old_idx + step) % len(API_KEYS)
        if not _is_exhausted(nxt):
            _current_key_index = nxt
            print(f"[Key Rotation] Switching from key {old_idx + 1} to key "
                  f"{nxt + 1} [{nxt + 1}/{len(API_KEYS)}]")
            return True
    print(f"[Key Rotation] All {len(API_KEYS)} keys exhausted; none to rotate to.")
    return False


def get_current_key_info():
    """Return info about current key for logging (index only, never the value)."""
    if PROVIDERS[PROVIDER].get('auth') == 'adc':
        return "ADC service account (no API key)"
    return f"key {_current_key_index + 1}/{len(API_KEYS)}"


# Print config when imported (for debugging)
if __name__ == '__main__':
    c = get_config()
    print(f"Provider:  {c['provider']}")
    print(f"Type:      {c['type']}")
    print(f"Model:     {c['model']}")
    print(f"Vision:    {c['supports_vision']}")
    print(f"Keys:      {len(API_KEYS)} configured, {keys_remaining()} usable")
