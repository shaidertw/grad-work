from scapy.all import *
from io import BytesIO

from parser.parser import parser, parser_deanon

def handle_ntlm_packet(packet):
    tcp_payload_bytes= bytes(packet[TCP].payload)
    #print(tcp_payload_bytes)
    if re.search(b'\\xfeSMB', tcp_payload_bytes) is not None:
        parser(bytes(packet))
    elif re.search(b'\\x16\\x03\\x01', tcp_payload_bytes) is not None or re.search(b'\\x47\\x45\\x54', tcp_payload_bytes) is not None:
        print("deanon")
        parser_deanon(bytes(packet))
