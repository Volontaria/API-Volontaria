import os
import sys
import inspect

# Paths
REPOSITORY_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
PROJECT_PATH = REPOSITORY_PATH

# Color constant to console print
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
ENDC = '\033[0m'


class Test:
    """
    A little class to iterate one or some check
    on the project
    """

    # List of test function we want to execute
    COMMAND_LIST = list()

    def __init__(self):
        # List all test method
        methods = inspect.getmembers(self)
        for method in methods:
            if method[0][:15] == '_Test__command_':
                self.COMMAND_LIST.append(method[0][15:])

    def help(self):
        print('Usage: tests [command [command]]')
        print('Example: tests test coverage')
        print()
        print('Commands:')
        for command in self.COMMAND_LIST:
            print(" |-" + command)

    def launch_commands(self, list_name=COMMAND_LIST):
        """
        Method to launch a list of tests
        """
        is_broken = False

        for command_name in list_name:
            # Launch the test
            self.launch_command(command_name)

            # User input to stop or continue
            if command_name != list_name[-1]:
                next = input("Do you want to continue (Y/N) ? [Y]")
                if next in ['Yes', 'yes', 'Y', 'y', '']:
                    pass
                else:
                    is_broken = True
                    break

        if is_broken:
            print(WARNING + "Tests canceled." + ENDC)
        else:
            print(OKGREEN + "OK - Tests successful." + ENDC)

    def launch_command(self, command_name):
        """
        Method to launch a specific command
        :param command_name: The name of the test method
        :return: None
        """
        if command_name in self.COMMAND_LIST:
            # Get the method and call it to know the test case
            method = getattr(self, '_Test__command_' + command_name)
            name, description, commands = method()

            # Execute the command
            self.__execute_command(name, description, commands)
        else:
            raise ValueError(
                '`' + command_name + '` is not a valid command name.'
            )

    @staticmethod
    def __execute_command(name, description, commands):
        message = "Running -- " + name + "..."
        separator = "-" * len(message)

        print(OKGREEN + separator + ENDC)
        print(OKGREEN + message + ENDC)
        print(OKGREEN + separator + ENDC)
        print(OKBLUE + description + ENDC)

        for command in commands:
            print(HEADER + command + ENDC)
            os.system(command)

            if command != commands[-1]:
                input("Press enter to continue...")

        print(OKBLUE + "Ran -- " + name + "." + ENDC)

    @staticmethod
    def __command_coverage():
        """
        Method to test coverage of all the application
        """
        name = "Tests and Coverage"
        description = "We will run all tests of the project. " \
                      "This can take several minutes."

        test = "coverage run " + PROJECT_PATH + "/manage.py " \
               "test " + PROJECT_PATH

        coverage = "coverage report"

        return name, description, [test, coverage]

    @staticmethod
    def __command_style():
        """
        Method to run Pycodestyle
        """
        name = "Pycodestyle"
        description = "Output will be empty if there are no styling errors."
        styling = "pycodestyle --config=.pycodestylerc " + PROJECT_PATH

        return name, description, [styling]


if __name__ == "__main__":
    test = Test()

    if len(sys.argv) > 1 and sys.argv[1] in ['help', '-h', '--help']:
        test.help()
    else:
        # If we have a specific argument
        # we launch the associated test
        if len(sys.argv) > 1:
            test.launch_commands(sys.argv[1:])
        else:
            test.launch_commands()
