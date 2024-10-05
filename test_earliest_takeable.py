from earliest_takeable import max_semester, min_semester, next_semester_available,\
    first_semester_reqs_finished, first_semester_takeable
from course import Course

def test_max_semester() -> None:
    assert(max_semester([(0, 'Winter'), (1, 'Fall'), (2, 'Fall-Winter')])) == \
        (2, 'Fall-Winter')
    
    assert(max_semester([(2, 'Winter'), (1, 'Fall'), (2, 'Fall')])) == \
        (2, 'Winter')
    
    assert(max_semester([(2, 'Winter'), (3, 'Fall'), (2, 'Fall')])) == \
        (3, 'Fall')
    
def test_min_semester() -> None:
    assert(min_semester([(0, 'Winter'), (1, 'Fall'), (2, 'Fall-Winter')])) == \
        (0, 'Winter')
    
    assert(min_semester([(2, 'Winter'), (1, 'Fall'), (2, 'Fall')])) == \
        (1, 'Fall')
    
    assert(min_semester([(2, 'Winter'), (3, 'Fall'), (2, 'Fall')])) == \
        (2, 'Fall')

def test_next_semester_available() -> None:
    available_semesters = ["Fall"]

    assert next_semester_available(available_semesters, (1, 'Fall'), (0, 'Fall')) == \
        (1, 'Fall')

    assert next_semester_available(available_semesters, (1, 'Fall'), (0, 'Winter')) == \
        (1, 'Fall')
    
    assert next_semester_available(available_semesters, (1, 'Fall'), (1, 'Fall')) == \
        (2, 'Fall')
    
    assert next_semester_available(available_semesters, (1, 'Fall'), (1, 'Winter')) == \
        (2, 'Fall')

    available_semesters += ["Winter"]

    assert next_semester_available(available_semesters, (1, 'Winter'), (0, 'Fall')) == \
        (1, 'Winter')

    assert next_semester_available(available_semesters, (1, 'Fall'), (0, 'Winter')) == \
        (1, 'Fall')
    
    assert next_semester_available(available_semesters, (1, 'Fall'), (1, 'Fall')) == \
        (1, 'Winter')
    
    assert next_semester_available(available_semesters, (1, 'Fall'), (1, 'Winter')) == \
        (2, 'Fall')

def test_first_semester_reqs_finished():
    course_list = {
        "AAA100H1" : None,
        "AAA101H1" : None,
        "AAA102H1" : None,
        "AAA103H1" : None,
        "AAA104H1" : None,
        "AAA105H1" : None,
    }

    earliest_takeable = {
        "AAA100H1" : (0, "Fall"),
        "AAA101H1" : (0, "Winter"),
        "AAA102H1" : (0, "Fall-Winter"),
        "AAA103H1" : (1, "Fall"),
        "AAA104H1" : (1, "Winter"),
        "AAA105H1" : (1, "Fall-Winter"),
    }

    req_list = [
        "any",
        "AAA101H1",
        "AAA105H1",
        [
            "all",
            "AAA102H1",
            "AAA103H1"
        ]
    ]

    assert first_semester_reqs_finished(course_list,earliest_takeable,req_list) == \
        (0, 'Winter')
    
    req_list = [
        "all",
        "AAA101H1",
        [
            "any",
            "AAA103H1",
            "AAA105H1"
        ]
    ]

    assert first_semester_reqs_finished(course_list,earliest_takeable,req_list) == \
        (1, 'Fall')
    
    req_list = [
      "all",
      "AAA102H1",
      "AAA103H1",
      "AAA104H1"
    ]

    assert first_semester_reqs_finished(course_list,earliest_takeable,req_list) == \
        (1, 'Winter')

    req_list = [
      "all",
      "AAA102H1",
      "AAA101H1",
      "AAA100H1"
    ]

    assert first_semester_reqs_finished(course_list,earliest_takeable,req_list) == \
        (0, 'Winter')

def test_first_semester_takeable() -> None:
    course_list = {
        "AAA100H1" : None,
        "AAA101H1" : None,
        "AAA102H1" : None,
        "AAA103H1" : None,
        "AAA104H1" : None,
        "AAA105H1" : None,
    }

    earliest_takeable = {
        "AAA100H1" : (10, "Fall"),
        "AAA101H1" : (10, "Winter"),
        "AAA102H1" : (10, "Fall-Winter"),
        "AAA103H1" : (11, "Fall"),
        "AAA104H1" : (11, "Winter"),
        "AAA105H1" : (11, "Fall-Winter"),
    }

    course_1 = Course()
    course_1.set_name('AAA106H1')
    course_1.add_session(['20249'], 1, 1, 1)
    course_list['AAA106H1'] = course_1

    prereq_list = "AAA102H1;AAA103H1;AAA104H1"
    course_1.set_prerequisites(prereq_list)

    coreq_list = ""
    course_1.set_corequisites(coreq_list)

    first_semester_takeable(course_list, earliest_takeable, 'AAA106H1')
    assert earliest_takeable['AAA106H1'] == (12, 'Fall')
    
    coreq_list = 'AAA104H1,AAA105H1'
    course_1.set_corequisites(coreq_list)

    first_semester_takeable(course_list, earliest_takeable, 'AAA106H1')
    assert earliest_takeable['AAA106H1'] == (12, 'Fall')

def test_get_completion_options() -> None:
    pass

if __name__ == '__main__':
    import pytest
    pytest.main(['test_earliest_takeable.py'])