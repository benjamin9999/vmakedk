
SECTORS_1GB = 1 * 1024 * 1024 * 1024 / 512
SECTORS_2GB = 2 * 1024 * 1024 * 1024 / 512

ADAPTER_TYPE_IDE = 'ide'
ADAPTER_TYPE_BUSLOGIC = 'buslogic'
ADAPTER_TYPE_LSILOGIC = 'lsilogic'

CREATE_TYPE_VMFS = 'vmfs'
CREATE_TYPE_MONOLITHIC_FLAT = 'monolithicFlat'

EXTENT_TYPES = {
    CREATE_TYPE_VMFS: 'VMFS',
    CREATE_TYPE_MONOLITHIC_FLAT: 'FLAT',
}


VMDK_TEMPLATE = ('version=1\n'
                 'encoding="UTF-8"\n'
                 'CID=fffffffe\n'
                 'parentCID=ffffffff\n'
                 'isNativeSnapshot="no"\n'
                 'createType="{{create_type}}"\n'
                 'RW {{sectors}} {{extent_type}} "{{filename}}" 0\n'
                 'ddb.adapterType = "{{adapter_type}}"\n'
                 'ddb.geometry.cylinders = "{{cylinders}}"\n'
                 'ddb.geometry.heads = "{{heads}}"\n'
                 'ddb.geometry.sectors = "{{sectors_per_track}}"\n'
                 'ddb.virtualHWVersion = "6"\n')

def make_vmdk(filename, sectors,
              create_type, adapter_type=ADAPTER_TYPE_LSILOGIC):
    """Render a vmdk descriptor file as a string.

    It is assumed that a single extent covers the entire disk.

    Args:
        filename: filename of the backing storage/extent
        sectors: total disk/extent sectors
        create_type: one of CREATE_TYPE_* constants
        adapter_type: one of ADAPTER_TYPE_* constants

    Returns:
        string containing the vmdk descriptor file data
    """

    heads, spt, cylinders = sectors_to_geometry(sectors)

    return VMDK_TEMPLATE.replace('{{filename}}', filename)\
                        .replace('{{create_type}}', create_type)\
                        .replace('{{extent_type}}', EXTENT_TYPES[create_type])\
                        .replace('{{adapter_type}}', adapter_type)\
                        .replace('{{sectors}}', str(sectors))\
                        .replace('{{cylinders}}', str(int(cylinders)))\
                        .replace('{{sectors_per_track}}', str(int(spt)))\
                        .replace('{{heads}}', str(int(heads)))


def sectors_to_geometry(sectors):
    """Calculate disk geometry based on total sector count

    See VMware kb # 1026266 for details

    Args:
        sectors: disk's total number of sectors

    Returns:
        tuple of (#heads, #sectors-per-track, #cylinders)
    """
    if sectors < SECTORS_1GB:
        return 64, 32, sectors / (64 * 32)
    elif sectors < SECTORS_2GB:
        return 128, 32, sectors / (128 * 32)
    else:
        return 255, 63, sectors / (255 * 63)

