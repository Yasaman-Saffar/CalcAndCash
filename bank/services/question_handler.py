from ..models import Question
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

class QuestionHandler:
    """
    Provides question selection, answer checking,
    searching and filtering utilities.
    """
    
    def question_answer_checker(self, group_question):
        return group_question.question.answer == group_question.group_answer
    
    def get_random_question(self, level):
        """
        Return one available question for the given difficulty level.
        skip_locked=True prevents two groups from buying the same question
        at the same time.
        """
        
        questions = Question.with_owner_status().filter(has_owner=False, difficulty=level)
        q = (
            questions.select_for_update(skip_locked=True)
            .order_by('?')
            .first()
        )
        return q
    
    @transaction.atomic
    def update_group_question(self, group_question):
        """
        Mark a group question as solved and save its reward time.
        """
        group_question.is_solved = True
        group_question.receive_reward_time = timezone.now()
        group_question.save()
        
    def search_question(self, q, queryset):
        if q.isdigit():
            questions = queryset.filter(Q(number=int(q)) | Q(question_prompt__icontains=q))
        else:
            questions = queryset.filter(Q(question_prompt__icontains=q))
        return questions
    
    def filter_difficulty(self, difficulties, queryset):
        return queryset.filter(difficulty__id__in=difficulties) if difficulties else queryset
    
    def filter_bank_status(self, status, queryset):
        if status == 'Yes':
            return queryset.filter(has_owner=False)
        elif status == 'No':
            return queryset.filter(has_owner=True)
        return queryset