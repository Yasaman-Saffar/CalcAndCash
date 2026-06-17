from .exceptions import NotAnswered, WrongAnswered

class QuestionHandling():
    
    @staticmethod
    def check_answer(gquestion, tp):
        if not gquestion.group_answer:
            raise NotAnswered("You must enter an answer first.")
        
        solved = tp.process_answer(gquestion)
        if not solved:
            raise WrongAnswered("Your answer was wrong. Please try again.")