"""
.. module:: enumerations
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains runtime enumerations.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from enum import Enum


"""
    Characteristics of different runtimes or usages of commands and logs.

    Service:
        * Long running
        * rotational logs
        * don't necessarily have consold output, console output is for debugging
        * when run with a console, generally logging will go to the console

    Command:
        * Generally have standard out and standard input
        * Generally commands print everything to the screen

    Interactive Console:
        * Standard out and standard input are for user interaction
        * Should have a log that log output goes to so screen does not have log
          output and disrupt user interaction

    Job:
        * Generally have a output folder where the by-products of the job are collected such as logs and results
        * Jobs can be multiple types, Infrastructure, Build, Orchestration, TestRun
    
"""


class ActivationProfile(str, Enum):
    Command = "command"
    Console = "console"
    Job = "job"
    Service = "service"

class JobType(str, Enum):
    Unknown = "Unknown"
    Build = "Build"
    Infrastructure = "Infrastructure"
    Orchestration = "Orchestration"
    TestRun = "TestRun"
