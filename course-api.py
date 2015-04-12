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


# @function aggregate
# @brief Combines the course descriptions, schedules, and FCEs data sets into
#        one object.
# @param descs: Course desciptions object as returned by parse_descs.
# @param schedules: Course schedules object as returned by parse_descs.
# @param fces: FCEs object as returned by parse_descs.
def aggregate(descs, schedules, fces):
    courses = {}

    for department in schedules:
        for course in department['courses']:
            for desc in descs:
                if ('num' in desc and desc['num'] == int(course['num'])):
                    desc['department'] = department['department']
                    desc['lectures'] = course['lectures']

                    num = desc['num']
                    del desc['num']

                    courses[str(num)] = desc

    return {'courses': courses, 'fces': fces}


if __name__ == '__main__':
    # Verify arguments
    if not (len(sys.argv) == 5 or len(sys.argv) == 3):
        print(USAGE)
        sys.exit()

    semester = sys.argv[1]
    outpath = sys.argv[2]

    if semester not in ['S', 'M1', 'M2', 'F']:
        print('Requested quarter is not one of [\'S\', \'M1\', \'M2\', \'F\']')
        sys.exit()

    if (len(sys.argv) == 3):
        username = input('Username: ')
        password = getpass.getpass()
    else:
        username = sys.argv[3]
        password = sys.argv[4]

    print('Scottylabs CMU Course-API')

    print('Retrieving course descriptions:')
    descs = parse_descs(DESC_SOURCES)

    print('Retrieving course schedule:')
    schedules = parse_schedules(semester)

    print('Retrieving FCEs:')
    fces = parse_fces(username, password)

    print('Aggregating data...')
    results = aggregate(descs, schedules, fces)

    print('Writing data...')
    with open(outpath, 'w') as outfile:
        json.dump(results, outfile)

    print('Done!')
