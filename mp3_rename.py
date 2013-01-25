import os, sys
import datetime
import eyeD3
import subprocess
import shutil

sourcefolder = "/path/to/source"

def processfile(sourcemp3):
    """
    Rename an mp3 file using the artist and title in its metadata
    """
    # I snuck this in for cases where I want to give the file a 
    # specific date; otherwise it defaults to the current date.
    try:
        today = str(sys.argv[1])
    except IndexError:
        today = str(datetime.date.today()).replace("-", "")

    tag = eyeD3.Tag()
    tag.link(sourcemp3)

    artist = tag.getArtist()
    title = tag.getTitle()
    i_artist = artist
    i_title = title
    album = tag.getAlbum()

    if (artist[0:4] == 'The '):
        artist = artist.replace(artist[0:4], "")
        # artistMeta = 'u"'+ artist +'"'
        tag.setArtist(artist)
        tag.update(eyeD3.ID3_V2)
        artist = tag.getArtist()

    stripchars = [" ", ",", ")", ".", "'", "_", "/"]
    for char in stripchars:
        artist = artist.replace(char, "")
        title = title.replace(char, "")
    artist = artist.replace("&", "and")
    title = title.replace("&", "and")
    title = title.replace("(", "_")

    newmp3 = sourcemp3
    if title:
        newmp3 = ('%s/%s_%s_%s.mp3') %(sourcefolder,today,artist,title)
        os.rename(sourcemp3, newmp3)
        print "Renamed", newmp3

    if len(today) == 6:
        print "Transfer", newmp3
        t = transferfile(newmp3)

        # write records to a csv for bulk insert later
        # insertfile = "%s/bulkinsert_%s.csv" % (sourcefolder, today)
        i_artist = i_artist.replace("&", "and")
        i_title = i_title.replace("&", "and")
        album = album.replace("&", "and")

        insertfile = "%s/bulkinsert.csv" % (sourcefolder)
        filepath = ('mp3/%s_%s_%s.mp3') %(today,artist,title)
        created_at = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
        newline = """INSERT INTO playlist_song (user_id, artist, title, album, 
                     filepath, active, created_at) VALUES(1, '%s', '%s', '%s', 
                     '%s', 't', %r);\n""" % (i_artist, i_title, album, filepath, created_at)
        with open(insertfile, "a") as ifile:
            ifile.write(newline)

    return newmp3

def transferfile(mp3):
    try:
        send = subprocess.check_call(["scp", mp3, "user@127.0.0.1:/path/to/downloads"])
        shutil.move(mp3, sourcefolder + "/processed/")
        return True
    except:
        return False

def identify():
    """
    Do a non-recursive walk of the source folder
    and identify files with the .mp3 extension
    """
    files = []
    for folder in os.listdir(sourcefolder):
        fullpathname = os.path.join(sourcefolder, folder)
        if os.path.isfile(fullpathname):
            x = len(sourcefolder)
            name = fullpathname[x+1:]
            if name[-3:] == 'mp3':
                files.append(fullpathname)
    return files


def main():
    files = identify()
    for file in files:
        p = processfile(file)

if __name__ == "__main__":
    main()

