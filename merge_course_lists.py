from course import Course, from_json_file, to_json_file
from calendar_scraper import exists_matching_course as calendar_exists_matching_course
from ttb_scraper import exists_matching_course as ttb_exists_matching_course
import time

ttb_courses = from_json_file("./Data/ttb_courses.json")
calendar_courses = from_json_file("./Data/calendar_courses.json")

#A list of the courses in both the ttb and calendar course lists
intersecting_names = [course_name for course_name in ttb_courses if course_name in calendar_courses]

merged_course_list = {}
for course_name in intersecting_names:
    if ttb_courses[course_name] == calendar_courses[course_name]:
        merged_course_list[course_name] = ttb_courses[course_name]
    else:
        #If the only difference between the courses is the title, takes the version from the academic calendar
        ttb_courses[course_name].set_title(calendar_courses[course_name].get_title())
        if ttb_courses[course_name] == calendar_courses[course_name]:
            merged_course_list[course_name] = ttb_courses[course_name]
        else:
            print("Error: the ttb and calendar versions of " + course_name + " are not the same")

for course_name in ttb_courses:
    if course_name not in calendar_courses:
        time.sleep(0.01)
        if calendar_exists_matching_course(ttb_courses[course_name]):
            merged_course_list[course_name] = ttb_courses[course_name]
        else:
            print("Error: there is no calendar version of the course " + course_name)

for course_name in calendar_courses:
    if course_name not in ttb_courses:
        time.sleep(0.01)
        if ttb_exists_matching_course(calendar_courses[course_name]):
            merged_course_list[course_name] = calendar_courses[course_name]
        else:
            print("Error: there is no ttb version of the course " + course_name)

to_json_file(merged_course_list, './Data/merged_courses.json')