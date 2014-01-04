# coding: utf-8


def date2text(date=None):
    """ Convert date to human-friendly string """
    return date.strftime('%-d %B %Y')


def doy_leap(date=None):
    """ Adjust day of year int to account for leap year.

        Not an ideal solution, but we are simply subtracting 1 from tm_yday if
        tm_year is found to be leap and tm_yday > 60 (Feb 29). Thus, Feb 29 is
        indistinguishable from March 1, but every year has 365 days.
    """

    doy = date.timetuple().tm_yday
    year = date.timetuple().tm_year

    if year % 4 == 0:
        if doy > 60:
            doy -= 1

    return doy
