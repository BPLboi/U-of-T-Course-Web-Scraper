import requests
from bs4 import BeautifulSoup
from course import Course, to_json_file

def get_links_element(course_row, element_type: str, class_type: str) -> list:
    link_list = []
    if course_row.find(element_type, class_=class_type) is not None:
        links = course_row.find(element_type, class_=class_type).find(element_type).find_all('a')
    
        for link in links:
            link_list += [link.text]

    return link_list

def get_text_element(course_row, element_type: str, class_type: str) -> str:
    text_string = ""
    if course_row.find(element_type, class_=class_type) is not None:
        text_string = course_row.find(element_type, class_=class_type).find(element_type).text
        
    return text_string

def get_courses_webpage(website_url: str) -> dict:
    """
    Given a department code (ex. "CSC, MAT, STA") within the arts and sciences, 
        finds all the courses with that three-letter designator, 

    , and returns a dictionary of {"Course name": the Course object containing all of the relevant information}
    """
    courses = {}

    #Gets the html from the webpage
    response = requests.get(website_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #Finds the first course row
    course_row = soup.find('div', class_ = 'views-row')
    
    while course_row is not None:
        #Sets up the course which is being viewed
        this_class = Course()

        #On the first instance of views-row, there is one division which contains 
        #   both the course name and title
        title_text = course_row.find('div').text
        (course, title) = title_text.split(' - ', 1)
        course = course.strip()
        title = title.strip()

        this_class.set_name(course)
        this_class.set_title(title)

        #Iterates to the next course_row, which is the second part of this course's description
        course_row = course_row.find_next('div', class_ = 'views-row')

        #Get the exclusions
        exclusions_list = get_links_element(course_row, "span", "views-field views-field-field-exclusion")
        this_class.set_exclusions(exclusions_list)

        #Finds all the prerequisites for this class
        prereq_string = get_text_element(course_row, "span", "views-field views-field-field-prerequisite")
        this_class.set_prerequisites(prereq_string)

        #Finds all the corequisites for this class
        coreq_string = get_text_element(course_row, "span", "views-field views-field-field-corequisite")            
        this_class.set_corequisites(coreq_string)

        #Adds the course to the dictionary
        courses[course] = this_class

        #Iterates to the next course
        course_row = course_row.find_next('div', class_ = 'views-row')

    return courses

def get_courses(departments: list) -> dict:
    course_list = {}

    for department in departments:
        webpage_courses = {"a":"b"}
        page = 0
        while len(webpage_courses) > 0:
            webpage_courses = get_courses_webpage(
                f"https://artsci.calendar.utoronto.ca/search-courses?field_section_value={department}&page={page}")
            
            #Appends the webpage courses to the list
            course_list = course_list | webpage_courses
            page += 1
    
    return course_list

def exists_matching_course(other_course: Course) -> bool:
    website_url = f"https://artsci.calendar.utoronto.ca/course/{other_course.get_name()}"

    response = requests.get(website_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_text = soup.find('h1', class_ = "page-title").text

    #Checks if the course page even exists
    if title_text.strip() == "Page not found" or len(title_text.split(':')) != 2:
        return False
    else:
        new_course = Course()

        #Finds the course name and title
        (course_name, title) = title_text.split(':')
        course_name = course_name.strip()
        title = title.strip()

        new_course.set_name(course_name)
        new_course.set_title(title)

        #Finds all the exclusions for the class
        exclusions_list = get_links_element(soup, "div", 
                "w3-row field field--name-field-exclusion field--type-text-long field--label-inline clearfix")
        new_course.set_exclusions(exclusions_list)

        #Finds all the prerequisites for this class
        prereq_string = get_text_element(soup, "div", 
                "w3-row field field--name-field-prerequisite field--type-text-long field--label-inline clearfix")
        new_course.set_prerequisites(prereq_string)

        #Finds all the corequisites for this class
        coreq_string = get_text_element(soup, "div",
                "w3-row field field--name-field-corequisite field--type-text-long field--label-inline clearfix")            
        new_course.set_corequisites(coreq_string)

        return new_course == other_course

if __name__ == '__main__':
    courses = get_courses(["Mathematics", "Computer+Science", "Physics", 
                           "Statistical+Sciences", "Data+Science"])
    to_json_file(courses, './Data/calendar_courses.json')