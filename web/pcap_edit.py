from scapy.all import rdpcap, wrpcap, Packet, NoPayload
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from scapy.utils import PcapWriter
import pyshark
from pyshark.tshark import tshark
import datetime
import time

"""
Meant to sanitize and change dates in pcapng file (using sslkeylog, works with tls1.3 and 1.2 well)
"""
ip_map = {
    "192.168.0.9": "10.0.0.100",
    # add more mappings as needed
}

mac_map = { #original mac : new mac
    "XX:XX:XX:XX:XX:XX": "de:ad:be:ef:de:ad",
    "YY:YY:YY:YY:YY:YY":  "ca:fe:ba:be:00:00",
    # add more mappings as needed
}

def main():
    """
    provide an initial capture file and initial kelog file, then you get the output after it processes
    """
    process_packets("capture.pcapng", "keylog.log", "output_final.pcapng")

def process_packets(input_pcap,ssl_keylog_file, output_pcap):
    # Decrypt SSL traffic with pyshark
    cap = pyshark.FileCapture(input_pcap, 
                              override_prefs={'tls.keylog_file': ssl_keylog_file}, 
                              use_json=True, include_raw=True, debug=True)
    # you can add display_filter as an argument to cut down even further, but I did that in wireshark already
    # original filter was this: ((ip.dst == 255.255.255.0) or (ip.src == 255.255.255.0)) or (dns or ocsp) or (tcp.stream eq 19)  and !(quic or igmp or udp)
    writer = PcapWriter(output_pcap, append=True, sync=True)
    
    for pkt in cap:
        try:
            # Convert pyshark packet back to scapy
            scapy_pkt = Ether(pkt.get_raw_packet())

            # Adjust timestamp and sanitize MAC addresses
            adjust_year(scapy_pkt)
            sanitize_addr(scapy_pkt)

            # Write modified packet to output file
            writer.write(scapy_pkt)
        except Exception as e:
            print(f"Failed to process packet: {e}")

    cap.close()
    writer.close()
    
def sanitize_addr(pkt):
    if Ether in pkt: #MAC
        if pkt[Ether].src in mac_map:
            pkt[Ether].src = mac_map[pkt[Ether].src]
        if pkt[Ether].dst in mac_map:
            pkt[Ether].dst = mac_map[pkt[Ether].dst]
            
    if IP in pkt: #IPV4
        if pkt[IP].src in ip_map:
            pkt[IP].src = ip_map[pkt[IP].src]
        if pkt[IP].dst in ip_map:
            pkt[IP].dst = ip_map[pkt[IP].dst]
    
def adjust_year(pkt):
    if pkt.time:
        # Convert to datetime
        ts = datetime.datetime.fromtimestamp(pkt.time)
        # Change year from 2024 to 2029 (for the sake of the CTF)
        if ts.year == 2024:
            ts = ts.replace(year=2029)
            pkt.time = time.mktime(ts.timetuple()) + ts.microsecond / 1E6   # Convert back to Unix time
            
if __name__ == "__main__":
    main()