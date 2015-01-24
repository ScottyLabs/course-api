#!/usr/bin/env python3
# @file parse_fces.py
# @brief Parses FCE data for MSXML files downloaded from
#        http://cmu.smartevals.com into a JSON file.
#
#        MSXML is used to compensate for a bug in the FCE export feature: The
#        first few lines of any output are cut off. MSXML is the only format to
#        have enough useless metadata at the beginning of the file to prevent
#        important data from being cutoff.
#
#        Usage: python parse_fces.py [INFILE] [OUTFILE]
#
#        INFILE: A .msxml file downloaded from the FCE website.
#        OUTFILE: Where to place resulting JSON.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-01-22

import sys
import json
import bs4


# @function parse_table
# @brief Parses FCE data from a BeautifulSoup XML table object.
# @param table: Table object from an FCE XML file.
# @return [{}]: Array of data which represents FCE data by section.
def parse_table(table):
    rows = table.find_all('row')
    columns = []
    result = []

    for row in rows:
        cells = row.find_all('cell')
        if len(cells) > 0 and cells[0].string == 'Semester':
            # Columns are not consistent in a table - update them when
            # new labels are found.
            columns = [lbl.string.strip() for lbl in row if lbl.string.strip()]
        else:
            # Remove empty cells
            cells = cells[:len(columns)]

            # Build object to represent this section
            obj = {}
            for index, cell in enumerate(cells):
                # Parse cell value
                value = cell.string.strip()
                if cell.data['ss:type'] == 'Number':
                    if (columns[index][0].isdigit()):
                        # Rating for a question
                        value = float(value)
                    else:
                        # Other measures
                        value = int(value)
                obj[columns[index]] = value

            result.append(obj)

    return result


# @function parse_fces
# @brief Parses FCE data from the passed file, and writes it as JSON to the
#        output file.
# @param inpath: File path for a text file containing fully qualified
#        URLS for course description pages, separated by newlines.
# @param outpath: File path to write output JSON to.
def parse_fces(inpath, outpath):

    # Get information
    with open(inpath, 'r') as infile:

        print('Reading file data...')
        soup = bs4.BeautifulSoup(infile)

        print('Parsing...')
        data = parse_table(soup.find('table'))

        print('Success!')

    print('Writing output to file ' + sys.argv[2] + '...')

    # Write to output file
    with open(outpath, 'w') as outfile:
        json.dump(data, outfile)

    print('Done!')


if __name__ == '__main__':
    # Verify arguments
    if len(sys.argv) != 3:
        print('Usage: parse_fces.py [INFILE] [OUTFILE]')
        sys.exit()

    parse_fces(sys.argv[1], sys.argv[2])
