#!/usr/bin/env python3
"""
Sports Events JSON Generator v6
- embedhd.org API: event details ONLY (no stream links from API)
- Cricket API: event details ONLY (no channel links)
- ALL streaming links sourced exclusively from M3U playlists
- Proper league name formatting
- Smart sport type detection
- Outputs to app-files/events.json
"""

import requests
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta

# ─── Configuration ───────────────────────────────────────────────────────────

EVENT_API = "https://embedhd.org/api-event.php"
CRICKET_API = "https://raw.githubusercontent.com/farhad-iptv/crichd-event-scraper/refs/heads/main/matches.json"

PLAYLIST_URLS = [
    "https://raw.githubusercontent.com/srhady/axsports/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/srhady/SonyLiv/refs/heads/main/sonyliv_playlist.m3u",
    "https://raw.githubusercontent.com/sm-monirulislam/FanCode-Auto-Update-Playlist/refs/heads/main/fancode_bd.m3u",
    "https://raw.githubusercontent.com/srhady/bingstream/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/sports/refs/heads/main/powerv2/powerv2.m3u8",
    "https://raw.githubusercontent.com/BuddyChewChew/sports/refs/heads/main/liveeventsfilter.m3u8",
    "https://raw.githubusercontent.com/BINOD-XD/Toffee-Auto-Update-Playlist/refs/heads/main/toffee_OTT_Navigator.m3u",
    "https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/events.m3u8",
    "https://raw.githubusercontent.com/hoangcon1808/SM-Live-TV/refs/heads/main/live_playlist.m3u",
    "https://raw.githubusercontent.com/srhady/willow-event/refs/heads/main/live_sports.m3u",
]

DEFAULT_STREAM_URL = "https://github.com/farhad-iptv/app-link/raw/refs/heads/main/FREEFLIX-extended.mp4"
DEFAULT_STREAM_NAME = "FREEFLIX"
CDN_BASE = "https://cdn.img4every1.org"
OUTPUT_PATH = "app-files/events.json"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
)

BST = timezone(timedelta(hours=6))

# ─── League Name Mapping ────────────────────────────────────────────────────

LEAGUE_NAME_MAP = {
    # Football
    "fifa world cup": "FIFA World Cup",
    "world cup": "FIFA World Cup",
    "fifa world cup 2026": "FIFA World Cup 2026",
    "world cup 2026": "FIFA World Cup 2026",
    "fifa world cup qualifying": "FIFA World Cup Qualifying",
    "world cup qualifiers": "FIFA World Cup Qualifying",
    "premier league": "Premier League",
    "english premier league": "English Premier League",
    "epl": "English Premier League",
    "la liga": "La Liga",
    "laliga": "La Liga",
    "serie a": "Serie A",
    "bundesliga": "Bundesliga",
    "ligue 1": "Ligue 1",
    "champions league": "UEFA Champions League",
    "uefa champions league": "UEFA Champions League",
    "ucl": "UEFA Champions League",
    "europa league": "UEFA Europa League",
    "uefa europa league": "UEFA Europa League",
    "uel": "UEFA Europa League",
    "conference league": "UEFA Conference League",
    "uefa conference league": "UEFA Conference League",
    "copa america": "Copa América",
    "copa américa": "Copa América",
    "euro": "UEFA Euro",
    "uefa euro": "UEFA Euro",
    "european championship": "UEFA Euro",
    "copa libertadores": "Copa Libertadores",
    "libertadores": "Copa Libertadores",
    "copa sudamericana": "Copa Sudamericana",
    "mls": "MLS",
    "major league soccer": "MLS",
    "eredivisie": "Eredivisie",
    "primeira liga": "Primeira Liga",
    "liga portugal": "Liga Portugal",
    "süper lig": "Süper Lig",
    "super lig": "Süper Lig",
    "scottish premiership": "Scottish Premiership",
    "championship": "EFL Championship",
    "efl championship": "EFL Championship",
    "fa cup": "FA Cup",
    "carabao cup": "Carabao Cup",
    "efl cup": "Carabao Cup",
    "league cup": "Carabao Cup",
    "copa del rey": "Copa del Rey",
    "dfb pokal": "DFB-Pokal",
    "dfb-pokal": "DFB-Pokal",
    "coupe de france": "Coupe de France",
    "coppa italia": "Coppa Italia",
    "club friendly": "Club Friendly",
    "international friendly": "International Friendly",
    "friendly": "Friendly",
    "concacaf champions cup": "CONCACAF Champions Cup",
    "concacaf gold cup": "CONCACAF Gold Cup",
    "gold cup": "CONCACAF Gold Cup",
    "concacaf nations league": "CONCACAF Nations League",
    "concacaf": "CONCACAF",
    "conmebol": "CONMEBOL",
    "afc champions league": "AFC Champions League",
    "caf champions league": "CAF Champions League",
    "a-league": "A-League",
    "a league": "A-League",
    "j-league": "J-League",
    "j league": "J-League",
    "j1 league": "J1 League",
    "k-league": "K-League",
    "k league": "K-League",
    "k league 1": "K League 1",
    "indian super league": "Indian Super League",
    "isl": "Indian Super League",
    "saudi pro league": "Saudi Pro League",
    "spl": "Saudi Pro League",
    "liga mx": "Liga MX",
    "brasileirao": "Brasileirão",
    "brasileirão": "Brasileirão",
    "community shield": "FA Community Shield",
    "nations league": "UEFA Nations League",
    "uefa nations league": "UEFA Nations League",
    "africa cup of nations": "Africa Cup of Nations",
    "afcon": "Africa Cup of Nations",
    "asian cup": "AFC Asian Cup",
    "afc asian cup": "AFC Asian Cup",
    "club world cup": "FIFA Club World Cup",
    "fifa club world cup": "FIFA Club World Cup",
    "chinese super league": "Chinese Super League",
    "superliga argentina": "Superliga Argentina",
    "belgian pro league": "Belgian Pro League",
    "swiss super league": "Swiss Super League",
    "danish superliga": "Danish Superliga",
    "allsvenskan": "Swedish Allsvenskan",
    "eliteserien": "Norwegian Eliteserien",
    "ekstraklasa": "Polish Ekstraklasa",
    "supercopa de españa": "Supercopa de España",
    "supercoppa italiana": "Supercoppa Italiana",
    # Cricket
    "ipl": "Indian Premier League",
    "indian premier league": "Indian Premier League",
    "bpl": "Bangladesh Premier League",
    "bangladesh premier league": "Bangladesh Premier League",
    "psl": "Pakistan Super League",
    "pakistan super league": "Pakistan Super League",
    "big bash league": "Big Bash League",
    "bbl": "Big Bash League",
    "big bash": "Big Bash League",
    "cpl": "Caribbean Premier League",
    "caribbean premier league": "Caribbean Premier League",
    "the hundred": "The Hundred",
    "hundred": "The Hundred",
    "sa20": "SA20",
    "ilt20": "ILT20",
    "mlc": "Major League Cricket",
    "mlc t20": "Major League Cricket",
    "major league cricket": "Major League Cricket",
    "wpl": "Women's Premier League",
    "t20 blast": "Vitality T20 Blast",
    "vitality blast": "Vitality T20 Blast",
    "vitality t20 blast": "Vitality T20 Blast",
    "county championship": "County Championship",
    "royal london cup": "Royal London One-Day Cup",
    "asia cup": "Asia Cup",
    "champions trophy": "ICC Champions Trophy",
    "icc champions trophy": "ICC Champions Trophy",
    "icc world cup": "ICC Cricket World Cup",
    "cricket world cup": "ICC Cricket World Cup",
    "t20 world cup": "ICC T20 World Cup",
    "t20 wc": "ICC T20 World Cup",
    "icc t20 world cup": "ICC T20 World Cup",
    "wt20 wc": "ICC Women's T20 World Cup",
    "women's t20 world cup": "ICC Women's T20 World Cup",
    "ashes": "The Ashes",
    "the ashes": "The Ashes",
    "ranji trophy": "Ranji Trophy",
    "ranji": "Ranji Trophy",
    "eng vs nz": "England vs New Zealand",
    "ind vs aus": "India vs Australia",
    "ind vs eng": "India vs England",
    "wi vs sl": "West Indies vs Sri Lanka",
    "ban vs afg": "Bangladesh vs Afghanistan",
    "sa vs wi": "South Africa vs West Indies",
    "aus vs eng": "Australia vs England",
    "nz vs eng": "New Zealand vs England",
    # Basketball
    "nba": "NBA",
    "nba playoffs": "NBA Playoffs",
    "nba finals": "NBA Finals",
    "wnba": "WNBA",
    "euroleague": "EuroLeague",
    "fiba": "FIBA",
    "ncaa basketball": "NCAA Basketball",
    "march madness": "NCAA March Madness",
    # Baseball
    "mlb": "MLB",
    "major league baseball": "MLB",
    "world series": "World Series",
    "npb": "NPB",
    "kbo": "KBO League",
    "kbo league": "KBO League",
    # Ice Hockey
    "nhl": "NHL",
    "nhl playoffs": "NHL Playoffs",
    "stanley cup": "Stanley Cup",
    "stanley cup playoffs": "Stanley Cup Playoffs",
    "khl": "KHL",
    "iihf": "IIHF",
    "iihf world championship": "IIHF World Championship",
    # American Football
    "nfl": "NFL",
    "nfl playoffs": "NFL Playoffs",
    "super bowl": "Super Bowl",
    "ncaa football": "NCAA Football",
    "college football": "NCAA Football",
    "xfl": "XFL",
    # Tennis
    "atp": "ATP Tour",
    "atp tour": "ATP Tour",
    "atp 250": "ATP 250",
    "atp 500": "ATP 500",
    "atp 1000": "ATP Masters 1000",
    "atp masters 1000": "ATP Masters 1000",
    "wta": "WTA Tour",
    "wta tour": "WTA Tour",
    "wimbledon": "Wimbledon",
    "roland garros": "Roland-Garros",
    "french open": "Roland-Garros",
    "us open": "US Open",
    "australian open": "Australian Open",
    "davis cup": "Davis Cup",
    "laver cup": "Laver Cup",
    # Golf
    "pga": "PGA Tour",
    "pga tour": "PGA Tour",
    "lpga": "LPGA Tour",
    "masters": "The Masters",
    "the masters": "The Masters",
    "the open championship": "The Open Championship",
    "pga championship": "PGA Championship",
    "ryder cup": "Ryder Cup",
    "liv golf": "LIV Golf",
    # Motorsport
    "formula 1": "Formula 1",
    "formula1": "Formula 1",
    "formula one": "Formula 1",
    "f1": "Formula 1",
    "motogp": "MotoGP",
    "moto gp": "MotoGP",
    "moto2": "Moto2",
    "moto3": "Moto3",
    "nascar": "NASCAR",
    "nascar cup series": "NASCAR Cup Series",
    "indycar": "IndyCar Series",
    "indycar series": "IndyCar Series",
    "formula e": "Formula E",
    "formula-e": "Formula E",
    "wrc": "WRC",
    "le mans": "24 Hours of Le Mans",
    # Rugby
    "six nations": "Six Nations",
    "rugby world cup": "Rugby World Cup",
    "super rugby": "Super Rugby",
    "super rugby pacific": "Super Rugby Pacific",
    "premiership rugby": "Premiership Rugby",
    "top 14": "Top 14",
    "urc": "United Rugby Championship",
    "nrl": "NRL",
    "rugby league": "Rugby League",
    # Combat
    "ufc": "UFC",
    "bellator": "Bellator MMA",
    "bellator mma": "Bellator MMA",
    "pfl": "PFL",
    "one championship": "ONE Championship",
    "boxing": "Boxing",
    "wwe": "WWE",
    "wwe raw": "WWE Raw",
    "wwe smackdown": "WWE SmackDown",
    "aew": "AEW",
    # Other
    "afl": "AFL",
    "kabaddi": "Pro Kabaddi League",
    "pro kabaddi": "Pro Kabaddi League",
    "pro kabaddi league": "Pro Kabaddi League",
    "pkl": "Pro Kabaddi League",
    "tour de france": "Tour de France",
    "giro d'italia": "Giro d'Italia",
    "vuelta a españa": "Vuelta a España",
    "darts": "PDC Darts",
    "pdc": "PDC Darts",
    "pdc darts": "PDC Darts",
    "snooker": "World Snooker",
    "world snooker": "World Snooker",
    "table tennis": "Table Tennis",
    "badminton": "Badminton",
    "volleyball": "Volleyball",
    "handball": "Handball",
    "esports": "Esports",
}

ACRONYMS_SET = {
    'mlb', 'nfl', 'nba', 'nhl', 'mls', 'ufc', 'wwe', 'aew', 'afl',
    'ipl', 'bpl', 'psl', 'cpl', 'bbl', 'mlc', 'wpl',
    'fifa', 'uefa', 'icc', 'afc', 'caf', 'concacaf', 'conmebol',
    'f1', 'wrc', 'wec', 'dtm',
    'pga', 'lpga', 'wta', 'atp', 'itf',
    'nrl', 'urc', 'pdc', 'bwf', 'fivb', 'ehf', 'ittf', 'fiba',
    'nascar', 'indycar', 'usa', 'uk', 'uae', 'khl',
    'sa20', 'ilt20', 't20', 'odi', 'dfb', 'dfl', 'efl',
}

LOWERCASE_WORDS = {
    'de', 'del', 'di', 'da', 'das', 'der', 'des', 'du',
    'la', 'le', 'les', 'los', 'las', 'el',
    'a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'at',
    'to', 'for', 'with', 'by', 'vs', 'v',
}


def smart_title_case(text):
    if not text:
        return ""
    words = text.strip().split()
    result = []
    for i, word in enumerate(words):
        wl = word.lower()
        wc = re.sub(r'[^a-z0-9]', '', wl)
        if wc in ACRONYMS_SET:
            result.append(word.upper())
        elif i > 0 and wl in LOWERCASE_WORDS:
            result.append(wl)
        elif '-' in word:
            parts = []
            for p in word.split('-'):
                pc = re.sub(r'[^a-z0-9]', '', p.lower())
                parts.append(p.upper() if pc in ACRONYMS_SET else p.capitalize())
            result.append('-'.join(parts))
        else:
            result.append(word.capitalize())
    return ' '.join(result)


def format_league_name(raw_league):
    if not raw_league:
        return ""
    raw = raw_league.strip()
    raw_lower = raw.lower()

    # Exact match
    if raw_lower in LEAGUE_NAME_MAP:
        return LEAGUE_NAME_MAP[raw_lower]

    # Strip common prefixes
    cleaned = raw_lower
    for prefix in ['the ', 'league: ', 'tournament: ']:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    cleaned = cleaned.strip()
    if cleaned in LEAGUE_NAME_MAP:
        return LEAGUE_NAME_MAP[cleaned]

    # Longest substring match
    best_match = None
    best_len = 0
    for key, display in LEAGUE_NAME_MAP.items():
        if key in raw_lower and len(key) > best_len:
            best_match = display
            best_len = len(key)
    if best_match and best_len >= 3:
        return best_match

    # Smart title case fallback
    return smart_title_case(raw)


# ─── Sport type detection ────────────────────────────────────────────────────

SPORT_KEYWORDS = [
    ("formula 1", "Formula 1"), ("formula1", "Formula 1"),
    ("formula one", "Formula 1"), ("f1 grand prix", "Formula 1"),
    ("f1 gp", "Formula 1"), ("f1 race", "Formula 1"),
    ("f1 qualifying", "Formula 1"), ("grand prix", "Formula 1"),
    ("motogp", "MotoGP"), ("moto gp", "MotoGP"),
    ("moto2", "MotoGP"), ("moto3", "MotoGP"),
    ("nascar", "NASCAR"), ("indycar", "IndyCar"),
    ("formula e", "Formula E"), ("wrc", "Rally"),
    ("le mans", "Endurance Racing"), ("motorsport", "Motorsport"),
    ("cricket", "Cricket"), ("ipl", "Cricket"),
    ("t20i", "Cricket"), ("t20 blast", "Cricket"),
    ("vitality blast", "Cricket"), ("test match", "Cricket"),
    ("big bash", "Cricket"), ("bbl", "Cricket"),
    ("cpl", "Cricket"), ("the hundred", "Cricket"),
    ("sa20", "Cricket"), ("ilt20", "Cricket"),
    ("bpl", "Cricket"), ("mlc t20", "Cricket"),
    ("wpl", "Cricket"), ("county championship", "Cricket"),
    ("asia cup", "Cricket"), ("champions trophy", "Cricket"),
    ("ashes", "Cricket"),
    ("nfl", "American Football"), ("american football", "American Football"),
    ("super bowl", "American Football"), ("ncaa football", "American Football"),
    ("xfl", "American Football"),
    ("afl", "AFL"), ("australian football", "AFL"),
    ("ufc", "MMA"), ("mma", "MMA"), ("bellator", "MMA"),
    ("one championship", "MMA"),
    ("boxing", "Boxing"), ("wba", "Boxing"), ("wbc", "Boxing"),
    ("ibf", "Boxing"), ("wbo", "Boxing"),
    ("wrestling", "Wrestling"), ("wwe", "Wrestling"),
    ("nba", "Basketball"), ("basketball", "Basketball"),
    ("euroleague", "Basketball"), ("fiba", "Basketball"), ("wnba", "Basketball"),
    ("nhl", "Ice Hockey"), ("ice hockey", "Ice Hockey"),
    ("hockey", "Ice Hockey"), ("khl", "Ice Hockey"),
    ("mlb", "Baseball"), ("baseball", "Baseball"),
    ("world series", "Baseball"),
    ("tennis", "Tennis"), ("atp", "Tennis"), ("wta", "Tennis"),
    ("wimbledon", "Tennis"), ("roland garros", "Tennis"),
    ("davis cup", "Tennis"),
    ("golf", "Golf"), ("pga", "Golf"), ("lpga", "Golf"),
    ("ryder cup", "Golf"),
    ("rugby", "Rugby"), ("six nations", "Rugby"),
    ("super rugby", "Rugby"), ("nrl", "Rugby League"),
    ("rugby league", "Rugby League"),
    ("table tennis", "Table Tennis"), ("badminton", "Badminton"),
    ("volleyball", "Volleyball"), ("handball", "Handball"),
    ("kabaddi", "Kabaddi"), ("pro kabaddi", "Kabaddi"),
    ("cycling", "Cycling"), ("tour de france", "Cycling"),
    ("darts", "Darts"), ("snooker", "Snooker"),
    ("esports", "Esports"),
    ("premier league", "Football"), ("la liga", "Football"),
    ("serie a", "Football"), ("bundesliga", "Football"),
    ("ligue 1", "Football"), ("champions league", "Football"),
    ("europa league", "Football"), ("conference league", "Football"),
    ("copa america", "Football"), ("world cup", "Football"),
    ("fifa", "Football"), ("copa libertadores", "Football"),
    ("mls", "Football"), ("eredivisie", "Football"),
    ("concacaf", "Football"), ("fa cup", "Football"),
    ("copa del rey", "Football"),
    ("football", "Football"), ("soccer", "Football"),
]

F1_INDICATORS = [
    "red bull racing", "mercedes amg", "ferrari", "mclaren", "aston martin",
    "alpine", "williams", "haas", "alphatauri", "sauber",
    "verstappen", "hamilton", "leclerc", "norris", "sainz", "perez",
    "alonso", "piastri", "russell", "gasly", "ocon",
    "monaco gp", "silverstone", "monza", "suzuka",
    "bahrain gp", "jeddah", "miami gp", "canadian gp",
    "spanish gp", "austrian gp", "british gp", "hungarian gp",
    "belgian gp", "dutch gp", "italian gp", "singapore gp",
    "japanese gp", "qatar gp", "las vegas gp", "abu dhabi gp",
]

CRICKET_TEAM_INDICATORS = [
    "chennai super kings", "mumbai indians", "royal challengers",
    "kolkata knight riders", "delhi capitals", "punjab kings",
    "rajasthan royals", "sunrisers hyderabad", "gujarat titans",
    "lucknow super giants", "karachi kings", "lahore qalandars",
    "islamabad united", "peshawar zalmi", "quetta gladiators",
    "multan sultans", "melbourne stars", "sydney sixers",
    "perth scorchers", "adelaide strikers",
    "trinbago knight riders", "jamaica tallawahs", "barbados royals",
]


def detect_sport_type_smart(text_parts):
    if not text_parts:
        return "Football"
    combined = " ".join(str(p) for p in text_parts if p).lower()
    if not combined.strip():
        return "Football"
    if sum(1 for ind in F1_INDICATORS if ind in combined) >= 1:
        if not any(kw in combined for kw in [
            "premier league", "la liga", "serie a", "bundesliga",
            "champions league", "europa league"
        ]):
            return "Formula 1"
    if any(ind in combined for ind in CRICKET_TEAM_INDICATORS):
        return "Cricket"
    for keyword, sport_type in SPORT_KEYWORDS:
        if keyword in combined:
            return sport_type
    return "Football"


# ─── Team name aliases ──────────────────────────────────────────────────────

TEAM_NAME_ALIASES = {
    "usa": ["united states", "us", "u.s.a", "united states of america"],
    "south-korea": ["korea republic", "korea", "south korea", "republic of korea"],
    "turkiye": ["turkey", "türkiye"],
    "curacao": ["curaçao", "curacao"],
    "cote-divoire": ["ivory coast", "côte d'ivoire", "cote d'ivoire"],
    "bosnia": ["bosnia and herzegovina", "bosnia & herzegovina"],
    "czech-republic": ["czechia", "czech republic", "czech"],
    "new-zealand": ["new zealand", "nz"],
    "south-africa": ["south africa", "sa", "rsa", "proteas"],
    "saudi-arabia": ["saudi arabia"],
    "sri-lanka": ["sri lanka", "sl"],
    "west-indies": ["west indies", "wi", "windies"],
    "costa-rica": ["costa rica"],
    "hong-kong": ["hong kong"],
    "england": ["england", "eng"],
    "australia": ["australia", "aus"],
    "india": ["india", "ind"],
    "pakistan": ["pakistan", "pak"],
    "bangladesh": ["bangladesh", "ban", "bd"],
    "afghanistan": ["afghanistan", "afg"],
    "zimbabwe": ["zimbabwe", "zim"],
    "ireland": ["ireland", "ire"],
    "scotland": ["scotland", "sco"],
    "netherlands": ["netherlands", "ned", "holland"],
    "rcb": ["royal challengers bengaluru", "royal challengers bangalore"],
    "csk": ["chennai super kings"],
    "mi": ["mumbai indians"],
    "dc": ["delhi capitals"],
    "kkr": ["kolkata knight riders"],
    "pbks": ["punjab kings"],
    "rr": ["rajasthan royals"],
    "srh": ["sunrisers hyderabad"],
    "gt": ["gujarat titans"],
    "lsg": ["lucknow super giants"],
    "man-city": ["manchester city", "man city"],
    "man-utd": ["manchester united", "man united", "man utd"],
    "real-madrid": ["real madrid"],
    "atletico-madrid": ["atletico madrid", "atlético madrid"],
    "bayern-munich": ["bayern munich", "bayern münchen", "fc bayern"],
    "psg": ["paris saint-germain", "paris saint germain"],
    "inter-milan": ["inter milan", "internazionale"],
    "ac-milan": ["ac milan"],
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def safe_request(url, timeout=30, retries=3):
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"  [WARN] Attempt {attempt+1}/{retries}: {url[:80]}... : {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None


def normalize_team_name(name):
    if not name:
        return ""
    name = name.strip().lower()
    name = re.sub(r'[^\w\s\'-]', '', name)
    return re.sub(r'\s+', ' ', name).strip()


def team_slug(name):
    if not name:
        return ""
    s = name.strip().lower()
    s = s.replace("'", "").replace("\u2019", "")
    for pat, rep in [
        (r'[àáâãäå]', 'a'), (r'[èéêë]', 'e'), (r'[ìíîï]', 'i'),
        (r'[òóôõö]', 'o'), (r'[ùúûü]', 'u'), (r'[ñ]', 'n'), (r'[ç]', 'c'),
    ]:
        s = re.sub(pat, rep, s)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s).strip('-')
    return re.sub(r'-+', '-', s)


def get_known_slug(name):
    norm = normalize_team_name(name)
    if not norm:
        return None
    for slug, aliases in TEAM_NAME_ALIASES.items():
        if norm == slug.replace('-', ' '):
            return slug
        for alias in aliases:
            if norm == alias.lower():
                return slug
    return None


def get_team_logo_smart(team_name):
    known = get_known_slug(team_name)
    if known:
        return f"{CDN_BASE}/team/{known}/logo.webp"
    s = team_slug(team_name)
    if not s:
        return f"{CDN_BASE}/team/unknown/logo.webp"
    return f"{CDN_BASE}/team/{s}/logo.webp"


def timestamp_to_bst(ts):
    try:
        ts = int(ts)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.astimezone(BST).strftime("%I:%M %p %d/%m/%Y")
    except (ValueError, TypeError, OSError):
        return ""


def format_start_time(time_str):
    if not time_str:
        return ""
    time_str = str(time_str).strip()

    # Unix timestamp (digits only)
    if time_str.isdigit():
        return timestamp_to_bst(time_str)

    # Float that looks like timestamp
    try:
        ts = float(time_str)
        if ts > 1000000000:
            return timestamp_to_bst(int(ts))
    except (ValueError, TypeError):
        pass

    # Standard date formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%Y-%m-%d",
    ]:
        try:
            dt = datetime.strptime(time_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(BST).strftime("%I:%M %p %d/%m/%Y")
        except ValueError:
            continue

    # Already correct format
    try:
        datetime.strptime(time_str, "%I:%M %p %d/%m/%Y")
        return time_str
    except ValueError:
        pass

    return time_str


def is_playable_url(url):
    """
    Check if a URL is an actual playable stream (m3u8, mpd, mp4, ts)
    and NOT an embed page, PHP script, or HTML page.
    """
    if not url:
        return False

    url_lower = url.lower().split('|')[0].split('?')[0]

    # Reject embed/fetch/player pages
    reject_patterns = [
        'embedhd.org',
        'fetch.php',
        'player.php',
        'embed.php',
        'source/fetch',
        'cricstreams.org/player',
        '/embed/',
        '/iframe/',
        'crichd.top',
    ]
    for pattern in reject_patterns:
        if pattern in url.lower():
            return False

    # Accept known stream extensions
    playable_extensions = ['.m3u8', '.mpd', '.mp4', '.ts', '.m3u', '.mkv', '.flv']
    for ext in playable_extensions:
        if ext in url_lower:
            return True

    # Accept known CDN/stream domains
    stream_domains = [
        'akamaized.net', 'cloudfront.net', 'cdn.', 'edge',
        'stream', 'live', 'hls', 'dash', 'playlist',
        '.m3u8', 'index.m3u8', 'master.m3u8', 'index.mpd',
        'phantemlis', 'caster.pro', 'wfty.st',
    ]
    for domain in stream_domains:
        if domain in url.lower():
            return True

    # Accept raw GitHub content (like default fallback)
    if 'raw.githubusercontent.com' in url or 'github.com' in url:
        return True

    return False


# ─── M3U Parser ──────────────────────────────────────────────────────────────

class M3UEntry:
    def __init__(self):
        self.title = ""
        self.url = ""
        self.group = ""
        self.tvg_name = ""
        self.tvg_logo = ""
        self.referer = ""
        self.origin = ""
        self.user_agent = ""
        self.drm_scheme = ""
        self.drm_license = ""
        self.extra_headers = {}


def parse_m3u_playlists(playlist_urls):
    all_entries = []
    for purl in playlist_urls:
        print(f"  Fetching: {purl[:80]}...")
        resp = safe_request(purl, timeout=45)
        if not resp:
            print(f"  [SKIP] Failed: {purl[:80]}")
            continue
        try:
            content = resp.text
        except Exception:
            continue
        entries = parse_m3u_content(content.splitlines())
        # Filter: only keep entries with playable URLs
        playable = [e for e in entries if is_playable_url(e.url)]
        all_entries.extend(playable)
        skipped = len(entries) - len(playable)
        extra = f" (skipped {skipped} non-playable)" if skipped else ""
        print(f"    → {len(playable)} playable entries{extra}")
    print(f"  Total playable entries: {len(all_entries)}")
    return all_entries


def parse_m3u_content(lines):
    entries = []
    current = None
    pending = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#EXTINF:'):
            current = M3UEntry()
            pending = {}
            m = re.search(r',(.+)$', line)
            if m:
                current.title = m.group(1).strip()
            m = re.search(r'tvg-name="([^"]*)"', line)
            if m:
                current.tvg_name = m.group(1).strip()
            m = re.search(r'tvg-logo="([^"]*)"', line)
            if m:
                current.tvg_logo = m.group(1).strip()
            m = re.search(r'group-title="([^"]*)"', line)
            if m:
                current.group = m.group(1).strip()

        elif line.startswith('#EXTVLCOPT:'):
            opt = line[len('#EXTVLCOPT:'):].strip()
            if '=' in opt:
                key, val = opt.split('=', 1)
                key = key.strip().lower()
                if key in ('http-referrer', 'http-referer'):
                    pending['referer'] = val.strip()
                elif key == 'http-origin':
                    pending['origin'] = val.strip()
                elif key == 'http-user-agent':
                    pending['user_agent'] = val.strip()

        elif line.startswith('#KODIPROP:'):
            prop = line[len('#KODIPROP:'):].strip()
            if '=' in prop:
                key, val = prop.split('=', 1)
                key = key.strip().lower()
                if 'license_type' in key:
                    pending['drm_scheme'] = val.strip()
                elif 'license_key' in key:
                    pending['drm_license'] = val.strip()
                elif key == 'inputstream.adaptive.manifest_headers':
                    try:
                        for hp in val.split('&'):
                            if '=' in hp:
                                hk, hv = hp.split('=', 1)
                                pending[hk.strip().lower()] = hv.strip()
                    except Exception:
                        pass

        elif line.startswith('#EXTHTTP:'):
            try:
                hdrs = json.loads(line[len('#EXTHTTP:'):].strip())
                for hk, hv in hdrs.items():
                    hkl = hk.lower()
                    if 'referer' in hkl:
                        pending['referer'] = hv
                    elif 'origin' in hkl:
                        pending['origin'] = hv
                    elif 'user-agent' in hkl:
                        pending['user_agent'] = hv
                    else:
                        pending[hk] = hv
            except Exception:
                pass

        elif not line.startswith('#'):
            if current is not None:
                if '|' in line:
                    parts = line.split('|', 1)
                    current.url = parts[0].strip()
                    for hdr in parts[1].strip().split('&'):
                        if '=' in hdr:
                            hk, hv = hdr.split('=', 1)
                            hkl = hk.strip().lower()
                            if 'referer' in hkl:
                                current.referer = hv.strip()
                            elif 'origin' in hkl:
                                current.origin = hv.strip()
                            elif 'user-agent' in hkl:
                                current.user_agent = hv.strip()
                            elif 'drmscheme' in hkl:
                                current.drm_scheme = hv.strip()
                            elif 'drmlicense' in hkl:
                                current.drm_license = hv.strip()
                            else:
                                current.extra_headers[hk.strip()] = hv.strip()
                else:
                    current.url = line.strip()

                # Apply pending headers
                if 'referer' in pending and not current.referer:
                    current.referer = pending['referer']
                if 'origin' in pending and not current.origin:
                    current.origin = pending['origin']
                if 'user_agent' in pending and not current.user_agent:
                    current.user_agent = pending['user_agent']
                if 'drm_scheme' in pending and not current.drm_scheme:
                    current.drm_scheme = pending['drm_scheme']
                if 'drm_license' in pending and not current.drm_license:
                    current.drm_license = pending['drm_license']

                if current.url and (current.url.startswith('http') or current.url.startswith('//')):
                    entries.append(current)
                current = None
                pending = {}

    return entries


def build_stream_url(entry):
    """Build full stream URL with pipe-separated headers."""
    url = entry.url
    if not url:
        return ""

    parts = []
    if entry.drm_scheme:
        s = entry.drm_scheme.lower()
        if 'clearkey' in s:
            parts.append("drmScheme=clearkey")
        elif 'widevine' in s:
            parts.append("drmScheme=widevine")
        elif 'playready' in s:
            parts.append("drmScheme=playready")
        else:
            parts.append(f"drmScheme={entry.drm_scheme}")

    if entry.drm_license:
        parts.append(f"drmLicense={entry.drm_license.strip()}")
    if entry.referer:
        parts.append(f"Referer={entry.referer}")
    if entry.origin:
        parts.append(f"Origin={entry.origin}")
    if entry.user_agent:
        parts.append(f"User-Agent={entry.user_agent}")
    elif entry.referer or entry.origin:
        parts.append(f"User-Agent={DEFAULT_USER_AGENT}")

    for hk, hv in entry.extra_headers.items():
        if hk.lower() not in ('referer', 'origin', 'user-agent', 'drmscheme', 'drmlicense'):
            parts.append(f"{hk}={hv}")

    return f"{url}|{'&'.join(parts)}" if parts else url


def extract_base_url(url):
    """Extract base URL for deduplication (strips time-sensitive params)."""
    u = url.split('|')[0] if '|' in url else url
    u = re.sub(r'[?&](st|e|expires|exp|token|t|ts|timestamp|md5v1|md5v2|hash)=[^&]*', '', u)
    return re.sub(r'\?$', '', u)


# ─── Stream Matching ─────────────────────────────────────────────────────────

def _name_in_text(original, norm, text):
    if not norm or len(norm) < 3:
        return False
    if norm in text:
        return True
    slug = get_known_slug(original)
    if slug:
        if slug.replace('-', ' ') in text:
            return True
        for alias in TEAM_NAME_ALIASES.get(slug, []):
            if alias.lower() in text:
                return True
    return False


def match_entry_to_event(entry, home, away, match_name, league=""):
    text = f"{entry.title} {entry.tvg_name} {entry.group}".lower()
    hn = normalize_team_name(home)
    an = normalize_team_name(away)

    hf = _name_in_text(home, hn, text)
    af = _name_in_text(away, an, text)
    if hf and af:
        return True

    # Check vs patterns
    for sep in [' vs ', ' v ', ' - ', ' vs. ']:
        for a, b in [(hn, an), (an, hn)]:
            if a and b and f"{a}{sep}{b}" in text:
                return True

    # Single word teams both present
    if (hn and an and len(hn) > 3 and len(an) > 3
            and ' ' not in hn and ' ' not in an
            and hn in text and an in text):
        return True

    # Match name fallback
    mn = normalize_team_name(match_name)
    if mn and len(mn) > 8 and mn in text:
        return True

    return False


def find_streams_for_event(event, m3u_entries):
    """Find all matching playable streams from M3U entries."""
    seen = set()
    matched = []
    for entry in m3u_entries:
        if not entry.url:
            continue
        if match_entry_to_event(
            entry,
            event.get('homeTeamName', ''),
            event.get('awayTeamName', ''),
            event.get('matchName', ''),
            event.get('league', ''),
        ):
            full = build_stream_url(entry)
            # Double-check the final URL is playable
            if not is_playable_url(full.split('|')[0]):
                continue
            base = extract_base_url(full)
            if base not in seen:
                seen.add(base)
                matched.append(full)
    return matched


def build_event_streams(event, m3u_entries):
    """Build streams array — M3U playlists ONLY, no API links."""
    streams = []
    seen = set()
    num = 1
    default_base = extract_base_url(DEFAULT_STREAM_URL)

    # Find streams from M3U playlists only
    for url in find_streams_for_event(event, m3u_entries):
        base = extract_base_url(url)
        if base in seen or base == default_base:
            continue
        seen.add(base)
        streams.append({
            "name": f"Server {num}",
            "url": url,
            "isPrimary": num == 1,
        })
        num += 1

    # Default fallback if no streams found
    if not streams:
        streams.append({
            "name": DEFAULT_STREAM_NAME,
            "url": DEFAULT_STREAM_URL,
            "isPrimary": True,
        })

    return streams


# ─── Event Fetchers ──────────────────────────────────────────────────────────

def fetch_main_events():
    """
    Fetch events from embedhd.org API.
    ONLY extracts event details (teams, time, league, sport).
    Does NOT use any stream/source links from the API.
    """
    print("Fetching main events API...")
    resp = safe_request(EVENT_API)
    if not resp:
        print("  [ERROR] Could not fetch main events API")
        return []

    try:
        text = resp.text.strip()
        if text.startswith('\ufeff'):
            text = text[1:]
        data = json.loads(text)
    except json.JSONDecodeError:
        print("  [ERROR] Could not parse main events API")
        return []

    events = []

    # Handle nested days → items structure
    if isinstance(data, dict) and 'days' in data:
        days = data['days']
        if isinstance(days, list):
            for day in days:
                if not isinstance(day, dict):
                    continue
                items = day.get('items', [])
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        e = parse_embedhd_event(item)
                        if e:
                            events.append(e)
            print(f"  Found {len(events)} main events (from {len(days)} days)")
            return events

    # Fallback: flat list
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = None
        for key in ['events', 'data', 'matches', 'results', 'items']:
            if key in data and isinstance(data[key], list):
                raw = data[key]
                break
        if raw is None:
            raw = [data]
    else:
        return []

    for item in raw:
        if isinstance(item, dict):
            e = parse_embedhd_event(item)
            if e:
                events.append(e)
    print(f"  Found {len(events)} main events")
    return events


def parse_embedhd_event(item):
    """
    Parse event details from embedhd.org API item.
    Extracts ONLY: teams, logos, league, sport, time, status.
    Does NOT extract any stream URLs.
    """
    # Match name
    match_name = item.get('title') or item.get('matchName') or item.get('name') or ""

    # Teams
    home_team = item.get('home_team') or ""
    away_team = item.get('away_team') or ""
    teams_obj = item.get('teams', {})
    if not home_team and isinstance(teams_obj, dict):
        h = teams_obj.get('home', {})
        if isinstance(h, dict):
            home_team = h.get('name', '')
    if not away_team and isinstance(teams_obj, dict):
        a = teams_obj.get('away', {})
        if isinstance(a, dict):
            away_team = a.get('name', '')

    # Split title if no team names
    if not home_team and not away_team and match_name:
        for sep in [' - ', ' vs ', ' v ']:
            if sep in match_name:
                p = match_name.split(sep, 1)
                home_team, away_team = p[0].strip(), p[1].strip()
                break
        if not home_team:
            home_team = match_name

    if not match_name:
        match_name = f"{home_team} vs {away_team}" if home_team and away_team else home_team

    # Logos — use API logos if valid, otherwise CDN
    home_logo = item.get('home_logo') or ""
    away_logo = item.get('away_logo') or ""
    if isinstance(teams_obj, dict):
        if not home_logo:
            h = teams_obj.get('home', {})
            if isinstance(h, dict):
                home_logo = h.get('logo') or ""
        if not away_logo:
            a = teams_obj.get('away', {})
            if isinstance(a, dict):
                away_logo = a.get('logo') or ""
    if not home_logo:
        home_logo = get_team_logo_smart(home_team)
    if not away_logo:
        away_logo = get_team_logo_smart(away_team)

    # League — properly formatted
    raw_league = item.get('league') or item.get('tournament') or item.get('competition') or ""
    league = format_league_name(raw_league)

    # Sport type
    raw_cat = item.get('category') or item.get('sport') or item.get('sportType') or ""
    sport_type = detect_sport_type_smart([raw_cat, raw_league, match_name, home_team, away_team])

    # Time — ts_et (Unix timestamp) is the primary source
    start_time = ""
    ts_et = item.get('ts_et')
    if ts_et is not None:
        start_time = timestamp_to_bst(ts_et)
    if not start_time:
        for tf in ['startTime', 'start_time', 'date', 'datetime', 'time', 'kickoff', 'match_time']:
            v = item.get(tf)
            if v:
                start_time = format_start_time(str(v))
                if start_time:
                    break
    if not start_time:
        d = item.get('date_et', '')
        if d:
            start_time = format_start_time(d)

    # Status
    status = item.get('status') or item.get('isLive') or ""
    if isinstance(status, str):
        is_live = status.strip().upper() in ('LIVE', 'TRUE', '1', 'IN_PROGRESS')
    else:
        is_live = bool(status)

    is_hot = item.get('isHot', item.get('is_hot', False))
    if isinstance(is_hot, str):
        is_hot = is_hot.lower() in ('true', '1', 'yes')

    # NOTE: We intentionally do NOT extract streams from the API.
    # API streams are embed page URLs (fetch.php), not playable streams.

    return {
        'matchName': match_name,
        'sportType': sport_type,
        'league': league,
        'homeTeamName': home_team,
        'homeTeamLogo': home_logo,
        'awayTeamName': away_team,
        'awayTeamLogo': away_logo,
        'isLive': bool(is_live),
        'isHot': bool(is_hot),
        'startTime': start_time,
        'link': '',
    }


def fetch_cricket_events():
    """Fetch cricket events. Teams/logos from API only, no channel URLs."""
    print("Fetching cricket events...")
    resp = safe_request(CRICKET_API)
    if not resp:
        print("  [ERROR] Could not fetch cricket events")
        return []

    try:
        text = resp.text.strip()
        if text.startswith('\ufeff'):
            text = text[1:]
        data = json.loads(text)
    except json.JSONDecodeError:
        print("  [ERROR] Could not parse cricket events")
        return []

    if isinstance(data, dict) and 'matches' in data:
        raw = data['matches']
    elif isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = None
        for k in ['events', 'data', 'results']:
            if k in data and isinstance(data[k], list):
                raw = data[k]
                break
        if raw is None:
            raw = [data]
    else:
        return []

    events = []
    for item in raw:
        if isinstance(item, dict):
            e = parse_cricket_event(item)
            if e:
                events.append(e)
    print(f"  Found {len(events)} cricket events")
    return events


def parse_cricket_event(item):
    """Parse cricket event. Does NOT use Channels — streams come from M3U only."""
    match_name = (
        item.get('match name') or item.get('match_name') or
        item.get('matchName') or item.get('title') or
        item.get('name') or ""
    )
    home_team = (
        item.get('Team 1 Name') or item.get('homeTeamName') or
        item.get('home_team') or item.get('team1') or ""
    )
    away_team = (
        item.get('Team 2 Name') or item.get('awayTeamName') or
        item.get('away_team') or item.get('team2') or ""
    )
    home_logo = item.get('Team 1 Logo') or item.get('homeTeamLogo') or ""
    away_logo = item.get('Team 2 Logo') or item.get('awayTeamLogo') or ""

    raw_league = (
        item.get('Tour/Group name') or item.get('league') or
        item.get('tournament') or item.get('series') or ""
    )
    league = format_league_name(raw_league)

    # TBD away team
    if away_team and away_team.strip().upper() == "TBD":
        away_team = league or item.get('Category') or "TBD"
        if not away_logo or 'default' in away_logo:
            away_logo = get_team_logo_smart(away_team)

    if not home_team and not away_team and match_name:
        for sep in [' vs ', ' v ', ' - ']:
            if sep in match_name.lower():
                p = re.split(re.escape(sep), match_name, maxsplit=1, flags=re.IGNORECASE)
                home_team = p[0].strip()
                away_team = p[1].strip() if len(p) > 1 else ""
                break
        if not home_team:
            home_team = match_name

    if not match_name:
        match_name = f"{home_team} vs {away_team}" if home_team and away_team else home_team

    start_time_raw = (
        item.get('Start time') or item.get('start_time') or
        item.get('startTime') or item.get('date') or ""
    )
    start_time = format_start_time(str(start_time_raw)) if start_time_raw else ""

    status = item.get('Status') or item.get('status') or item.get('isLive') or ""
    if isinstance(status, str):
        is_live = status.strip().upper() in ('LIVE', 'TRUE', '1')
    else:
        is_live = bool(status)

    is_hot = item.get('isHot', item.get('is_hot', False))
    if isinstance(is_hot, str):
        is_hot = is_hot.lower() in ('true', '1', 'yes')

    if not home_logo:
        home_logo = get_team_logo_smart(home_team)
    if not away_logo:
        away_logo = get_team_logo_smart(away_team)

    return {
        'matchName': match_name,
        'sportType': 'Cricket',
        'league': league,
        'homeTeamName': home_team,
        'homeTeamLogo': home_logo,
        'awayTeamName': away_team,
        'awayTeamLogo': away_logo,
        'isLive': bool(is_live),
        'isHot': bool(is_hot),
        'startTime': start_time,
        'link': '',
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Sports Events JSON Generator v6")
    print("=" * 60)

    # Step 1: Fetch event details
    print("\n[Step 1] Fetching event details from APIs...")
    print("  (Event APIs provide ONLY match info — no stream links)")
    main_events = fetch_main_events()
    cricket_events = fetch_cricket_events()
    all_events = main_events + cricket_events
    print(f"\nTotal events: {len(all_events)}")

    if not all_events:
        print("[WARN] No events found.")
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return

    # Step 2: Fetch M3U playlists (the ONLY source for stream links)
    print("\n[Step 2] Fetching M3U playlists (stream source)...")
    print("  (ALL streaming links come exclusively from these playlists)")
    m3u_entries = parse_m3u_playlists(PLAYLIST_URLS)

    # Step 3: Match streams to events and build output
    print("\n[Step 3] Matching streams to events...")
    timestamp = int(time.time() * 1000)
    output_events = []
    sport_stats = {}

    for idx, event in enumerate(all_events):
        streams = build_event_streams(event, m3u_entries)
        sport = event.get('sportType', 'Football')
        sport_stats[sport] = sport_stats.get(sport, 0) + 1

        output_events.append({
            "id": f"imported-{timestamp}-{idx}",
            "matchName": event.get('matchName', ''),
            "sportType": sport,
            "league": event.get('league', ''),
            "homeTeamName": event.get('homeTeamName', ''),
            "homeTeamLogo": event.get('homeTeamLogo', ''),
            "awayTeamName": event.get('awayTeamName', ''),
            "awayTeamLogo": event.get('awayTeamLogo', ''),
            "isLive": event.get('isLive', False),
            "isHot": event.get('isHot', False),
            "startTime": event.get('startTime', ''),
            "link": event.get('link', ''),
            "streams": streams,
        })

        has_real = any(s['url'] != DEFAULT_STREAM_URL for s in streams)
        icon = "\u2713" if has_real else "\u25cb"
        info = f"{len(streams)} streams" if has_real else "default"
        t = event.get('startTime', 'no time')
        lg = event.get('league', '')[:20]
        mn = event.get('matchName', '?')[:35]
        print(f"  [{idx+1:3d}] [{sport:15s}] {mn:35s} | {lg:20s} | {t:22s} | {icon} {info}")

    # Step 4: Write output
    print(f"\n[Step 4] Writing to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output_events, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Generated {len(output_events)} events\n")
    print("Sport breakdown:")
    for s, c in sorted(sport_stats.items(), key=lambda x: -x[1]):
        print(f"  {s:20s}: {c}")

    total = sum(len(e['streams']) for e in output_events)
    real = sum(1 for e in output_events if any(s['url'] != DEFAULT_STREAM_URL for s in e['streams']))
    print(f"\nTotal stream links: {total}")
    print(f"Events with M3U streams: {real}/{len(output_events)}")
    print(f"Events with default fallback: {len(output_events) - real}/{len(output_events)}")

    # Verify no embed/fetch URLs leaked through
    bad_urls = []
    for e in output_events:
        for s in e['streams']:
            url = s['url']
            if 'embedhd.org' in url or 'fetch.php' in url or 'player.php' in url:
                bad_urls.append(url[:80])
    if bad_urls:
        print(f"\n⚠ WARNING: {len(bad_urls)} non-playable URLs found:")
        for u in bad_urls[:5]:
            print(f"  - {u}")
    else:
        print("\n✓ All stream URLs are playable (no embed/fetch URLs)")

    print(f"\nSample output:")
    print("-" * 110)
    for e in output_events[:8]:
        print(f"  [{e['sportType']:12s}] {e['matchName'][:30]:30s} | {e['league'][:22]:22s} | {e['startTime']:22s}")
    print("-" * 110)
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
