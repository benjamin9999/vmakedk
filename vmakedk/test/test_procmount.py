import unittest
from StringIO import StringIO
from mock import mock_open, patch, MagicMock

from vmakedk.procmount import ProcMount, ProcMounts


# http://www.ichimonji10.name/blog/6/
from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # pylint:disable=import-error
else:
    import builtins  # pylint:disable=import-error


REFERENCE = '''rootfs / rootfs rw 0 0
proc /proc proc rw,relatime 0 0
sysfs /sys sysfs rw,relatime 0 0
devtmpfs /dev devtmpfs rw,relatime,size=1900092k,nr_inodes=475023,mode=755 0 0
devpts /dev/pts devpts rw,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs /dev/shm tmpfs rw,relatime 0 0
/dev/sdc / ext4 rw,relatime,barrier=1,data=ordered 0 0
/proc/bus/usb /proc/bus/usb usbfs rw,relatime 0 0
/dev/sda1 /boot ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/sdf /var ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/sde /opt ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/sdh /tmp ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/sdd /usr/local ext4 rw,relatime,barrier=1,data=ordered 0 0
none /mnt/benjamin vboxsf rw,nodev,relatime 0 0
/dev/sdi /mnt/mongodata ext4 rw,noatime,barrier=1,data=ordered 0 0
none /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
'''
"""obtained from dumping my /proc/mounts.  line-endings should match the hexdump"""


class TestProcMount(unittest.TestCase):
    def test_with_device(self):
        line = '/dev/sda1 /boot ext4 rw,relatime,barrier=1,data=ordered 0 0'
        a = ProcMount.from_procfs_line(line)
        self.assertIsInstance(a, ProcMount)
        self.assertEquals(a.path, '/boot')
        self.assertEquals(a.fstype, 'ext4')
        self.assertEquals(a.device, '/dev/sda1')
        self.assertEquals(a.options, 'rw,relatime,barrier=1,data=ordered')

    def test_with_no_device(self):
        line = 'none /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0'
        a = ProcMount.from_procfs_line(line)
        self.assertIsInstance(a, ProcMount)
        self.assertEquals(a.path, '/proc/sys/fs/binfmt_misc')
        self.assertEquals(a.fstype, 'binfmt_misc')
        self.assertEquals(a.device, 'none')
        self.assertEquals(a.options, 'rw,relatime')


class TestProcMounts(unittest.TestCase):
    def test_objects(self):
        mockopen = MagicMock()
        fake_proc_mounts = StringIO(REFERENCE)
        with patch.object(builtins, 'open', mockopen):
            manager = mockopen.return_value.__enter__.return_value
            manager.read.return_value = REFERENCE
            manager.__iter__.return_value = fake_proc_mounts.__iter__()
            items = list(ProcMounts.objects())

        self.assertEquals(len(items), 16)

        # check the first few lines to see if they match the reference
        itemiter = iter(items)
        item = next(itemiter)
        self.assertEquals(item.device, 'rootfs')
        item = next(itemiter)
        self.assertEquals(item.device, 'proc')
        item = next(itemiter)
        self.assertEquals(item.device, 'sysfs')
        item = next(itemiter)
        self.assertEquals(item.device, 'devtmpfs')

    def test_find_by_device_with_match(self):
        mockopen = MagicMock()
        fake_proc_mounts = StringIO(REFERENCE)
        with patch.object(builtins, 'open', mockopen):
            manager = mockopen.return_value.__enter__.return_value
            manager.read.return_value = REFERENCE
            manager.__iter__.return_value = fake_proc_mounts.__iter__()

            cursor = ProcMounts.find(device='/dev/sdf')
            item = next(cursor)
            self.assertEquals(item.path, '/var')
            with self.assertRaises(StopIteration):
                item = next(cursor)

    def test_find_by_path_with_match(self):
        mockopen = MagicMock()
        fake_proc_mounts = StringIO(REFERENCE)
        with patch.object(builtins, 'open', mockopen):
            manager = mockopen.return_value.__enter__.return_value
            manager.read.return_value = REFERENCE
            manager.__iter__.return_value = fake_proc_mounts.__iter__()

            cursor = ProcMounts.find(path='/var')
            item = next(cursor)
            self.assertEquals(item.device, '/dev/sdf')
            with self.assertRaises(StopIteration):
                item = next(cursor)

    def test_find_by_path_without_match(self):
        mockopen = MagicMock()
        fake_proc_mounts = StringIO(REFERENCE)
        with patch.object(builtins, 'open', mockopen):
            manager = mockopen.return_value.__enter__.return_value
            manager.read.return_value = REFERENCE
            manager.__iter__.return_value = fake_proc_mounts.__iter__()

            cursor = ProcMounts.find(path='/var/blah/blah')
            with self.assertRaises(StopIteration):
                item = next(cursor)
        
    def test_find_without_criteria_returns_all(self):
        mockopen = MagicMock()
        fake_proc_mounts = StringIO(REFERENCE)
        with patch.object(builtins, 'open', mockopen):
            manager = mockopen.return_value.__enter__.return_value
            manager.read.return_value = REFERENCE
            manager.__iter__.return_value = fake_proc_mounts.__iter__()

            cursor = ProcMounts.find()
            items = list(cursor)
            self.assertEquals(len(items), 16)


if __name__ == '__main__':
    unittest.main()

