
SCSI_DISK_TEMPLATE = ('scsi{{bus}}:{{id}}.present = "TRUE"\n'
                      'scsi{{bus}}:{{id}}.fileName = "{{filename}}"\n'
                      'scsi{{bus}}:{{id}}.deviceType = "scsi-hardDisk"\n'
                      'scsi{{bus}}:{{id}}.redo = ""\n')

SCSI_BUS_TEMPLATE = ('scsi{{bus}}.present = "TRUE"\n'
                     'scsi{{bus}}.virtualDev = "pvscsi"\n')

scsi_ids = (num for num in range(0, 16) if num != 7)

