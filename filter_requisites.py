#All classes must be assigned after this semester
CURRENT_SEMESTER = (1, "Fall")

#A list of all already completed classes
COMPLETED_STRINGS = [
    r"High school level calculus",
    r"High school level algebra\.?",
    r"Grade 12 Mathematics",
    r"equivalent programming experience",
    r"proficiency in C or C\+\+",
    r"(Any )?0.5 credit in CSC",
    r"MCV4U Calculus & Vectors",
    r"MCB4U Functions & Calculus",
    r"SPH4U Physics",
    r"SCH4U Chemistry",
    r"ICS4U Computer Science",
    r"SES4U Earth and Space Science"
]

COMPLETED_COURSES = [
    r"MAT223H1",
    r"MAT240H1",
    r"CSC110Y1",
    r"SPA302H1",
    r"PHY151H1",
    r"PHY152H1"
]

PLANNED_COURSES = {
    "MAT157Y1": (1, "Fall-Winter"),
    "MAT247H1": (1,"Winter"),
    "CSC111H1" : (1, "Winter"),
    "CSC240H1" : (1, "Winter"),
    "CSC300H1" : (1,"Winter"),
    "MAT257Y1" : (2, "Fall-Winter"),
}

MANUAL_INPUT = {
    "MAT363H1": (2, 'Winter')
}

#Strings that will cause a note to be generated in clear_patterns
NOTEABLE = {
    r"[pP]ermission of the Associate Chair for Undergraduate Studies and of the prospective supervisor": 
        "Need undergrad chair permission",
    r"Consult the Physics Associate Chair \(Undergraduate Studies\)": "Need undergrad chair permission",
    r"Possible additional topic-specific prerequisites":
        "Possible topic-specific prereqs",
    r"\((\s)?[A-Z0-9]{8} can be taken concurrently\)" : ".Note: ",
    #Some number of credits at at least some level in some department
    r"[0-9].[0-9] credits with a CGPA of at least [0-9].[0-9], and" : ".Need ",
    r"(and at least )?[0-9]\.[0-9] [A-Z]{3}/[A-Z]{3} credit(s)? at the [0-9]00(/[0-9]00)?(\+)?(-|\s)level" : ".Prereq: ",
    r"[0-9]\.[0-9] [A-Z]{3}/[A-Z]{3} credit(s)? at the 100, 200 and 300-level": ".Prereq: ",
    r"[0-9]\.[0-9] credits of [0-9]00\+ level [A-Z]{3} courses" : ".Prereq: ",
    r"[0-9]\.[0-9] credits of [0-9]00\+ level CSC courses" : ".Prereq: ",
    r"(and )?(at least )?[0-9]\.[0-9] credit(s)? (in [A-Z]{3} )?at the [0-9]00(-|\+ )level( or higher)?( in [A-Z]{3}/[A-Z]{3})?": ".Prereq: ",
    r"[0-9]\.[0-9] credit(s)? in [A-Z]{3}": ".Prereq: ",
    r"[0-9]\.[0-9] credits": ".Prereq: ",
    #Other exemptions
    r" or by permission of the instructor": "Can take with instructor permission",
    r"Students who do not meet these prerequisites are encouraged to contact the Department":
        " can contact department for prereq exemptions",
    r"[Nn]ote:\s+[A-Z0-9]{8}\s+may be taken as a co-requisite": ".",
    r"\([Nn]ote:[A-Z0-9\s\(\),/;]*(are )?very strongly recommended(\.)?\)": ".",
    r"\([A-Za-z\s\.:]+\)": ".",
    r"equivalent mathematical background": "can skip some prereqs with enough math experience",
    r"\*Note\: the corequisite may be completed either concurrently or in advance": ".",
    r"proficiency in C, C\+\+, or Fortran" : ".Note: can skip stuff with",
    r"or equivalent (AST )?readings(;|,) consult the instructor": ".Note: can skip stuff with",
    r"and exposure to PDEs": "Might need PDE exposure"
}

#A list of strings that will be deleted in clear_patterns
TO_DELETE = [
    r"Corequisite: ",
    r"Prerequisite: ",
    r"Exclusion(s)?: ",
    r"Any CSC 0.5 credit, and balloting",
    r"For FASE students, [A-Z0-9,\(\)\\\s]*",
    r"No prior experience with physical science will be required, but familiarity with Grade 10 mathematics will be assumed",
    r"[0-9].[0-9] [A-Z]{3} credit at the 100-level",
    #Deletes minimum GPA requirements
    r"[mM]inimum GPA( of)? [0-9]\.[0-9] (for|of|in) [A-Z]{3} and [A-Z]{3} courses",
    r"Minimum GPA of [0-9]\.[0-9]",
    #Removes all kinds of expressions that specify a minimum grade
    r"with a minimum mark of (at least )?[0-9][0-9](%)?",
    r"minimum (grade )?(of )?[0-9][0-9]%",
    r"minimum of [0-9]{2}% in ",
    r"[0-9][0-9]% or higher( in)?",
    r"[0-9][0-9]%( in )?( )?",
    #Removes recommended courses (I only care about required ones...)
    r"\([.]* recommended\)",
    r"recommended",
    r"[A-Z0-9]{6}[HY][35]", #removes non-st.george courses
    r"\s", #at the end, deletes whitespaces
    r"\.", #and punctuation (presumably left by previous sentences)
    r"\u200b", #whitespace character
    r"\u00a0",
    r"\xa0",
    r"None",
    r"\(\)", #deletes stray pairs of parenthases
    r"\[\]"
]

