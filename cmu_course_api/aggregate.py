# @file aggregate.py
# @brief One script to rule them all.
#
#        Downloads schedule data for a specific semester, including course
#        meeting times, course descriptions, pre/corequisites, FCEs, and so on.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-04-07


import json
import os.path
from cmu_course_api.parse_descs import parse_descs
from cmu_course_api.parse_schedules import parse_schedules
from cmu_course_api.parse_fces import parse_fces


# Constants
SOURCES = os.path.join(os.path.dirname(__file__), 'data/schedule_pages.txt')


# @function aggregate
# @brief Combines the course descriptions, schedules, and FCEs data sets into
#        one object.
# @param descs: Course desciptions object as returned by parse_descs.
# @param schedules: Course schedules object as returned by parse_descs.
# @param fces: FCEs object as returned by parse_descs.
# @return An object containing the aggregate of the three datasets.
def aggregate(descs, schedules, fces):
    courses = {}

    for department in schedules:
        for course in department['courses']:
            for desc in descs:
                if ('num' in desc and desc['num'] == int(course['num'])):
                    desc['department'] = department['department']
                    desc['lectures'] = course['lectures']
                    desc['sections'] = course['sections']

                    num = desc['num']
                    del desc['num']

                    courses[str(num)] = desc

    return {'courses': courses, 'fces': fces}


# @function get_course_data
# @brief Used for retrieving all information from the course-api for a given
#        semester.
# @param semester: The semester to get data for. Must be one of [S, M1, M2, F].
# @param username: Username to use for andrew authentication.
# @param password: Password to use for andrew authentication.
# @return Object containing all course-api data - see README.md for more
#        information.
def get_course_data(semester, username, password):
    descs = parse_descs(SOURCES)
    schedules = parse_schedules(semester)
    try:
        fces = parse_fces(username, password)
    except Exception:
        fces = []
        print("Something went wrong. Running without FCEs for now...")
    return aggregate(descs, schedules, fces)
