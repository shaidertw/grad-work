
from parser import service
from consts import *

def get_source_ip(raw_internet_packet: bytes):
    ip = raw_internet_packet[12:][:4]
    #dst_ip = raw_internet_packet[16:][:4]
    return '.'.join(map(str, ip))

def decode_string(byte_string: bytes):
    return byte_string.decode('UTF-8').replace('\x00', '')

# The decode_int() function was taken from: 
# https://github.com/b17zr/ntlm_challenger
def decode_int(byte_string: bytes):
    return int.from_bytes(byte_string, 'little')

users_list = []

def print_users():
    for user in users_list:
        user.print()

def get_index_user_by_session_id(session_id:str) -> int:
    for index in range(0, len(users_list)):
        if session_id == users_list[index].session_id:
            return index
    return None


def parse_ntlmssp(data:bytes) -> bool:
    server_challenge = None
    # NTLMSSP message signatures

    offset = data.find(NTLMSSP_SIG)

    if offset == -1:
        return False
    
    current_NTLMSSP_TYPE = data[offset:][:len(NTLMSSP_TYPE_1)]
    if current_NTLMSSP_TYPE == NTLMSSP_TYPE_1:
        print("NTLMSSP Message Type 1: Negotiation")
    elif current_NTLMSSP_TYPE == NTLMSSP_TYPE_2:
        print("NTLMSSP Message Type 2: Challenge")
        session_id = data[(offset - 0x3F):][:0x8].hex()

        server_challenge_offset = offset + 0x18
        server_challenge = data[server_challenge_offset:][:0x8].hex()

        service.add_challenge_packet(session_id=session_id, server_challenge=server_challenge)
    elif current_NTLMSSP_TYPE == NTLMSSP_TYPE_3:
        print("NTLMSSP Message Type 3: Authentication")

        ip = get_source_ip(data[offset - 0xA7 + 0xE:][:0x14])
        print(f"Source ip: {ip}")

        domain_length_offset = offset + 0x1C
        domain_length = decode_int(data[domain_length_offset:][:0x2])
        domain_offset_offset = offset + 0x20
        domain_offset = decode_int(data[domain_offset_offset:][:0x4]) + offset
        domain = decode_string(data[domain_offset:][:domain_length])
        #print(f"Domain: {domain}")

        username_length_offset = offset + 0x24
        username_length = decode_int(data[username_length_offset:][:0x2])
        username_offset_offset = offset + 0x28
        username_offset = decode_int(data[username_offset_offset:][:0x4]) + offset
        username = decode_string(data[username_offset:][:username_length])
        #print(f"Username: {username}")

        workstation_length_offset = offset + 0x2C
        workstation_length = decode_int(data[workstation_length_offset:][:0x2])
        workstation_offset_offset = offset + 0x30
        workstation_offset = decode_int(data[workstation_offset_offset:][:0x4]) + offset
        workstation = decode_string(data[workstation_offset:][:workstation_length])
        #print(f"Host name: {workstation}")

        session_id = data[(offset - 0x45):][:0x8].hex()

        ntlm_lenght_offset = offset + 0x14
        ntlm_lenght = decode_int(data[ntlm_lenght_offset:][:0x2])

        ntlm_offset_offset =  offset + 0x18
        ntlm_offset = decode_int(data[ntlm_offset_offset:][:0x4])

        ntproofstr = data[offset + ntlm_offset:][:0x10].hex()
        ntlm_response = data[offset + ntlm_offset + 0x10:][:ntlm_lenght-0x10].hex()

        service.add_auth_packet(username=username, hostname=workstation, domain=domain, source_ip=ip, session_id=session_id, ntproofstr=ntproofstr, ntlm_response=ntlm_response)
        return True

def parse_smb(data:bytes) -> bool:
    
    offset = data.find(SMB_SIG)
    
    if offset == -1:
        return False

    # smb2 and smb2.cmd == 11 and smb2.flags.response == 0
    command = data[offset+0xC:][:0x2]
    if command != IOCTL_COMMAND:
        return False

    flags = decode_int(data[offset+0x10:][:0x4])
    if ((flags & ( 1 << 0 )) >> 0) != IOCTL_REQUEST:
        return False

    ioctl_func_current = decode_int(data[offset + 0x44:][:0x4])
    if ioctl_func_current != IOCTL_FUNC:
        return False

    session_id = data[offset + 0x28:][:0x8].hex()
    path_offset = decode_int(data[offset + 0x58:][:0x4])
    path_size = decode_int(data[offset + 0x5C:][:0x4])
    path = decode_string(data[offset+path_offset:][:path_size])
    print(path)
    print(len(path))
    path = path[path.rfind("\\") + 1 : ]
    service.add_path_packet(session_id=session_id, md5_org_name=path)
    return True

def parser(raw_bytes):
    if not parse_ntlmssp(raw_bytes):
        parse_smb(raw_bytes)

def parser_deanon(raw_bytes: bytes):
    offset_nbss = raw_bytes.find(NBSS_SIG)
    ip = get_source_ip(raw_bytes[offset_nbss - 0x36 + 0xE:][:0x14])
    service.add_source_ip(ip)

