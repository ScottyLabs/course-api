#!/usr/bin/env python3
# @file course-api.py
# @brief One script to rule them all.
#
#        Downloads schedule data for a specific semester, including course
#        meeting times, course descriptions, pre/corequisites, FCEs, and so on.
#        Output is parsed into a single JSON output file.
#
#        If you want to download just one of Course description data, course
#        schedule data, or FCE data see the scripts/ folder.
#
#        Usage: python course-api.py [SEMESTER] [OUTFILE] <USERNAME PASSWORD>
#
#        SEMESTER: The semester of data desired (one of S/M1/M2/F)
#        OUTFILE: Where to place resulting JSON.
#        USERNAME: Andrew username to use to download data.
#        PASSWORD: Andrew password to use to download data.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-04-07


import json
import sys
import getpass
from scripts.parse_descs import parse_descs
from scripts.parse_schedules import parse_schedules
from scripts.parse_fces import parse_fces


# Constants
USAGE = 'Usage: python parse_fces.py [SEMESTER] [OUTFILE] <USERNAME PASSWORD>'
DESC_SOURCES = 'data/schedule_pages.txt'


if __name__ == '__main__':
    # Verify arguments
    if not (len(sys.argv) == 5 or len(sys.argv) == 3):
        print(USAGE)
        sys.exit()

    semester = sys.argv[1]
    outpath = sys.argv[2]

    if (len(sys.argv) == 3):
        username = input('Username: ')
        password = getpass.getpass()
    else:
        username = sys.argv[3]
        password = sys.argv[4]

    print('Scottylabs CMU Course-API')

    results = {}

    print('Retrieving course descriptions:')
    results['descs'] = parse_descs(DESC_SOURCES)

    print('Retrieving course schedule:')
    results['schedules'] = parse_schedules(semester)

    print('Retrieving FCEs:')
    results['fces'] = parse_fces(username, password)

    print('Writing data...')
    with open(outpath, 'w') as outfile:
        json.dump(results, outfile)

    print('Done!')
