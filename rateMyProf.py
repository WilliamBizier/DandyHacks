import ratemyprofessor

professor_name = input()
professor = ratemyprofessor.get_professor_by_school_and_name(
    ratemyprofessor.get_school_by_name("University of Rochester"), professor_name)
if professor is not None:
    print("%s works in the %s Department of %s." % (professor.name, professor.department, professor.school.name))
    print("Rating: %s / 5.0" % professor.rating)
    print("Difficulty: %s / 5.0" % professor.difficulty)
    print("Total Ratings: %s" % professor.num_ratings)
    if professor.would_take_again is not None:
        print(("Would Take Again: %s" % round(professor.would_take_again, 1)) + '%')
    else:
        print("Would Take Again: N/A")

