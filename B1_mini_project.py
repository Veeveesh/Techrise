# score_analyzer.py
"""
Student Score Analyzer — Week 1 Project
Asks for three test scores, calculates the average,
and determines pass or fail.
"""
while True:
    def get_score(prompt):
        """
        Ask the user for a valid score between 0 and 100.
        Keeps asking until a valid number is entered.
        """
        while True:
            try:
                score = float(input(prompt)) # try to convert to float
                if 0 <= score <= 100:
                    return score # valid — return it
                else:
                    print("Score must be between 0 and 100. Try again.")
            except ValueError:
                print("Please enter a valid number.")
    def main():
        """This is the function to call the student code analyzer"""
        print("=== Student Score Analyzer ===")
        # TODO: call get_score() three times to collect the scores
        score1 = get_score("Enter score 1 (0-100): ")
        # add score2 and score3 here
        score2 = get_score("Enter score 2(0-100): ")
        score3 = get_score("Enter score 3(0-100): ")
        # TODO: calculate the average
        scores=[score1,score2,score3]
        averages = round(sum(scores)/ 3,2)
        # TO : determine pass or fail (average >= 50)
        if averages>= 50:
            print("Student passed")
        else:
            print("Student failed")
        # TODO: print the formatted summary
        # BONUS: wrap everything in a while loop for multiple students
repeat = input("Do you want to insert for another student?(yes/no)")
if repeat.lower() =="no":
    break
    if __name__ == "__main__":
        main()
   