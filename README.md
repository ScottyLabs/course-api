# Course API

The new version of the Scheduling API, now with prerequisites, course descriptions, FCEs and more!

This project is structured as a number of scraper scripts which parse
information from various sources including the Course Catalog, the
Schedule of Classes, and the site for FCEs.

## Setup

The Scottylabs Course API is now available as a pip package! All you need to do to install is run:

```
$ pip install cmu-course-api
```

## Usage

To use from the command line, run:

```
$ cmu-course-api [SEMESTER] [OUTFILE]
$ cmu-course-api [SEMESTER] [OUTFILE] <USERNAME> <PASSWORD>
```

`SEMESTER` is the school semester for which you wish to retrieve scheduling data. It must be one of S, M1, M2, or F.

`OUTFILE` is a path to write the output JSON to.

`USERNAME` is the Andrew username used for authentication. If not specified, you will be prompted to input one.

`PASSWORD` is the Andrew password used for authentication. If not specified, you will be prompted to input one.

Alternatively, you can use the course API in your Python 3 projects:

```
import cmu_course_api

data = cmu_course_api.get_course_data(semester, username, password)
```

Then, `data` will contain the course information as a Python object.

## Minification

By default, all output data is stored as a minified JSON file. To get human readable JSON, use the command (for output file `out.json`):

```
python -m json.tool out.json
```

## Output format

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
lectures   | {}         | Lectures and sections for this semester. See the [Lectures section](#Lectures) for more info.
fces       | {}         | All historical FCEs, organized by section. See the [FCEs section](#FCEs) for more info.

### FCEs

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

### Lectures

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
