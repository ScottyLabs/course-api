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
#        Usage: python parse_fces.py [OUTFILE] <USERNAME PASSWORD>
#
#        OUTFILE: Where to place resulting JSON.
#        USERNAME: Andrew username to use to download data.
#        PASSWORD: Andrew password to use to download data.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-01-22

import sys
import json
import bs4
import copy
import cmu_auth
import urllib.parse
import getpass


# Constants
USAGE = 'Usage: python parse_fces.py [OUTFILE] <USERNAME PASSWORD>'
LOGIN_URL = 'https://cmu.smartevals.com/secure/Login.aspx'
SOURCE_URL = 'https://student.smartevals.com/reporting/SurveyResults.aspx'
URL_PARAMS = {
    'xp': 't',
    'hg': 't',
    'dep': 'all',
    't': 'all',
    'lvty': 'all/all/all',
    'st': 'meantext',
    'sat': 'all',
    'cat': 'all',
    'q': 'all',
    'y': 'all',
    'gb': 'CourseID',
    'b': 'all',
    'c': 'all',
    'cg': 'all',
    'u': 'all',
    'ds': 'normal',
    'srfall': 'Y'
}
FORM_DATA = {
    '_ctl0:cphContent:rddset:sfexporter:drp_FileType': 'msoXML',
    '_ctl0:cphContent:rddset:sfexporter:chk_Defaults': 'on',
    '_ctl0:cphContent:rddset:sfexporter:chk_ShowColumnTitles': 'on',
    '_ctl0:cphContent:rddset:sfexporter:btnSubmit': 'Export',
    '_ctl0:chkColumns_0': 'on',
    '_ctl0:chkColumns_1': 'on',
    '_ctl0:chkColumns_2': 'on',
    '_ctl0:chkColumns_5': 'on',
    '_ctl0:chkColumns_6': 'on',
    '_ctl0:chkColumns_7': 'on',
    '_ctl0:chkColumns_8': 'on',
    '_ctl0:chkColumns_9': 'on',
}
DIVS = [683, 693, 685, 691, 684, 687, 690, 2369, 733]


# @function authenticate
# @brief Gets the authenication token that needs to be included to query FCE
#        data.
# @param username: Andrew username to use for authentication.
# @param password: Andrew password to use for authentication.
def authenticate(username, password):
    # Login
    s = cmu_auth.authenticate(LOGIN_URL, username, password)
    login_page = s.get(LOGIN_URL)
    soup = bs4.BeautifulSoup(login_page.text)

    # Parse needed authenication token
    login_link = soup.find('a', {'id': 'HyperLink1'})['href']
    login_link_queries = urllib.parse.urlparse(login_link)[4]
    hdnPersonAuth = urllib.parse.parse_qs(login_link_queries)['a2e'][0]

    return hdnPersonAuth


# @function download_fces
# @brief Downloads FCE data from the smartevals website as MSXML.
# @param div: The smartevals website divides departments into 'div''s seemingly
#        arbitrarily, each one having a code.
# @param username: Andrew username to use for authentication.
# @param password: Andrew password to use for authentication.
# @param authtoken: Authenication token returned by authenticate.
# @return: Raw text for the MSXML file for this division's FCE data
def download_fces(div, username, password, authtoken):
    # Create target URL
    parameters = copy.copy(URL_PARAMS)
    parameters['div'] = div
    url = SOURCE_URL + '?' + urllib.parse.urlencode(parameters)

    # Build form input
    formdata = copy.copy(FORM_DATA)
    formdata['_ctl0:hdnPersonAuth'] = authtoken

    # Get viewstate
    s = cmu_auth.authenticate(url, username, password)
    export_page = s.get(url, data=formdata).content
    soup = bs4.BeautifulSoup(export_page)
    viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
    formdata['__VIEWSTATE'] = viewstate

    # Download output MSXML
    pst2 = s.post(url, data=formdata)
    return pst2.text


# @function parse_table
# @brief Parses FCE data from a BeautifulSoup XML table object.
# @param table: Table object from an FCE XML file.
# @return [{}]: Array of data which represents FCE data by section.
def parse_table(table):
    rows = table.find_all('row')
    columns = []
    result = []
    question_start = 0

    for row in rows:
        cells = row.find_all('cell')
        if len(cells) > 0 and cells[0].string == 'Semester':
            # Columns are not consistent in a table - update them when
            # new labels are found.
            columns = [lbl.string.strip() for lbl in row if lbl.string.strip()]
            question_start = next((i for i, col in enumerate(columns)
                                   if col[0].isdigit()), len(columns))
        else:
            # Remove empty cells
            cells = cells[:len(columns)]

            # Build object to represent this section
            obj = {}
            questions = {}
            for index, cell in enumerate(cells):
                # Parse cell value
                value = cell.string.strip()
                if not value:
                    value = None
                if index < question_start:
                    if cell.data['ss:type'] == 'Number' and value:
                        value = int(value)
                    obj[columns[index]] = value
                else:
                    if value:
                        value = float(value)
                    questions[columns[index]] = value

            obj['Questions'] = questions
            result.append(obj)

    return result


# @function parse_fces
# @brief Downloads and parses FCE data to JSON.
# @param username: Andrew username to use for authentication.
# @param password: Andrew password to use for authentication.
# @return: FCE data for all departments and years as JSON.
def parse_fces(username, password):
    data = []

    # Authenticate
    print('Authenticating...')
    authtoken = authenticate(username, password)

    # Iterate through all colleges
    for div in DIVS:
        # Download FCE data
        print('Downloading data for div ' + str(div) + '...')
        downloaded = download_fces(div, username, password, authtoken)

        # Parse data into dictionary
        print('Parsing...')
        soup = bs4.BeautifulSoup(downloaded)
        data += parse_table(soup.find('table'))

    # Return as JSON
    return data


if __name__ == '__main__':
    # Verify arguments
    if not (len(sys.argv) == 4 or len(sys.argv) == 2):
        print(USAGE)
        sys.exit()

    outpath = sys.argv[1]

    if (len(sys.argv) == 2):
        print('Please input your Andrew username and password. '
              'We never store your login info.')
        username = input('Username: ')
        password = getpass.getpass()
    else:
        username = sys.argv[2]
        password = sys.argv[3]

    # Get and write out JSON
    print('Parsing FCEs. This will take a few minutes...')
    data = parse_fces(username, password)

    print('Writing data...')
    with open(outpath, 'w') as outfile:
        json.dump(data, outfile)

    print('Done!')
