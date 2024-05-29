import time
import re
from actions import custom_exceptions
from random import randrange
from datetime import datetime

class Timers:
    def __init__(self):
        pass
    
    #returns the current time
    def time_current():
        #splits time so it has no miliseconds
        timer = str(time.time()).split(".")
        return int(timer[0])
    
    #checks to see if -t, -T, etc is contained in the message, then returns a string for the proper format
    def formatter(message):
        #Key: the commands for every format
        #Value: the output for each format
        formats = {
        "-t": ":t",
        "-T": ":T",
        "-d": ":d",
        "-D": ":D",
        "-f": ":f",
        "-F": ":F",
        "-R": ":R"
        }
        # Check if the message matches any key in the switch dictionary
        for format_command, format_key in formats.items():
            if re.search(rf'(^|\s){format_command}(?=\s|$)', message):
                return format_key
        
        # If no match is found, return the default format
        return ""
        
    #used for time_from_now and time_ago functions further down
    def time_input(message, timescale):
        #searches for years/months/weeks/etc inside of message string using regex
        #captures any numbers to the right of the timescale separated optionally by a whitespace
        match = re.search(rf"(?<!\S)(\d+)\s*{timescale}", message, re.IGNORECASE)
        if match:
            #returns the value of the first grouping in match, e.g. (\d+), the digits
            inputted_time = match.group(1)
        else:
            #user did not input time value to the left of timescale
            raise custom_exceptions.NoTimeValueError
        
        return int(inputted_time)

    #returns x time ago/from now. opeartor is 1 if in the future, -1 if in the past
    def time_calc(message, operator):
        #splits time so it has no miliseconds
        timer = str(time.time()).split(".")
        current_time = int(timer[0])

        #flag to be raised when a pattern is found. if not raise, exception happens at end of method
        pattern_found = False

        try:
            #dictionary regex for every possible time combination. [s]? allows for the time to be plural optionally.
            #the value represents the seconds in each timescale. e.g. there are 60 seconds in a minute.
            time_patterns = {
                "year[s]?": 31536000,
                "month[s]?": 2628288,
                "week[s]?": 604800,
                "day[s]?": 86400,
                "hour[s]?": 3600,
                "minute[s]?": 60,
                "second[s]?": 1,
            }

            
            for pattern, seconds in time_patterns.items():
                #if the pattern (e.g. year[s]? is found in the message)
                if re.search(pattern, message, re.IGNORECASE):
                    current_time += (operator * Timers.time_input(message, pattern) * seconds)
                    pattern_found = True
            
            if not pattern_found:
                raise custom_exceptions.NoTimeStringError
        
        except custom_exceptions.NoTimeValueError:
            raise custom_exceptions.NoTimeValueError
        
        return current_time
    
    #takes unix timestamp out of message and returns as int
    def time_epoch(message):
        operator = ""
        #searches to see if there is a - behind the number
        if re.search(r'(?<=\d)\s*-', message):
            operator = "-"
        time = "".join(c for c in message if c.isdigit())
        return operator + time
    
    def time_random():
        return randrange(Timers.time_current())
    
    def time_convert(message):
        date = None
        time = None

        if message.startswith("!time "):
            message = message[6:].lower()

        else:
            message = message[3:].lower()

        #searches to see if the message ends with a - and letter, such as -D for format, then removes it
        parts = re.split(r'-[a-zA-Z]$', message)
        message = parts[0].strip()
        print(f"Message: {message}")

        try:
            # Check for date format ####-##-## or ##-##
            if re.findall(r'\d{4}-\d{2}-\d{2}|(?<!:)\d{2}-\d{2}', message):
                print("Date found")
                # Capture the date pattern
                date = re.findall(r'\d{4}-\d{2}-\d{2}|(?<!:)\d{2}-\d{2}', message)
                #findall returns as a list so we convert it back into a string since we know we will only ever find one
                date = date[0]

            # Check for time format ##:##:## or ##:##
            if re.findall(r'\d{1,2}:\d{2}:\d{2}|(?<!:)\d{1,2}:\d{2}', message):
                print("Time found")
                # Capture the time pattern
                time = re.findall(r'\d{1,2}:\d{2}:\d{2}\s|(?<!:)\d{1,2}:\d{2}', message)
                #findall returns as a list so we convert it back into a string since we know we will only ever find one
                time = time[0]

                #adds 12 hour clock support
                if "pm" in message or "p.m." in message:
                    print("PM found")
                    time = time.split(":")
                    time[0] = str(int(time[0]) + 12)
                    time = ":".join(time)


        except AttributeError:
            raise custom_exceptions.NoTimeValueError
        
        print (f"Time: {time}")
        print (f"Date: {date}")
        return