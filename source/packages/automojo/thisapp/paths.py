"""
.. module:: paths
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains the :class:`TaskBase` object which is used as the base.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


# pylint: disable=global-statement

from typing import List, Optional

import os
import tempfile

from automojo.errors.exceptions import ConfigurationError, SemanticError

from automojo.xmodules.fspath import expand_path

from automojo.thisapp.enumerations import JobType
from automojo.thisapp.runtimevariables import RuntimeVariables


DIR_PRESENCE_DIRECTORY = None
DIR_CACHE_DIRECTORY = None
DIR_DIAGNOSTICS_DIRECTORY = None
DIR_RESULTS_DIRECTORY = None
DIR_SHARED_STORE_DIRECTORY = None
DIR_TESTRESULTS_DIRECTORY = None
DIR_TESTCASE_BYPRODUCTS_DIRECTORY = {}

TRANSLATE_TABLE_NORMALIZE_FOR_PATH = str.maketrans(",.:;", "    ")


def collect_python_modules(search_dir: str, max_depth=None) -> List[str]:
    """
        Walks a directory tree of python modules and collects the names
        of all of the python module files or .py files.  This method allows
        for python namespaces by not forcing the root folder to contain a
        __init__.py file.

        :params searchdir: The root directory to search when collecting python modules.
    """
    pyfiles = []

    search_dir = os.path.abspath(search_dir)
    search_dir_len = len(search_dir)

    for root, dirs, files in os.walk(search_dir, topdown=True):

        if max_depth is not None:
            dir_leaf = root[search_dir_len:].strip(os.path.sep)
            depth = 0
            if dir_leaf != '':
                dir_leaf_parts = dir_leaf.split(os.path.sep)
                depth = len(dir_leaf_parts)

            if depth >= max_depth:
                dirs[:] = []

        for fname in files:
            fbase, fext = os.path.splitext(fname)
            if fext == '.py' and fbase != "__init__":
                ffull = os.path.join(root, fname)
                pyfiles.append(ffull)

    return pyfiles


def ensure_directory_is_package(package_dir: str, package_title: Optional[str] = None):
    """
        Ensures that a directory is represented to python as a package by checking to see if the
        directory has an __init__.py file and if not it adds one.

        :param package_dir: The direcotry to represent as a package.
        :param package_title: Optional title to be written into the documentation string in the package file.
    """
    package_dir_init = os.path.join(package_dir, "__init__.py")
    if not os.path.exists(package_dir_init):
        with open(package_dir_init, 'w') as initf:
            initf.write('"""\n')
            if package_title is not None:
                initf.write('   %s\n' % package_title)
            initf.write('"""\n')
    return


def get_directory_for_cached_files(create=True) -> str:
    """
        Returns the path to the {home}/cache directory.
    """

    global DIR_CACHE_DIRECTORY

    if DIR_CACHE_DIRECTORY is None:
        
        runtime_home_dir = expand_path(RuntimeVariables.AM_PRESENCE_DIR)
        DIR_CACHE_DIRECTORY = os.path.join(runtime_home_dir, "cache")
        if create and not os.path.exists(DIR_CACHE_DIRECTORY):
            os.makedirs(DIR_CACHE_DIRECTORY)

    return DIR_CACHE_DIRECTORY


def get_directory_for_code_container(container: str) -> str:
    """
        Returns the directory for a code container (module or package)

        :param container: The code container you want to get a directory for.

        :returns: The string that represents the parent directory of the code
                  container specified.
    """
    if hasattr(container, '__path__'):
        container_dir = str(container.__path__[0]).rstrip(os.sep)
    elif hasattr(container, '__file__'):
        container_dir = os.path.dirname(container.__file__).rstrip(os.sep)
    else:
        raise RuntimeError("Unable to get parent dir for module") from None

    return container_dir


def get_path_for_artifacts(label: str) -> str:
    """
        Returns a path in the form (testresultdir)/artifacts/(label)

        :param label: A label to associate with the collection of artifacts. The label is used for
                      the name of the artifact container folder.

        :returns: A path that is descendant from (testresultdir)/artifacts
    """

    if RuntimeVariables.AM_JOB_TYPE == JobType.Unknown:
        errmsg = f"The 'artifacts' folder is only available for runtimes activated as a job. jobtype={RuntimeVariables.AM_JOB_TYPE}"
        raise SemanticError(errmsg)

    trdir = get_path_for_output()
    afdir = os.path.join(trdir, "artifacts", label)

    if not os.path.exists(afdir):
        os.makedirs(afdir)

    return afdir


def get_path_for_output(create=True) -> str:
    """
        Returns the timestamped path where test results and artifacts are deposited to
    """
    global DIR_RESULTS_DIRECTORY

    if DIR_RESULTS_DIRECTORY is None:
        
        DIR_RESULTS_DIRECTORY = expand_path(RuntimeVariables.AM_OUTPUT_DIRECTORY)
        if create and not os.path.exists(DIR_RESULTS_DIRECTORY):
            os.makedirs(DIR_RESULTS_DIRECTORY)

    return DIR_RESULTS_DIRECTORY


def get_path_for_shared_store(create=True) -> str:
    """
        Returns the path to the designated shared storage directory.  This will typically need
        to be a machine specific path so don't expand user home or vars.
    """
    global DIR_SHARED_STORE_DIRECTORY

    if DIR_SHARED_STORE_DIRECTORY is None:

        store_dir = RuntimeVariables.AM_SHARED_STORE_DIRECTORY
        if store_dir is None:
            errmsg = "The shared store directory (AM_SHARED_STORE_DIRECTORY) is not configured."
            raise ConfigurationError(errmsg)

        DIR_SHARED_STORE_DIRECTORY = expand_path(store_dir)

        if create:
            if not os.path.exists(DIR_SHARED_STORE_DIRECTORY):
                os.makedirs(DIR_SHARED_STORE_DIRECTORY)
    
    return DIR_SHARED_STORE_DIRECTORY


def get_path_for_diagnostics(label: str) -> str:
    """
        Returns a path in the form (testresultdir)/diagnostics/(label)

        :param label: A label to associate with the collection of diagnostic captures.
                      The label is used for the name of the diagnostic container folder.

        :returns: A path that is descendant from (testresultdir)/diagnostics

        .. notes: Paths that are relative to the output directory should always call
                  get_path_for_output instead of calling for the directory of any
                  one job type.
    """

    if RuntimeVariables.AM_JOB_TYPE == JobType.Unknown:
        errmsg = f"The 'diagnostics' folder is only available for runtimes activated as a job. jobtype={RuntimeVariables.AM_JOB_TYPE}"
        raise SemanticError(errmsg)

    trdir = get_path_for_output()
    diagnostics_dir = os.path.join(trdir, "diagnostics", label)

    if not os.path.exists(diagnostics_dir):
        os.makedirs(diagnostics_dir)

    return diagnostics_dir


def get_path_for_testresults() -> str:
    """
        Returns the path to the testresults directory.

        :returns: The path to the testresults directory

        ..note : This path is generally only used by the commandline because
        it can intentionally provide a different result than get_path_for_output
        if the current job is not a TESTRUN job.  If your running in a TESTRUN job,
        utilize get_path_for_output instead of this API.
    """

    if RuntimeVariables.AM_JOB_TYPE == JobType.Unknown:
        errmsg = f"The 'testresults' folder is only available for runtimes activated as a job. jobtype={RuntimeVariables.AM_JOB_TYPE}"
        raise SemanticError(errmsg)

    global DIR_TESTRESULTS_DIRECTORY

    if DIR_TESTRESULTS_DIRECTORY is None:
        
        tr_dir = RuntimeVariables.AM_RESULT_PATH_FOR_TESTS
        if tr_dir is None:
            tr_dir = get_path_for_output()
        else:
            tr_dir = expand_path(tr_dir)

        DIR_TESTRESULTS_DIRECTORY = tr_dir

        if not os.path.exists(DIR_TESTRESULTS_DIRECTORY):
            os.makedirs(DIR_TESTRESULTS_DIRECTORY)

    return DIR_TESTRESULTS_DIRECTORY


def get_path_for_testcase_by_products(test_id: str) -> str:
    """
        Returns a path to the tc-by-products
    """

    if RuntimeVariables.AM_JOB_TYPE == JobType.Unknown:
        errmsg = f"The 'tc-by-products' folder is only available for runtimes activated as a job. jobtype={RuntimeVariables.AM_JOB_TYPE}"
        raise SemanticError(errmsg)

    global DIR_TESTCASE_BYPRODUCTS_DIRECTORY

    if DIR_TESTCASE_BYPRODUCTS_DIRECTORY is None:
        DIR_TESTCASE_BYPRODUCTS_DIRECTORY = {}

    if test_id not in DIR_TESTCASE_BYPRODUCTS_DIRECTORY:

        trdir = get_path_for_testresults()
        byproducts_dir = os.path.join(trdir, "tc-by-products", test_id)

        if not os.path.exists(byproducts_dir):
            os.makedirs(byproducts_dir)

        DIR_TESTCASE_BYPRODUCTS_DIRECTORY[test_id] = byproducts_dir

    return DIR_TESTCASE_BYPRODUCTS_DIRECTORY[test_id]


def get_presence_directory() -> str:
    """
        Returns the path to the presence directory.
    """
    
    global DIR_PRESENCE_DIRECTORY

    if DIR_PRESENCE_DIRECTORY is None:
        
        presence_dir = RuntimeVariables.AM_PRESENCE_DIR
        DIR_PRESENCE_DIRECTORY = expand_path(presence_dir)
    
    return DIR_PRESENCE_DIRECTORY


def get_summary_html_template_source() -> str:
    """
        Looks up a source path for the summary html template.

        :returns: The path to the html summary template
    """
    
    template = expand_path(RuntimeVariables.AM_RESULTS_STATIC_SUMMARY_TEMPLATE)

    if template is None:
        errmsg = "Error attempting to lookup the summary html template source."
        raise RuntimeError(errmsg)

    return template


def get_summary_static_resource_dest_dir(create=True) -> str:
    """
        Returns the path where the static resources for test summaries should be published.
    """
    res_dir = expand_path(RuntimeVariables.AM_RESULTS_STATIC_RESOURCE_DEST_DIR)

    if create and not os.path.exists(res_dir):
        os.makedirs(res_dir)

    return res_dir


def get_summary_static_resource_src_dir() -> str:
    """
        Returns the path that is the source path for the test summary static resources.
    """
    res_dir = expand_path(RuntimeVariables.AM_RESULTS_STATIC_RESOURCE_SRC_DIR)

    return res_dir


def get_temporary_directory() -> str:
    """
        Returns the path of a temporary directory in the output directory.
    """
    temp_dir = os.path.join(get_path_for_output(), "temp")

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    return temp_dir


def get_temporary_file(suffix: str = '', prefix: str = '') -> str:
    """
        Returns the path of a temporary file in the output directory.
    """
    tempdir = get_temporary_directory()

    fd, tmpfile = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=tempdir)
    os.close(fd)

    return tmpfile


def normalize_name_for_path(name: str) -> str:
    """
        Normalizes a path string by replacing ",.:;" with space and then removing
        white space.

        :param name: A name as a str which is to be normalized to allow it to be used in a path.

        :returns: The normalized string which can be used in a path.
    """
    norm_name = name.translate(TRANSLATE_TABLE_NORMALIZE_FOR_PATH).replace(" ", "")
    return norm_name


def utilizing_shared_output_path() -> bool:
    """
        Returns a boolean value indicating the runtime is configured to use a shared output
        path across compute resources.
    """

    op_is_shared = RuntimeVariables.AM_HAS_SHARED_OUTPUT_DIRECTORY

    return op_is_shared
