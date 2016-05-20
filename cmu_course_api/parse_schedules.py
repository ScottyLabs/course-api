'''
parse_schedules.py
Andrew Benson

Parses scheduling information from the Schedule Of Classes for a
    given school quarter and year

for reference, here is what each column number refers to in the raw HTML
0: COURSE i.e. '15122'
1: TITLE i.e. 'Principles of Imperative Computation'
2: UNITS i.e. '10.0'
3: LEC/SEC i.e. 'Lec 1', 'M'
4: DAYS i.e. 'TR'
5: BEGIN i.e. '09:00AM'
6: END i.e. '10:20AM'
7: BUILDING/ROOM i.e. 'DH 2210'
8: LOCATION i.e. 'Pittsburgh, Pennsylvania'
9: INSTRUCTOR i.e. 'Simmons, Wright'

It's hard to determine what is a lecture and what is a section/recitation.
After extended examination of course data and how it shows up in SIO, I have
found two main types of courses: letter-lectures and ... non-letter-lectures.

Non-letter-lectures are courses like 15-122 (Principles of Imperative
Computation) or 80-180 (Nature of Language). The course has large central
meeting(s) that a large portion of the students attend (the lectures) each of
which are separated into sections (usually denoted with letters). The
lectures themselves are denoted with something like 'Lec' or 'Lec 1' or 'W'
(for a Qatar lecture). Sometimes they are even denoted with numbers.

Letter-lectures are courses like 21-295 (Putnam Seminar) or 15-295
(Competition Programming and Problem Solving). These are courses without large
central meetings that opt instead for a division into smaller (but still
significant) lettered groups. Because typically each group is taught by an
instructor and not by a TA, I call these lettered groups 'lectures'. Courses
meant for only certain majors, like advanced physics courses, have only one
lettered lecture and comprise much of this category of courses.
'''

import urllib.request
import bs4


def get_page(quarter):
    '''
    return a BeautifulSoup that represents the HTML page specified by quarter

    quarter: one of ['S', 'M1', 'M2', 'F']

    if get_page fails, None will be returned
    '''
    # determine url
    url = None
    if quarter == 'S':
        url = 'http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm'
    elif quarter == 'M1':
        url = 'http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_summer_1.htm'
    elif quarter == 'M2':
        url = 'http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_summer_2.htm'
    elif quarter == 'F':
        url = 'http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_fall.htm'

    # obtain and return data
    try:
        response = urllib.request.urlopen(url)
    except:
        return None

    return bs4.BeautifulSoup(response.read(), 'html.parser')


def get_table_rows(page):
    '''
    return a list of relevant <tr> bs4 Tags

    page: a BeautifulSoup with a <table> with interesting rows
    '''
    # the first row is a weird empty row
    # the second row is the header row (Course, Title, Units, etc.)
    return page.find_all('tr')[2:]


def fix_known_errors(page):
    '''
    return a BeautifulSoup representing a fixed version of page

    page: a Beautiful Soup representing a malformed HTML page

    CMU doesn't seem to know how to write HTML. I could rant more,
    but that doesn't fix the issue. Here's a list of known issues:
    - The first row following a department name lacks a starting <tr> tag
      (this causes BeautifulSoup to skip over it when finding <tr>'s). Even
      worse, BeautifulSoup gets so confused that each time it happens it ends
      the HTML document there (with a </html> and such) and begins a new one.
    - Some rows don't even have 10 columns (i.e. they leave out the
      instructor column for no good reason). that's just annoying to parse.
    - Some rows decide to split everything into two rows JUST 'CAUSE THEY CAN.
      To be more specific, it looks like the course title is split into two.
      SIO's behavior appears to be just using the second line.
    - Some rows are empty except for the course title, sometimes appended with
      a colon. Not sure what's up with that, but it adds nonsense meetings to
      the previous section.
    '''
    for row_tag in get_table_rows(page):
        # detect department name. if found, bundle the tds into a tr
        row = process_row(row_tag)
        if row[0] and not row[0].isdigit():
            tds = []
            last_not = row_tag
            # find all tds up to next non-td
            while True:
                # sometimes we hit the end of the document due to corrupted bs4
                # parsing
                if not last_not.next_sibling:
                    break
                # idk why there are newlines, but we ignore them
                elif last_not.next_sibling == '\n':
                    last_not = last_not.next_sibling
                    continue
                # just in case we don't hit corrupted bs4 parsing after all
                elif last_not.next_sibling.name != 'td':
                    break
                # extract removes it from the document, and it acts like a
                # doubly-linked list, so it patches the next_sibling pointers
                else:
                    tds.append(last_not.next_sibling.extract())
            # make a new tr tag, add in the tds
            tr = page.new_tag('tr')
            counter = 0
            for td in tds:
                tr.append(td)
                counter += 1
            # ensure that the new row has 10 columns
            while counter < 10:
                tr.append(page.new_tag('td'))
                counter += 1
            # paste it back in
            row_tag.insert_after(tr)

            # continue with this new row
            row_tag = row_tag.next_sibling
            row = process_row(tr)
        # detect a row with only a course number, title, and credits
        if all(row[:3]) and not any(row[3:]):
            # extract course number and credits, and move to following row.
            # then delete this orphan row
            course_num = row[0]
            course_credits = row[2]
            next_row = row_tag
            while True:
                next_row = next_row.next_sibling
                if next_row != '\n':
                    break
            next_row.contents[0].string = course_num
            next_row.contents[2].string = course_credits
            row_tag.extract()
        # detect a row that's empty except for possibly the course title.
        # delete.
        elif not row[0] and row[1] and not any(row[2:]):
            row_tag.extract()
        else:
            # ensure that the new row has 10 columns
            i = len(row)
            while i < 10:
                row_tag.append(page.new_tag('td'))
                i += 1


def process_row(row_tag):
    '''
    return row_tag as a list of HTML-tag-stripped strings

    row_tag: a <tr> bs4 Tag, where each column contains exactly one string
    '''
    res = []
    for tag in row_tag.children:
        if not tag.string or tag.string.isspace():
            res.append(None)
        else:
            res.append(tag.string)
    return res


def parse_row(row):
    '''
    return (kind, data) where kind represents the kind of data returned

    row: list of HTML-tag-stripped strings that represent a data table row

    example return values:
    ('department', 'Computer Science')
    ('course', { num: 15122, title: 'Principles of Imperative...', ...})
    ('lecsec', { section: 'N', days: ['M'], ...})
    ('meeting', { days: ['N'], begin: '03:30PM', ...})
    (None, {})
    '''
    # local helper functions
    def parse_lec_sec(lec_sec_data):
        '''
        return a dictionary containing the values in lec_sec_data
        '''
        data = {}
        data['times'] = [parse_meeting(lec_sec_data)]
        data['name'] = lec_sec_data[3]
        if lec_sec_data[9]:
            data['instructors'] = \
                    [inst for inst in lec_sec_data[9].split(', ')]
        else:
            data['instructors'] = None
        return data

    def parse_meeting(meeting_data):
        '''
        return a dictionary containing the values in meeting_data
        '''
        data = {}
        data['days'] = meeting_data[4]
        data['begin'] = meeting_data[5]
        data['end'] = meeting_data[6]
        data['room'] = meeting_data[7]
        data['location'] = meeting_data[8]
        return data

    # the data can be very irregular, so we wrap with try-except
    try:
        # case department (non-empty, non-numeric string course)
        if row[0] and not row[0].isdigit():
            return ('department', row[0])
        # case course (determined by having a numeric course)
        elif row[0] and row[0].isdigit():
            data = {}
            data['num'] = row[0]
            data['title'] = row[1]
            data['units'] = row[2]
            data['lectures'] = [parse_lec_sec(row)]
            data['sections'] = []
            return ('course', data)
        # case lecture or section
        elif row[3]:
            return ('lecsec', parse_lec_sec(row))
        # case meeting
        else:
            return ('meeting', parse_meeting(row))
    except Exception as e:
        print('Failed to parse row: %s; %s' % (row, e))
        return (None, {})


def extract_data_from_row(tr, data, curr_state):
    '''
    extract the data from tr and put it in data. update curr_state accordingly
    '''
    # helper functions
    def is_lecture(letter, is_first_line):
        '''
        return whether the letter represents a lecture (rather than a section)
        '''
        letter = letter.lower()
        if is_first_line:
            # W can be a lecture, but only if it's on the first line
            # weirdly enough, lectures can sometimes be simple numbers
            return 'lec' in letter or 'w' in letter or letter.isdigit()
        else:
            return 'lec' in letter

    # parse the row into a dictionary
    (kind, row_data) = parse_row(process_row(tr))
    # determine whether to store the dictionary, and update curr_state
    if kind == 'department':
        curr_state['curr_courses'] = []
        data.append({'department': row_data,
                     'courses': curr_state['curr_courses']})
    elif kind == 'course':
        curr_state['curr_course'] = row_data
        # the course determines whether lectures are denoted with 'lec' or
        # letters
        if not is_lecture(row_data['lectures'][0]['name'], True):
            curr_state['is_letter_lecture'] = True
        else:
            curr_state['is_letter_lecture'] = False
            curr_state['curr_lecture'] = row_data['lectures'][0]
        curr_state['curr_lec_sec'] = row_data['lectures'][0]
        curr_state['curr_course']['sections'] = []

        # add in course
        curr_state['curr_courses'].append(row_data)
    elif kind == 'lecsec':
        curr_state['curr_lec_sec'] = row_data

        # if course is a letter-lecture, then this is for sure another lecture
        if curr_state['is_letter_lecture']:
            # add in lecture
            curr_state['curr_course']['lectures'].append(row_data)

        # not-letter-lecture
        else:
            # determine if lecture or section
            if is_lecture(row_data['name'], False):
                curr_state['curr_lecture'] = row_data
                # add in lecture
                curr_state['curr_course']['lectures'].append(row_data)
            else:
                # add in section
                curr_state['curr_course']['sections'].append(row_data)
    elif kind == 'meeting':
        curr_state['curr_lec_sec']['times'].append(row_data)
    else:
        raise Exception('Unexpected kind: %s', kind)


def parse_schedules(quarter):
    '''
    given a quarter, return a Python dictionary representing the data for it
    '''
    # get the HTML page, fix its errors, and find its table rows
    print('Requesting the HTML page from the network...')
    page = get_page(quarter)
    if not page:
        print('Failed to obtain the HTML document! '
              'Check your internet connection.')
        sys.exit()
    print('Done.')
    print('Fixing errors on page...')
    fix_known_errors(page)
    print('Done.')
    print('Finding table rows on page...')
    trs = get_table_rows(page)
    print('Done.')
    # parse each row and insert it into 'data' as appropriate
    curr_state = {
        'curr_courses': None,       # where courses should go
        'curr_course': None,        # where lectures should go
        'curr_lec_sec': None,       # where meeting times should go
        'curr_lecture': None,       # where lectures should go
        'is_letter_lecture': False  # whether lectures are denoted by letters
    }
    data = []
    print('Parsing rows...')
    for tr in trs:
        extract_data_from_row(tr, data, curr_state)
    print('Done.')
    return data
