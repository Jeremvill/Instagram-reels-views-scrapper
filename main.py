from flask import Flask, request, jsonify
import requests
import re
import os
from bs4 import BeautifulSoup
import html
import unicodedata
import logging
import time
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

app = Flask(__name__)

# En-têtes simples (ajustez si besoin)
COOKIE = "tt_csrf_token=elEn6owq-nIwTLNi0TqM60uZPxbH601E4nRw; tt_chain_token=QPMsm5ktRw3A+JxFrlLb/A==; delay_guest_mode_vid=8; passport_csrf_token=d4746bdc5ef7628595c4ef291085748f; passport_csrf_token_default=d4746bdc5ef7628595c4ef291085748f; fbm_1862952583919182=base_domain=.www.tiktok.com; s_v_web_id=verify_met2md3j_l3jqfjV5_aFzT_4FkB_B2FD_ZQkWB31VXKdw; multi_sids=7194288964244177947%3Afd7df6552c0c7f02d44939edd058f09a; cmpl_token=AgQQAPOFF-RO0rPp0RWle10i8s-w6BaIv4MOYN06Ig; passport_auth_status=c14be790b472cd71efa27de8f023c7a9%2C; passport_auth_status_ss=c14be790b472cd71efa27de8f023c7a9%2C; uid_tt=924aa0a4365fb21b4b67f399167c77349e29cd696af4f75deb6a72d7abd26c2c; uid_tt_ss=924aa0a4365fb21b4b67f399167c77349e29cd696af4f75deb6a72d7abd26c2c; sid_tt=fd7df6552c0c7f02d44939edd058f09a; sessionid=fd7df6552c0c7f02d44939edd058f09a; sessionid_ss=fd7df6552c0c7f02d44939edd058f09a; store-idc=alisg; store-country-code=vn; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=j36th5dt2kOx3qXFAvU8lXl1ffMzLppU5KXRkWgOoMsc9iG5nPOaSrl01ee2UxlB9haptJf1WDdvg4IbdyKEQPJXLNqLyANtr4oQUNdLl2vw9xMo6dCJN55kXz0OBEp1RSSQOfe2_Emnf-hczydgo889AGH_y-uQZ8y0dxouWZV2fX4pQe9SZ7zydxXJ_3FspFaHMoFdhoe_kCSosdtPzm-P6jLRbtm2b8x9rTqSK4Cj2PA5-uzFD6b9-uym7CkGxhA1FsUKHT1-nCBxtvugW1Aj-q4StHrdXygfirz5B1vDzab-i5OcoRgyVyex9ltWrQkxUcdYxyTsLt7r6arKYLFFxQA9ee300rvqChwjEKIYpVEVC6N-nwzxfPcAEmUCltLpofw7tbaHPMMOWmgpOie-9Auq6ybxZTVE7gyLOhAuOHCaR8HKBOnI43haiuMYx3B5mTKRQC7KmZxGEm6fs2OkzdUvqIEB3Vh-2Qe5JSVhkP2mKvJ8YNyObpHimCPn; last_login_method=google; tiktok_webapp_theme_source=auto; tiktok_webapp_theme=dark; sid_guard=fd7df6552c0c7f02d44939edd058f09a%7C1756244586%7C15551987%7CSun%2C+22-Feb-2026+21%3A42%3A53+GMT; sid_ucp_v1=1.0.0-KDJkMTFkOTdjZDE1NjZiMGJkNjcyOWI1ZTAzMDBhMzBhM2RmMjM1YzIKGQibiKbqovbP62MQ6tS4xQYYsws4CEASSAQQAxoDc2cxIiBmZDdkZjY1NTJjMGM3ZjAyZDQ0OTM5ZWRkMDU4ZjA5YQ; ssid_ucp_v1=1.0.0-KDJkMTFkOTdjZDE1NjZiMGJkNjcyOWI1ZTAzMDBhMzBhM2RmMjM1YzIKGQibiKbqovbP62MQ6tS4xQYYsws4CEASSAQQAxoDc2cxIiBmZDdkZjY1NTJjMGM3ZjAyZDQ0OTM5ZWRkMDU4ZjA5YQ; passport_fe_beating_status=true; perf_feed_cache={%22expireTimestamp%22:1758841200000%2C%22itemIds%22:[%227542724144736079122%22%2C%227529482274161708295%22%2C%227541768154716917009%22]}; ttwid=1%7CV3yOZGU5_oLycOpSzDGrZ82c8ZPlCDQOhWQ6XnJPQHc%7C1756251425%7C34e3c72e640c3eb675756e85b9fe5aab3670edfffd607294f7064aac2e817927; store-country-sign=MEIEDKz7SNlAQpiE8wQaUgQg5dBCcmHCggOJXpnOdlObhQMH_WifmJFcnvYc_PKNoQcEEO7OjkLbEFoWd22sA7pKxfM; odin_tt=6e2aa21365b32d549f1feaf9d49b3143edc2bbc61cf7752b41b9143864c535e12e8c51dff3f4b3902a267994a12b0d27719668be50e0a359aa7a19676c19d9349bcda05b5b28cb9e6eb6f7ca51355ad8; msToken=ZBoiEW-04GncRsg_XkWIi2d-xNLwp9WJa4r1NeEzeMcuwB97vnoKJXGUt392bgsoKDsiSV6MujqApvJr-58cWmCoSQQsTBhy8DGLhbKeZTafOEkLvV16rFra6XbyLNSX1JzxhgF9sWHETlo2PTEhVqEa; msToken=TVuC0BYZjN1pPqa_a8GRI5LlPjp6cwajA3C7_WhO9V-l3dTAmR8W45nDpnyXFaqse2tPjxgWOb90E6UWGUOaxmqlSrOX9lFUxpAKe3D34KkBw2FMvCj7MFpEAz02lnFidnBvuURu5Pd3Tx095rjpVQqI"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

# Les anciens HEADERS utilisaient un cookie TikTok, non pertinent pour YouTube.
# On définit plutôt des en-têtes YouTube de base.
ACCEPT_LANGUAGE = os.environ.get("YT_ACCEPT_LANGUAGE", "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7")
HEADERS_BASE = {"User-Agent": USER_AGENT, "Accept-Language": ACCEPT_LANGUAGE}


# Logging
LOG_LEVEL = logging.DEBUG if os.environ.get("YT_DEBUG") in ("1", "true", "True") else logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("yt-api")


# --------- Gestion de session et cookies de consentement YouTube ---------
def _lang_country_from_accept_language(al: str):
    try:
        primary = al.split(',')[0]
        parts = primary.split(';')[0].split('-')
        lang = parts[0]
        country = parts[1].upper() if len(parts) > 1 else (lang.upper() if len(lang) == 2 else "US")
        return lang, country
    except Exception:
        return "en", "US"


def _augment_url(u: str, *, accept_language: str) -> str:
    lang, country = _lang_country_from_accept_language(accept_language)
    p = urlparse(u)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q.setdefault("hl", lang)
    q.setdefault("gl", country)
    new_q = urlencode(q)
    p2 = p._replace(query=new_q)
    return urlunparse(p2)


def _build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS_BASE)
    # Définir des cookies de consentement pour éviter la page cookies YouTube
    consent = os.environ.get("YT_CONSENT", "YES+1")  # valeur courante pour contourner l'interstitiel
    socs = os.environ.get("YT_SOCS", "CAI")
    pref_lang, _pref_country = _lang_country_from_accept_language(HEADERS_BASE["Accept-Language"])  # ex: fr
    pref = os.environ.get("YT_PREF", f"hl={pref_lang}")
    for domain in [".youtube.com", ".google.com", ".consent.youtube.com"]:
        try:
            s.cookies.set("CONSENT", consent, domain=domain)
            s.cookies.set("SOCS", socs, domain=domain)
            s.cookies.set("PREF", pref, domain=domain)
        except Exception:
            s.cookies.set("CONSENT", consent)
            s.cookies.set("SOCS", socs)
            s.cookies.set("PREF", pref)
    extra_cookie = os.environ.get("YT_EXTRA_COOKIE")
    if extra_cookie:
        s.headers["Cookie"] = extra_cookie
    return s


SESSION = _build_session()


def _dump_html(html_text: str, url: str, status: int, *, force_dump: bool = False, target_dir: str | None = None) -> str | None:
    """Dump le HTML dans un fichier et retourne le chemin si effectué.
    - Par défaut, ne dump que si YT_DUMP_HTML=1. Si force_dump=True, dump quoi qu'il arrive.
    - target_dir par défaut est /tmp.
    """
    dump_enabled = force_dump or os.environ.get("YT_DUMP_HTML") in ("1", "true", "True")
    dumped_path: str | None = None
    try:
        snippet = html_text[:1200].replace("\n", " ")
        logger.debug(f"HTML snippet (first 1200 chars): {snippet}")
        if dump_enabled:
            ts = int(time.time())
            safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:60]
            base_dir = target_dir or "/tmp"
            os.makedirs(base_dir, exist_ok=True)
            dumped_path = os.path.join(base_dir, f"yt_page_{ts}_{status}_{safe}.html")
            with open(dumped_path, "w", encoding="utf-8") as f:
                f.write(html_text)
            logger.info(f"HTML dumped to: {dumped_path}")
    except Exception as e:
        logger.debug(f"Failed to dump HTML: {e}")
    return dumped_path


def _is_page_loaded(html_text: str) -> bool:
    """Heuristique simple pour vérifier que la page vidéo est chargée."""
    if not html_text:
        return False
    markers = [
        "<html",  # Structure de base
        "ytInitialPlayerResponse",  # Données video présentes côté client
        "view-count-factoid-renderer",  # Nouveau composant d'affichage
    ]
    score = sum(1 for m in markers if m in html_text)
    logger.debug(f"Page load heuristic score={score}/3")
    return score >= 1


def _normalize_int(text: str) -> int | None:
    """Normalise un nombre avec séparateurs locaux (espaces insécables, points, virgules) en int.
    Ex: "2 349 363" -> 2349363
    """
    if not text:
        return None
    # Unescape HTML, normalise unicode (pour retirer U+202F, U+00A0, etc.)
    t = html.unescape(text)
    t = unicodedata.normalize('NFKC', t)
    # Garde uniquement les chiffres
    digits = ''.join(ch for ch in t if ch.isdigit())
    return int(digits) if digits else None


def _extract_views_textual(html_text: str) -> int | None:
    """Essaye d'extraire un comptage de vues depuis plusieurs motifs textuels/JSON localisés.
    Couvre FR/EN et casse Shorts: "vues" ou "views" avec espaces insécables (U+202F/U+00A0) et séparateurs.
    """
    if not html_text:
        return None
    patterns = [
        # ytInitialData: viewCountText.simpleText: "2 349 946 vues"
        r'"viewCountText"\s*:\s*\{[^}]*"simpleText"\s*:\s*"([0-9\s\u202F\u00A0\.,]+)\s*(?:vues|views)"',
        # Shorts: shortViewCountText.simpleText
        r'"shortViewCountText"\s*:\s*\{[^}]*"simpleText"\s*:\s*"([0-9\s\u202F\u00A0\.,]+)\s*(?:vues|views)"',
        # aria-label="2 349 946 vues"
        r'aria-label\s*=\s*"([0-9\s\u202F\u00A0\.,]+)\s*(?:vues|views)"',
        # Fallback brut: nombre + mot clé (FR/EN)
        r'([0-9][0-9\s\u202F\u00A0\.,]+)\s*(?:vues|views)',
    ]
    for pat in patterns:
        m = re.search(pat, html_text, flags=re.I)
        if m:
            raw = m.group(1)
            logger.debug(f"Textual views match '{raw}' via pattern: {pat[:60]}...")
            n = _normalize_int(raw)
            if isinstance(n, int):
                return n
    return None


def get_youtube_views(url: str, max_retry: int = 3, delay: float = 1.5, page_html: str | None = None):
    """Retourne le nombre de vues YouTube via le HTML initial.
    Essaie plusieurs motifs connus (ytInitialPlayerResponse.videoDetails.viewCount).
    """
    # Si on fournit déjà le HTML, on tente un seul parsing sans refaire de requête
    if page_html is not None:
        html_text = page_html
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            fact = soup.find('view-count-factoid-renderer')
            if fact:
                val_span = fact.select_one('.ytwFactoidRendererValue') or fact.find('span')
                if val_span:
                    raw_text = val_span.get_text(strip=True)
                    logger.debug(f"[prefetched] Found factoid value='{raw_text}'")
                    n = _normalize_int(raw_text)
                    if isinstance(n, int):
                        logger.info(f"[prefetched] Views from factoid renderer: {n}")
                        return n
            else:
                logger.debug("[prefetched] <view-count-factoid-renderer> not found; trying JSON patterns")
        except Exception as e:
            logger.debug(f"[prefetched] BeautifulSoup error: {e}")
        m = re.search(r'"videoDetails"\s*:\s*\{[^}]*"viewCount"\s*:\s*"(\d+)"', html_text)
        if m:
            val = int(m.group(1))
            logger.info(f"[prefetched] Views from videoDetails.viewCount: {val}")
            return val
        m = re.search(r'"viewCount"\s*:\s*\{[^}]*"simpleText"\s*:\s*"([0-9,\.]+)\s+views"', html_text, re.I)
        if m:
            val = int(m.group(1).replace(',', '').replace('.', ''))
            logger.info(f"[prefetched] Views from simpleText: {val}")
            return val
        # Essai supplémentaire FR/EN (vues/views) y compris Shorts
        val = _extract_views_textual(html_text)
        if isinstance(val, int):
            logger.info(f"[prefetched] Views from textual patterns: {val}")
            return val
        return None

    for attempt in range(1, max_retry + 1):
        try:
            fetch_url = _augment_url(url, accept_language=HEADERS_BASE["Accept-Language"]) 
            logger.debug(f"Fetching URL (attempt {attempt}/{max_retry}): {fetch_url}")
            r = SESSION.get(fetch_url, timeout=10, allow_redirects=True)
            logger.debug(f"Response status={r.status_code}, content-type={r.headers.get('Content-Type')}, len={len(r.text)}")
            _dump_html(r.text, url, r.status_code)
            if r.status_code != 200:
                continue
            html_text = r.text
            if not _is_page_loaded(html_text):
                logger.warning("Heuristique: la page ne semble pas complètement chargée (ou est protégée).")
                # On continue parsing quand même; la factoid peut être présente côté HTML statique.
            # 0) Nouveau rendu front: <view-count-factoid-renderer> ... "2 349 363" ...
            try:
                soup = BeautifulSoup(html_text, 'html.parser')
                fact = soup.find('view-count-factoid-renderer')
                if fact:
                    # Valeur dans .ytwFactoidRendererValue ou premier span texte
                    val_span = fact.select_one('.ytwFactoidRendererValue') or fact.find('span')
                    if val_span:
                        raw_text = val_span.get_text(strip=True)
                        logger.debug(f"Found factoid renderer value text='{raw_text}'")
                        n = _normalize_int(raw_text)
                        if isinstance(n, int):
                            logger.info(f"Views parsed from factoid renderer: {n}")
                            return n
                else:
                    logger.debug("<view-count-factoid-renderer> not found; trying JSON patterns")
            except Exception as e:
                logger.debug(f"BeautifulSoup parsing error: {e}")
            # 1) videoDetails.viewCount:"<digits>"
            m = re.search(r'"videoDetails"\s*:\s*\{[^}]*"viewCount"\s*:\s*"(\d+)"', html_text)
            if m:
                val = int(m.group(1))
                logger.info(f"Views parsed from videoDetails.viewCount: {val}")
                return val
            # 2) viewCount":{"simpleText":"12,345 views"}
            m = re.search(r'"viewCount"\s*:\s*\{[^}]*"simpleText"\s*:\s*"([0-9,\.]+)\s+views"', html_text, re.I)
            if m:
                val = int(m.group(1).replace(',', '').replace('.', ''))
                logger.info(f"Views parsed from simpleText: {val}")
                return val
            # 3) Motifs textuels localisés FR/EN (y compris Shorts)
            val2 = _extract_views_textual(html_text)
            if isinstance(val2, int):
                logger.info(f"Views parsed from textual patterns: {val2}")
                return val2
        except requests.RequestException as e:
            logger.warning(f"HTTP error: {e}")
        try:
            logger.debug(f"Retrying after {delay}s...")
            time.sleep(delay)
        except Exception as e:
            logger.debug(f"Sleep error ignored: {e}")
    return None


@app.route("/get_views", methods=["POST"])
def get_views_api():
    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])
    dump_dir = data.get("dumpDir") or os.environ.get("YT_DUMP_DIR") or "/tmp"
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400
    logger.info(f"Incoming request from {request.remote_addr} with {len(urls)} url(s)")
    out = {}
    for u in urls:
        logger.debug(f"Processing URL: {u}")
        dumped_file = None
        status = None
        html_text = None
        try:
            fetch_url = _augment_url(u, accept_language=HEADERS_BASE["Accept-Language"]) 
            r = SESSION.get(fetch_url, timeout=15, allow_redirects=True)
            status = r.status_code
            html_text = r.text
            dumped_file = _dump_html(html_text, u, status or 0, force_dump=True, target_dir=dump_dir)
        except Exception as e:
            logger.warning(f"Failed to fetch/dump HTML for {u}: {e}")
        # Parse en utilisant le HTML pré-téléchargé si dispo, sinon fallback interne
        views_val = get_youtube_views(u, max_retry=1, delay=0.5, page_html=html_text)
        out[u] = {
            "views": views_val,
            "dump_file": dumped_file,
            "status": status,
        }
        logger.debug(f"Result for {u}: {out[u]}")
    logger.info(f"Response payload: {out}")
    return jsonify(out)


if __name__ == "__main__":
    # Exécute sur 0.0.0.0:5001 par défaut
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
