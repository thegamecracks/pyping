import src.modes as ping_modes
from src.util import pingutil
from src.util.get_param import get_param


def main():
    modes = {
        'standard': ping_modes.standard,
        'high filter': ping_modes.highfilter
    }
    print('Modes:', '\n'.join([m.title() for m in modes]), sep='\n')
    mode = modes.get(input('Select a mode to use: ').lower().strip())
    while mode is None:
        mode = modes.get(input('Unknown mode: ').lower().strip())

    mode.main()


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('Ping loop interrupted')
        except Exception as e:
            print('===== Fatal Error =====')
            print(f'{e.__class__.__name__}: {e}')
            input('Press Enter to close ')
            break
        input('Press Enter to restart program ')
