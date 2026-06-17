from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class ContestStatus(models.TextChoices):
    NOT_STARTED = 'not-started', 'Not-Started'
    RUNNING = 'running', 'Running'
    PAUSED = 'paused', 'Paused'
    FINISHED = 'finished', 'Finished'
    
class TimeControl(models.Model):
    """
    Stores the single contest timer state, including pause/resume tracking.
    """
    
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    duration = models.DurationField()
    status = models.CharField(max_length=15, choices=ContestStatus, default='not-started')
    
    start_time = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    total_paused = models.DurationField(default=timedelta)
    
    current_inflation = models.OneToOneField("bank.Event", on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f'{self.duration} duration => {self.status}'
    
    def save(self, *args, **kwargs):
        if not self.pk and TimeControl.objects.exists():
            raise ValidationError("You can only have one instance of TimeControl.")
        self.full_clean()
        super().save(*args, **kwargs)
        
    def start(self):
        self.start_time = timezone.now()
        self.status = 'running'
        self.save(update_fields=['start_time', 'status'])
    
    def end_time(self):
        if not self.start_time:
            return None
        return self.start_time + self.duration + self.total_paused
        
    def pause(self):
        if self.status == 'running':
            self.paused_at = timezone.now()
            self.status = 'paused'
            self.save(update_fields=['paused_at', 'status'])
    
    def resume(self):
        if self.paused_at:
            paused_seconds = timezone.now() - self.paused_at
            self.total_paused += paused_seconds
            self.paused_at = None
            self.status = 'running'
            self.save(update_fields=['total_paused', 'paused_at', 'status'])
    
    def  reset_timer(self):
        self.status = "not-started"
        self.start_time = None
        self.paused_at = None
        self.total_paused = timedelta()
        self.current_inflation = None
        self.save()
            
    def passed_time(self):
        if self.status == "not-started" or not self.start_time:
            return timezone.timedelta()
        
        if self.status == 'running':
            elapsed = timezone.now() - self.start_time
        elif self.status == 'paused':
            elapsed = self.paused_at - self.start_time
        elif self.status == 'not-started':
            elapsed = timezone.timedelta()
        else:
            elapsed = self.duration
            
        effective = elapsed - self.total_paused
        
        if effective < timezone.timedelta():
            return timezone.timedelta()
        return effective
    
    def remaining(self):
        r = int((self.duration - self.passed_time()).total_seconds())
        if r < 0:
            return 0
        return r
        
    def finish(self):
        self.status = 'finished'
        self.save(update_fields=['status'])
        
    def set_current_inflation(self, inflation):
        self.current_inflation = inflation
        self.save(update_fields=['current_inflation'])