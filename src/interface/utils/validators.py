import re

def is_token_valid(token: str) -> bool:
    pattern = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}'
    return bool(re.match(pattern, token))

def is_guild_id_valid(guild_id: str) -> bool:
    return guild_id.isdigit() and len(guild_id) > 16 