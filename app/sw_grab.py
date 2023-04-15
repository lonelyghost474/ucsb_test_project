import re
import os
import argparse
from logger import Logger
from models import *
from typing import Optional, Union, NoReturn
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException, ReadTimeout


class Service(Logger):
    """The Service class is used to receive data from the switch. The output is carried out to the terminal in a form
    convenient for the operator and is written to a file in the json format.

    The main application is to receive the following data from the switch:
                                - software and hardware version;
                                - starting configuration;
                                - current configuration;
                                - information about access control lists (ACL) of the switch;
                                - information about the interfaces of the switch.

    Note:
        There may be problems with waiting for data to be received from the switch (ReadTimeout).

    Attributes
    ----------
    self.session: Union[ConnectHandler, None]
        full path to text file
    self.data: dict
        list of source file lines
    self.connect_opt: dict
        dictionary that stores data for connecting to the switch
    Methods
    -------
    self.main(self) -> NoReturn
        The method that implements the main logic for the class. Connected to the switch. Executes the specified
        commands sequentially. Displays the data received from the switch in a form convenient for the operator.
        Saves data received from the switch to a json file.
    """

    def __init__(self):
        super().__init__(name='sw_grab')
        self.session: Union[ConnectHandler, None] = None
        self.data: dict = AllData().dict()
        self.connect_opt: dict = self.__parse_options(options=Options().dict())

    @staticmethod
    def __parse_options(options: dict) -> dict[str: Any]:
        """
        A method that parses command line arguments and passes them to the data model for connecting to the switch.

        :param options: A dictionary built on the basis of a data model that must contain the necessary data to connect
        to the switch.
        :return: Dictionary with settings for connecting to the switch.
        """
        parser = argparse.ArgumentParser()
        # Link to documentation
        help_str = "Please see https://ktbyers.github.io/netmiko/docs/netmiko/index.html#netmiko.ConnectHandler"
        # Add command line arguments
        for _, arg_name in enumerate(options):
            parser.add_argument(arg_name, help=help_str) if arg_name in ["host", "port",
                                                                         "device_type"] else parser.add_argument(
                f"--{arg_name}", help=help_str)
        # Adding command line arguments to the dictionary with connection settings
        for _, key in enumerate(list((args := vars(parser.parse_args())))):
            if args[key] is not None:
                options[key] = args[key]
        # Removing fields with value None
        for _, key in enumerate(list(options.keys())):
            if options[key] is None:
                del options[key]
        return options

    def __distributor(self, command: str, data: str) -> NoReturn:
        """
        A method that writes the data received depending on the command sent to the required keys.

        :param command: The command that was sent to the switch.
        :param data: Data received from the switch depending on the command.
        :return: NoReturn
        """
        match command:
            # Get the version of the switch and its software
            case "show version":
                self.data["sw_version"]["soft_version"], self.data["sw_version"]["hard_version"] = self.__get_version(
                    data=data)
            # Get the current configuration
            case "show running-config":
                self.data["sw_config"]["running_config"] = data
            # Getting the start configuration
            case "show startup-config":
                self.data["sw_config"]["start_config"] = data
            # Get access lists
            case "show access-lists":
                self.data["sw_acl"] = data
            # Getting data about interfaces
            case "show interfaces":
                self.data["sw_interface"] = data
            # Get data about ip interfaces
            case "show ip interface brief":
                self.data["sw_ip_interface"] = data

    @staticmethod
    def __get_version(data: str) -> Union[tuple[str, str], tuple[None, None]]:
        """
        Method for parsing the software and hardware version of the device.

        :param data: Dictionary with data received from the switch corresponding to the data model for storage.
        :return: Software and hardware version.
        """
        # Finding the switch version using regular expressions
        if (soft_version := re.findall(r"Cisco\b.*\bfc2.", data)) and \
                (hard_version := re.findall(r"Cisco\b.*\bmemory.", data)):
            return soft_version[0], hard_version[0]
        else:
            return None, None

    @staticmethod
    def __write_file(name: str, data: str | dict[str: Any], mode: str) -> NoReturn:
        """
        Method for writing data received from the switch to a file.

        :param name: Output file name.
        :param data: Dictionary with data received from the switch corresponding to the data model for storage.
        :param mode: Flag for writing to a file.
        :return: NoReturn
        """
        # Create folder if not already created
        if not os.path.exists("./!db"):
            os.mkdir("./!db")
        # Write to file
        with open(f"./!db/{name.replace(' ', '_')}.txt", mode) as file:
            file.write(str(data))

    def __connection(self, options: Optional) -> bool:
        """
        Method for connecting to the switch.

        :param options: Dictionary with data for connecting to the switch.
        :return: Boolean value indicating successful connection to the switch.
        """
        try:
            self.session = ConnectHandler(**options)
            self.session.enable()
        except (NetmikoTimeoutException, NetmikoAuthenticationException, ReadTimeout, TimeoutError,
                ConnectionRefusedError) as error:
            self.add_log.error(error)
            return False
        return True

    def __output_to_console(self) -> NoReturn:
        """
        A method for outputting data received from the switch in a format convenient for the operator.

        :return: NoReturn
        """
        # Для печати таблицы
        line = f"+{'-' * 120}+\n"
        title = lambda name: f"|{name:^120}|\n"  # PEP8 violation: E731
        text = lambda name: f"|{name:<120}|\n"  # PEP8 violation: E731
        final_list = [line, title("SWITCH OUT DATA"), line, title("Switch software and hardware version:"), line]
        # Добавление версии коммутатора
        self.__add_row(data=self.data["sw_version"], func=text, input_list=final_list)
        # Добавление стартовой конфигурации
        final_list.extend([line, title("Contents of startup configuration:"), line])
        self.__add_row(data=self.data["sw_config"]["start_config"], func=text, input_list=final_list)
        # Добавление текущей конфигурации
        final_list.extend([line, title("Current operating configuration:"), line])
        self.__add_row(data=self.data["sw_config"]["running_config"], func=text, input_list=final_list)
        # Добавление ACL
        final_list.extend([line, title("List access lists:"), line])
        self.__add_row(data=self.data["sw_acl"], func=text, input_list=final_list)
        # Добавление IP information
        final_list.extend([line, title("IP interface status and configuration:"), line])
        self.__add_row(data=self.data["sw_ip_interface"], func=text, input_list=final_list)
        # Добавление Interface status and configuration
        final_list.extend([line, title("Interface status and configuration:"), line])
        self.__add_row(data=self.data["sw_interface"], func=text, input_list=final_list)
        # Добавление закрытия таблицы
        final_list.extend([line, title("Thanks for the interesting challenge!"), line.strip()])
        # Печать всех данных
        self.add_log.info("\n" + "".join(final_list))

    @staticmethod
    def __add_row(data: dict[str: Any], input_list: list[str], func) -> NoReturn:
        """
        Method for adding a string to print data to the console.

        :param data: Dictionary with data received from the switch corresponding to the data model for storage.
        :param input_list: List to which lines are added for output to the console.
        :param func: A function that determines what format of text will be output to the console.
        :return: NoReturn
        """
        for row in list(filter(None, data if isinstance(data, dict) else data.split("\n"))):
            if isinstance(data, dict):
                input_list.append(func(data[row]))
            else:
                input_list.append(func(row))

    @staticmethod
    def __check_data(data: dict[str: Any]) -> bool:
        """
        A method to verify that all specified data has been received from the switch.

        :param data: Dictionary with data received from the switch corresponding to the data model for storage.
        :return: A boolean value indicating whether the received values match the specified validation rules.
        """
        return all([data[key] for _, key in enumerate(data) if not isinstance(data[key], dict)] + [
            data['sw_version'][key] for _, key in enumerate(data['sw_version'])] + [
                       data['sw_config'][key] for _, key in enumerate(data['sw_config'])])

    def main(self) -> NoReturn:
        """
        The method in which all the logic of the program is implemented.

        :return: NoReturn
        """
        # Commands to execute
        commands = ["show version", "show startup-config", "show running-config", "show access-lists",
                    "show ip interface brief", "show interfaces"]
        # Connecting to the switch
        self.add_log.info("Initialized connection to the switch ...")
        if not self.__connection(options=self.connect_opt):
            self.add_log.info("The program ends its work")
            return
        self.add_log.info("Connection was successful")
        self.add_log.info("Receiving data from the switch ...")
        # Sequential execution of specified commands on the switch
        for command in commands:
            try:
                output_data: str = self.session.send_command_timing(command)
            except Exception as error:
                self.add_log.error(error)
                self.add_log.info("The program ends its work")
                return
            # Filling out the dictionary
            self.__distributor(command, output_data)
        # Check that all data has been received
        if not self.__check_data(self.data):
            self.add_log.info("For some reason, the required data was not received. The program ends its work")
            return
        self.add_log.info("Data received from the switch successfully!")
        self.add_log.info("Outputting received data to the terminal:")
        # Output received data to the console
        self.__output_to_console()
        self.add_log.info("Writing received data to a file")
        # Write output to file
        self.__write_file(name="output_data", data=self.data, mode="a+")
        self.add_log.info("The program worked successfully!")


if __name__ == "__main__":
    s = Service()
    s.main()
