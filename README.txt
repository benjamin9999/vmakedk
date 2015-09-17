=======
vmakedk
=======

vmakedk provides command-line tools for creating VMDK images
backed by sparse files based on a user supplied layout described
with JSON.

In most cases, it runs as root and performs the following:

* Create sparse files to provide the backing store for each VMDK
* Generate VMDK descriptior files for all disks
* Create filesystems (mkfs) with labels for each disk
* Attach free loopback devices (/dev/loopN) to each disk image
* Mount all devices in a sandbox/chroot environment

It can also output an appropriate /etc/fstab for the same layout.

