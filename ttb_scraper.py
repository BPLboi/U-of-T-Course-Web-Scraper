from course import Course, to_json_file
from http.client import HTTPSConnection
from math import ceil
from bs4 import BeautifulSoup
import json
import re

server = 'api.easi.utoronto.ca'

default_headers = open("./Data/ttb_request_headers.json", "r")
headers = json.loads(default_headers.read())

default_json_payload = json.loads(open("./Data/ttb_request_payload.json", "r").read())
default_json_payload["page"] = 0

def get_matching_departments(term: str, divisions: list) -> list:
    """
    Takes in a term and a list of departments (ex. "ARTSCI", "APSC"),
    and returns a list of every department that matches that term

    >>> get_matching_departments("math", ["ARTSCI"])
    [{'division': 'ARTSC', 'department': 'Department of Mathematics', 'type': 'DEPARTMENT'},\
        {'division': 'ARTSC', 'department': 'Mathematics', 'type': 'SECTION'}]
    """
    path = f'/ttb/getMatchingDepartments?term={term}&divisions={'&divisions='.join(divisions)}'

    json_payload = {}
    payload = json.dumps(json_payload)

    #Connect to the ttb api and make a request
    conn = HTTPSConnection(server)
    conn.request('GET', path, payload, headers)
    res = conn.getresponse()

    #Sometimes the response code and headers are useful for debugging
    res_code = res.code
    if res_code != 200:
        print("Error: invalid response to the payload " + str(payload)+ ". Data recieved: " + res.read().decode('utf-8'))

    #Gets the JSON data from the request
    res_data = res.read()
    json_res_data =  json.loads(res_data.decode('utf-8'))

    #Parses the JSON string
    matching_departments = []
    for department in json_res_data['payload']['departments']:
        for item in json_res_data['payload']['departments'][department]:
            matching_departments += [{
                'division': item['faculty']['code'],
                'department': item['name'],
                'type': item['type'], 
            }]

    return matching_departments

def get_matching_departments_multiple(terms: list, divisions: list) -> list:
    matching_departments = []
    for term in terms:
        matching_departments += get_matching_departments(term, divisions)

    return matching_departments

def make_search_json_request(json_payload: dict) -> dict:
    path = '/ttb/getPageableCourses'
    payload = json.dumps(json_payload)

    conn = HTTPSConnection(server)
    conn.request('POST', path, payload, headers)
    res = conn.getresponse()

    #Sends an error message; used for debugging
    # res_code = res.code
    # if res_code != 200:
    #     print("Error: no response to the payload " + str(payload))

    #Gets the JSON data from the request
    res_data = res.read()

    return json.loads(res_data.decode('utf-8'))

def create_course_obj(course_dict: dict) -> Course:
    course_obj = Course()

    course_obj.set_name(course_dict['code'])
    course_obj.set_title(course_dict['name'])
    
    if course_dict['cmCourseInfo'] is None:
        print("Error reading course " + str(course_obj))
        assert False

    #Note: some of the course information has html in it, so we use BeautifulSoup to get rid of it
    if course_dict['cmCourseInfo']['prerequisitesText'] is None:
        course_obj.set_prerequisites('')
    else:
        course_obj.set_prerequisites(
            BeautifulSoup(course_dict['cmCourseInfo']['prerequisitesText'], 'html.parser').text
        )

    if course_dict['cmCourseInfo']['corequisitesText'] is None:
        course_obj.set_corequisites('')
    else:
        course_obj.set_corequisites(
            BeautifulSoup(course_dict['cmCourseInfo']['corequisitesText'],  'html.parser').text
        )

    #Filters the text into a list of course names
    if course_dict['cmCourseInfo']['exclusionsText'] is None:
        course_obj.set_exclusions([])
    else:
        course_obj.set_exclusions(
            re.findall(r'[A-Z]{3}[0-9]{3}[A-Z][0-9]',course_dict['cmCourseInfo']['exclusionsText'])
        )

    course_obj.add_session(course_dict['sessions'],
        sum([section['currentEnrolment'] for section in course_dict['sections'] if section['type'] == 'Lecture']),
        sum([section['maxEnrolment'] for section in course_dict['sections'] if section['type'] == 'Lecture']),
        sum([section['currentWaitlist'] for section in course_dict['sections'] if section['type'] == 'Lecture']))

    return course_obj

def get_courses_page(json_payload: dict, all_courses: dict[str,Course]):
    page = make_search_json_request(json_payload)
    
    if page['payload'] is None:
        return
    
    for course_dict in page['payload']['pageableCourse']['courses']:
        if course_dict['code'] in all_courses:
            all_courses[course_dict['code']].add_session(course_dict['sessions'],
                    sum([section['currentEnrolment'] for section in course_dict['sections']]),
                    sum([section['maxEnrolment'] for section in course_dict['sections']]),
                    sum([section['currentWaitlist'] for section in course_dict['sections']]))       
        else:
            all_courses.update({course_dict['code']: create_course_obj(course_dict)})

def get_all_courses_departments(departments: list) -> dict:
    #Sets up the payload
    json_payload = default_json_payload
    json_payload['departmentProps'] = departments
    json_payload['page'] = 0

    divisions_set = {department['division'] for department in departments}
    json_payload['divisions'] = list(divisions_set)

    zero_page = make_search_json_request(json_payload)
    num_courses = zero_page['payload']['pageableCourse']['total']
    page_size = zero_page['payload']['pageableCourse']['pageSize']

    all_courses = {}
    for page_num in range(1, ceil(num_courses/page_size)+1):
        json_payload['page'] = page_num
        get_courses_page(json_payload, all_courses)

    return all_courses


def exists_matching_course(course: Course) -> bool:
    json_payload = default_json_payload

    json_payload['page'] = 1
    json_payload['courseCodeAndTitleProps']['courseTitle'] = course.get_name()
    json_payload['courseCodeAndTitleProps']['searchCourseDescription'] = True
    
    page_courses = {}
    get_courses_page(json_payload, page_courses)

    if course.get_name() not in page_courses:
        return False
    else:
        if course == page_courses[course.get_name()]:
            course.copy_sessions(page_courses[course.get_name()])
            return True 
        else:
            return False

if __name__ == "__main__":
    departments = get_matching_departments_multiple(['math', 'computer', 'physics', 'statistic'], ["ARTSC"])
    # Prints all the departments
    for department in departments:
        print(department)
    
    course_list = get_all_courses_departments(departments)
    to_json_file(course_list, "./Data/ttb_courses.json")