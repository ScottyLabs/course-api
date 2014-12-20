# Course API

The new version of the Scheduling API, now with prerequisites, course descriptions, and more!

## scripts/parse_descs.py

This script is used to get course data from http://coursecatalog.web.cmu.edu pages.

### Setup

Install the project requirements (including [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/bs4/doc)) by running:

```
$ pip install -r requirements.txt
```

###Usage

```
$ python scripts/parse_descs.py [INFILE] [OUTFILE]
```

`INFILE` is the path of a file containing a list of newline delineated fully qualified links to the pages to parse. A file which includes links to all departments pages is included in `scripts/schedule_pages.txt`, up to date as of 2014-12-15.

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