import datetime
import time

import pythonping

from src.util import pingutil
from src.util.get_param import get_param


def main():
    # Get parameters from user
    ping_kwargs = pingutil.get_ping_params()
    delay = get_param(
        pingutil.DEFAULT_DELAY,
        'Input the delay between each ping in milliseconds '
        f'(default: {pingutil.DEFAULT_DELAY}): ',
        int,
        'Invalid input (must be an integer and 100ms or above): ',
        verify_func=lambda x: x >= 100
    ) / 1000

    ping_coro = pingutil.ping_coroutine(**ping_kwargs)
    ping_count = 0
    ping_packets = ping_kwargs['count']

    print(f'Starting ping loop')

    while True:
        ping_count += 1
        time_now = datetime.datetime.now()

        # Display time
        print(time_now.strftime('%c'), f'#{ping_count:,}',
              end=': ', flush=True)

        # Ping
        results = next(ping_coro)

        if not isinstance(results, pythonping.executor.ResponseList):
            # Connection failure; end loop
            pingutil.print_ping_error(results)
            print('  Ending ping loop')
            return results

        # Interpret results
        if not results.success(option=pingutil.DEFAULT_SUCCESS_TOLERANCE):
            # Failed ping
            failures = [r for r in results if not r.success]
            failures, error = len(failures), failures[0].error_message
            print(f'\n  Failed ping: {failures}/{ping_packets} failed;', error)
        else:
            avg = '{:.2f}'.format(results.rtt_avg_ms)
            if ping_packets > 1:
                mini = '{:.2f}'.format(results.rtt_min_ms)
                maxi = '{:.2f}'.format(results.rtt_max_ms)
                print(f'PING: {mini}-{avg}-{maxi}')
            else:
                print(f'PING: {avg}')

        time.sleep(delay)
