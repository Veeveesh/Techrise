# CLASS_SN B1
#
def validate_scores(*scores):
    valid_scores = []
    invalid_entries = []

    for score in scores:
        try:
            number = float(score)
        except (ValueError, TypeError):# if it can not be turned into a number.
            print(f"Warning: {score} is not a valid score.")
            invalid_entries.append(score)
            continue

        if 0 <= number <= 100:
            valid_scores.append(number)
        else:
            print(f"Warning: {score} is out of range (0-100).")
            invalid_entries.append(score)

    return valid_scores, invalid_entries



def get_grade(average):
    """Summary
    average(numeric): the average score of the student
    get_grade returns the correct letter grade for the average of a student given
    """
    try:
        if 0 < average > 100: 
               raise ValueError
        if average > 70:
                grades = "A(Distinction)"
                return grades
        elif average >60:
                grades= "B(Merit)"
                return grades
        elif average >50:
                grades = "C(Pass)"
                return grades
        elif average >40:
                grades = "D(Below average)"
                return grades
        elif average >0:
                grades = "F(Fail)"
                return grades
    except ValueError:
           return "Average cannot be negative or greater than 100"
    
if __name__ == "__main__":
        
    raw = (85, "pass", 72, 101, 63, None, 55)
    valid, invalid = validate_scores(*raw)
    # Warning: 'pass' is not a valid score.
    # Warning: 101 is out of range (0–100).
    # Warning: None is not a valid score.


    avg   = sum(valid) / len(valid)   # 68.75
    grade = get_grade(avg)            # B
    print(f"Average: {avg:.2f} | Grade: {grade}")
    # Average: 68.75 | Grade: B

