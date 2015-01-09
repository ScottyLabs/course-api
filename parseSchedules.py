#!/usr/bin/env python
#
# parseSchedules.py
# Andrew Benson
#
# Parses scheduling information from the Schedule Of Classes for a
#     given school quarter and year
#
# Usage: python parseSchedules.py [QUARTER] [OUTFILE]
#
# QUARTER: The school quarter of the schedule desired
#     (one of S/M1/M2/F)
# OUTFILE: An file where resulting JSON will be written

# for reference, here is what each column number refers to in the raw HTML
# 0: COURSE i.e. "15122"
# 1: TITLE i.e. "Principles of Imperative Computation"
# 2: UNITS i.e. "10.0"
# 3: LEC/SEC i.e. "Lec 1", "M"
# 4: DAYS i.e. "TR"
# 5: BEGIN i.e. "09:00AM"
# 6: END i.e. "10:20AM"
# 7: BUILDING/ROOM i.e. "DH 2210"
# 8: LOCATION i.e. "Pittsburgh, Pennsylvania"
# 9: INSTRUCTOR i.e. "Simmons, Wright"

from urllib2 import urlopen
import bs4
import json
import sys

def getPage(quarter):
  '''
  return a BeautifulSoup that represents the HTML page specified by quarter

  quarter: one of ["S", "M1", "M2", "F"]

  if getPage fails, None will be returned
  '''
  # error checking
  quarter = quarter.upper()
  if quarter not in ["S", "M1", "M2", "F"]:
    return None

  # determine url
  url = None
  if quarter == "S":
    url = "http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_spring.htm"
  elif quarter == "M1":
    url = "http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_summer_1.htm"
  elif quarter == "M2":
    url = "http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_summer_2.htm"
  elif quarter == "F":
    url = "http://enr-apps.as.cmu.edu/assets/SOC/sched_layout_fall.htm"

  # obtain and return data
  try:
    response = urlopen(url)
  except:
    return None

  return bs4.BeautifulSoup(response.read())

def getTableRows(page):
  '''
  return a list of relevant <tr> bs4 Tags

  page: a BeautifulSoup with a <table> with interesting rows
  '''
  # the first row is a weird empty row
  # the second row is the header row (Course, Title, Units, etc.)
  return page.find_all("tr")[2:]

def fixKnownErrors(page):
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
    ^not fixed yet
  '''
  # TODO: finish implement the spec
  for rowTag in getTableRows(page):
    # detect department name. if found, bundle the tds into a tr
    row = processRow(rowTag)
    if row[0] and not row[0].isdigit():
      tds = []
      lastNot = rowTag
      # find all tds up to next non-td
      while True:
        # sometimes we hit the end of the document due to corrupted bs4 parsing
        if not lastNot.next_sibling:
          break
        # idk why there are newlines, but we ignore them
        elif lastNot.next_sibling == "\n":
          lastNot = lastNot.next_sibling
          continue
        # just in case we don't hit corrupted bs4 parsing after all
        elif lastNot.next_sibling.name != "td":
          break
        # extract removes it from the document, and it acts like a doubly-linked
        # list, so it patches the next_sibling pointers for us
        else:
          tds.append(lastNot.next_sibling.extract())
      # make a new tr tag, add in the tds
      tr = page.new_tag("tr")
      counter = 0
      for td in tds:
        tr.append(td)
        counter += 1
      # ensure that the new row has 10 columns
      while counter < 10:
        tr.append(page.new_tag("td"))
        counter += 1
      # paste it back in
      rowTag.insert_after(tr)
    else:
      # ensure that the new row has 10 columns
      i = len(row)
      while i < 10:
        rowTag.append(page.new_tag("td"))
        i += 1
       
def processRow(rowTag):
  '''
  return rowTag as a list of HTML-tag-stripped strings

  rowTag: a <tr> bs4 Tag, where each column contains exactly one string
  '''
  res = []
  for tag in rowTag.children:
    if not tag.string or tag.string.isspace():
      res.append(None)
    else:
      res.append(tag.string)
  return res

def parseRow(row):
  '''
  return (kind, data) where kind represents the kind of data returned

  row: list of HTML-tag-stripped strings that represent a data table row

  example return values:
  ("department", "Computer Science")
  ("course", { num: 15122, title: "Principles of Imperative...", ...})
  ("lecture", { number: "Lec 1", days: ["T", "R"], ...})
  ("section", { letter: "N", days: ["M"], ...})
  (None, {})
  '''
  # local helper functions
  def parseLecture(lectureData):
    '''
    return a dictionary containing the values in lectureData
    '''
    data = parseMeeting(lectureData)
    data["number"] = lectureData[3]
    data["sections"] = []
    return data

  def parseSection(sectionData):
    '''
    return a dictionary containing the values in sectionData
    '''
    data = {}
    data["meetings"] = [parseMeeting(sectionData)]
    data["letter"] = sectionData[3]
    return data

  def parseMeeting(meetingData):
    '''
    return a dictionary containing the values in meetingData
    '''
    data = {}
    data["days"] = meetingData[4]
    data["begin"] = meetingData[5]
    data["end"] = meetingData[6]
    data["room"] = meetingData[7]
    data["location"] = meetingData[8]
    if meetingData[9] == "Instructor TBA":
      data["instructor"] = ["Instructor TBA"]
    elif meetingData[9]:
      data["instructor"] = [inst for inst in meetingData[9].split(", ")]
    else:
      data["instructor"] = None
    return data

  # the data can be very irregular, so we wrap with try-except
  try:
    # case department (determined by a non-empty, non-numeric string course)
    if row[0] and not row[0].isdigit():
      return ("department", row[0])
    # case course (determined by having a numeric course)
    elif row[0] and row[0].isdigit():
      data = {}
      data["num"] = int(row[0])
      data["title"] = row[1]
      data["units"] = row[2]
      data["lectures"] = [parseLecture(row)]
      return ("course", data)
    # case lecture (determined by some form of "Lec" in the Lec/Sec column)
    elif row[3] and "lec" in row[3].lower():
      return ("lecture", parseLecture(row))
    # case section (everything else, hopefully)
    else:
      # it's possible for a section row not to have a section letter
      if row[3]:
        return ("section", parseSection(row))
      else:
        return ("section", parseMeeting(row))
  except Exception as e:
    print "Failed to parse row: %s; %s" %(row, e)
    return (None, {})

def parseDataForQuarter(quarter):
    # get the HTML page, fix its errors, and find its table rows
    print "Requesting the HTML page from the network..."
    page = getPage(quarter)
    if not page:
      print "Failed to obtain the HTML document! Check your internet "+ \
            "connection and make sure your quarter is one of S, M1, M2, or F."
      sys.exit()
    print "Done."
    print "Fixing errors on page..."
    fixKnownErrors(page)
    print "Done."
    print "Finding table rows on page..."
    trs = getTableRows(page)
    print "Done."
    # parse each row and insert it into 'data' as appropriate
    currCourses = None
    currCourse = None
    currLecture = None
    currSection = None
    data = []
    print "Parsing rows..."
    for tr in trs:
        (kind, rowData) = parseRow(processRow(tr))
        if kind == "department":
            currCourses = []
            data.append({"department":rowData, "courses":currCourses})
        elif kind == "course":
            currCourse = rowData
            currLecture = rowData["lectures"][0]
            currCourses.append(rowData)
        elif kind == "lecture":
            currLecture = rowData
            currCourse["lectures"].append(rowData)
        elif kind == "section":
            # if a letter exists, it's a new section
            if rowData.has_key("letter"):
                currSection = rowData
                currLecture["sections"].append(rowData)
            # else, it's another meeting time for an existing section
            else:
                # sometimes the instructor won't be filled in
                if not rowData["instructor"]:
                    rowData["instructor"] = \
                            currSection["meetings"][-1]["instructor"]
                currSection["meetings"].append(rowData)
        else:
            raise Exception("Unexpected kind: %s", kind)
    print "Done."
    return data

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print "Usage: parseSchedules [QUARTER] [OUTFILE]"
    sys.exit()

  # parse data
  data = parseDataForQuarter(sys.argv[1])

  # write to output file
  print "Writing to output file..."
  try:
    with open(sys.argv[2], 'w') as outfile:
      json.dump(data, outfile)
      print "Done."
  except:
    print "An error occurred when writing the data to the given file."
