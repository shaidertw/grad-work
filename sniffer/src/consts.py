SMB_SIG        = b'\xfe\x53\x4d\x42\x40'                                # SMB    
NTLMSSP_SIG    = b'\x4e\x54\x4c\x4d\x53\x53\x50\x00'	                # NTLMSSP\x00
NTLMSSP_TYPE_1 = NTLMSSP_SIG + b'\x01\x00\x00\x00'                      # NTLMSSP\x00 0x01000000
NTLMSSP_TYPE_2 = NTLMSSP_SIG + b'\x02\x00\x00\x00'                      # NTLMSSP\x00 0x02000000
NTLMSSP_TYPE_3 = NTLMSSP_SIG + b'\x03\x00\x00\x00'                      # NTLMSSP\x00 0x03000000

IOCTL_COMMAND = b'\x0b\x00'
IOCTL_REQUEST= 0x0 
# FSCTL_DFS_GET_REFERRALS
IOCTL_FUNC= 0x00060194


NBSS_SIG = b'\x16\x03\x01'
