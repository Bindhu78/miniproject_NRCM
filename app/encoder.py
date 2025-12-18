from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .corpus import SNIPPETS, BINARY_MAP

model = SentenceTransformer('all-MiniLM-L6-v2')

def encode_message(text: str):
    # Convert to binary
    binary = ''.join(f"{ord(c):08b}" for c in text)
    # Pad to multiple of 2 bits
    if len(binary) % 2 != 0:
        binary += '0'
    selected_snippets = []
    for i in range(0, len(binary), 2):
        bits = binary[i:i+2]
        cat = BINARY_MAP[bits]
        emb_cat = model.encode(cat)
        # pick highest-semantic snippet
        best = max(
            SNIPPETS[cat],
            key=lambda s: cosine_similarity([emb_cat], [model.encode(s)])[0][0]
        )
        selected_snippets.append(best)
    return selected_snippets
