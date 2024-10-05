from course import Course, from_json_file
from filter_requisites import CURRENT_SEMESTER, PLANNED_COURSES, COMPLETED_COURSES, MANUAL_INPUT

"""
Note: semesters are represented as tuples of (academic year, semester)
Ex:

(1, "Winter")
(2, "Fall")
(1, "Fall-Winter")
"""

SEMESTER_FLOAT_MAP = {
    'Fall': 0,
    'Winter':  0.5,
    'Fall-Winter': 0.5  
}

#To get the correct semester and year addition, search NEXT_SEMESTER_MAP[available_semester][after_semester]
#A 1 in the first entry of the resulting tuple indicates that the course needs to be taken a year later
NEXT_SEMESTER_MAP = {
    'Fall': {
        'Fall': (1, 'Fall'),
        'Winter': (1, 'Fall'),
        'Fall-Winter': (1,'Fall')
    },
    'Winter': {
        'Fall': (0, 'Winter'),
        'Winter': (1, 'Winter'),
        'Fall-Winter': (1,  'Winter')
    },
    'Fall-Winter': {
        'Fall': (1, 'Fall-Winter'),
        'Winter': (1, 'Fall-Winter'),
        'Fall-Winter': (1, 'Fall-Winter')
    }
}

NOT_BEFORE_SEMESTER_MAP = {
    'Fall': {
        'Fall': (0, 'Fall'),
        'Winter': (1, 'Fall'),
        'Fall-Winter': (0,'Fall')
    },
    'Winter': {
        'Fall': (0, 'Winter'),
        'Winter': (0, 'Winter'),
        'Fall-Winter': (0,  'Winter')
    },
    'Fall-Winter': {
        'Fall': (0, 'Fall-Winter'),
        'Winter': (0, 'Fall-Winter'),
        'Fall-Winter': (0, 'Fall-Winter')
    }
}

def is_strictly_before(semester_1: tuple, semester_2: tuple) -> bool:
    """
    Checks if semester_1 is before semester_2.
    If semester_1 and semester2 are the same, returns false
    """

    if semester_1[0] < semester_2[0]:
        return True
    else: 
        return SEMESTER_FLOAT_MAP[semester_1[1]] < SEMESTER_FLOAT_MAP[semester_2[1]]

def max_semester(dates: list):
    return max(dates, key= lambda date: date[0] + SEMESTER_FLOAT_MAP[date[1]])

def min_semester(dates: list):
    return min(dates, key= lambda date: date[0] + SEMESTER_FLOAT_MAP[date[1]])

def next_semester_available(available_semesters: list, not_before_semester: tuple, after_semester: list):
    """
    Returns the first semester in available_semesters that is after semester and not before current_semester
    """
    next_available = (10000, 'Fall')

    for available_semester in available_semesters:
        to_add = NEXT_SEMESTER_MAP[available_semester][after_semester[1]]
        possibility_1 = (after_semester[0] + to_add[0], to_add[1])

        to_add = NOT_BEFORE_SEMESTER_MAP[available_semester][not_before_semester[1]]
        possibility_2 = (not_before_semester[0] + to_add[0], to_add[1])

        semester_earliest = max([possibility_1, possibility_2])

        next_available = min([next_available, semester_earliest])
    
    return next_available

def first_semester_reqs_finished(course_list: dict, earliest_semesters: dict, reqs_list: list) -> tuple[int,str]:
    """
    Returns the first semester in which all the requisites in reqs_list will have been finished.
    """

    isBlank = True

    if reqs_list[0] == 'all':
        first_semester_finished = (0, 'Fall')

        for req in reqs_list[1:]:
            if req in COMPLETED_COURSES or req == 'completed':
                isBlank = False
                continue
            elif type(req) == list:
                isBlank = False
                sublist_first_semester = first_semester_reqs_finished(course_list, earliest_semesters, req)
                
                first_semester_finished = max([first_semester_finished, sublist_first_semester])
            elif req in course_list:
                isBlank = False
                if req not in earliest_semesters:
                    first_semester_takeable(course_list, earliest_semesters, req)
    
                first_semester_finished = max([first_semester_finished, earliest_semesters[req]])
                
    elif reqs_list[0] == 'any':
        #TODO: figure out a way to do this without initializing a variable here
        first_semester_finished = (1000, 'Fall')

        for req in reqs_list[1:]:
            if req in COMPLETED_COURSES or req == 'completed':
                return (0, 'Fall')
            elif type(req) == list:
                sublist_first_semester = first_semester_reqs_finished(course_list, earliest_semesters, req)
                
                if sublist_first_semester[0] != -1:
                    isBlank = False
                    first_semester_finished = min([first_semester_finished, sublist_first_semester])
            elif req in course_list:
                isBlank = False
                if req not in earliest_semesters:
                    first_semester_takeable(course_list, earliest_semesters, req)
                
                first_semester_finished = min([first_semester_finished, earliest_semesters[req]])
            elif req == "COMPLETED_COURSES":
                return (0, 'Fall')

    if isBlank:
        return (-1, 'Fall')
    else:
        return first_semester_finished


def first_semester_takeable(course_list: dict, earliest_semesters: dict, course_name: str):
    """
    Returns the earliest semester in which it is possible to take a course.
    This is the first semester which 
        - All prerequisites can have been COMPLETED_COURSES
        - All corequisites have either been COMPLETED_COURSES, or are being taken
        - Is after `CURRENT_SEMESTER`
    """
    if course_name in COMPLETED_COURSES: 
        earliest_semesters.update({course_name :(0, 'Fall')})
    elif course_name in PLANNED_COURSES:
        earliest_semesters.update({course_name : PLANNED_COURSES[course_name]})
    else: 
        earliest_semesters.update({course_name: next_semester_available(
            course_list[course_name].get_semesters(),
            first_semester_reqs_finished(course_list, earliest_semesters, course_list[course_name].get_corequisites()),
            max([
                first_semester_reqs_finished(course_list, earliest_semesters, course_list[course_name].get_prerequisites()),
                CURRENT_SEMESTER
            ])
        )})

def get_completion_options(earlist_semesters: dict, course_earlist_semester: tuple, req_list: list, is_before: bool, include_planned:bool = True) -> tuple[bool,str]:
    """
    Returns the possibilities for how to complete `req_list` before `course_earlist_semester`.
    If `is_before` is False, also allows things in `req_list` to be completed concurrently with `course_earlist_semester`

    Does not include completed courses

    Preferrentially includes courses in `PLANNED_COURSES`. For example, if both MAT100 and MAT101 suffice as the requisite,
    and MAT100 is in the list of planned courses, will write `MAT100`

    If `include_planned` is True, will include the courses from `PLANNED_COURSES` in this list.
    Otherwise, will only show the un-planned courses that still have to be completed.
    """
    #We keep track of whether all of the requisites in req_list are planned/completed
    all_planned = True
    result_str = ''

    if req_list[0] == 'all':
        for req in req_list[1:]:
            if type(req) == list:
                planned,sublist_str = get_completion_options(earlist_semesters, course_earlist_semester, req, is_before, include_planned)
                if len(sublist_str) > 0:
                    #Checks whether there's more than one course in the sublist
                    if len(sublist_str) > 8:
                        sublist_str = '(' + sublist_str + ')'
                    result_str += ';' + sublist_str
                if not planned:
                    all_planned = False
            elif req in COMPLETED_COURSES or req == "completed":
                pass
            elif req not in PLANNED_COURSES:
                all_planned = False
                result_str += ';' + req

                if req not in earlist_semesters:
                    result_str += '(unaccounted)'
            elif include_planned:
                result_str += ';'+ req

        return (all_planned, result_str[1:])
    elif req_list[0] == 'any':
        #If this sublist has been 'completed', we return a blank string
        #Otherwise, returns only the planned options (if planned options exist),
        # and unplanned options if there are no planned options
        planned_options = []
        unplanned_options = []

        for req in req_list[1:]:
            if type(req) == list:
                planned, sublist_str = get_completion_options(earlist_semesters, course_earlist_semester, req, is_before, include_planned)

                #Checks whether the sublist was entirely completed
                if planned and sublist_str == "":
                    return (True, "")
                elif planned:
                    if len(sublist_str) > 8:
                        sublist_str = '(' + sublist_str + ')'
                    planned_options += [sublist_str]
                else:
                    unplanned_options += ['(' + sublist_str + ')']
            elif req in COMPLETED_COURSES or req == "completed":
                return (True,"")
            elif req in PLANNED_COURSES:
                if is_before and is_strictly_before(earlist_semesters[req], course_earlist_semester):
                    planned_options += [req]
                elif (not is_before) and (not is_strictly_before(course_earlist_semester, earlist_semesters[req])):
                    planned_options += [req]
            elif req not in earlist_semesters:
                unplanned_options += [req + '(unaccounted)']
            else:
                if is_before and is_strictly_before(earlist_semesters[req], course_earlist_semester):
                    unplanned_options += [req]
                elif (not is_before) and (not is_strictly_before(course_earlist_semester, earlist_semesters[req])):
                    unplanned_options += [req]

        if len(planned_options) > 0 and include_planned:
            return (True,'/'.join(planned_options))
        elif len(planned_options) > 0:
            return (True, '') 
        elif len(planned_options) == 0:
            return (False,'/'.join(unplanned_options))


if __name__ == '__main__':
    courses = from_json_file("./Data/merged_courses.json")
    earliest_sems = PLANNED_COURSES.copy()
    earliest_sems = earliest_sems | MANUAL_INPUT

    for course in courses:
        if course not in earliest_sems:
            first_semester_takeable(courses, earliest_sems, course)

    import pandas as pd
    printable_data = {
        "Title": [],
        "Earliest Semester Takeable": [],
        "Prereqs": [],
        "Coreqs": [],
        "Exclusions": [],
        "Notes": [],
        "Semesters Available": [],
        "Raw Prereqs": []
    }

    course_names = []

    for course in courses:
        course_obj = courses[course]

        course_names.append(course_obj.get_name())

        _, prereq_list = get_completion_options(earliest_sems, earliest_sems[course], course_obj.get_prerequisites(), True, include_planned=False)
        _, coreq_list = get_completion_options(earliest_sems, earliest_sems[course], course_obj.get_corequisites(), False, include_planned=False)
        
        semesters = course_obj.get_sessions()
        close_to_full = [name for name,enrollment in semesters.items() if (enrollment[0] + enrollment[2] > 1.1 * enrollment[1])
                        or (enrollment != "Winter" and enrollment[0] > 0.9 * enrollment[1])]

        printable_data['Title'].append(course_obj.get_title())
        
        printable_data['Earliest Semester Takeable'].append(str(earliest_sems[course])
                    + ('!!' if earliest_sems[course][1] in close_to_full else ''))
        printable_data['Prereqs'].append(prereq_list)
        printable_data['Coreqs'].append(coreq_list)
        printable_data['Notes'].append(course_obj.get_notes())
        printable_data['Exclusions'].append(','.join(course_obj.get_exclusions()))


        printable_data['Semesters Available'].append(','.join(
            [semester + ('!!' if semester in close_to_full else '') for semester,_ in semesters.items()]
        ))

        printable_data['Raw Prereqs'].append(course_obj.get_prerequisites_raw())
    
    df = pd.DataFrame(printable_data, course_names)
    df.to_csv('./Data/processed_courses.csv')

        # print(course + ": " + str(earliest_sems[course]) + "\n" + prereq_list + "\n" + coreq_list + "\n")