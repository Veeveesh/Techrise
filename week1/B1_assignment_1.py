# CLASS SN: B1

# Task 1
# The students record is a list of dicts...
students = [] # this creates an empty list 

while True :
    name = input("Enter student name(or'done' to exit): ").strip()
    if name.upper() == 'DONE':
        break
    if name == "":
        print ("Enter a valid name, this cannot be empty")
        continue
    scores = [] # this is a list
    for i in range(1,4): # this line allows us to ask the user to enter the score 3 times
        while True: # while the for loop is true this will run
            scores_ind = input(f"Enter individual's score {i}: ") # asks the individual to input the score for each try
            if scores_ind.isdigit(): # if the input is a digit then the code will do nothing
                pass
            else: 
                print(f"Invalid input, try a number") # if it is not a digit this will be printed
                continue # this allows the loop to continue

            scores_ind = int(scores_ind) # this converts the inputed values to integers from strings
            if scores_ind < 0 or scores_ind > 100: # this checks if the score is between 0 and 100 
                print("Invalid score. Enter 0-100") # if the condition above fails then this is printed 
                continue # this will allow us to continue
            scores.append(scores_ind) # this adds the inputed values to the scores
            break # this end


# to create the dictionary that will store the name and scores as students
    student={
    "name": name,
    "scores": scores,
    "average": 0,
    "grade" : "",
    "status":" "
    }

# now i will fill in the student dictionary from the inputed data into the students list
    students.append(student)
    print("Entry has been recorded")


 #Task 2

for student in students: # this allows us to looop through all the student entries in the list of dictionaries 
    average = round(sum(student["scores"])/ len(student["scores"]),1) #to calculate the average scores
    student["average"] = average #this updates the dictionary with the calculated average

    if average >= 80:
            student["grade"] = "A"
    elif average >= 65:
            student["grade"] = "B"
    elif average >= 50:
            student["grade"] = "C"
    elif average >= 40:
            student["grade"] = "D"
    elif average < 40:
            student["grade"] = "F"    

        
    if average >= 50:
            student["status"] = "Pass"
    else:
            student["status"] = "Fail"
#print(students) # this showed me whether i was successful or not

    # Task 3 
top_student = None 
top_average = 0    # use tracking variables to find the highest average rather than use max()

for student in students:
        if student['average'] > top_average:
            top_average = student["average"]
            top_student = student



    # Task 4
failing_score_students = [] #-- any individual score< 40
perfect_score_students =[]  #-- any individual score == 100 
for student in students:
      for score in student["scores"]: # this is a nested loop allowing us to loop through the scores each time we loop through students
            if score<40: # if the score is less than 40
                  if student["name"] not in failing_score_students: # and the student is not already in the list of failing score students
                        failing_score_students.append(student["name"]) # this adds their name to the list
            if score == 100:
                  if student["name"] not in perfect_score_students:
                        perfect_score_students.append(student["name"])

# Task 5 --Class average
classtotal=0 # this is an acummulator that stores the running total
for student in students:
    classtotal += student["average"] # this add each students average to the running total

class_average= float(round(classtotal/ len(students),1)) # the class average is calculated by dividing the running total by the lenght of the students list , rounding it up to one decimal point and converting it to a float as indicated

#  Task 6
# to print the output like the format given using loops and f strings

print( "-" * 50)
print(f"\n STUDENT PERFORMANCE REPORT ")
print( "-" * 50 )

for index, student in enumerate(students,1):
    print(f"\n{index}.{student["name"]}")
    print(f"   Scores: {student["scores"]}")
    print(f"   Average: {student["average"]}")
    print(f"   Grade: {student["grade"]}")
    print(f"   Status: {student["status"]}")
print("\n" + "-" * 50)
print(f"Class Average: {class_average}")

if top_student:
    print(f"Top Performer: {top_student['name']} ({top_student['average']})")

if len(failing_score_students)>0:
    print(f"Students with failing scores: {failing_score_students}")
else:
    print("Students with failing scores: None")

if len(perfect_score_students)>0:
    print(f"Students with perfect scores: {perfect_score_students}")
else:
    print("Students with perfect scores: None")
print("-"*50)
