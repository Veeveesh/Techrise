 # CLASS SN : B1


# write a function called "Grade_summary and student_card"

def grade_summary(*args,subject="general"):
    """summary:
    parameters:
        args(Int/float):Takes any number of scores
        subject(str): Takes the name of the subject
        
    returns:
         a string of the summarised values including the subject score,
        highest, lowest and average
        returns 'No score provided' if none is given 
        """
    if not args:
        return f" No scores provided"
    highest = args[0]
    lowest = args[0]
    total = 0
    for score in args : # this loop iterates through the scores to find the highest, lowest and total
        if score > highest: # if the score is greater than the current highest , it becomes the new highest
            highest= score
        if score < lowest: #if a score is greater than the current lowest, it becomes the new lowest
            lowest= score # this uses
        total += score # calculates the running total 
    average = total/ len(args)
    return print(f"Subject : {subject} | Scores : {len(args)} | Highest:{highest} | Lowest: {lowest}| Average: {round(average, 2)}")

grade_summary(67,76,56,43,23,23,1,9,99, subject="Mathematics")
#print(grade_summary())


def student_card(name,cohort, **kwargs):
    """
    Summary:
    Positional parameters:
        name(str): "input the name of the student"\n
        cohort(str): "input the cohort of the student"
        kwargs(str)= "input the value of any additional field here" 
        """ 
    student_details = {
        "Name": name,
        "Cohort": cohort
        
    }
    for field,values in kwargs.items():
        student_details[field.lower()]= values # this runs through the additional fields, and creates a key "field" in the student_details dictionary and assigns the values to it
    for student,details in student_details.items():
        print(f"{student.ljust(12)}: {details}")

student_card("Ihesiaba","cohort 3",track="Python",hall="Big hall", residence="Offcampus")