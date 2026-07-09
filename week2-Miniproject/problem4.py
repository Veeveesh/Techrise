# CLASS_SN B1

def lookup_student(student_id, records):
    """— accepts a student ID (string) and a records dictionary. 
    Returns the student's data dict if found. 
    Raises a KeyError with a clear message if the ID does not exist. 
    Raises a TypeError if student_id is not a string.
    """
    try:
        if not isinstance(student_id,str):
            raise TypeError(f"Student ID must be a string")
        return records[student_id]
    except KeyError:
        raise KeyError(f"Student ID{student_id} does not exist")
    except Exception as e:
        raise Exception(f"Something unexpected happened with Student ID")


def run_lookup_loop(records):
    while True:
        student_id = input("Enter student ID (or 'quit'): ")

        if student_id.lower() == "quit":
            print("Session ended.")
            break

        try:
            student = lookup_student(student_id, records)
            print(f"Name:  {student['name']}")
            print(f"Score: {student['score']}")
            print(f"Grade: {student['grade']}")
        except KeyError as error:
            print(f"Error: {error}")
        except TypeError:
            print("Please enter a text ID, not a number.")


if __name__ == "__main__":
    

    RECORDS = {
        "TR3001": {"name": "Ada Okafor",   "score": 88, "grade": "A"},
        "TR3002": {"name": "Kemi Balogun", "score": 74, "grade": "B"},
        "TR3003": {"name": "Tunde Fashola","score": 55, "grade": "C"},
        "TR3004": {"name": "Ngozi Eze",    "score": 91, "grade": "A"},
    }


    print(lookup_student("TR3002", RECORDS))
    # {'name': 'Kemi Balogun', 'score': 74, 'grade': 'B'}

    try:
        lookup_student("TR9999", RECORDS)
    except KeyError as error:
        print(f"Error: {error}")
            # Error: "Student ID 'TR9999' not found in records"


    run_lookup_loop(RECORDS)
