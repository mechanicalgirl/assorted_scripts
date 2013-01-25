# http://www.mechanicalgirl.com/post/ms-excel-and-pythons-csv-module/

import csv

infile = '~/set_lists.csv'
outfile = '~/new_song_records.csv'

def parse(infile):
    ofile  = open(outfile, "wb")
    writer = csv.writer(ofile)

    # open the source file in universal-newline mode
    with open(infile, 'rU') as f:
        reader = csv.reader(f)
        for row in reader:
            # the last cell is the one with the song data
            # split on newline character to generate multiple elements
            songs = row[5].split("\n")
            for song in songs:
                # each of those new elements gets a row
                # with the metadata from the original row prepended
                line = [row[0], row[1], row[2], row[3], row[4], song.lstrip()]
                writer.writerow(line)
    ofile.close()

def main():
    parse(infile)

if __name__ == "__main__":
    main()
