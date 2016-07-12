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
                    num = line[cat]
                    if len(num) == 4:
                        num = '0' + num
                    entry[categories[cat]] = num[:2] + '-' + num[2:]

                # If a category starts with a number, file it as a question
                elif categories[cat][0].isdigit():
                    entry['Questions'][categories[cat]] = line[cat]

                else:
                    entry[categories[cat]] = line[cat]

            results.append(entry)

    # Return as JSON
    return results
