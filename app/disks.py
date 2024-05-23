win_types = {
   0: "USB",
   3: "HDD",
   4: "SSD",
   5: "SCM"
}

class Drive():

   index: int = None
   path: str
   total_sectors: str
   total_cylinders: str = "512"
   disk_type = None
   name: str
   block_size: int = 512
   capacity: int
   serial_num = None


   def __init__(self, name, path, disk_type, block_size, capacity, dev_id, index, total_sectors, total_cylinders):
      self.name = name
      if isinstance(disk_type, int):
         self.disk_type = win_types[disk_type]
      else:
         self.disk_type = disk_type
      self.path = path
      if block_size is not None:
         self.block_size = block_size
      self.capacity = capacity
      self.serial_num = dev_id
      self.index = index
      if total_sectors is not None:
         self.total_sectors = total_sectors
      if total_cylinders is not None:
         self.total_cylinders = total_cylinders
