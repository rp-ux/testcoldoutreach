#!/usr/bin/env python3
"""
Improved EthCC[9] speaker extractor.
Parses INDEX.md for "Name (Company)" patterns, cleans data, deduplicates,
and fills in missing companies from known mappings.
"""

import re
import json
import csv

# Known speaker-company mappings (from web search, README highlights, etc.)
KNOWN_COMPANIES = {
    "vitalik buterin": "Ethereum Foundation",
    "stani kulechov": "Aave Labs",
    "jean-marc stenger": "Société Générale-Forge",
    "marc stenger": "Société Générale-Forge",
    "sergey nazarov": "Chainlink Labs",
    "charles guillemet": "Ledger",
    "johann kerbreat": "Robinhood",
    "kite liu": "Uniswap Labs",
    "antonio sanso": "Ethereum Foundation",
    "jerome de tychey": "Ethereum France",
    "ed felten": "Offchain Labs",
    "karl floersch": "Optimism",
    "arthur breitman": "Tezos",
    "sebastien borget": "The Sandbox",
    "justin sun": "Tron",
    "sergej kunz": "1inch",
    "zac williamson": "Aztec",
    "paul brody": "EY (Ernst & Young)",
    "barnabé monnot": "Ethereum Foundation",
    "patricio worthalter": "POAP",
    "tomasz stanczak": "Nethermind",
    "richard meissner": "Safe",
    "ambre soubiran": "Kaiko",
    "emilio frangella": "Aave Labs",
    "alex cutler": "Aerodrome",
    "mariia keiko": "CoW DAO",
    "suki yang": "—",
    "christoph schlegel": "Flashbots",
    "luis correia": "Flashbots",
    "jonathan passerat-palmbach": "Flashbots",
    "terence tsao": "Offchain Labs",
    "krzysztof gogol": "—",
    "corinne powers": "—",
    "stefan loesch": "—",
    "nisedo": "Trail of Bits",
    "tomer ganor": "Aave Labs",
    "charles cooper": "Vyper",
    "mooly sagiv": "Certora",
    "bob summerwill": "ETC Cooperative",
    "faustine fleuret": "Adan",
    "oskarth": "Waku / Status",
    "simon polrot": "Ethereum France",
    "marina markezic": "European Crypto Initiative",
    "florian glatz": "European Crypto Initiative",
    "reid simon": "Figure Technology",
    "patrick hansen": "Circle",
    "gísli kristjánsson": "Monerium",
    "ophelia snyder": "21Shares",
    "laszlo szabo": "Kiln",
    "fredrik haga": "Dune Analytics",
    "tom trowbridge": "Peaq",
    "andrew o'neill": "S&P Global",
    "meinhard benn": "SatoshiPay",
    "david leonardi": "Polygon",
    "sebastien borget": "The Sandbox",
    "doo wan nam": "StableDAO",
    "pablo veyrat": "Angle Protocol",
    "suhyeon lee": "—",
    "william george": "—",
    "tiago santana": "—",
    "oghenekaro elem": "—",
    "mark ballandies": "ETH Zurich",
    "adrián brink": "Anoma",
    "adrian brink": "Anoma",
    "yi sun": "OpenVM / Axiom",
    "toni wahrstaetter": "Ethereum Foundation",
    "marius van der wijden": "Ethereum Foundation",
    "cperezz": "Ethereum Foundation",
    "derek sorensen": "Ethereum Foundation",
    "ladislaus von daniels": "Ethereum Foundation",
    "jihoon song": "Ethereum Foundation",
    "justin drake": "Ethereum Foundation",
    "nicolas consigny": "Ethereum Foundation",
    "jordi baylina": "ZisK / Polygon",
    "friederike ernst": "Gnosis",
    "rebecca liao": "Saga",
    "yaniv tal": "The Graph",
    "lioba heimbach": "ETH Zurich",
    "sarah hicks": "—",
    "liz steininger": "Least Authority",
    "suji": "Mask Network",
    "pol lanski": "Peaq",
    "henri lieutaud": "Blockchain Oracle Summit",
    "drake breeding": "Arc",
    "matt pearring": "—",
    "mohsen ahmadvand": "—",
    "hong kim": "Hashed",
    "qi zhou": "EthStorage",
    "yoichi hirai": "Ethereum Foundation",
    "hildobby": "Dragonfly",
    "griff": "Giveth / TheDAO",
    "jonjon clark": "Uniswap",
    "konstantin dubus": "Verifiable Finance",
    "val gui": "Kiln",
    "jan setina": "Trezor",
    "pedro gomes": "WalletConnect",
    "ellie davidson": "—",
    "jean-marc stenger": "Société Générale-Forge",
    "victor chiea": "—",
    "petar atanasovski": "—",
    "dan ligocky": "—",
    "anthony caravello": "—",
    "kelly roegies": "—",
    "reka medvecz": "—",
    "seth for privacy": "Monero / FOSS",
    "artem sinyakin": "—",
    "laurence day": "Wildcat Protocol",
    "federico ast": "Kleros",
    "cactus raazi": "—",
    "martin bruncko": "—",
    "izzy lido": "Lido",
    "prabal banerjee": "Avail",
    "wish wu": "—",
    "kaloyan kosev": "—",
    "jan gorzny": "—",
    "simon masson": "Ethereum Foundation",
    "hester bruikman": "Ethereum Foundation",
    "pamina georgiev": "—",
    "oliver desenfans": "Aleph Cloud",
    "olivier desenfans": "Aleph Cloud",
    "stéphane tetsing": "Remix IDE",
    "dayan brunie": "Consensys",
    "will papper": "Syndicate",
    "nahim terrazas": "Across Protocol",
    "gajinder singh": "Ethereum Foundation",
    "johannes kern": "—",
    "julie bader": "—",
    "romain menetrier": "—",
    "alina tielnova": "—",
    "marcin kazmierczak": "RedStone Oracles",
    "claire balva": "—",
    "sebastian widmann": "—",
    "belma gutlic": "—",
    "ishan sharma": "—",
    "harry horsfall": "—",
    "martin leclercq": "—",
    "joseph jelacic": "—",
    "josef jelacic": "—",
    "devansh mehta": "—",
    "clement lesaege": "Kleros",
    "pranay valson": "—",
    "jonathan han": "—",
    "alexander müller": "—",
    "vasily sidorov": "—",
    "yeho hwang": "—",
    "zach pandl": "Grayscale",
    "arman sarhaddar": "—",
    "murat ögat": "Aktionariat",
    "greg swirski": "—",
    "lola rigaut-luczak": "—",
    "devon martens": "—",
    "chase manning": "—",
    "sam reeves": "—",
    "david pearce": "—",
    "alan li": "—",
    "oleg lodygensky": "—",
    "wolfgang vitale": "—",
    "slobodan lukovic": "—",
    "nischal sharma": "—",
    "max lomu": "—",
    "ami nagata": "—",
    "denitza valjavec": "—",
    "chunda mccain": "—",
    "pauline shangett": "—",
    "raza zaidi": "—",
    "maria magenes": "—",
    "nadia ivanova-banda": "—",
    "ernesto garcía": "OpenZeppelin",
    "joan alavedra": "—",
    "hayat outahar": "—",
    "nicolas assouad": "—",
    "steffen kux": "Colibri",
    "eugene joo": "Fhenix",
    "martin hansen": "—",
    "otto jacobsson": "—",
    "ece orsel": "—",
    "bianca buzea": "—",
    "andy m. lee": "—",
    "charles d'haussy": "dYdX Foundation",
    "xiangru ma": "—",
    "fabrizio romano genovese": "—",
    "stefano gogioso": "—",
    "paul schoenfelder": "Miden (Polygon)",
    "oisín kyne": "—",
    "kirk baird": "Sigma Prime",
    "jon stephens": "—",
    "daniel von fange": "—",
    "stephan duan": "—",
    "mario baxter cabrera": "Aave",
    "kolten bergeron": "Stellar Development Foundation",
    "amit chaudhary": "—",
    "alejandro ranchal-pedrosa": "—",
    "merlin egalite": "Morpho",
    "yorick downe": "DAppNode",
    "dyma budorin": "Hacken",
    "stefano de angelis": "—",
    "leo fan": "Cysic",
    "ryan sauge": "—",
    "alec novella": "—",
    "jake salerno": "—",
    "andreas melhede": "Elata Protocol",
    "conor": "Coinbase",
    "tom david": "—",
    "peter us": "—",
    "ernestoOlmedo pereira": "SG Forge",
    "ernesto olmedo pereira": "SG Forge",
    "sunny jiang": "—",
    "andrea canidio": "CoW Protocol",
    "darius moukhtarzade": "—",
    "louis o'connor": "—",
    "louie o'connor": "—",
    "daniel elkins": "DGRS Labs",
    "uros trbovic": "—",
    "brenda loya": "Tellor",
    "akaki mamageishvili": "Offchain Labs",
    "kevin weaver": "Optimism",
    "declan fox": "Linea (Consensys)",
    "leo": "MigaLabs",
    "joshua foster": "QuickNode",
    "luca winter": "Serenita",
    "ken smith": "NextBlock Solutions",
    "kubi mensah": "Gattaca",
    "redwan meslem": "ERC-3643",
    "ambroise helaine": "Bybit",
    "norbert vadas": "Zenith / Canton",
    "tomer weller": "Stellar Development Foundation",
    "chris mccabe": "Session",
    "andrii bondar": "Matter Labs (zkSync)",
    "stepan nilov": "Tangem",
    "wesley crook": "FP Block",
    "sejal": "Protocol Labs / Filecoin",
    "dima gusakov": "Lido",
    "cyrille brière": "f(x) Protocol",
    "fisher yu": "Babylon",
    "simona pop": "Angel Investor & Advisor",
    "jacob": "—",
    "agaperste": "—",
    "realdenniso": "—",
    "wei3erhase": "HAI Finance",
    "jacobc.eth": "—",
    "0xalex": "Kleros",
    "0xpenryn": "World (Worldcoin)",
    "zk_evm": "—",
    "albicodes": "—",
    "btchip": "Ledger",
    "cheeky-gorilla": "—",
    "dee_centralized": "—",
    "definikola": "—",
    "ottdogg": "—",
    "pbj": "—",
    "seven": "—",
    "costanza": "—",
    "dmh": "—",
    "reno": "—",
    "conor": "Coinbase",
    "mende": "—",
    "han": "—",
    "alice": "—",
    "anya": "—",
    "anne": "—",
    "lera": "—",
    "satya": "—",
    "deca": "—",
    "gwen": "—",
    "sajida": "—",
    "rémi": "—",
    "binji": "—",
    "noid": "—",
    "jean": "—",
    "jose": "—",
    "e.g.": "—",
    "iva": "—",
}

# Names to SKIP (artifacts from parsing, not real speaker names)
SKIP_NAMES = {
    "adrian brink privacy and self",
    "anthurine introducing web3://",
    "darius moukhtarzade why token launches fail",
    "kasra khosravi (goldsky (and also erpc open",
    "kayden moroz liebl (https://github.com/reamlabs/re",
    "leo fan making sub",
    "stefano de angelis rethinking peerdas: transparent",
    "privacy requires system",
    "crypto agility framework for ethereum",
    "pedrosa",
    "vabuk (max planck institute for so",
    "yorick downe home staking behind cgnat",
    "latam",
    "asi",
    "chow",
    "jerome  de tychey ethereum france",
    "nenter",
    "sws",
    "re",
    "nathan",
    "shane",
    "richardson",
    "perezz",
    "mohsen ahmadvand )",
    "james wo )",
    "he who remains",
}

# Corrected names mapping
NAME_CORRECTIONS = {
    "jerome  de tychey": "Jerome de Tychey",
    "stani  kulechov": "Stani Kulechov",
    "nicolas  consigny": "Nicolas Consigny",
    "david  leonardi": "David Leonardi",
    "val  gui": "Val Gui",
    "michael  wu": "Michael Wu",
    "stefan  kobrc": "Stefan Kobrc",
    "daiki  endo": "Daiki Endo",
    "joan  alavedra": "Joan Alavedra",
    "adrian brink privacy and self": None,  # skip
}


def clean_name(name):
    """Clean up a speaker name."""
    name = name.strip().rstrip(',').strip()
    # Remove trailing parenthetical junk
    name = re.sub(r'\s*\)$', '', name)
    # Fix double spaces
    name = re.sub(r'\s+', ' ', name)
    return name


def title_case_name(name):
    """Proper title case for names, preserving intentional casing."""
    if name.startswith('0x') or name.endswith('.eth'):
        return name
    parts = name.split()
    result = []
    for p in parts:
        if p.startswith('(') or p.startswith('0x') or p.isupper() and len(p) <= 4:
            result.append(p)
        elif p[0].islower() and len(p) > 3:
            result.append(p.capitalize())
        else:
            result.append(p)
    return ' '.join(result)


with open('/home/user/testcoldoutreach/ethcc9_full_index.md', 'r') as f:
    content = f.read()

speakers_raw = []
current_stage = ""

for line in content.split('\n'):
    stage_match = re.match(r'^## (.+?) \((\d+) talks\)', line)
    if stage_match:
        current_stage = stage_match.group(1).replace(' Stage', '')
        continue

    if not re.match(r'^\d+\.', line.strip()):
        continue

    bold_match = re.search(r'\*\*(.+?)\*\*', line)
    if not bold_match:
        continue

    bold_text = bold_match.group(1)
    after_bold = line[bold_match.end():]
    speaker_after = re.match(r'\s*--\s*(.+?)(?:\s*\||\s*$)', after_bold)

    # Extract all "Name (Company)" patterns from bold_text
    panel_speakers = re.findall(
        r'([A-ZÀ-Ÿa-zà-ÿ0-9][A-Za-zÀ-ÿ\-\'\.\s]+?)\s*\(([^)]+)\)',
        bold_text
    )
    for name, company in panel_speakers:
        name = clean_name(name)
        if len(name) > 2:
            speakers_raw.append({
                'name': name,
                'company': company.strip(),
                'stage': current_stage,
            })

    # Extract speaker after "--"
    if speaker_after:
        sp_text = speaker_after.group(1).strip()
        sp_text = re.sub(r'\s*\[.*', '', sp_text).strip()

        sp_companies = re.findall(
            r'([A-ZÀ-Ÿa-zà-ÿ0-9][A-Za-zÀ-ÿ\-\'\.\s]+?)\s*\(([^)]+)\)',
            sp_text
        )
        if sp_companies:
            for name, company in sp_companies:
                name = clean_name(name)
                if len(name) > 2:
                    speakers_raw.append({
                        'name': name,
                        'company': company.strip(),
                        'stage': current_stage,
                    })
            # Remaining names without companies
            remaining = re.sub(
                r'[A-Za-zÀ-ÿ\-\'\.\s]+?\s*\([^)]+\)', '', sp_text
            )
            for part in remaining.split(','):
                part = clean_name(part)
                if part and len(part) > 2 and re.match(r'^[A-Z0-9]', part):
                    speakers_raw.append({
                        'name': part,
                        'company': '',
                        'stage': current_stage,
                    })
        else:
            for part in sp_text.split(','):
                part = clean_name(part)
                if part and len(part) > 1:
                    speakers_raw.append({
                        'name': part,
                        'company': '',
                        'stage': current_stage,
                    })

# Deduplicate, clean, and enrich
seen = {}
for sp in speakers_raw:
    name = sp['name']

    # Apply name corrections
    name_lower = name.lower().strip()
    if name_lower in NAME_CORRECTIONS:
        corrected = NAME_CORRECTIONS[name_lower]
        if corrected is None:
            continue
        name = corrected

    # Skip garbage entries
    if name_lower in SKIP_NAMES:
        continue
    if len(name) <= 2:
        continue

    name = clean_name(name)
    key = re.sub(r'\s+', ' ', name.lower().strip())

    # Skip if already seen (keep entry with best company info)
    if key in seen:
        if sp['company'] and not seen[key]['company']:
            seen[key]['company'] = sp['company']
        continue

    # Lookup company from known mappings
    company = sp['company']
    if not company or company == '—':
        lookup = KNOWN_COMPANIES.get(key, '')
        if lookup and lookup != '—':
            company = lookup

    # Clean company name
    if company:
        company = company.strip().rstrip(')')
        if company.startswith('and also'):
            company = ''

    seen[key] = {
        'name': title_case_name(name),
        'company': company,
        'stage': sp['stage'],
    }

# Sort by name
unique_speakers = sorted(seen.values(), key=lambda x: x['name'].lower())

# Filter out remaining junk entries
final_speakers = []
for sp in unique_speakers:
    name = sp['name']
    # Skip entries that look like talk titles, not names
    if any(w in name.lower() for w in [
        'introducing', 'rethinking', 'privacy and self',
        'why token', 'home staking', 'framework for',
        'github.com', 'https://', 'making sub',
    ]):
        continue
    if len(name) > 50:
        continue
    final_speakers.append(sp)

print(f"Final cleaned speakers: {len(final_speakers)}")

# Write CSV
with open('/home/user/testcoldoutreach/ethcc9_speakers.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['#', 'Speaker', 'Company', 'Stage', 'Conference', 'Location', 'Date'])
    for i, sp in enumerate(final_speakers, 1):
        writer.writerow([
            i,
            sp['name'],
            sp['company'] if sp['company'] else '',
            sp['stage'],
            'EthCC[9]',
            'Palais des Festivals, Cannes, France',
            'March 30 - April 2, 2026',
        ])

# Write JSON
with open('/home/user/testcoldoutreach/ethcc9_speakers.json', 'w') as f:
    json.dump(final_speakers, f, ensure_ascii=False, indent=2)

# Stats
with_company = sum(1 for sp in final_speakers if sp['company'])
print(f"With company: {with_company}/{len(final_speakers)} ({100*with_company//len(final_speakers)}%)")

# Print preview
print("\n| # | Speaker | Company | Stage |")
print("|---|---------|---------|-------|")
for i, sp in enumerate(final_speakers, 1):
    print(f"| {i} | {sp['name']} | {sp['company'] or '—'} | {sp['stage']} |")
