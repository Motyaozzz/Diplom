class Drive():

   index: int = None
   path: str
   total_sectors: str
   disk_type = None
   name: str
   block_size: int = 512
   capacity: int
   serial_num = None

   def __init__(self, name, path, disk_type, block_size, capacity, dev_id, index):
      self.name = name
      self.disk_type = disk_type
      self.path = path
      if block_size is not None:
         self.block_size = block_size
      self.capacity = capacity
      self.serial_num = dev_id
      self.index = index
      
