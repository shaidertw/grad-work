from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship

from db.db import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("session_id_index", "session_id"),
    )

    id = Column("id", Integer, primary_key=True)
    username = Column("username", String)
    hostname = Column("hostname", String)
    domain = Column("domain", String)
    source_ip = Column("source_ip", String)
    session_id = Column("session_id", String)
    server_challenge = Column("server_challenge", String)
    org_name_id = Column(ForeignKey("orgs.id"))
    ntproofstr = Column("ntproofstr", String)
    ntlm_response = Column("ntlm_response", String)

    orgs = relationship("Orgs")
    
    def __init__(self, username=None, hostname=None, domain=None, source_ip=None, session_id=None, server_challenge=None, org_name=None, ntproofstr=None, ntlm_response=None):
        self.username = username
        self.hostname = hostname
        self.domain = domain
        self.source_ip = source_ip
        self.session_id = session_id
        self.server_challenge = server_challenge
        self.org_name = org_name
        self.ntproofstr = ntproofstr 
        self.ntlm_response = ntlm_response 

class Orgs(Base):
    __tablename__ = "orgs"
    
    id = Column("id", Integer, primary_key=True)
    org_name = Column("org_name", String, unique=True)
    md5_org_name = Column("md5_org_name", String)

    def __init__(self, org_name=None, md5_org_name=None):
        self.org_name = org_name
        self.md5_org_name = md5_org_name

class Source_ips(Base):
    __tablename__ = "source_ips"
    
    id = Column("id", Integer, primary_key=True)
    source_ip = Column("source_ip", String)
    date = Column("time", String)

    def __init__(self, source_ip=None, date=None):
        self.source_ip = source_ip
        self.date = date
        
