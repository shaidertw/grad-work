from datetime import datetime

from db.models import User, Source_ips
from db import queries

def add_packet(username=None, hostname=None, domain=None, source_ip=None, session_id=None,\
        server_challenge=None, ntproofstr=None, ntlm_response=None):

    user = User(username=username, hostname=hostname, domain=domain, source_ip=source_ip, session_id=session_id,\
        server_challenge=server_challenge, ntproofstr=ntproofstr, ntlm_response=ntlm_response)

    # add md5_org_name
    if md5_org_name is not None:
        queries.add_md5_org_name(session_id, md5_org_name)
    # add server challenge
    elif username is None:
        queries.add_packet(user)
    # auth
    else:
        queries.update_user(user)

def add_path_packet(session_id, md5_org_name):
    queries.add_path(session_id, md5_org_name)

def add_auth_packet(username=None, hostname=None, domain=None, source_ip=None, session_id=None,\
        ntproofstr=None, ntlm_response=None):

    user = User(username=username, hostname=hostname, domain=domain, source_ip=source_ip, session_id=session_id,\
        ntproofstr=ntproofstr, ntlm_response=ntlm_response)

    queries.update_user(user)

def add_challenge_packet(server_challenge=None, session_id=None):

    user = User(session_id=session_id, server_challenge=server_challenge)

    queries.add_packet(user)


def add_source_ip(source_ip):

    now = datetime.now()
    current_time = now.strftime('%Y-%m-%dT%H:%M:%S')
    source_ip = Source_ips(source_ip=source_ip, date=current_time)
    queries.add_ip_addr(source_ip)

