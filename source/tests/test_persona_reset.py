"""
    .. module:: test_persona_reset
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Unit tests for resetting the application persona.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import unittest

from ccai.thisapp import persona
from ccai.thisapp import wellknown

from ccai.thisapp.persona import (
    AppPersona, establish_app_persona, reset_app_persona
)


class PersonaResetTests(unittest.TestCase):
    """
        Verifies a persona can be cleared and another established.
    """

    def setUp(self):
        """
            Start from no persona, whatever earlier tests left behind.
        """
        reset_app_persona()
        return

    def tearDown(self):
        """
            Leave no persona behind for the next test.
        """
        reset_app_persona()
        return

    def test_reset_clears_the_established_flag(self):

        establish_app_persona(name="demo", logger_name="demo",
                              log_basename="demo")
        self.assertTrue(persona.APP_PERSONA_ESTABLISHED)

        reset_app_persona()

        self.assertFalse(persona.APP_PERSONA_ESTABLISHED)
        return

    def test_reset_clears_the_singleton(self):

        establish_app_persona(name="demo", logger_name="demo",
                              log_basename="demo")
        self.assertIsNotNone(wellknown.THISAPPLICATION_SINGLETON)

        reset_app_persona()

        self.assertIsNone(wellknown.THISAPPLICATION_SINGLETON)
        return

    def test_reset_clears_the_persona_attributes(self):

        establish_app_persona(name="demo", logger_name="demo-logger",
                              log_basename="demo-log")

        reset_app_persona()

        self.assertIsNone(AppPersona.AM_NAME)
        self.assertIsNone(AppPersona.AM_LOGGER_NAME)
        self.assertIsNone(AppPersona.AM_LOG_BASENAME)
        self.assertIsNone(AppPersona.AM_PRESENCE_DIR)
        self.assertIsNone(AppPersona.AM_LOG_DIRECTORY)
        self.assertIsNone(AppPersona.AM_SETTINGS_FILENAME)
        self.assertIsNone(AppPersona.AM_EXTENSIONS)
        self.assertIsNone(AppPersona.AM_SERVICE_NAME)
        return

    def test_reset_clears_the_configured_super_factory(self):

        # The super factory is built from the persona's extension modules, so
        # leaving it in place would hand the next persona the previous one's
        # extensions.
        establish_app_persona(name="demo", logger_name="demo",
                              log_basename="demo")
        wellknown.CONFIGURED_SUPER_FACTORY = object()

        reset_app_persona()

        self.assertIsNone(wellknown.CONFIGURED_SUPER_FACTORY)
        return

    def test_a_second_persona_can_be_established_after_reset(self):

        # This is the point of the helper: without it, establishing a persona
        # is a once-per-process operation and a test process that needs two
        # has no way past the guard.
        establish_app_persona(name="first", logger_name="first",
                              log_basename="first")
        reset_app_persona()

        establish_app_persona(name="second", logger_name="second",
                              log_basename="second")

        self.assertEqual(AppPersona.AM_NAME, "second")
        self.assertIsNotNone(wellknown.THISAPPLICATION_SINGLETON)
        return

    def test_the_second_persona_is_a_new_instance(self):

        establish_app_persona(name="first", logger_name="first",
                              log_basename="first")
        first = wellknown.THISAPPLICATION_SINGLETON

        reset_app_persona()
        establish_app_persona(name="second", logger_name="second",
                              log_basename="second")

        self.assertIsNot(wellknown.THISAPPLICATION_SINGLETON, first)
        return

    def test_reset_is_safe_with_no_persona_established(self):

        # Called from a tearDown, it must not care whether a persona was set.
        reset_app_persona()
        reset_app_persona()

        self.assertFalse(persona.APP_PERSONA_ESTABLISHED)
        self.assertIsNone(wellknown.THISAPPLICATION_SINGLETON)
        return


if __name__ == "__main__":
    unittest.main()
