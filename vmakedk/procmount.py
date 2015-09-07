
class ProcMount(object):
    def __init__(self, device, path, fstype, options):
        self.path = path
        self.fstype = fstype
        self.device = device
        self.options = options

    @classmethod
    def from_procfs_line(cls, line):
        parts = line.split(' ')
        return cls(parts[0], parts[1], parts[2], parts[3])

    def __repr__(self):
        return '<ProcMount %s=%s (%s, %s)>' %\
               (self.path, self.device, self.fstype, self.options)


class ProcMounts(object):
    @classmethod
    def objects(cls):
        with open('/proc/mounts', 'r') as fd:
            for line in fd:
                yield ProcMount.from_procfs_line(line.strip())

    @classmethod
    def find(cls, device=None, path=None, fstype=None):
        for mount in cls.objects():
            match = True
            match &= (path and mount.path == path)
            match &= (device and mount.device == device)
            match &= (fstype and mount.fstype == fstype)
            if match:
                yield mount

