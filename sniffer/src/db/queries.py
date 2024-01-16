
from db.db import Session
from db.models import User, Orgs, Source_ips


def get_id_by_session_id(session_id):
    try:
        user_id = None
        session = Session()
        user_id = session.query(User.id).filter(User.session_id == session_id).one()[0]
    except:
        pass
    finally:
        session.close()
    return user_id

def update_user(user:User):
    try:

        session = Session()
        user_id = get_id_by_session_id(user.session_id)
        if user_id is None:
            return

        session.query(User).filter(User.id==user_id).update({
            "username":user.username,
            "hostname":user.hostname,
            "domain":user.domain,
            "source_ip":user.source_ip,
            "session_id":user.session_id,
            "ntproofstr":user.ntproofstr,
            "ntlm_response":user.ntlm_response

        })
        session.commit()

    except Exception as exc:
        print("Excepiton: " + str(exc))
        session.rollback()
    finally:
        session.close()


def add_packet(user:User):
    try:
        session = Session()
        session.add(user)
        session.commit()
    except Exception as exc:
        print("Excepiton: " + str(exc))
        session.rollback()
    finally:
        session.close()

def add_path(session_id, md5_org_name):
    try:
        session = Session()
        user_id = get_id_by_session_id(session_id)

        if user_id is None:
            return

        org_name_id = session.query(Orgs.id).filter(Orgs.md5_org_name == md5_org_name).one()[0]

        session.query(User).filter(User.id==user_id).update({
            "org_name_id":org_name_id
        })
        session.commit()

    except Exception as exc:
        print("Excepiton: " + str(exc))
        session.rollback()
    finally:
        session.close()

def add_ip_addr(source_ip: Source_ips):
    try:
        session = Session()
        session.add(source_ip)
        session.commit()
    except Exception as exc:
        print("Excepiton: " + str(exc))
        session.rollback()
    finally:
        session.close()

