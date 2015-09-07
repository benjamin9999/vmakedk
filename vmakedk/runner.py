
import subprocess

class RealRunner(object):
    def mkdir_p(self, path):
        subprocess.check_output(['mkdir', '-p', path])

    def mountfs(self, dev, dir):
        subprocess.check_output(['mount', dev, dir])

    def bindfs(self, src, dir):
        subprocess.check_output(['mount', '-o', 'bind', src, dir])

    def umountfs(self, dir):
        subprocess.check_output(['umount', dir])

    def create_sparse_file(self, filename, sectors):
        subprocess.check_output(['dd', 'of='+filename, 'seek='+str(sectors), 'count=0'])

    def copy_file(self, src, dst):
        subprocess.check_output(['dd', 'if='+src, 'of='+dst])

    def passthru(self, params):
        return subprocess.check_output(params)


class DryRunner(object):
    def mkdir_p(self, path):
        print 'exec: mkdir -p', path

    def mountfs(self, dev, dir):
        print 'exec: mount', dev, dir

    def bindfs(self, src, dir):
        print 'exec: mount -o bind', src, dir

    def umountfs(self, dir):
        print 'exec: umount', dir

    def create_sparse_file(self, filename, sectors):
        print 'exec: dd of=%s bs=512 seek=%d count=0' % (filename, sectors)

    def copy_file(self, src, dst):
        print 'exec: dd if=%s of=%s' % (src, dst)

    def passthru(self, params):
        print 'exec:', ' '.join(params)

