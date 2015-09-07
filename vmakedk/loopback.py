
import subprocess


class LoopNotFound(Exception):
    pass


class Loopback(object):

    exe = ['losetup']
    fake_dev = 0
    dry_run = False

    @classmethod
    def get_device(cls):
        dev = cls.run(['-f']).strip()
        return dev

    @classmethod
    def connect(cls, loop, filename, offset=None):
        offset_params = ['-o', str(int(offset))] if offset else []
        cls.run(offset_params + [loop, filename])

    @classmethod
    def disconnect(cls, loop):
        cls.run(['-d', loop])

    @classmethod
    def run(cls, params):
        if cls.dry_run:
            print 'running: ', ' '.join(['losetup'] + params)
            if params[0] == '-f':
                cls.fake_dev += 1
                return '/dev/loop' + str(cls.fake_dev)
        else:
            return subprocess.check_output(['losetup'] + params)

    @classmethod
    def find(cls, fn):
        def loopparse(s):
            left,mid,right = s.split(' ')
            dev_part = left[:-1] # trim the ':'
            file_part = right[1:-1]
            return dev_part, file_part

        data = subprocess.check_output(['losetup', '-a']).strip()
        lines = data.split("\n")
        pairs = (loopparse(line) for line in lines)
        for dev, file_ in pairs:
            if file_ == fn:
                return dev
        raise LoopNotFound()

