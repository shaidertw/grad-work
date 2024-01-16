from sqlalchemy import update, select

from src.db import Session
from src.user.models import User, Orgs
from src.user.schemas import User as UserSch

def get_username_list()->list:
    users_list = []
    error:str = ""
    try:
        session = Session()
        users = session.execute(
            select(User).order_by(User.id.desc())
        )
        for user in users:
            user = user[0]
            hash = None
            print(user.username, user.server_challenge)

            if user.username is None:
                continue
            elif user.domain is None:
                hash = user.username + "::" + user.hostname + ":" + user.server_challenge + \
                        ":" + user.ntproofstr + ":" + user.ntlm_response 
            else:
                hash = user.username + "::" + user.domain + ":" + user.server_challenge + \
                        ":" + user.ntproofstr + ":" + user.ntlm_response 

            org_name = session.query(Orgs.org_name).filter(Orgs.id == user.org_name_id).one()[0]

            if org_name is None:
                continue

            users_list.append(UserSch(
                id=user.id,
                username=user.username,
                source_ip=user.source_ip,
                org_name = org_name,
                ntlm_hash = hash
                )
            )

    except Exception as exc:
        error = str(exc)
    finally:
        session.close()

    if len(error) != 0:
        raise Exception(error)
    return users_list

def get_orgs_list()->list:
    orgs_list = []
    error:str = ""
    try:
        session = Session()
        orgs = session.execute(
            select(Orgs).order_by(Orgs.id.desc())
        )
        for org in orgs:
            org = org[0]
            #print(org.org_name)
            orgs_list.append(org)

    except Exception as exc:
        error = str(exc)
    finally:
        session.close()

    if len(error) != 0:
        raise Exception(error)
    return orgs_list


def get_orgs_hash(org_name:str) -> str:
    ''' Return all hashes and sources ip from database'''
    orgs_hash = ""
    error:str = ""
    try:
        session = Session()
        org_name_id = session.query(Orgs.id).filter(Orgs.org_name == org_name).first()

        if org_name_id is None:
            return ""

        org_name_id = org_name_id[0]
        users = session.query(User).filter(User.org_name_id == org_name_id)

        for user in users:
            hash = None
            if user.username is None:
                continue
            elif user.domain is None:
                hash = user.username + "::" + user.hostname + ":" + user.server_challenge + \
                        ":" + user.ntproofstr + ":" + user.ntlm_response
            else:
                hash = user.username + "::" + user.domain + ":" + user.server_challenge + \
                         ":" + user.ntproofstr + ":" + user.ntlm_response
            orgs_hash = orgs_hash + "source ip: " + user.source_ip + " " + hash + " " + "\n"
    except Exception as exc:
        error = str(exc)
    finally:
        session.close()
    if len(error) != 0:
        raise Exception(error)
    elif len(orgs_hash) == 0:
        return "Hashes weren't found!".split("\n")

    return orgs_hash.split('\n')

def get_users(offset, limit)->list:
    users_list = []
    error:str = ""
    try:
        session = Session()
        users = session.execute(
            select(User).order_by(User.id.desc()).offset(offset).limit(limit)
        )
        for user in users:
            user = user[0]
            hash = None
            if user.domain is None:
                hash = user.username + "::" + user.hostname + ":" + user.server_challenge + \
                        ":" + user.ntproofstr + ":" + user.ntlm_response 
            else:
                hash = user.username + "::" + user.domain + ":" + user.server_challenge + \
                        ":" + user.ntproofstr + ":" + user.ntlm_response 

            users_list.append(UserSch(
                id=user.id,
                username=user.username,
                source_ip=user.source_ip,
                org_name = str(user.path),
                ntlm_hash = hash
                )
            )
    except Exception as exc:
        error = str(exc)
    finally:
        session.close()

    if len(error) != 0:
        raise Exception(error)
    return users_list


def delete_hashes_by_org_name(org_name) -> bool:
    error:str = ""
    try:
        session = Session()
        org_name_id = session.query(Orgs.id).filter(Orgs.org_name == org_name).one()[0]
        if org_name_id is None:
            return False

        session.query(User).filter_by(org_name_id=org_name_id).delete()
        session.commit()

    except Exception as exc:
        error = str(exc)
    finally:
        session.close()

    if len(error) != 0:
        raise Exception(error)
    return True
