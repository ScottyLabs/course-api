# @file aggregate.py
# @brief One script to rule them all.
#
#        Downloads schedule data for a specific semester, including course
#        meeting times, course descriptions, pre/corequisites, FCEs, and so on.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-04-07

import json
import os.path
from datetime import date
from cmu_course_api.parse_descs import get_course_desc
from cmu_course_api.parse_schedules import parse_schedules

# imports used for multithreading
import threading
from queue import Queue
from os import cpu_count
from queue import Empty


# Constants
SOURCES = os.path.join(os.path.dirname(__file__), 'data/schedule_pages.txt')
SEMESTER_ABBREV = {
    'Spring': 'S',
    'Fall': 'F',
    'Summer': 'M'
}


# @function aggregate
# @brief Combines the course descriptions and schedules into one object.
# @param schedules: Course schedules object as returned by parse_descs.
# @return An object containing the aggregate of the three datasets.
def aggregate(schedules):
    courses = {}

    semester = schedules['semester'].split(' ')[0]
    semester = SEMESTER_ABBREV[semester]
    year = schedules['semester'].split(' ')[-1][2:]

    count = cpu_count()
    lock = threading.Lock()
    queue = Queue()

    if count is None:
        count = 4

    for course in schedules['schedules']:
        queue.put(course)

    queue_size = queue.qsize()
    fces_processed = 0

    def run():
        while True:
            try:
                course = queue.get(timeout=4)
            except Empty:
                return

            nonlocal queue_size, fces_processed
            with lock:
                fces_processed += 1
                
            print('\r[{}/{}] Getting description for {}...'.format(
                fces_processed, queue_size, course['num']), end="")

            desc = get_course_desc(course['num'], semester, year)
            desc['name'] = course['title']

            try:
                desc['units'] = float(course['units'])
            except ValueError:
                desc['units'] = None

            desc['department'] = course['department']
            desc['lectures'] = course['lectures']
            desc['sections'] = course['sections']
            names_dict = desc.pop('names_dict', {})

            for key in ('lectures', 'sections'):
                for meeting in desc[key]:
                    if meeting['name'] in names_dict:
                        meeting['instructors'] = names_dict[meeting['name']]

            number = course['num'][:2] + '-' + course['num'][2:]
            with lock:
                courses[number] = desc
            queue.task_done()

    print("running on " + str(count) + " threads")
    for _ in range(count):
        thread = threading.Thread(target=run)
        thread.setDaemon(True)
        thread.start()

    queue.join()
    print("")

    return {'courses': courses, 'rundate': str(date.today()),
            'semester': schedules['semester']}


# @function get_course_data
# @brief Used for retrieving all information from the course-api for a given
#        semester.
# @param semester: The semester to get data for. Must be one of [S, M1, M2, F].
# @return Object containing all course-api data - see README.md for more
#        information.
def get_course_data(semester):
    schedules = parse_schedules(semester)
    return aggregate(schedules)
