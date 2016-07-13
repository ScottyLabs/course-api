# Course API

The new version of the Scheduling API, now with prerequisites, course descriptions, FCEs and more!

This project is structured as a number of scraper scripts which parse
information from various sources including the Course Catalog, the
Schedule of Classes, and the site for FCEs.

## Setup

The Scottylabs Course API is now available as a pip package! All you need to do to install is run:

```
$ pip3 install cmu-course-api
```

## Course Schedules & Descriptions Usage

To get course schedules and descriptions from the command line, run:

```
$ cmu-course-api [SEMESTER] [OUTFILE]
```

`SEMESTER` is the school semester for which you wish to retrieve scheduling data. It must be one of S, M1, M2, or F.

`OUTFILE` is a path to write the output JSON to.

Alternatively, you can use the course API in your Python 3 projects:

```python
import cmu_course_api

data = cmu_course_api.get_course_data(semester)
```

Then, `data` will contain the course information as a Python object.

See [Course output format](#course-output-format) for details.

## FCEs Usage

To parse FCE data, download the relevant data set from the [CMU FCE website](https://cmu.smartevals.com) by logging in, clicking "See Results from Past Years", then the Excel icon at the lop left of the table. Make sure to choose CSV format. Place all files at the top level of a folder.

Parse the data by running the following from the command line:

```
$ cmu-fce-api [FOLDER] [OUTFILE]
```

`FOLDER` is the folder containing CSV files to parse.

`OUTFILE` is a path to write the output JSON to.

Alternatively, you can use the FCE API in your Python 3 projects:

```python
import cmu_course_api

fces = cmu_course_api.parse_fces(csvpath)
```

Then `fces` will contain the FCE data in the file `csvpath`.

See [FCE output format](#fce-output-format) for details.

## Minification

By default, all output data is stored as a minified JSON file. To get human readable JSON, use the command (for output file `out.json`):

```
$ python -m json.tool out.json
```

## Course output format

Scraped data is output in the following form:

```
{
    "courses": {
        ...,
        "15-122": {
            "name": "Principles of Imperative Computation",
            "department": "Computer Science",
            "units": 10.0,
            "desc": "For students with a basic understanding of programming...",
            "prereqs": "15-112",
            "prereqs_obj": {"invert": false, "reqs_list": [["15-112"]] },
            "coreqs": "15-151 and 21-127",
            "coreqs_obj": {"invert": false, "reqs_list": [["21-127"],["15-151"]] },
            "lectures": <Meeting object>,
            "sections": <Meeting object>
        },
        ...
    },
    "rundate": "2016-05-27",
    "semester": "Spring 2016"
}
```

Field      | Type       | Description
-----------|------------|------------
courses    | {}         | Object containing course information, with course numbers as keys
name       | String     | Course name
department | String     | Department name
units      | float      | Units awarded by course. Null if the number of units is not specified or variable (common for independent study)
desc       | String     | Course description
prereqs    | String     | Course prerequisites as a string
prereqs_obj| Object     | Course prerequisites as an object representation
coreqs     | String     | Course corequisites as a string
coreqs_obj | Object     | Course corequisites as an object representation
lectures   | {}         | Lectures for this semester. See the [Meetings section](#meetings) for more info.
sections   | {}         | Sections for this semester. See the [Meetings section](#meetings) for more info.
rundate    | String     | Date that this JSON blob was generated in ISO format (YYYY-MM-DD).
semester   | String     | Semester that this data's schedules represent.

### Prerequisites/Corequisites Object Representation:

The fields prereqs_obj and coreqs_obj are object representations of a course's prerequisites/corequisites respectively. Each of these objects has a field "invert", which
is a boolean, and a field "reqs_list" which is a 2-dimensional list representation of the requisites. If a course does not have any prerequisites/corequisites then the
fields of the corresponding object will be null.

Field       | Type       | Description
------------|------------|------------
invert      | Boolean    | Boolean that indicates whether the reqs_list logic is inverted or not.
reqs_list   | [[String]] | 2-dimensional list representation of prerequisites/corequisites

In most cases, courses will have requisites with the invert field equal to false, this will be the primary representation. Under the primary representation, the elements
inside the inner lists operate under 'or' logic while the inner lists with respect to other inner lists operate under 'and' logic. If the invert field is true then the
primary representation is reversed.

######Invert = false (Primary Representation):

[ [ A ] ]                    => "A"

[ [ A, B ] ]                 => "A or B"

[ [ A ], [ B ] ]               => "A and B"

[ [ A, B ], [ C ] ]            => "(A or B) and C"

[ [ A, B ], [ C ], [ D, E, F ] ] => "(A or B) and C and (D or E or F)"


###### Invert = true:

[ [ A ] ]                    => "A"

[ [ A, B ] ]                 => "A and B"

[ [ A ], [ B ] ]               => "A or B"

[ [ A, B ], [ C ] ]            => "(A and B) or C"

[ [ A, B ], [ C ], [ D, E, F ] ] => "(A and B) or C or (D and E and F)"


###### Examples:

{"invert": false, "reqs_list": [ [ "15-213", "18-243" ], [ "18-370", "18-396" ] ] } => "(15-213 or 18-243) and (18-370 or 18-396)"

{"invert": true,"reqs_list": [ [ "18-320", "18-300" ], [ "18-402" ] ] }          => "(18-320 and 18-300) or 18-402"

### Meetings

A meeting has the form:

```
{
    "instructors": [
        "Kosbie, David",
        "Andersen, David"
    ],
    "name": "Lec 1",
    "times": [
        ...,
        <time object>,
        ...
    ]
}
```

Field       | Type      | Description
------------|-----------|------------
instructors | [String]  | List of names of instructors of the meeting. A name is formated as "Last, First".
name        | String    | The meetings's identifier. Typically a capital letter or something like "Lec 1".
times       | [time]    | List of meeting times for the meeting. See below for description of a time object.

A time has the form:

```
{
    "begin": "03:30PM",
    "days": [1, 3, 5],
    "end": "04:20PM",
    "location": "Pittsburgh, Pennsylvania",
    "building": "PH",
    "room": "226B"
}
```

Field    | Type     | Description
---------|----------|------------
begin    | String   | The time at which the lecture or section begins. This field is null if times have not been announced yet.
days     | [int]    | The days the lecture or section meets at this time, in a list of integers. Days are numbered from Sunday (at 0) to Saturday (at 6). This field is null if times have not been announced yet.
end      | String   | The time at which the lecture or section ends. This field is null if times have not been announced yet.
location | String   | The location of the lecture or section's meeting. Probably Pittsburgh, Pennsylvania or Doha, Qatar.
building | String   | The building in which the lecture or section meets. Null if the meeting location is TBA.
room     | String   | The room in which the meeting is held. Null if the meeting location is TBA.

## FCE output format

Beware that any field below may have `null` instead of the expected value.

Output data is formatted as a list of sections, each with their own statistics:

```
[
    ...,
    {
        "Course ID": "12-671",
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


## Submitting New Versions

This section is directed towards maintainers.

To upload a new version of the Course API to PiPy (so it's accessable through pip):

1. Increment the version number in `setup.py`. We use [semantic versioning](http://semver.org), so in a version `x.y.z`, `z` should be incremented for bugfixes, `y` for new features, and `x` for versions that break compatibility.
2. To upload a new distribution, run `python3 setup.py register sdist upload` from the root of the project. Use `ScottyLabs` as the username. The password can be found on the ScottyLabs Google Drive password store.
