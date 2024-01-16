#import uvicorn
from time import sleep
from scapy.all import *

# local files for parser
from sniff.sniff import handle_ntlm_packet
from db.db import create_table, engine


if __name__ == "__main__":
    print("Start sniff...")

    create_table(engine)
#    sniffer = AsyncSniffer(prn=handle_ntlm_packet, filter="tcp port 445 or tcp port 139", store=False) 
#    sniffer.start()
#    sleep(999999)
#    sniffer.stop()

    #create_table(engine)

    sniff(prn=handle_ntlm_packet, filter="tcp port 445 or tcp port 139", store=False) 

