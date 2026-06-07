
import unittest
from ccai.thisapp.contextpaths import ContextPaths

class TestContextPathsUpdate(unittest.TestCase):
    def test_result_path_for_build(self):
        self.assertTrue(hasattr(ContextPaths, 'RESULT_PATH_FOR_BUILD'))
        self.assertEqual(ContextPaths.RESULT_PATH_FOR_BUILD.value, "/configuration/runtime/paths/results/build")

if __name__ == '__main__':
    unittest.main()
