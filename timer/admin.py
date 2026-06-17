from django.contrib import admin
from django import forms
from .models import TimeControl

class TimeControlForm(forms.ModelForm):
    class Meta:
        model = TimeControl
        fields = '__all__'
        widgets = {
            'duration': forms.TextInput(attrs={
                'placeholder': 'For example 00:40:20'
            })
        }
        

@admin.register(TimeControl)
class TimeControlAdmin(admin.ModelAdmin):
    form = TimeControlForm
    model = TimeControl
    list_display = ('status', 'duration')
    
    def has_add_permission(self, request):
        if TimeControl.objects.exists():
            return False
        return True