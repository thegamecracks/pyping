import datetime
import time

import pythonping

from src.util import pingutil
from src.util.get_param import get_param

__copyright__ = """
MIT License

Copyright (c) 2020 thegamecracks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def get_ping_params():
    target_name = get_param(
        pingutil.DEFAULT_TARGET,
        'Input the target host to ping '
        f'(default: {pingutil.DEFAULT_TARGET}): ',
        str,
        'Invalid input: '
    )
    timeout = get_param(
        pingutil.DEFAULT_TIMEOUT,
        'Input the timeout in milliseconds '
        f'(default: {pingutil.DEFAULT_TIMEOUT}): ',
        int,
        'Invalid input (must be an integer and over 0ms): ',
        verify_func=lambda x: x > 0
    )
    count = get_param(
        pingutil.DEFAULT_PACKET_COUNT,
        'Input the amount of packets to send per ping '
        f'(default: {pingutil.DEFAULT_PACKET_COUNT}): ',
        int,
        'Invalid input (must be a positive integer): ',
        verify_func=lambda x: x > 0
    )
    size = get_param(
        pingutil.DEFAULT_PAYLOAD_SIZE,
        'Input the payload size for each ping in bytes '
        f'(default: {pingutil.DEFAULT_PAYLOAD_SIZE}): ',
        int,
        'Invalid input (must be a positive integer): ',
        verify_func=lambda x: x > 0
    )
    print(f'Total ping size: {count * size:,} '
          f"byte{'s' if count * size > 1 else ''}")
    delay = get_param(
        pingutil.DEFAULT_DELAY,
        'Input the delay between each ping in milliseconds '
        f'(default: {pingutil.DEFAULT_DELAY}): ',
        int,
        'Invalid input (must be an integer and 100ms or above): ',
        verify_func=lambda x: x >= 100
    )
    message_timeout = get_param(
        timeout,
        'Input the minimum latency for pings to be displayed '
        '(defaults to the timeout duration): ',
        int,
        'Invalid input (must be an integer over 0ms and less than timeout '
        f'({timeout}ms)): ',
        verify_func=lambda x: 0 < x < timeout
    )

    timeout /= 1000
    delay /= 1000
    message_timeout /= 1000

    return {
        'target': target_name,
        'timeout': timeout,
        'count': count,
        'size': size
    }, delay, message_timeout

    
def main():
    # Get parameters from user
    ping_kwargs, delay, message_timeout = get_ping_params()

    ping_coro = pingutil.ping_coroutine(**ping_kwargs)
    ping_count = 0
    ping_count_since_displayed = 0
    ping_packets = ping_kwargs['count']
    has_displayed_ping = False

    print(f'Starting ping loop')

    while True:
        ping_count += 1
        ping_count_since_displayed += 1
        time_now = datetime.datetime.now()

        # Ping
        results = next(ping_coro)

        if not isinstance(results, pythonping.executor.ResponseList):
            # Connection failure; end loop
            print()
            pingutil.print_ping_error(results)
            print('  Ending ping loop')
            return results

        # Interpret results
        failures, over_timeouts = [], []
        for r in results:
            if not r.success:
                failures.append(r)
            elif r.time_elapsed >= message_timeout:
                over_timeouts.append(r)

        if not failures and not over_timeouts:
            # No failures or pings over message_timeout
            has_displayed_ping = True
            print(f'\r{ping_count_since_displayed:,} '
                  f"ping{'s' if ping_count_since_displayed != 1 else ''} "
                  f'({ping_count:,} total)', end='')
        else:
            ping_count_since_displayed = 0
            if has_displayed_ping:
                has_displayed_ping = False
                print()
            print(time_now.strftime('%c'), f'#{ping_count:,}', end=': ')
            messages = []
            if failures:
                error = failures[0].error_message
                messages.append(
                    f'{len(failures)}/{ping_packets} failed; {error}')
            if over_timeouts:
                if not failures and len(over_timeouts) == 1:
                    ping = over_timeouts[0].time_elapsed_ms
                    messages.append(f'{ping:.2f}ms')
                else:
                    timeout_count = len(over_timeouts)
                    timeout_avg = sum(r.time_elapsed_ms
                                      for r in over_timeouts) / timeout_count
                    messages.append(f'{timeout_count}/{ping_packets} '
                                    f'averaged {timeout_avg:.2f}ms')
            if len(messages) == 1:
                print(messages[0])
            else:
                print()
                for s in messages:
                    print(' ', s)

        time.sleep(delay)
