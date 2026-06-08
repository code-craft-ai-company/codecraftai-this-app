"""
    Testbase conversion of the ``Context`` / ``ContextCursor`` unit tests.

    These tests exercise path validation, insert/lookup/remove semantics,
    default-value behaviour, cursor access, template filling, and error
    raising on the ``ccai.thisapp.context`` module. Each test is an
    independent module-level ``test_*`` function; assertions use bare
    ``assert`` so an ``AssertionError`` is reported as a Failure and any
    other exception as an Error.
"""

from ccai.thisapp.context import Context, ContextCursor, validate_path_name


def test_validate_path_name_simple() -> None:
    """
        A leading-slash path with two segments validates to those two
        segments, and a trailing slash is ignored.
    """
    parts = validate_path_name('/level1/level2')
    assert parts == ['level1', 'level2']
    trailing = validate_path_name('/level1/level2/')
    assert trailing == ['level1', 'level2']
    return


def test_validate_path_name_single_segment_allows_dot() -> None:
    """
        A single un-slashed segment containing a dot is treated as one
        literal segment.
    """
    parts = validate_path_name('context.var')
    assert parts == ['context.var']
    return


def test_context_insert_and_lookup() -> None:
    """
        A value inserted at a path can be looked up via both the string
        path and the equivalent list-of-segments path.
    """
    ctx = Context()
    ctx.insert('/a/b', 1)
    assert ctx.lookup('/a/b') == 1
    assert ctx.lookup(['a', 'b']) == 1
    return


def test_context_exists_and_remove() -> None:
    """
        ``exists`` reports presence, ``remove`` returns and deletes the
        value, and removing a non-existent path is a no-op when
        ``ignore_missing`` is True.
    """
    ctx = Context()
    ctx.insert('/a/b', 1)
    assert ctx.exists('/a/b')
    removed = ctx.remove('/a/b')
    assert removed == 1
    assert not ctx.exists('/a/b')

    # Removing a non-existent path should not raise when ignore_missing=True
    assert ctx.remove('/c/d', ignore_missing=True) is None
    return


def test_context_lookup_default_value() -> None:
    """
        Looking up a missing path with a default both returns the default
        and persists it for subsequent lookups.
    """
    ctx = Context()
    value = ctx.lookup('/x/y', default=5)
    assert value == 5
    assert ctx.lookup('/x/y') == 5
    return


def test_context_lookup_default_dict_returns_cursor() -> None:
    """
        Looking up a missing path with a dict default returns a
        ``ContextCursor`` whose inserts are visible through the root context.
    """
    ctx = Context()
    cursor = ctx.lookup('/d', default={})
    assert isinstance(cursor, ContextCursor)
    cursor.insert('/name', 'foo')
    assert ctx.lookup('/d/name') == 'foo'
    return


def test_context_contains_and_item_access() -> None:
    """
        Item-style assignment is observable via ``in`` and item-style
        retrieval.
    """
    ctx = Context()
    ctx['key'] = 123
    assert 'key' in ctx
    assert ctx['key'] == 123
    return


def test_context_cursor_fill_template() -> None:
    """
        A cursor over a dict value can fill a printf-style template from its
        keys.
    """
    ctx = Context()
    ctx.insert('/info', {'name': 'foo', 'value': 42})
    cursor = ctx.lookup('/info')
    assert isinstance(cursor, ContextCursor)
    filled = cursor.fill_template('Name:%(name)s Value:%(value)s')
    assert filled == 'Name:foo Value:42'
    return


def test_lookup_raise_error() -> None:
    """
        Looking up a missing path with ``raise_error=True`` raises a
        ``LookupError``.
    """
    ctx = Context()
    raised = False
    try:
        ctx.lookup('/missing', raise_error=True)
    except LookupError:
        raised = True
    assert raised
    return


def test_insert_invalid_path_raises() -> None:
    """
        Inserting at the root path raises ``ValueError``, and removing the
        root path with ``ignore_missing=False`` raises ``ValueError``.
    """
    ctx = Context()
    raised_insert = False
    try:
        ctx.insert('/', 'bad')
    except ValueError:
        raised_insert = True
    assert raised_insert

    raised_remove = False
    try:
        ctx.remove('/', ignore_missing=False)
    except ValueError:
        raised_remove = True
    assert raised_remove
    return
