
import os
import sys
import json
import optparse

from .volume import VMVolume, VolumeSet

ENV_PREFIX = 'VMAKEDK'
VERSION = '0.2.1'


def main():
    parser = optparse.OptionParser(
        usage=('%prog <command> [options]\n'
               '\n'
               'Commands:\n'
               ' open     Create disks and mount virtual filesystem\n'
               ' reopen   (re)Mount previously created disks\n'
               ' fstab    Output the fstab to stdout'),
        version=VERSION,
        conflict_handler='resolve',
    )

    parser.add_option(
        '-h', '--help',
        action='help',
        help='Print help text and exit')
    parser.add_option(
        '-v', '--version',
        action='version',
        help='Print version and exit')
    parser.add_option(
        '-d', '--dry-run',
        action='store_true', default=False,
        help='Only show commands that would have been executed')
    parser.add_option(
        '-t', '--store',
        dest='store',
        default=os.environ.get(ENV_PREFIX + 'STORE', None),
        help='Path to vmdk storage (or %sSTORE from env)' % (ENV_PREFIX,))
    parser.add_option(
        '-r', '--root',
        dest='root',
        default=os.environ.get(ENV_PREFIX + 'ROOT', None),
        help='Path to vm (ch)root (or %sROOT from env)' % (ENV_PREFIX,))
    parser.add_option(
        '-l', '--layout',
        dest='layout',
        default=os.environ.get(ENV_PREFIX + 'LAYOUT', None),
        help='Path to layout json (or %sLAYOUT from env)' % (ENV_PREFIX,))
    parser.add_option(
        '-c', '--create-type',
        dest='create_type',
        default=os.environ.get(ENV_PREFIX + 'CREATE_TYPE', 'monolithicFlat'),
        help='vmdk create_type (or %sCREATE_TYPE from env) Must be either'
             ' "monolithicFlat" or "vmfs"' % (ENV_PREFIX,))

    opts, args = parser.parse_args(sys.argv[1:])
    if not opts.store:
        parser.error('must provide a directory for vmdk storage')
    if not opts.root:
        parser.error('must provide a directory for vm root/sandbox')
    if not opts.layout:
        parser.error('must provide a file with the vm disk layout json')
    if not args:
        parser.error('must provide a command')
    if len(args) > 1:
        parser.error('too many commands')
    command = args[0]

    if opts.dry_run:
        patch_dry_run()

    with open(opts.layout, 'r') as fd:
        layout = json.load(fd)
    volume_set = VolumeSet(
        volumes=(VMVolume.from_dict(vol) for vol in layout['volumes'])
    )


    if command == 'open' or command == 'reopen':
        if command == 'open':
            volume_set.create_data(opts.store, opts.create_type)
        volume_set.loop_data(opts.store)
        if command == 'open':
            volume_set.mkfs()
        volume_set.mount(opts.root)

    elif command == 'fstab':
        print volume_set.fstab()
        sys.exit(0)

    else:
        parser.error('unknown command %s' % (command,))


"""
elif cmd=='close':
    volume_set.umount(SANDBOX)
    volume_set.unloop_data()
"""

def patch_dry_run():
    from .runner import DryRunner
    import volume
    import loopback
    loopback.Loopback.dry_run = True
    volume.runner = DryRunner()

