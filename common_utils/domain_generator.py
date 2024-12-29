from itertools import product
import string

def generate_domains(suffix, max_len):
    if suffix.startswith('.'):
        suffix = suffix[1:]
    chars = string.ascii_lowercase + string.digits
    return [f"{''.join(combo)}.{suffix}" for length in range(1, max_len + 1) for combo in product(chars, repeat=length)]
