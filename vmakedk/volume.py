
import os
from itertools import chain

from .vmdk import make_vmdk
from .runner import RealRunner
from .loopback import Loopback, LoopNotFound
from .procmount import ProcMounts
from .vfstree import  VfsTree


runner = RealRunner()


class VolumeSet(object):

    def __init__(self, volumes=None):
        self.itree = VfsTree()
        self.nontree = []
        if volumes:
            for vol in volumes:
                self.add(vol)

    def add(self, vol):
        nodes, vol = vol.tree_ref()
        if nodes:
            self.itree.follow_and_set(nodes, vol)
        else:
            self.nontree.append(vol)

    def detect(self, store, sandbox):
        for vol in self.itree.sorted():
            vol.detect(store, sandbox)
            if vol.loop:
                print 'existing volume found on', vol.loop, ', ', 'mounted' if vol.up else 'not mounted'

    def fstab(self):
        node_entries = (vol.fstab_entry() for vol in self.itree.sorted() if vol.include_in_fstab)
        none_entries = (vol.fstab_entry() for vol in self.nontree if vol.include_in_fstab)
        all_entries = chain(node_entries, none_entries)
        return "\n".join(all_entries)

    def create_data(self, store, create_type):
        for vol in chain(self.itree.sorted(), self.nontree):
            vol.create_data(store)
            vol.create_vmdk(store, create_type)

    def loop_data(self, store):
        for vol in chain(self.itree.sorted(), self.nontree):
            vol.loop_data(store)

    def mkfs(self):
        for vol in chain(self.itree.sorted(), self.nontree):
            vol.mkfs()

    def mount(self, sandbox):
        for vol in self.itree.sorted():
            vol.mount(sandbox)

    def umount(self, sandbox):
        for vol in reversed(list(self.itree.sorted())):
            vol.umount(sandbox)

    def unloop_data(self):
        for vol in chain(self.itree.sorted(), self.nontree):
            vol.unloop_data()


class VMVolume(object):

    dump = 0
    fstype = 'raw'

    def loop_data(self, dir_):
        fn = os.path.join(dir_, self.dataname)
        #my_exec("losetup --find %s" % fn)  # safer: add then find
        next_loop_device = Loopback.get_device()
        Loopback.connect(next_loop_device, fn)
        self.loop = next_loop_device

    def unloop_data(self):
        if not self.loop:
            raise Exception("attempted to unloop the unlooped")
        Loopback.disconnect(self.loop)
        self.loop = None

    def __init__(self, label, vmdkname=None, dataname=None, include_in_fstab=None, options=None):
        self.label = label
        self.vmdkname = vmdkname if vmdkname else label+'.vmdk'
        self.dataname = dataname if dataname else label+'.'+self.fstype
        if include_in_fstab is None:
            self.include_in_fstab = True
        else:
            self.include_in_fstab = bool(include_in_fstab)
        if options is None:
            self.options = 'defaults'
        else:
            self.options = options

        self.loop = None
        self.up = False

    def detect(self, store, sandbox):
        data_fn = os.path.join(store, self.dataname)
        sand_fn = os.path.normpath(sandbox + self.mountpoint)

        try:
            self.loop = Loopback.find(data_fn)
        except LoopNotFound:
            self.loop = None

        if self.loop:
            mounts = list(ProcMounts.find(device=self.loop))
            if len(mounts) > 1:
                raise Exception("same device is mounted multiple times")
            elif len(mounts) == 0:
                self.up = False
            else:
                if mounts[0].path == sand_fn:
                    self.up = True
                else:
                    print mounts[0].path
                    print sand_fn
                    raise Exception("unexpected mountpoint for existing loop device")
        else:
            self.up = False


    def mount(self, dir_):
        finaldir = dir_ + self.mountpoint
        runner.mkdir_p(finaldir)
        runner.mountfs(self.loop, finaldir)
        self.up = True

    def umount(self, dir_):
        if not self.up:
            raise Exception("attempt to umount volume that is not up")
        finaldir = dir_ + self.mountpoint
        runner.umountfs(finaldir)
        self.up = False

    def tree_ref(self):
        if hasattr(self, 'mountpoint'):
            return path_to_list(self.mountpoint), self
        else:
            return [], self

    def fstab_entry(self):
        return ' '.join([
            'LABEL='+self.label,
            getattr(self,'mountpoint','none'),
            self.fstype,
            self.options,
            str(self.dump),
            str(self.check),
        ])

    @classmethod
    def from_dict(cls, dict_repr):
        volume_type = dict_repr.pop('type').strip().lower()
        if volume_type == VolumeExt4.volume_type:
            return VolumeExt4(**dict_repr)
        elif volume_type == VolumeXfs.volume_type:
            return VolumeXfs(**dict_repr)
        elif volume_type == VolumeBoot.volume_type:
            return VolumeBoot(**dict_repr)
        elif volume_type == VolumeSwap.volume_type:
            return VolumeSwap(**dict_repr)
        else:
            raise ValueError("Unknown volume type \"%s\"" % volume_type)

    def create_vmdk(self, dir_, create_type):
        fn = os.path.join(dir_, self.vmdkname)
        if os.path.isfile(fn):
            raise Exception('file exists "%s"' % (self.vmdkname,))
        vmdkdata = self.vmdk(create_type)
        with open(fn, 'w') as fd:
            fd.write(vmdkdata)


class VMSparseVolume(VMVolume):
    def __init__(self, label, sectors, vmdkname=None, dataname=None, include_in_fstab=None, options=None):
        super(VMSparseVolume, self).__init__(label, vmdkname=vmdkname, dataname=dataname, include_in_fstab=include_in_fstab, options=options)
        self.sectors = int(sectors)

    def create_data(self, dir_):
        fn = os.path.join(dir_, self.dataname)
        if os.path.isfile(fn):
            raise Exception("file exists")
        runner.create_sparse_file(fn, self.sectors)

    def vmdk(self, create_type):
        return make_vmdk(self.dataname, self.sectors, create_type=create_type)


class VolumeExt4(VMSparseVolume):
    volume_type = 'ext4'
    fstype = 'ext4'
    def __init__(self, label, size, mountpoint, check, options=None, vmdkname=None, dataname=None, include_in_fstab=None):
        super(VolumeExt4, self).__init__(label, decode_size(size), vmdkname=vmdkname, dataname=dataname, include_in_fstab=include_in_fstab, options=options)
        self.mountpoint = os.path.normpath(mountpoint)
        self.check = check

    def mkfs(self):
        if not self.loop:
            raise Exception("volume is not looped")
        #print 'exec:', "mkfs.ext4 -q -F -L %s %s" % (self.label, self.loop)
        runner.passthru(['mkfs.ext4', '-q', '-F', '-L', self.label, self.loop])


class VolumeXfs(VMSparseVolume):
    volume_type = 'xfs'
    fstype = 'xfs'
    def __init__(self, label, size, mountpoint, check, options=None, vmdkname=None, dataname=None, include_in_fstab=None):
        super(VolumeXfs, self).__init__(label, decode_size(size), vmdkname=vmdkname, dataname=dataname, include_in_fstab=include_in_fstab, options=options)
        self.mountpoint = os.path.normpath(mountpoint)
        self.check = check

    def mkfs(self):
        if not self.loop:
            raise Exception("volume is not looped")
        #print 'exec:', "mkfs.ext4 -q -F -L %s %s" % (self.label, self.loop)
        runner.passthru(['mkfs.xfs', '-q', '-f', '-L', self.label, self.loop])


class VolumeSwap(VMSparseVolume):
    volume_type = 'swap'
    fstype = 'swap'
    check = 0
    def __init__(self, label, size, vmdkname=None, dataname=None, include_in_fstab=None):
        super(VolumeSwap, self).__init__(label, decode_size(size), vmdkname=vmdkname, dataname=dataname, include_in_fstab=include_in_fstab, options='defaults')

    def mkfs(self):
        if not self.loop:
            raise Exception("volume is not looped")
        #print 'exec:', "mkswap -f -L %s %s" % (self.label, self.loop)
        runner.passthru(['mkswap', '-f', '-L', self.label, self.loop])

    def mount(self, dir_):
        pass

    def umount(self, dir_):
        pass


class VolumeBoot(VMVolume): # extends ext4?
    volume_type = 'boot'
    fstype = 'ext4'
    def __init__(self, label, source, offset, mountpoint, check, vmdkname=None, dataname=None, include_in_fstab=None, options=None):
        super(VolumeBoot, self).__init__(label, vmdkname=vmdkname, dataname=dataname, include_in_fstab=include_in_fstab, options=options)
        self.source = source
        self.offset = int(offset)
        self.mountpoint = mountpoint
        self.check = check
        #XXX self.sectors = os.stat(source).st_size / 512
        self.sectors = 1024

    def create_data(self, dir_):
        fn = os.path.join(dir_, self.dataname)
        if os.path.isfile(fn):
            raise Exception("file exists")
        runner.copy_file(self.source, fn)

    def loop_data(self, dir_):
        fn = os.path.join(dir_, self.dataname)
        #my_exec("losetup --find %s" % fn)  # safer: add then find
        next_loop_device = Loopback.get_device()
        Loopback.connect(next_loop_device, fn, sectors_to_bytes(self.offset))
        self.loop = next_loop_device

    def mkfs(self):
        if not self.loop:
            raise Exception("volume is not looped")
        #print 'exec:', "mkfs.ext4 -q -F -L %s %s" % (self.label, self.loop)
        runner.passthru(['mkfs.ext4', '-q', '-F', '-L', self.label, self.loop])

    def vmdk(self, create_type):
        return make_vmdk(self.dataname, self.sectors, create_type=create_type)


def path_to_list(path):
    """split a dir path into a list, adding a sentinal value for the root

    Args:
        path: string unix directory pathname e.g. '/usr/bin'

    Returns:
        list of each node in the path, plus a prepended '__root__'

    Raises:
        Exception if the input fails some validity tests
    """
    if path != path.strip():
        raise Exception('whitespace found in path "%s"' % (path,))
    if not path:
        raise Exception('empty path?')
    if path[0] != '/':
        raise Exception('path "%s" has no leading /' % (path,))
    path = '__root__' + path
    return os.path.normpath(path).split('/')


def decode_size(size_string):
    tsz = size_string.strip()
    lasttwo = tsz[-2:]
    amount = int(tsz[0:-2].strip())
    if amount <= 0:
        raise ValueError('bad size')
    if lasttwo.lower() == 'gb':
        return (amount * 1024 * 1024 * 1024) / 512
    elif lasttwo.lower() == 'mb':
        return (amount * 1024 * 1024) / 512
    else:
        raise ValueError('bad size')


def sectors_to_bytes(sectors):
    return sectors * 512
