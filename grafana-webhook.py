#!/usr/bin/env python3

# SimpleGXWEBHOOK (Grafana webhook server for XMPP) v0.1
# Copyright (C) 2022 Ichthyx
# SPDX-License-Identifier: GPL-3.0-only
# See the file LICENSE for copying permission.

from __future__ import annotations

import logging
from getpass import getpass
from argparse import ArgumentParser
from time import sleep
import json
import os
import sys
import asyncio
import aiohttp, slixmpp
from aiohttp import web


async def handle_webhook(request):
    """
    https://grafana.com/docs/grafana/next/alerting/old-alerting/notifications/#webhook

    POST
    Example json body:

    {
    "dashboardId": 1,
    "evalMatches": [
        {
        "value": 1,
        "metric": "Count",
        "tags": {}
        }
    ],
    "imageUrl": "https://grafana.com/assets/img/blog/mixed_styles.png",
    "message": "Notification Message",
    "orgId": 1,
    "panelId": 2,
    "ruleId": 1,
    "ruleName": "Panel Title alert",
    "ruleUrl": "http://localhost:3000/d/hZ7BuVbWz/test-dashboard?fullscreen\u0026edit\u0026tab=alert\u0026panelId=2\u0026orgId=1",
    "state": "alerting",
    "tags": {
        "tag name": "tag value"
    },
    "title": "[Alerting] Panel Title alert"
    }

    """

    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        return web.json_response(
            {"message": "Incorrect data type sent to the server"}, status=400
        )

    message = f"{data['title']} - {data['message']} - {data['ruleUrl']}"  # TODO: message formating
    client.send_message(mto=args.recipient, mbody=message)
    return web.Response(text="")  # TODO: just return a empty 200 ?


async def presence_stanza(event):
    """
    Process the session_start event.

    Typical actions for the session_start event are
    requesting the roster and broadcasting an initial
    presence stanza.
    """
    client.send_presence()
    await client.get_roster()


async def reconnect_event(event):
    sleep(1)
    client.connect()


if __name__ == "__main__":
    # Setup the command line arguments.
    parser = ArgumentParser()
    parser.add_argument(
        "-q",
        "--quiet",
        help="set logging to ERROR",
        action="store_const",
        dest="loglevel",
        const=logging.ERROR,
        default=logging.INFO,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="set logging to DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid", help="bot JID to use")
    parser.add_argument("-p", "--password", dest="password", help="bot password to use")

    # Other options.
    parser.add_argument("-r", "--recipient", help="Recipient JID")
    parser.add_argument("-ap", "--port", help="port of http server")
    parser.add_argument("-a", "--bindaddress", help="bind address of http server")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel, format="%(levelname)-8s %(message)s")

    # Get args
    if args.jid is None:
        if os.environ.get("JID", None) is None:
            print("[!] You need to specify a JID address")
            sys.exit(1)
        else:
            args.jid = os.environ["JID"]
    if args.password is None:
        if os.environ.get("PASSWORD", None) is None:
            print("[!] You need to specify a PASSWORD for JID")
            sys.exit(1)
        else:
            args.password = os.environ["PASSWORD"]
    if args.recipient is None:
        if os.environ.get("RECIPIENT", None) is None:
            print("[!] You need to specify a recipient address")
            sys.exit(1)
        else:
            args.recipient = os.environ["RECIPIENT"]
    if args.port is None:
        if os.environ.get("PORT", None) is None:
            args.port = "8080"  # default port
        else:
            args.recipient = os.environ["PORT"]
    if args.bindaddress is None:
        if os.environ.get("BINDADDRESS", None) is None:
            args.bindaddress = "127.0.0.1"  # default addr
        else:
            args.recipient = os.environ["BINDADDRESS"]

    loop = asyncio.get_event_loop()
    http_app = aiohttp.web.Application(loop=loop)
    http_app.router.add_route(
        "POST", "/webhook", handle_webhook, expect_handler=aiohttp.web.Request.json
    )
    http_handler = http_app.make_handler()
    http_create_server = loop.create_server(http_handler, args.bindaddress, args.port)
    http_server = loop.run_until_complete(http_create_server)
    print(f"Listening for incoming webhooks on http://{args.bindaddress}:{args.port}/")

    client = slixmpp.ClientXMPP(args.jid, args.password)
    client.add_event_handler("session_start", presence_stanza)
    client.add_event_handler("disconnected", reconnect_event)
    client.register_plugin("xep_0030")  # Service Discovery
    client.register_plugin("xep_0199")  # XMPP Ping
    client.connect()
    client.process()
