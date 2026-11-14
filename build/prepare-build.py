#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Nick Foy
"""Fetch checksum-pinned upstream recipes and apply reviewed J514M deltas.

This prepares files only. It never runs makepkg or installs packages.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent


def checked(data, expected, label):
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('SHA256 mismatch: ' + label)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', choices=['all', 'linux-aurora', 'm1n1-aurora'], default='all')
    parser.add_argument('--output', type=pathlib.Path, help='new directory outside this checkout')
    parser.add_argument('--check-only', action='store_true', help='verify remote inputs and preparation in a temporary directory; leave no build tree')
    args = parser.parse_args()
    if not args.check_only and args.output is None:
        parser.error('--output is required unless --check-only is selected')
    if args.output is not None:
        output = args.output.resolve()
        if output == ROOT or ROOT in output.parents:
            parser.error('output must be outside the checkout (upstream logos are downloaded there)')
        if output.exists():
            parser.error('output directory must not exist')
    lock = json.loads((ROOT / 'build/sources.lock.json').read_text())
    with tempfile.TemporaryDirectory(prefix='j514m-prepare-') as temp:
        staging = pathlib.Path(temp)
        for name, item in lock.items():
            if args.package not in ('all', name):
                continue
            target = staging / name
            target.mkdir()
            for filename, spec in item['files'].items():
                with urllib.request.urlopen(spec['url'], timeout=60) as response:
                    data = checked(response.read(), spec['sha256'], spec['url'])
                (target / filename).write_bytes(data)
                (target / filename).chmod(int(spec['mode'], 8))
            for key in ['source_patch', 'recipe_patch']:
                patch = checked((ROOT / 'patches' / item[key]).read_bytes(), item[key + '_sha256'], item[key])
                if key == 'source_patch':
                    (target / item[key]).write_bytes(patch)
                else:
                    subprocess.run(['patch', '--batch', '--fuzz=0', '-p1'], input=patch, cwd=target, check=True, stdout=subprocess.PIPE)
            if name == 'm1n1-aurora':
                shutil.copyfile(ROOT / 'build/m1n1-build-qualification.json', target / 'build-qualification.json')
            checked((target / 'PKGBUILD').read_bytes(), item['prepared_pkgbuild_sha256'], name + '/PKGBUILD')
            subprocess.run(['bash', '-n', str(target / 'PKGBUILD')], check=True)
            print(name + ': pinned upstream inputs and prepared recipe verified')
        if not args.check_only:
            shutil.copytree(staging, output)
            print('Prepared: ' + str(output))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
