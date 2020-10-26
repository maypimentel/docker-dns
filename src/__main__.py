#!/usr/bin/env python3

import sys
import os
from argparse import ArgumentParser, Action, ArgumentTypeError as Fatal

import config
import util

# COMMANDS
import tunnel
import show_domain
import status
import install
import uninstall


parser = ArgumentParser(
    prog=config.APP,
    usage="%(prog)s COMMAND [-t tag] [-n name] [-d tld] -h",
    fromfile_prefix_chars="@"
)

parser.add_argument(
    "COMMAND",
    choices=["install", "uninstall", "show-domain", "status", "tunnel"],
    default='status',
    # required=True,
    help="""
    command to be executed
    """
)

parser.add_argument(
    "-t", "--tag",
    default=config.DOCKER_CONTAINER_TAG,
    help="""
    tag of Docker container
    """
)

parser.add_argument(
    "-n", "--name",
    default=config.DOCKER_CONTAINER_NAME,
    help="""
    name of Docker container
    """
)

parser.add_argument(
    "-d", "--tld",
    default=config.TOP_LEVEL_DOMAIN,
    help="""
    domain that will be used when resolving containers name. Example, if you have an container running with name "memcached", it will be availble resolving "memcached.docker" if your TLD is "docker"
    """
)


def super_check():
    if not util.is_super_user():
        print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
        sys.exit(1)


def run():
    if not util.is_supported():
        print('Sorry, your OS is not supported.')
        if util.on_windows and not util.on_wsl:
            print('Please make sure you are running on a WSL2 shell.')
        return 1

    opt = parser.parse_args()

    try:
        if opt.COMMAND == 'show-domain':
            show_domain.main()

        elif opt.COMMAND == 'install':
            super_check()
            install.main(name=opt.name, tag=opt.tag, tld=opt.tld)

        elif opt.COMMAND == 'uninstall':
            super_check()
            uninstall.main()

        elif opt.COMMAND == 'tunnel':
            super_check()
            tunnel.connect()

        else:
            status.main()
        return 0

    except Fatal as e:
        print(f'fatal: {e}')
        return 1
    except KeyboardInterrupt:
        print('Keyboard interrupt: exiting.')
        return 1


if __name__ == '__main__':
    sys.exit(run())
