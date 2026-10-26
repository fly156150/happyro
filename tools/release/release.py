#!/usr/bin/env python3
"""Source-side release commands; deployment commands live in tools/deployment."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.release import images, package, publish, workflow, split
from tools.release.lifecycle import Layout, clean, require_managed_lock, version_lock
import os

from tools.deployment import progress

ROOT = Path(__file__).resolve().parents[2]


def print_help(command, plain):
    def color(code, text):
        return text if plain else f'\033[{code}m{text}\033[0m'
    descriptions = {
        'run': 'Build a new offline package in a managed version directory',
        'rebuild': 'Clean this version including its ZIP, then fully rebuild',
        'split': 'Split a verified managed ZIP, with merge instructions in both archives',
        'clean': 'Preview or remove registered local version outputs',
        'prepare': 'Prepare resources and offline deployment files',
        'build': 'Build all five multi-platform images without cache',
        'package': 'Verify and assemble the complete offline ZIP',
        'push': 'Publish the verified batch and check both remote tags',
    }
    title = 'HappyRO release tools' + (f' / {command}' if command else '')
    print('\n' + color('1;36', title) + '\n')
    print(color('1;33', 'Usage'))
    print('  python3 tools/release/release.py ' + color('1;32', command or '<command>') + ' [options]')
    if command:
        print('\n' + color('1;33', 'Options'))
        print('  --workspace PATH  Source workspace (default: this repository)')
        if command in ('run', 'rebuild', 'clean', 'split'):
            required = 'required' if command != 'run' else 'default: deploy/docker/VERSION'
            print(f'  --version VERSION Target version ({required})')
            if command in ('run', 'rebuild'):
                print('  --split           Also create resources and images ZIPs with merge instructions')
                print('  --push            Explicitly publish to Docker Hub and update latest after packaging')
            if command == 'clean':
                print('  --execute         Perform cleanup; otherwise preview only')
                print('  --include-package Also remove full/split ZIPs and split report (logs remain)')
            elif command == 'rebuild':
                print('  Automatically deletes this version’s local ZIP and intermediate outputs.')
        elif command in ('prepare', 'build'):
            kind = 'deployment' if command == 'prepare' else 'images'
            print(f'  --output PATH     New output directory (default: artifacts/{kind}/release)')
        else:
            print('  --images PATH     OCI batch directory (default: artifacts/images/release)')
            print('  --bundle PATH     Offline bundle directory (default: artifacts/deployment/release)')
        if command == 'push':
            print('  --evidence PATH   New verification directory (default: work/dockerhub/<UTC batch>)')
        print('  --no-color        Disable ANSI colors')
        print('  -h, --help        Show this help without executing the phase')
    else:
        print('\n' + color('1;33', 'Commands'))
        for name, description in descriptions.items():
            print('  ' + color('1;32', name.ljust(10)) + description)
    print('\n' + color('1;33', 'Examples'))
    for name in ([command] if command else descriptions):
        example = name + (' --version "$(cat deploy/docker/VERSION)"' if name in ('rebuild', 'clean', 'split') else '')
        print(color('36', f'  python3 tools/release/release.py {example}'))
    if command:
        print(color('36', f'  python3 tools/release/release.py {command} --help --no-color'))
    print('\nNo Docker Hub push by default. Use --push with run/rebuild, or the push command.\n')


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    plain = '--no-color' in argv
    argv = [arg for arg in argv if arg != '--no-color']
    command_names = ('run', 'rebuild', 'clean', 'split', 'prepare', 'build', 'package', 'push')
    if not argv or argv in (['--help'], ['-h']):
        print_help(None, plain)
        return
    if argv[0] in command_names and any(arg in ('--help', '-h') for arg in argv[1:]):
        print_help(argv[0], plain)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in command_names:
        command = commands.add_parser(name)
        command.add_argument('--workspace', type=Path, default=ROOT)
        if name in ('run', 'rebuild', 'clean', 'split'):
            command.add_argument('--version', required=name != 'run')
            if name in ('run', 'rebuild'):
                command.add_argument('--split', action='store_true')
                command.add_argument('--push', action='store_true')
            if name == 'clean':
                command.add_argument('--execute', action='store_true')
                command.add_argument('--include-package', action='store_true')
        elif name in ('prepare', 'build'):
            command.add_argument('--output', type=Path)
        else:
            command.add_argument('--images', type=Path)
            command.add_argument('--bundle', type=Path)
        if name == 'push':
            command.add_argument('--evidence', type=Path)
    progress.configure(no_color=plain)
    args = parser.parse_args(argv)
    args.workspace = args.workspace.resolve()
    if args.command == 'split':
        return split.split(args)
    if args.command == 'clean':
        return clean(args)
    if args.command in ('run', 'rebuild'):
        return workflow.execute(args, rebuild=args.command == 'rebuild')
    if args.command in ('prepare', 'build'):
        kind = 'deployment' if args.command == 'prepare' else 'images'
        args.output = args.output or args.workspace / 'artifacts' / kind / 'release'
    else:
        args.images = args.images or args.workspace / 'artifacts/images/release'
        args.bundle = args.bundle or args.workspace / 'artifacts/deployment/release'
        args.output = args.images
    if args.command == 'push':
        batch = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        args.evidence = args.evidence or args.workspace / 'work/dockerhub' / batch
    # Advanced phase outputs are not implicitly adopted for deletion. Managed
    # writes come only from the locked workflow; publishing acquires that lock.
    paths = [args.output] if args.command in ('prepare', 'build') else [args.images, args.bundle]
    if args.command == 'push':
        base = args.workspace / 'artifacts/releases'
        managed = [Path(os.path.abspath(path)).relative_to(base) for path in paths
                   if Path(os.path.abspath(path)).is_relative_to(base)]
        if managed:
            if len(managed) != 2 or any(len(p.parts) != 2 for p in managed) or managed[0].parts[0] != managed[1].parts[0]:
                raise ValueError('Publish images and bundle must belong to the same managed version')
            layout = Layout(args.workspace, managed[0].parts[0])
            if [Path(os.path.abspath(p)) for p in paths] != [layout.images, layout.bundle]:
                raise ValueError('Use the registered images/ and bundle/ paths')
            with version_lock(layout) as descriptor:
                args.lock_fd = descriptor
                return publish.publish(args)
    for path in paths:
        require_managed_lock(args.workspace, path)
    return {'prepare': package.prepare, 'build': images.build,
            'package': images.package, 'push': publish.publish}[args.command](args)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        progress.message(str(error), 'failed')
        sys.exit(1)
