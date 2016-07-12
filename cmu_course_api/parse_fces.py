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


# @function parse_fces
# @brief Parses FCE data from a CSV file to JSON.
# @param path: File location of CSV to parse from.
# @return: FCE data as JSON.
def parse_fces(path):

    results = []

    # Iterate through lines of CSV
    categories = []
    with open(path, 'r') as f:
        for line in csv.reader(f):
            if line[0] == 'Semester':
                categories = line
            else:
                entry = {}
                for cat in range(len(categories)):
                    if categories[cat] != '':
                        entry[categories[cat]] = line[cat]
                results.append(entry)

    # Return as JSON
    return results
