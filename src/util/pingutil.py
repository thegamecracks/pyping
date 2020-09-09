import socket

import pythonping

from .get_param import get_param

DEFAULT_PACKET_COUNT = 4  # Amount of ICMP packets
DEFAULT_PAYLOAD_SIZE = 32  # In bytes
DEFAULT_TARGET = 'www.google.ca'
DEFAULT_TIMEOUT = 2000   # In milliseconds
DEFAULT_DELAY = 5000  # Delay between pings in seconds
DEFAULT_SUCCESS_TOLERANCE = 3
# 1:   At least 1 packet must succeed
# 2: Majority of packets must succeed
# 3:         All packets must succeed


def get_ping_params():
    target_name = get_param(
        DEFAULT_TARGET,
        f'Input the target host to ping (default: {DEFAULT_TARGET}): ',
        str,
        'Invalid input: '
    )
    timeout = get_param(
        DEFAULT_TIMEOUT,
        f'Input the timeout in milliseconds (default: {DEFAULT_TIMEOUT}): ',
        int,
        'Invalid input (must be an integer and over 0ms): ',
        verify_func=lambda x: x > 0
    ) / 1000
    count = get_param(
        DEFAULT_PACKET_COUNT,
        'Input the amount of packets to send per ping '
        f'(default: {DEFAULT_PACKET_COUNT}): ',
        int,
        'Invalid input (must be a positive integer): ',
        verify_func=lambda x: x > 0
    )
    size = get_param(
        DEFAULT_PAYLOAD_SIZE,
        'Input the payload size for each ping in bytes '
        f'(default: {DEFAULT_PAYLOAD_SIZE}): ',
        int,
        'Invalid input (must be a positive integer): ',
        verify_func=lambda x: x > 0
    )
    print(f'Total ping size: {count * size:,} '
          f"byte{'s' if count * size > 1 else ''}")

    return {
        'target': target_name,
        'timeout': timeout,
        'count': count,
        'size': size
    }


def ping_target(target, timeout, count, size):
    """Ping a target and handle socket errors.

    Returns:
        pythonping.ResponseList
        socket.error
        RuntimeError

    """
    try:
        return pythonping.ping(
            target=target,
            timeout=timeout,
            count=count,
            size=size
        )
    except (RuntimeError, socket.error) as e:
        return e


def ping_coroutine(target, timeout, count, size):
    while True:
        yield ping_target(target, timeout, count, size)


def print_ping_error(e):
    if isinstance(e, (RuntimeError, socket.gaierror)):
        print('  Failed ping: could not access the internet')
    elif isinstance(e, socket.error):
        print('  Failed ping: unspecified error\n'
              f'  {e.__class__.__name__}: {e}')
