import tiktoken
from config import DEFAULT_ENCODING

def count_tokens(text):
    """
    Count tokens in the provided text and return detailed token information
    
    Args:
        text (str): The text to analyze
        
    Returns:
        tuple: (token_count, token_details)
    """
    encoding = tiktoken.get_encoding(DEFAULT_ENCODING)
    tokens = encoding.encode(text)
    token_count = len(tokens)
    
    # Create a list to hold the token representations
    token_representations = []
    for token in tokens:
        # Decode each token individually to its text representation
        token_text = encoding.decode([token])
        token_representations.append({
            "token_id": int(token),
            "token_text": token_text
        })
    
    return token_count, token_representations