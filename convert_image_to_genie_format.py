from PIL import Image
import os
import sys
import struct

GVSP_PIX_MONO = 0x01000000
GVSP_PIX_OCCUPY8BIT = 0x00080000
GVSP_PIX_MONO8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x0001)

########################################################################
class GenieFileHeader:
   """"""

   #----------------------------------------------------------------------
   # File Header
   # ID : 14Bytes = GENIEIMAGERAW\0
   # HeaderSize : 2Bytes  
   # TimeStamp : 8Bytes  
   # PixelFormat : 4Bytes
   # SizeX : 4Bytes
   # SizeY : 4Bytes
   # OffsetX : 4Bytes
   # offsetY : 4Bytes
   # PaddingX : 2Bytes
   # PaddingY : 2Bytes   
   def __init__(self):
      """Constructor"""      
      self.fileId = bytes('GENIEIMAGERAW\x00', encoding="ascii")
      self.headerSize = 48
      self.timeStamp = 0x00000000
      self.pixelFormat = GVSP_PIX_MONO8
      self.sizeX = 0
      self.sizeY = 0
      self.offsetX = 0
      self.offsetY = 0
      self.paddingX = 0
      self.paddingY = 0
         
   #----------------------------------------------------------------------
   def pack(self):
      """"""
      return struct.pack('14s',self.fileId) + \
             struct.pack( 'H', self.headerSize) + \
             struct.pack( 'Q', self.timeStamp) + \
             struct.pack( 'IIIIIHH', self.pixelFormat, self.sizeX, self.sizeY, self.offsetX, self.offsetY, self.paddingX, self.paddingY)

########################################################################
class GenieFileImage: 
   def __init__(self, imagePath):     
      self.width = 0
      self.height = 0 
      self.header = None 
      self.image = [] 
      self.savePath = None
      self.imagePath = imagePath
      self.loadImage()
   
   def loadImage(self):
      with Image.open(self.imagePath) as im:
         self.image = im.tobytes()
         self.width = im.width
         self.height = im.height
         assert(len(self.image) == (self.width * self.height))

   def get_image(self):   
      return self.image
  
   def get_header(self):
      if self.header == None:
         self.header = GenieFileHeader()
         self.header.sizeX = self.width
         self.header.sizeY = self.height
      return self.header
   
   def save(self, path=None):
      if not path:
         path = os.path.splitext(self.imagePath)[0]+"-genie.img"
         
      print("Writing %s..."%(path))
      with open(path, 'wb') as f:
         f.write(self.get_header().pack() + self.get_image())        
         
      self.savePath = path
      return path

def convert_image(path):
   print("Converting %s to Genie Nano \"user image\" format" % (path))
   GenieFileImage(path).save()

def main():
   if len(sys.argv) == 1:
      print("usage: python convert_image_to_genie_format.py <image file path> or <path to directory with multiple images>")
      exit()
   args = sys.argv[1:]
   
   if os.path.isfile(args[0]):
      filename = args[0]
      if args[0][-3:] in ["jpg","tif", "bmp"]:
         convert_image(filename)
   elif os.path.isdir(args[0]):
      directory = args[0]
      for filename in os.listdir(directory):
         if filename.endswith(".jpg") or filename.endswith(".tif") or filename.endswith(".bmp"):
            convert_image(directory+"\\"+filename)
         else:
            continue
   else:
      print("Nothing to process. Exiting.")

if __name__ == "__main__":
    main()
