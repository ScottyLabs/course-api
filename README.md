# Course API

The new version of the Scheduling API, now with prerequisites, course descriptions, and more!

## Setup

Install the project requirements (including [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/bs4/doc)) by running:

```
$ pip install -r requirements.txt
```

## scripts/parse_descs.py

This script is used to get course data from http://coursecatalog.web.cmu.edu pages.

###Usage

```
$ python scripts/parse_descs.py [INFILE] [OUTFILE]
```

`INFILE` is the path of a file containing a list of newline delineated fully qualified links to the pages to parse. A file which includes links to all departments pages is included in `data/schedule_pages.txt`, up to date as of 2014-12-15.

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
units    | int        | Units awarded by course
semester | [String]   | List of semesters where the course is offered ("F" = Fall, "S" = Spring, "U" = Summer)
desc     | String     | Course description
prereqs  | String     | Course prerequisites as a string.
coreqs   | String     | Course corequisites as a string.

By default, this data is stored minified in the output file. To get human readable JSON, use the command (for output file `out.json`):

```
python -m json.tool out.json
```

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
        "deparment": "Computer Science"
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

By default, this data is stored minified in the output file. To get human readable JSON, use the command (for output file `out.json`):

```
python -m json.tool out.json
```
