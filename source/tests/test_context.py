
import unittest

from automojo.thisapp.context import Context, ContextCursor, validate_path_name


class TestContext(unittest.TestCase):

    def test_validate_path_name_simple(self):
        parts = validate_path_name('/level1/level2')
        self.assertEqual(parts, ['level1', 'level2'])
        trailing = validate_path_name('/level1/level2/')
        self.assertEqual(trailing, ['level1', 'level2'])

    def test_context_insert_and_lookup(self):
        ctx = Context()
        ctx.insert('/a/b', 1)
        self.assertEqual(ctx.lookup('/a/b'), 1)
        self.assertEqual(ctx.lookup(['a', 'b']), 1)

    def test_context_exists_and_remove(self):
        ctx = Context()
        ctx.insert('/a/b', 1)
        self.assertTrue(ctx.exists('/a/b'))
        removed = ctx.remove('/a/b')
        self.assertEqual(removed, 1)
        self.assertFalse(ctx.exists('/a/b'))

        # Removing a non-existent path should not raise when ignore_missing=True
        self.assertIsNone(ctx.remove('/c/d', ignore_missing=True))

    def test_context_lookup_default_value(self):
        ctx = Context()
        value = ctx.lookup('/x/y', default=5)
        self.assertEqual(value, 5)
        self.assertEqual(ctx.lookup('/x/y'), 5)

    def test_context_lookup_default_dict_returns_cursor(self):
        ctx = Context()
        cursor = ctx.lookup('/d', default={})
        self.assertIsInstance(cursor, ContextCursor)
        cursor.insert('/name', 'foo')
        self.assertEqual(ctx.lookup('/d/name'), 'foo')

    def test_context_contains_and_item_access(self):
        ctx = Context()
        ctx['key'] = 123
        self.assertIn('key', ctx)
        self.assertEqual(ctx['key'], 123)

    def test_context_cursor_fill_template(self):
        ctx = Context()
        ctx.insert('/info', {'name': 'foo', 'value': 42})
        cursor = ctx.lookup('/info')
        self.assertIsInstance(cursor, ContextCursor)
        filled = cursor.fill_template('Name:%(name)s Value:%(value)s')
        self.assertEqual(filled, 'Name:foo Value:42')

    def test_lookup_raise_error(self):
        ctx = Context()
        with self.assertRaises(LookupError):
            ctx.lookup('/missing', raise_error=True)

    def test_insert_invalid_path_raises(self):
        ctx = Context()
        with self.assertRaises(ValueError):
            ctx.insert('/', 'bad')
        with self.assertRaises(ValueError):
            ctx.remove('/', ignore_missing=False)


if __name__ == '__main__':
    unittest.main()
