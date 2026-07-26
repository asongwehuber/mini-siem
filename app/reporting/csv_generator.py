import csv


def create_csv(headers, rows, filename):
    """
    Creates a CSV file.

    Parameters
    ----------
    headers : list
    rows : list[list]
    filename : str
    """

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(headers)

        writer.writerows(rows)