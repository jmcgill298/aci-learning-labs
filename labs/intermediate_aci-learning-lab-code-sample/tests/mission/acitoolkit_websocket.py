#!/usr/bin/env python
from acitoolkit.acitoolkit import *

def main():
    URL = "https://apic"
    LOGIN = "admin"
    PASSWORD = "password"

    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    subscribe_to_events()


def subscribe_to_events():
    Tenant.subscribe(session)
    AppProfile.subscribe(session)
    
    while True:
        if Tenant.has_events(session):
            event = Tenant.get_event(session)

            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            print("\n{} {}".format(event.dn, status))

        elif AppProfile.has_events(session):
            event = AppProfile.get_event(session)

            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            print("\n{} {}".format(event.dn, status))


if __name__ == '__main__':
    main()