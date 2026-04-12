#!/usr/bin/env python3
"""Extract all speakers and companies from EthCC[9] INDEX.md"""

import re
import json

with open('/home/user/testcoldoutreach/ethcc9_full_index.md', 'r') as f:
    content = f.read()

speakers = []
current_stage = ""

for line in content.split('\n'):
    # Detect stage headers
    stage_match = re.match(r'^## (.+?) \((\d+) talks\)', line)
    if stage_match:
        current_stage = stage_match.group(1)
        continue

    # Match talk lines
    if not line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and \
       not re.match(r'^\d+\.', line.strip()):
        continue

    # Extract speaker info from the bold text
    bold_match = re.search(r'\*\*(.+?)\*\*', line)
    if not bold_match:
        continue

    bold_text = bold_match.group(1)

    # After ** there might be " -- Speaker Name"
    after_bold = line[bold_match.end():]
    speaker_after = re.match(r'\s*--\s*(.+?)(?:\s*\||\s*$)', after_bold)

    # Some entries have speaker names IN the bold text (panel format)
    # e.g., "**Johann Eid (Chainlink Labs), Emma Landriault (J.P. Morgan Chase)...**"
    # Others have "**Talk Title** -- Speaker Name"

    # Check if bold text contains company names in parentheses (panel format)
    has_companies = bool(re.search(r'\([A-Z]', bold_text))

    if has_companies or not speaker_after:
        # Panel format or speaker embedded in title
        # Extract "Name (Company)" patterns
        panel_speakers = re.findall(r'([A-Z][a-zÀ-ÿ\-\']+(?:\s+[A-Za-zÀ-ÿ\-\'\.]+)*)\s*\(([^)]+)\)', bold_text)
        if panel_speakers:
            for name, company in panel_speakers:
                name = name.strip().rstrip(',')
                if len(name) > 2 and not name.startswith(('From', 'The', 'How', 'Why', 'What')):
                    speakers.append({
                        'name': name,
                        'company': company.strip(),
                        'stage': current_stage,
                    })

        # Also check after bold
        if speaker_after:
            sp_text = speaker_after.group(1).strip()
            # Could contain "Name (Company)" or just "Name"
            sp_companies = re.findall(r'([A-Z][a-zÀ-ÿ\-\']+(?:\s+[A-Za-zÀ-ÿ\-\'\.]+)*)\s*\(([^)]+)\)', sp_text)
            if sp_companies:
                for name, company in sp_companies:
                    name = name.strip().rstrip(',')
                    if len(name) > 2:
                        speakers.append({
                            'name': name,
                            'company': company.strip(),
                            'stage': current_stage,
                        })
            else:
                # Just a name
                sp_text = re.sub(r'\s*\[.*', '', sp_text).strip().rstrip(',')
                if sp_text and len(sp_text) > 2 and not sp_text.startswith(('The ', 'A ', 'An ', 'How', 'Why', 'What')):
                    speakers.append({
                        'name': sp_text,
                        'company': '',
                        'stage': current_stage,
                    })
    else:
        # Standard format: "**Talk Title** -- Speaker Name"
        sp_text = speaker_after.group(1).strip()
        # Check for "Name (Company), Name2 (Company2)" pattern
        sp_companies = re.findall(r'([A-Z][a-zÀ-ÿ\-\']+(?:\s+[A-Za-zÀ-ÿ\-\'\.]+)*)\s*\(([^)]+)\)', sp_text)
        if sp_companies:
            for name, company in sp_companies:
                name = name.strip().rstrip(',')
                if len(name) > 2:
                    speakers.append({
                        'name': name,
                        'company': company.strip(),
                        'stage': current_stage,
                    })
            # Also get any names without companies
            remaining = re.sub(r'[A-Z][a-zÀ-ÿ\-\']+(?:\s+[A-Za-zÀ-ÿ\-\'\.]+)*\s*\([^)]+\)', '', sp_text)
            for name_part in remaining.split(','):
                name_part = name_part.strip().rstrip(',')
                if name_part and len(name_part) > 2 and re.match(r'^[A-Z]', name_part):
                    speakers.append({
                        'name': name_part,
                        'company': '',
                        'stage': current_stage,
                    })
        else:
            # Simple "Name" or "Name, Name2"
            for name_part in sp_text.split(','):
                name_part = re.sub(r'\s*\[.*', '', name_part).strip()
                if name_part and len(name_part) > 1:
                    speakers.append({
                        'name': name_part,
                        'company': '',
                        'stage': current_stage,
                    })

# Deduplicate by name
seen = set()
unique_speakers = []
for sp in speakers:
    key = sp['name'].lower().strip()
    if key not in seen and len(key) > 2:
        seen.add(key)
        unique_speakers.append(sp)

# Sort by name
unique_speakers.sort(key=lambda x: x['name'])

print(f"Total unique speakers extracted: {len(unique_speakers)}")
print()

# Save as JSON
with open('/home/user/testcoldoutreach/ethcc9_speakers.json', 'w') as f:
    json.dump(unique_speakers, f, ensure_ascii=False, indent=2)

# Save as formatted markdown
with open('/home/user/testcoldoutreach/ethcc9_speakers_complete.md', 'w') as f:
    f.write("# EthCC[9] — Complete Speakers List\n\n")
    f.write(f"**{len(unique_speakers)} unique speakers** extracted from 307 talks\n\n")
    f.write("EthCC[9] | March 30 - April 2, 2026 | Palais des Festivals, Cannes\n\n")
    f.write("Source: [Kropiunig/ethcc9-talks](https://github.com/Kropiunig/ethcc9-talks)\n\n")

    f.write("| # | Speaker | Company | Stage |\n")
    f.write("|---|---------|---------|-------|\n")
    for i, sp in enumerate(unique_speakers, 1):
        name = sp['name']
        company = sp['company'] if sp['company'] else '—'
        stage = sp['stage']
        f.write(f"| {i} | {name} | {company} | {stage} |\n")

# Print table
print("| # | Speaker | Company | Stage |")
print("|---|---------|---------|-------|")
for i, sp in enumerate(unique_speakers, 1):
    name = sp['name']
    company = sp['company'] if sp['company'] else '—'
    stage = sp['stage']
    print(f"| {i} | {name} | {company} | {stage} |")
