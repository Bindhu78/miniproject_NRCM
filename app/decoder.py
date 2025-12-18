from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np # For averaging embeddings
from .corpus import SNIPPETS, INV_BINARY_MAP, BINARY_MAP # Import BINARY_MAP for fallback

# Initialize the model globally to load it only once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute embeddings for category names (as a fallback)
CAT_NAME_EMBS = {cat_name: model.encode(cat_name) for cat_name in SNIPPETS.keys()}

# Precompute the AVERAGE embedding for snippets within each category
AVERAGE_CAT_CONTENT_EMBS = {}
for category, snippet_list in SNIPPETS.items():
    if not snippet_list: 
        # If a category has no snippets, fallback to its name's embedding for this average
        AVERAGE_CAT_CONTENT_EMBS[category] = CAT_NAME_EMBS.get(category, np.zeros(model.get_sentence_embedding_dimension()))
        print(f"Warning: Category '{category}' has no snippets in corpus. Using category name embedding as fallback for average.")
        continue

    category_snippet_embeddings = model.encode(snippet_list)
    AVERAGE_CAT_CONTENT_EMBS[category] = np.mean(category_snippet_embeddings, axis=0)

def decode_snippets(received_snippets):
    """
    Decodes a list of received text snippets back into the original message.
    """
    bits = ''
    if not received_snippets:
        return ""

    # Encode all received snippets. Batch encoding can be more efficient.
    try:
        received_snippet_embeddings = model.encode(received_snippets)
    except Exception as e:
        print(f"Error encoding received snippets: {e}")
        return "[Decoding Error: Could not process snippets]"

    for i, emb in enumerate(received_snippet_embeddings):
        current_snippet_text = received_snippets[i] # For logging/debugging
        best_cat = None
        max_sim = -float('inf') 

        # Primary strategy: Compare to average content embedding of each category
        for category_name, avg_cat_content_emb in AVERAGE_CAT_CONTENT_EMBS.items():
            try:
                similarity = cosine_similarity([emb], [avg_cat_content_emb])[0][0]
                if similarity > max_sim:
                    max_sim = similarity
                    best_cat = category_name
            except Exception as e:
                print(f"Error calculating similarity for snippet '{current_snippet_text[:30]}...' with category '{category_name}': {e}")
                continue # Skip this category comparison on error
        
        # Fallback strategy: If primary fails or yields low confidence, try category name matching
        # (A more sophisticated confidence threshold could be used here)
        if best_cat is None or max_sim < 0.5: # Example confidence threshold
            # print(f"Low confidence match ({max_sim:.2f}) for snippet '{current_snippet_text[:30]}...' with primary strategy. Trying fallback...")
            fallback_best_cat = None
            fallback_max_sim = -float('inf')
            for cat_name_key, cat_name_emb in CAT_NAME_EMBS.items():
                try:
                    similarity = cosine_similarity([emb], [cat_name_emb])[0][0]
                    if similarity > fallback_max_sim:
                        fallback_max_sim = similarity
                        fallback_best_cat = cat_name_key
                except Exception as e:
                    print(f"Error in fallback similarity for snippet '{current_snippet_text[:30]}...' with category name '{cat_name_key}': {e}")
                    continue
            
            if fallback_best_cat and fallback_max_sim > max_sim : # Only use fallback if it's better
                # print(f"Fallback match chosen: '{fallback_best_cat}' (sim: {fallback_max_sim:.2f})")
                best_cat = fallback_best_cat
            elif best_cat is None and fallback_best_cat: # If primary found nothing, use any fallback
                best_cat = fallback_best_cat


        if best_cat and best_cat in INV_BINARY_MAP:
            bits += INV_BINARY_MAP[best_cat]
        else:
            # If still no category or invalid category, this indicates a significant issue.
            # Append a default bit pattern (e.g., '00') to avoid crashing, but log the error.
            # This will likely lead to a corrupted message, but allows processing to continue.
            print(f"Critical Decoding Error: Could not map snippet '{current_snippet_text[:30]}...' to a valid category. Found '{best_cat}'. Appending '00'.")
            bits += '00' # Default/error bits

    # Split into 8-bit chunks (bytes)
    chars_binary = [bits[j:j+8] for j in range(0, len(bits), 8)]
    
    # Convert binary bytes to characters, only if they are complete 8-bit chunks
    msg = ''
    for b in chars_binary:
        if len(b) == 8:
            try:
                msg += chr(int(b, 2))
            except ValueError:
                print(f"Error converting binary byte to char: '{b}'")
                msg += '?' # Placeholder for corrupted byte
        # else:
            # Trailing bits that don't form a full byte are discarded.
            # This is expected if the original binary message length wasn't a multiple of 8.
            # The encoder pads to a multiple of 2 bits, so len(bits) should be even.
            # If len(bits) % 8 != 0, it means the original message's total bits was not a multiple of 8.
            # print(f"Discarding trailing bits: '{b}'")

    return msg