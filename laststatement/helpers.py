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


def printquery(statement, bind=None):
    """
    print a query, with values filled in
    for debugging purposes *only*
    for security, you should always separate queries from their values
    please also note that this function is quite slow
    """

    import sqlalchemy.orm
    if isinstance(statement, sqlalchemy.orm.Query):
        if bind is None:
            bind = statement.session.get_bind(
                statement._mapper_zero_or_none()
            )
        statement = statement.statement
    elif bind is None:
        bind = statement.bind

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(
                self, bindparam, within_columns_clause=False,
                literal_binds=False, **kwargs
        ):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause=within_columns_clause,
                literal_binds=literal_binds, **kwargs
            )

    compiler = LiteralCompiler(dialect, statement)
    print compiler.process(statement)
