from mcrcon import MCRcon
import logging

def whitelist(username):
    with MCRcon("localhost:25565", "") as mcr:
        resp = mcr.command(f"/whitelist add {username}")
        logging.info(resp)
