from course import Course, is_st_george_course

def test_is_st_george_course() -> None:
    assert is_st_george_course("MAT240H1") == \
        True
    
    assert is_st_george_course("CS101") == \
        False

    assert is_st_george_course("CSC120H3") == \
        False

def test_clear_patterns() -> None:
        course = Course()
        assert course.clear_patterns("60% or higher in CSC148H1") == \
            'CSC148H1'

        assert course.clear_patterns("with a minimum mark of at least 70%") == \
            ''

        assert course.clear_patterns(" CSC110Y1") ==\
            'CSC110Y1'

        assert course.clear_patterns("High school level calculus") == \
            'completed'

        assert course.clear_patterns("permission of the Associate Chair for\
 Undergraduate Studies and of the prospective supervisor.") == \
            ''
        assert course.get_notes() == \
            'Note: Need undergrad chair permission'

def test_clean_string() -> None:
        course = Course()
        assert course.clean_string("60% or higher in  CSC148H1/ 60% or higher in  CSC111H1/ ESC190H1") == \
            'CSC148H1/CSC111H1/ESC190H1'

        assert course.clean_string("CSC209H1/  CSC209H5/  CSC207H1") == \
            'CSC209H1//CSC207H1'

        assert course.clean_string("CSC165H1 (with a minimum mark of at least 85%)/\
 students with a strong mathematical background who have not completed CSC110Y1\
 or CSC165H1 may enrol in CSC240H1 as an enriched alternative to CSC165H1") == \
            'CSC165H1/'
        
        assert course.get_notes() == \
            'Uncleanable string: \"CSC165H1 (with a minimum mark of at least 85%)/\
 students with a strong mathematical background who have not completed CSC110Y1\
 or CSC165H1 may enrol in CSC240H1 as an enriched alternative to CSC165H1\"'

        course = Course()
        assert course.clean_string("CSC110H1/ CSC236H5; CSC111H1// CSC210H1") == \
            'CSC110H1/;CSC111H1//CSC210H1'

        assert course.clean_string("CSC23H1; CSC111H1/ not a course/ CSC210H1") == \
            ';CSC111H1//CSC210H1'

        assert course.clean_string("(60% or higher in CSC148H1, 60% or higher in CSC165H1)\
 / (60% or higher in CSC111H1)") == \
            '(CSC148H1,CSC165H1)/(CSC111H1)'

        assert course.get_notes() == \
            'Uncleanable string: \"CSC23H1; CSC111H1/ not a course/ CSC210H1\"'
        
        assert course.clean_string("High school level calculus") == \
            'completed'

def test_process_course_list() -> None:
    course = Course()

    assert course.process_course_list("CSC209H1") == \
        ['all', 'CSC209H1']
    
    assert course.process_course_list("CSC209H1/CSC207H1/CSC109H1") == \
        ['any', 'CSC209H1', 'CSC207H1', 'CSC109H1']

    assert course.process_course_list("CSC209H1/CSC207H1/CSC109H1;CSC309H1/CSC109H1") == \
        ['all', ['any', 'CSC209H1', 'CSC207H1', 'CSC109H1'], \
        ['any', 'CSC309H1', 'CSC109H1']]

    assert course.process_course_list("CSC100H1;CSC101H1/CSC102H1;CSC103H1") == \
        ['all', 'CSC100H1', ['any', 'CSC101H1', 'CSC102H1'], 'CSC103H1']
    
    assert course.process_course_list(";CSC165H1/") == \
    ['all', 'CSC165H1']
    
    assert course.process_course_list("(CSC148H1,CSC165H1)/(CSC111H1)") == \
        ['any', ['all', 'CSC148H1', 'CSC165H1'], 'CSC111H1']

    assert course.process_course_list("") == \
        ['all']
    
    assert course.process_course_list("CSC112H1;completed/CSC111H1") == \
        ['all', 'CSC112H1', ['any', 'completed', 'CSC111H1']]

    assert course.process_course_list("CSC112H1;completed;CSC111H1") == \
        ['all', 'CSC112H1', 'completed', 'CSC111H1']

if __name__ == '__main__':
    import pytest
    pytest.main(['test_course.py'])