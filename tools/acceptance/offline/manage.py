#!/usr/bin/env python3
"""Create and inspect isolated deployments from final offline ZIPs."""
import argparse
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.acceptance.offline import checks, environment

from tools.deployment import progress

ROOT = Path(__file__).resolve().parents[3]


def help_text(plain):
    def color(code, text):
        return text if plain else f'\033[{code}m{text}\033[0m'
    print('\n' + color('1;36', 'HappyRO offline acceptance') + '\n')
    print(color('1;33', 'Commands'))
    for command, description in [('start', 'Extract and start an isolated installation'),
                                 ('check', 'Verify bundle, services, HTTP and Luo An entering the game'),
                                 ('stop', 'Stop this batch, retaining data'),
                                 ('clean', 'Preview removal; --execute stops and removes only installation')]:
        print(color('1;32', f'  {command:8}') + description)
    print('\n' + color('1;33', 'Options'))
    print('  --version VERSION --batch NAME  Select one version and test batch')
    print('  --workspace PATH                Source workspace (default: this repository)')
    print('  start: --archive ZIP --gateway-port PORT --admin-port PORT')
    print('  check: --timeout SECONDS --browser-path PATH')
    print('  clean: --execute (without it, preview only)')
    print('  --no-color                      Disable terminal colors')
    print('\n' + color('1;33', 'Examples'))
    for command in ('start', 'check', 'stop', 'clean'):
        print(color('36', f'  python3 tools/acceptance/offline/manage.py {command} --version "$(cat deploy/docker/VERSION)" --batch smoke-1'))
    print('\nstart/check are explicit; packaging never starts acceptance automatically.\n')


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    plain = '--no-color' in argv
    argv = [arg for arg in argv if arg != '--no-color']
    if not argv or '--help' in argv or '-h' in argv:
        help_text(plain)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'check', 'stop', 'clean'):
        command = commands.add_parser(name)
        command.add_argument('--workspace', type=Path, default=ROOT)
        command.add_argument('--version', required=True)
        command.add_argument('--batch', required=True)
        if name == 'start':
            command.add_argument('--archive', type=Path)
            command.add_argument('--gateway-port', type=int)
            command.add_argument('--admin-port', type=int)
        if name == 'check':
            command.add_argument('--timeout', type=int, default=300)
            command.add_argument('--browser-path', type=Path)
        if name == 'clean':
            command.add_argument('--execute', action='store_true')
    progress.configure(no_color=plain)
    args = parser.parse_args(argv)
    batch = environment.Batch(args.workspace, args.version, args.batch)
    if args.command == 'start':
        archive = args.archive or batch.workspace / 'artifacts/releases' / batch.version / f'happyro-{batch.version}.zip'
        environment.start(batch, archive, args.gateway_port, args.admin_port)
    elif args.command == 'check':
        if not 1 <= args.timeout <= 3600:
            raise ValueError('Health wait timeout must be between 1 and 3600 seconds')
        checks.check(batch, args.timeout, args.browser_path)
    elif args.command == 'stop':
        environment.stop(batch)
    else:
        environment.clean(batch, args.execute)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        progress.message(str(error), 'failed')
        sys.exit(1)
