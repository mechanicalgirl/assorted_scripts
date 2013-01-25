import os, os.path, sys

rootdir = '/path/to/source/images'

def deletefile(filename):
  print "delete this file: " + filename
  os.remove(filename)

def resizefile(filename):
  print "resize this file: " + filename

  import PIL
  from PIL import Image
  import subprocess

  basewidth = 175
  img = Image.open(filename)
  wpercent = (basewidth / float(img.size[0]))
  hsize = int((float(img.size[1]) * float(wpercent)))
  new_filename = filename[:-8]+"_175.jpg"

  # print "convert " + filename + " -scale " + str(basewidth)+'x'+str(hsize)+'! ' + new_filename
  resize = str(basewidth)+"x"+str(hsize)+"!"
  convert = subprocess.check_call(["convert", filename, "-scale", resize, new_filename])

  """
  img = img.resize((basewidth, hsize), Image.ANTIALIAS) # here's the culprit
  img.save(new_filename)
  """

def removefolder(foldername):
  print "remove this folder: " + foldername
  import shutil
  shutil.rmtree(foldername)

def recursive():
  for root, subFolders, files in os.walk(rootdir):
    for folder in subFolders:
      sub = os.path.join(rootdir,folder)
      for files in os.walk(sub):
        for x in files:
          if x:
            for y in x:
             if y[-4:] == ".jpg":
               ifile = os.path.join(sub,y)
               # if ifile[-8:] == "_175.jpg":
               #   removefolder(sub)
               if ifile[-8:] == "_260.jpg":
                 resizefile(ifile)
                 # deletefile(ifile)
               # if ifile[-8:] == "_640.jpg":
               #   deletefile(ifile)
               # if ifile[-8:] == "_158.jpg":
               #   deletefile(ifile)

def main():
  files = recursive()

if __name__ == "__main__":
    main()

