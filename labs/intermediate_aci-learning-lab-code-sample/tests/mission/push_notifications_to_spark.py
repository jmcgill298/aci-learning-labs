import requests
import argparse
from acitoolkit.acitoolkit import *

cli_args = argparse.ArgumentParser("Post to Spark", "Collects an Access Token to connect to Spark Chatroom")
cli_args.add_argument('-t', '--token', required=True,
                      help="The Access Token provided by https://developer.ciscospark.com/ after login.")

args = cli_args.parse_args()
TOKEN = "Bearer {}".format(vars(args)["token"])


def main():
    URL = "https://apic"
    LOGIN = "admin"
    PASSWORD = "password"

    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    subscribe_to_events(session)


def subscribe_to_events(session):
    Tenant.subscribe(session)
    AppProfile.subscribe(session)
    EPG.subscribe(session)

    while True:
        if Tenant.has_events(session):
            event = Tenant.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))

        elif AppProfile.has_events(session):
            event = AppProfile.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))

        elif EPG.has_events(session):
            event = EPG.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))


def post_message_to_spark(message):
    header = {"Authorization": TOKEN, "Content-Type": "application/json"}
    message_url = "https://api.ciscospark.com/v1/messages"
    room_id = "Y2lzY29zcGFyazovL3VzL1JPT00vYTA3NTA0MTAtMDM4MC0xMWU3LWE1MzAtNmY2YjY2ZDJhMjg4"

    request_body = {"roomId": room_id, "text": message}
    response = requests.post(message_url, json=request_body, headers=header)

    if not response.ok:
        print("FAILED TO SEND {} TO SPARK".format(message))


if __name__ == "__main__":
    main()
