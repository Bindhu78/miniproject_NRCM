# A demo static corpus: category -> list of text snippets
SNIPPETS = {
    'Tech': [
        "Breakthrough AI beats human doctors at diagnosing diseases",
        "New smartphone release features quantum-inspired chip",
        "Cybersecurity firms warn of rise in AI-powered phishing"
    ],
    'Politics': [
        "Election campaigns intensify ahead of the national vote",
        "Government unveils new policy on renewable energy",
        "Parliament passes historic reform bill"
    ],
    'Sports': [
        "Local football team wins championship after penalty shootout",
        "Olympic committee announces new host city",
        "Tennis star sets record with 100th career title"
    ],
    'Health': [
        "New vaccine approved for emerging viral outbreak",
        "Study finds link between diet and longevity",
        "Mental health awareness campaign launched nationwide"
    ]
}

# Binary-to-category maps for 2-bit encoding:
BINARY_MAP = {
    '00': 'Sports',
    '01': 'Politics',
    '10': 'Tech',
    '11': 'Health'
}
INV_BINARY_MAP = {v: k for k, v in BINARY_MAP.items()}
