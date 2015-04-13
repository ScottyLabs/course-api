# Course API

The new version of the Scheduling API, now with prerequisites, course descriptions, and more!

This project is structured as a number of scraper scripts which parse
information from various sources including the Course Catalog, the
Schedule of Classes, and the site for FCEs.

## Setup

Install the project requirements (including [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/bs4/doc) and [cmu_auth](http://github.com/willcrichton/cmu_auth)) by running:

```
$ pip install -r requirements.txt
```

## Minification

By default, all output data is stored as a minified JSON file. To get human readable JSON, use the command (for output file `out.json`):

```
python -m json.tool out.json
```

## course-api.py

This script retrieves data from all three datasets for a specific semester.

###Usage

```
$ python3 course-api.py [SEMESTER] [OUTFILE]
$ python3 course-api.py [SEMESTER] [OUTFILE] <USERNAME> <PASSWORD>
```

`SEMESTER` is the school semester for which you wish to retrieve scheduling data. It must be one of S, M1, M2, or F.

`OUTFILE` is a path to write the output JSON to.

`USERNAME` is the Andrew username used for authentication. If not specified, you will be prompted to input one.

`PASSWORD` is the Andrew password used for authentication. If not specified, you will be prompted to input one.

### Output format

Scraped data is output in the following form:

```
{
    "courses": {
        ...,
        "15122": {
            "name": "Principles of Imperative Computation"
            "department": "Computer Science"
            "units": 10.0
            "semester": ["F", "S"]
            "desc": "For students with a basic understanding of programming..."
            "prereqs": "15-112"
            "coreqs": "15-151 and 21-127"
            "lectures": <Lecture object>
        },
        ...
    }
    "fces": <FCEs object>
}
```

Field      | Type       | Description
-----------|------------|------------
courses    | {}         | Object containing course information, with course numbers as keys
name       | String     | Course name
department | String     | Department name
units      | float      | Units awarded by course
semester   | [String]   | List of semesters where the course is offered ("F" = Fall, "S" = Spring, "M" = Summer)
desc       | String     | Course description
prereqs    | String     | Course prerequisites as a string
coreqs     | String     | Course corequisites as a string
lectures   | {}         | Lectures and sections for this semester. See the `parse_schedules.py` [documentation](#output-format-3) for more info.
fces       | {}         | All historical FCEs, organized by section. See the `parse_fces.py` [documentation](#output-format-2) for more info.

## scripts/parse_descs.py

This script is used to get course data from http://coursecatalog.web.cmu.edu pages.

###Usage

```
$ python scripts/parse_descs.py [INFILE] [OUTFILE]
```

`INFILE` is the path of a file containing a list of newline delineated fully qualified links to the pages to parse. A file which includes links to all departments' pages is included in `data/schedule_pages.txt`, up to date as of 2014-12-15.

`OUTFILE` is a path to write the output JSON to.

### Output format

Scraped data is output in the following form:

```
[
    ...,
    {
        "num": 15122
        "name": "Principles of Imperative Computation"
        "units": 10.0
        "semester": ["F", "S"]
        "desc": "For students with a basic understanding of programming..."
        "prereqs": "15-112"
        "coreqs": "15-151 and 21-127"
    },
    ...
]
```

Field    | Type       | Description
---------|------------|------------
num      | int        | Course number (without dash)
name     | String     | Course name
units    | float      | Units awarded by course
semester | [String]   | List of semesters where the course is offered ("F" = Fall, "S" = Spring, "U" = Summer)
desc     | String     | Course description
prereqs  | String     | Course prerequisites as a string.
coreqs   | String     | Course corequisites as a string.

## scripts/parse_fces.py

This script is used to get FCE data from https://cmu.smartevals.com/ pages.

### Usage

```
$ python3 scripts/parse_fces.py [OUTFILE]
$ python3 scripts/parse_fces.py [OUTFILE] <USERNAME> <PASSWORD>
```

`OUTFILE` is a path to write the output JSON to.

`USERNAME` is the Andrew username used for authentication. If not specified, you will be prompted to input one.

`PASSWORD` is the Andrew password u sed for authenication. If not specified, you will be prompted to input one.

### Output format

Beware that any field below may have `null` instead of the expected value.

Output data is formatted as a list of sections, each with their own statistics:

```
[
    ...,
    {
        "Course ID": 12671,
        "Course Name": "FND CONCPT COMP CEE",
        "Dept": "CEE",
        "Enrollment": 7,
        "Instructor": "FINGER, S.",
        "Resp. Rate %": "71%",
        "Responses": 5,
        "Section": "A3",
        "Semester": "Spring",
        "Type": "Lect",
        "Year": 2015,
        "Questions": {
            "1: Hrs Per Week 9": 10.0,
            "2: Interest in student learning": 4.8,
            "3: Explain course requirements": 4.4,
            "4: Clear learning goals": 4.4,
            "5: Feedback to students": 5.0,
            "6: Importance of subject": 4.4,
            "7: Explains subject matter": 4.8,
            "8: Show respect for students": 5.0,
            "9: Overall teaching": 4.8
            "10: Overall course": 4.6,
        }
    },
    ...
]
```

All fields are subject to change depending on how CMU's departments decide to structure their FCEs for a given semester. The fields available and their names are very likely to be different between semesters and departments. Please see https://cmu.smartevals.com/ for the exact format. All keys are column names corresponding to their value. Questions (columns starting with a number) are sorted into their own "Questions" field, with the question as the key and the result as a float value.

## scripts/parse_schedules.py

This script is used to get scheduling data from https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/completeSchedule pages.

### Usage

```
$ python3 scripts/parse_schedules.py [QUARTER] [OUTFILE]
```

`QUARTER` is the school quarter for which you wish to retrieve scheduling data. It must be one of S, M1, M2, or F.

`OUTFILE` is a path to write the output JSON to.

### Output format

Beware that any field below may have `null` or "TBA" instead of the expected string as a value.

Scraped data consists of a list of departments. A department has the form:

```
[
    ...,
    {
        "courses": [
            ...,
            <course object>,
            ...
        ],
        "department": "Computer Science"
    },
    ...
]
```

Field      | Type     | Description
-----------|----------|------------
courses    | [course] | List of courses in the department. See below for description of a course object.
department | String   | Department name

A course has the form:

```
{
    "lectures": [
        ...,
        <lecture object>,
        ...
    ],
    "num": "15122",
    "title": "Principles of Imperative Computation",
    "units": "10.0"
}
```

Field    | Type      | Description
---------|-----------|------------
lectures | [lecture] | List of lectures in the course. See below for description of a lecture object.
num      | String    | Course number (without dash)
title    | String    | Course name
units    | String    | Units awarded by course. Note that this isn't limited to floats - it could be a range, or VAR.

A lecture has the form:

```
{
    "instructors": [
        "Kosbie",
        "Andersen"
    ],
    "lecture": "Lec 1",
    "meetings": [
        ...,
        <meeting object>,
        ...
    ],
    "sections": [
        ...,
        <section object>,
        ...
    ]
}
```

Field       | Type      | Description
------------|-----------|------------
instructors | [String]  | List of last names of instructors of the lecture.
lecture     | String    | The lecture's identifier. Typically a capital letter or something like "Lec 1".
meetings    | [meeting] | List of meetings for the lecture. See below for description of a meeting object.
sections    | [section] | List of sections for the lecture. See below for description of a section object.

A section has the form:

```
{
    "instructors": [
        "Simmons"
    ],
    "meetings": [
        ...,
        <meeting object>,
        ...
    ],
    "section": "N"
}
```

Field       | Type      | Description
------------|-----------|------------
instructors | [String]  | List of last names of instructors of the section.
meetings    | [meeting] | List of meetings for the section. See below for description of a meeting object.
section     | String    | The section's identifier. Almost always a capital letter.

A meeting has the form:

```
{
    "begin": "03:30PM",
    "days": "F",
    "end": "04:20PM",
    "location": "Pittsburgh, Pennsylvania",
    "room": "PH 226B"
}
```

Field    | Type   | Description
---------|--------|------------
begin    | String | The time at which the lecture or section begins.
days     | String | The days the lecture or section meets at this time, abbreviated and concatenated.
end      | String | The time at which the lecture or section ends.
location | String | The location of the lecture or section's meeting. Probably Pittsburgh, Pennsylvania or Doha, Qatar.
room     | String | The building and/or room in which the lecture or section meets.

Note that the days of the week are abbreviated as U,M,T,W,R,F,S respectively.
