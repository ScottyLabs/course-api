# @file parse_descs.py
# @brief Parses course information from course descriptions pages on
#        http://coursecatalog.web.cmu.edu/ into an object.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2014-12-13


import urllib.request
import urllib.parse
import re
import bs4


# String constants
DESC_URL = "https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails"


# @function: create_reqs_obj
# @brief: Creates an object representation of the given prerequisites/
#         corequisites.
# @param reqs: A string of required prerequisites/corequisites.
# @return: {'invert': Bool indicating whether the representation is inverted,
#           'reqs_list': List representation of the pre/corequisites}.
def create_reqs_obj(reqs):

    # Determines whether the data structure should be inverted by using regex
    # to determine whether the expression "(xx-xxx and xx-xxx"  is present; the
    # x's represent any digit 0-9.
    def is_inverted(reqs):
        groups = re.findall(r'\((\d{2})(-)(\d{3}) and (\d{2})(-)(\d{3})', reqs)
        return len(groups) > 0

    # Creates a list from a string by splitting it at the given conjunction
    # and then formats the list by removing whitespace and parentheses around
    # each list element.
    def split_course_list(reqs, conj):
        split_list = reqs.split(conj)
        formatted_list = []
        for item in split_list:
            formatted_item = item.strip().strip('()')
            formatted_list.append(formatted_item)
        return formatted_list

    # Creates a 2-dimensional list given the reqs string and the principal
    # conjunction.
    def create_reqs_list(reqs, conj):

        # Separates the requisites into course groups by the given conjunction
        course_groups = split_course_list(reqs, conj)
        anti_conj = 'or' if conj == 'and' else 'and'
        reqs_list = []

        for course_group in course_groups:
            inner_list = []
            courses = split_course_list(course_group, anti_conj)

            for course in courses:
                formatted_str = course.strip()
                inner_list.append(formatted_str)

            reqs_list.append(inner_list)

        return reqs_list

    if reqs == '' or reqs is None:
        invert = None
        reqs_list = None
    elif is_inverted(reqs):
        invert = True
        reqs_list = create_reqs_list(reqs, 'or')
    else:
        invert = False
        reqs_list = create_reqs_list(reqs, 'and')
    return {'invert': invert, 'reqs_list': reqs_list}


# @function parse_reqs
# @brief Parses out the prerequisites and corequisites of a course from the
#        HTML of the search app.
# @param soup BeautifulSoup of the page's HTML.
# @return (prereqs, coreqs)
def parse_reqs(soup):

    # Regex replacement function
    def correct_course(num):
        num = num.group(0)
        return num[:2] + '-' + num[2:]

    # Find text
    prereqs = soup.find(string='Prerequisites').parent.parent.dd.string
    coreqs = soup.find(string='Corequisites').parent.parent.dd.string

    # Remove extra whitespace
    prereqs = ' '.join(prereqs.split())
    coreqs = ' '.join(coreqs.split())

    # Add dashes to course numbers
    prereqs = re.sub(r'(\d{5})', correct_course, str(prereqs))
    coreqs = re.sub(r'(\d{5})', correct_course, str(coreqs))

    # Replace commas with "or" (seems to be an error in their system)
    prereqs = re.sub(',', 'or', str(prereqs))
    coreqs = re.sub(',', 'or', str(coreqs))

    # Return null if no pre/corequisites
    if prereqs == 'None':
        prereqs = None
    if coreqs == 'None':
        coreqs = None

    return (prereqs, coreqs)


# @function parse_full_names
# @brief      Obtains full names of instructors.
# @param      soup  BeautifulSoup of the page's HTML.
# @return     {<section>: [<name>]} Dictionary of list of names.
#
def parse_full_names(soup):
    dict_of_names = {}

    # Determine the column for Section.
    # Usually, column=2 for S(spring) and F(fall) and column=3 for M(summer).
    column = 2
    try:
        thtags = soup.find_all('table', class_='table-striped')[0]\
            .select('thead > tr > th')

        for i in range(len(thtags)):
            if thtags[i].text == 'Section':
                break
        column = i
    except:
        pass

    # Parse the names from the web page.
    try:
        for ultag in soup.find_all('ul', class_='instructor'):
            # Get the section this list of names belongs to
            section = ultag.parent.parent.find_all('td', recursive=False)[column]\
                .text.strip()

            # Put all the names into a list
            names = [litag.text for litag in ultag.find_all('li')]
            if names == []:
                names = ['Instructor TBA']
            if section:
                dict_of_names[section] = names

        # Fix the discrepancy between SOC table and the SOC api
        # if there's only one lecture, then
        # dict_of_names['Lec'] is dict_of_names['Lec 1']
        if 'Lec 1' in dict_of_names:
            dict_of_names['Lec'] = dict_of_names['Lec 1']
    except TypeError:
        pass

    return dict_of_names


# @function get_page
# @brief Gets a webpage as an object
# @param url: URL of the page to get.
# @return: The page as a BeautifulSoup html object, or None if an error
#        occurred.
def get_page(url):
    try:
        response = urllib.request.urlopen(url)
    except (urllib.request.URLError, ValueError):
        return None

    return bs4.BeautifulSoup(response.read(), 'html.parser')


# @function get_course_desc
# @brief Returns the description, coreqs and prereqs for a course.
# @param num: Course number as a 5 character string, no dash
# @param semester: Semester to lookup (S, F, or M for spring, fall or summer)
# @param year: Two digit year (for example, 2016 is 16)
# @return {
#   'desc': Course description,
#   'prereqs': Course prerequisites,
#   'prereqs_obj': Prerequisites as an object,
#   'coreqs': Course corequisites,
#   'coreqs_obj': Corequisites as an object
# }
def get_course_desc(num, semester, year):

    # Generate target URL
    params = {
        'COURSE': num,
        'SEMESTER': semester + year
    }
    url = DESC_URL + '?' + urllib.parse.urlencode(params)

    # Retrieve page
    soup = get_page(url)

    # Parse data
    desc = soup.find(id='course-detail-description').p.string
    (prereqs, coreqs) = parse_reqs(soup)
    names_dict = parse_full_names(soup)

    prereqs_obj = create_reqs_obj(prereqs)
    coreqs_obj = create_reqs_obj(coreqs)

    return {
        'desc': desc,
        'prereqs': prereqs,
        'prereqs_obj': prereqs_obj,
        'coreqs': coreqs,
        'coreqs_obj': coreqs_obj,
        'names_dict': names_dict
    }
