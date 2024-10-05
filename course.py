import re
import json
from filter_requisites import NOTEABLE, TO_DELETE, COMPLETED_STRINGS

class Course:
    def __init__(self):
        self.notes = ""

    def get_notes(self):
        return self.notes

    def __str__(self) -> str:
        return self.name + ": " +  self.title

    def to_json(self) -> dict:
        """
        Converts each course into (a dictionary) of {attribute: value}
        """

        #Returns a copy of the dictionary so we don't edit the original values
        return self.__dict__.copy()

    def from_json(self, info: dict): 
        """
        Takes a dictionary, feeds all the data into this object
        """
        for key, value in info.items():
            self.__dict__[key] = value        

    def set_name(self, name: str):        
        self.name = name

    def get_name(self) -> str:
        return self.name

    def set_title(self, title: str):
        self.title = title

    def get_title(self) -> str:
        return self.title

    def set_exclusions(self, exclusions: list):
        #gets rid of courses that aren't in the St. George campus
        self.exclusions_list = [excluded for excluded in exclusions if re.search("^[A-Z]{3}[0-9]{3}(H|Y)1$", excluded)]

    def get_exclusions(self) -> list:
        return self.exclusions_list

    def set_prerequisites(self, prereq_string: str):
        """
        Generates a computer-friendly list of prerequisites, and stores it.
        NOTE: Auto-deletes prerequisite strings that have already been completed
        See `clean_string` and `process_course_list` for more info
        """
        self.prereq_string = prereq_string
        clean_prereqs = self.clean_string(prereq_string)
        self.prereq_list = self.process_course_list(clean_prereqs)

    def get_prerequisites(self) -> list:
        return self.prereq_list

    def get_prerequisites_raw(self) -> str:
        return self.prereq_string

    def set_corequisites(self, coreq_string: str):
        """
        Generates a computer-friendly list of cprequisites, and stores it.
        NOTE: Auto-deletes corequisite strings that have already been completed
        See `clean_string` and `process_course_list` for more info
        """
        self.coreq_string = coreq_string
        clean_coreqs = self.clean_string(coreq_string)
        self.coreq_list = self.process_course_list(clean_coreqs)

    def get_corequisites(self) -> list:
        return self.coreq_list

    def __eq__(self, other) -> bool:
        #Both self and other must have a name and title that are equivalent to be considered equal courses
        if 'name' not in self.__dict__ or 'title' not in self.__dict__ or\
            'name' not in other.__dict__ or 'title' not in other.__dict__:
            return False
        
        key_set = ['name', 'title', 'prereq_list', 'coreq_list', 'exclusions_list']
        #Checks that every attribute that both courses have is the same
        for key in key_set:
            if key in self.__dict__ and key in other.__dict__:
                if self.__dict__[key] != other.__dict__[key]:
                    return False

        return True

    def copy_sessions(self, other):
        self.sessions = other.sessions

    def add_session(self, sessions: list, curr_enroll: int, max_enroll: int, waitlist: int):
        """
        Adds information about whether the course is offered in Fall, Winter, both, or is a yearlong course
        """
        #Adds the attribute 'sessions' if it doesn't already exist
        if 'sessions' not in self.__dict__:
            self.sessions = {}
        
        #Stores stuff in the format {session: curr_enrollment, max_enrollment, waitlist}
        #NOTE: assumes the last digit of fall sessions is 9, and the last digit of winter sessions is 1 
        if len(sessions) == 2:
            self.sessions['Fall-Winter'] = (curr_enroll, max_enroll, waitlist)
        elif sessions[0][-1] == '9':
            self.sessions['Fall'] = (curr_enroll, max_enroll, waitlist)
        elif sessions[0][-1] == '1':
            self.sessions['Winter'] = (curr_enroll, max_enroll, waitlist)
        else:
            print('Error reading in session in formation for ' + str(self))
            assert False

    def get_semesters(self) -> list:
        """
        Returns a list of the semesters in which it's possible to take this course
        """
        return [semester for semester in self.sessions]
    
    def get_sessions(self) -> dict:
        return self.sessions

    def process_course_list(self, clean_str: str) -> list:
        """
        Turns a clean string into a list of courses.
        If you have to take all of a list of courses, the 0th index of the list is "all",
        and if any course from a series of courses will suffice, the 0th index is "any"
        """
        
        course_list = ["all"]
        self.process_course_list_recursive(course_list, clean_str)

        #If the list has exactly one element that's a list, extract it and return that instead
        if len(course_list) == 2 and type(course_list[1]) == list:
            course_list = course_list[1]
        
        return course_list

    def process_course_list_recursive(self, course_list: list, remaining_str: str) -> str:
        #If only one course remains, add it to the current list and return a blank string 
        if re.search(r"[\(\),/\[\];]", remaining_str) is None:
                if remaining_str != "":
                    course_list.append(remaining_str)
                return ""
        
        idx = re.search(r"[\(\),/\[\];]", remaining_str).start()

        #Finds the current course and delimiter
        course = remaining_str[:idx]
        delimiter = remaining_str[idx]
        remaining_str = remaining_str[idx+1:]

        if delimiter in ('(','[') and course != "":
            #We should never have a course followed by a parenthases without a delimiter
            print("Error reading in information from " + str(self) + " ; could not parse \""
                   + self.prereq_string + "\"." + "Best attempt was \"" + self.clean_string(self.prereq_string) + "\"") 
            assert False

        if course != "":
            course_list.append(course)

        #If we need to create a new branch, we do so
        if delimiter in (';' ,',') and course_list[0] == "any":
            return ";" + remaining_str
        
        elif delimiter == '/' and  course_list[0] == "all":
            new_list = ["any"]

            if len(course_list) > 1:
                #The last element of course_list should have been inside this all statement
                new_list.append(course_list.pop())

            remaining_str = self.process_course_list_recursive(new_list, remaining_str)

            if len(new_list) == 2:
                #If only one item was inside the parenthases, we add it to this list
                course_list.append(new_list[1])
            elif len(new_list) > 2:
                course_list.append(new_list)

            if len(remaining_str) > 0 and remaining_str[0] == ')':
                return remaining_str
        elif delimiter in ('(','['):
            new_list = ["all"]
            remaining_str = self.process_course_list_recursive(new_list, remaining_str)

            if remaining_str[0] == ')':
                remaining_str = remaining_str[1:]
            else:
                print('Error with parenthases when processing prerequisite in course' + str(self))
                assert False
            
            if len(new_list) == 2:
                #If only one item was inside the parenthases, we add it to this list
                course_list.append(new_list[1])
            elif len(new_list) > 2:
                #If there was more than 1 item inside the parenthases, we add the 
                #   list from the parenthases to our current list
                course_list.append(new_list)

        elif delimiter in (')', ']'):
            return ')' + remaining_str

        #Once we return out of a sublist, we continue with the recursion
        return self.process_course_list_recursive(course_list, remaining_str)

    def clean_string(self, messy_str: str) -> str:
        """
        Returns a version of the string that contains only courses, separated by
        the characters "(),/;"

        So, text fragments such as "60% or higher in CSC148H1" are removed. If an unrecognized string is 
        contained, it is added to the notes.
        """
        result = ""

        remaining_str = self.clear_patterns(messy_str)
        uncleanable = False

        while len(remaining_str) > 0:
            if re.search(r"[\(\),/\[\];]", remaining_str) is not None:
                idx = re.search(r"[\(\),/\[\];]", remaining_str).start()
            else:
                idx = len(remaining_str)
            
            portion = remaining_str[:idx].strip()

            if is_st_george_course(portion) or portion == 'completed':
                result += portion
            elif portion != "":
                # print(portion)
                uncleanable = True
            
            #If there was an ending delimiter, add it back
            if idx < len(remaining_str):
                result += remaining_str[idx]

            remaining_str = remaining_str[idx+1:]

        if uncleanable:
            self.notes += "Uncleanable string: \"" + messy_str + "\""
            # print(str(self) + ": " +  self.notes)
        
        return result

    def clear_patterns(self, messy_str: str) -> str:
        """
        Modifies expressions that matches the regexes in `test_course.py`
        Expressions in `to_delete` are deleted
        Expressions in `notable` are removed, and a note is added to self.notes
        """

        for pattern, message in NOTEABLE.items():
            if re.search(pattern, messy_str) is not None:
                if message[0] == ".":
                    self.notes += message[1:] + ' '.join([str(text) for text in re.findall(pattern, messy_str)])
                else:
                    self.notes += "Note: " + message
               
                messy_str = re.sub(pattern, '', messy_str)

        for pattern in COMPLETED_STRINGS:
            messy_str = re.sub(pattern, 'completed', messy_str)

        for pattern in TO_DELETE:
            messy_str = re.sub(pattern, '', messy_str)

        messy_str = re.sub(r"and", ';', messy_str)

        return messy_str

def is_st_george_course(test_string: str) -> bool:
    """
    Checks if a course code matches the format for a St.George campus course
    """
    return (len(test_string) == 8 and test_string[0:3].isalpha() and test_string[3:6].isnumeric()
                and test_string[6].isalpha() and test_string[7]=='1')

def to_json_file(course_list: dict[str,Course], filename: str):
    """
    Takes a dictionary of the form {course name: course object},
    and writes all of its information to filename
    """

    json_course_list = {course: course_object.to_json() 
                    for course, course_object in course_list.items()}

    pretty_json = json.dumps(json_course_list, indent=2, sort_keys=False)

    with open(filename, "w") as file:
        file.write(pretty_json)

def from_json_file(filename: str) -> dict[str,Course]:
    """
    Takes a file with JSON data for all the courses,
    and turns it into a dictionary of courses
    """
    course_list = {}

    file = open(filename, "r")
    json_course_list = json.loads(file.read())

    for course in json_course_list:
        temp_course = Course()
        temp_course.from_json(json_course_list[course])
        course_list[course] = temp_course

    return course_list