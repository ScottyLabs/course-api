# @brief Parses FCE data for MSXML files downloaded from
#        http://cmu.smartevals.com.
#
#        MSXML is used to compensate for a bug in the FCE export feature: The
#        first few lines of any output are cut off. MSXML is the only format to
#        have enough useless metadata at the beginning of the file to prevent
#        important data from being cutoff.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-01-22


import csv
import re


# @function parse_fces
# @brief Parses FCE data from a CSV file to JSON.
# @param path: File location of CSV to parse from.
# @return: FCE data as JSON.
def parse_fces(path):

    results = []
    categories = []

    # Iterate through lines of CSV
    with open(path, 'r') as f:
        for line in csv.reader(f):

            # If this row specifies new column tags, update our categories
            if line[0] == 'Semester':
                categories = line
                continue

            entry = {}
            entry['Questions'] = {}

            for cat in range(len(categories)):

                # Set null if no data supplied
                if line[cat] == '':
                    line[cat] = None

                # Skip unused columns
                if categories[cat] == '':
                    continue

                # Ensure course IDs have the proper format (##-###)
                if categories[cat] == 'Course ID' and line[cat] != None:
                    if re.search('^[0-9]+$', line[cat]):
                        fmt = "%05d" % int(line[cat])
                        entry[categories[cat]] = "%s-%s" % (fmt[:2], fmt[2:])
                    else:
                        entry[categories[cat]] = line[cat]

                # If a category starts with a number, file it as a question
                elif categories[cat][0].isdigit():
                    if line[cat] == None:
                        entry['Questions'][categories[cat]] = None
                    else:
                        entry['Questions'][categories[cat]] = float(line[cat])

                # General categories
                elif line[cat] == None:
                    entry['Questions'][categories[cat]] = None

                elif re.search('^[0-9]+$', line[cat]):
                    entry[categories[cat]] = int(line[cat])

                elif re.search('^[0-9]+\.[0-9]+$', line[cat]):
                    entry[categories[cat]] = float(line[cat])

                else:
                    entry[categories[cat]] = line[cat]

            results.append(entry)

    # Return as JSON
    return results
