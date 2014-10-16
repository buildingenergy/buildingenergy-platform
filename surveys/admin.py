from django.contrib import admin
from surveys.models import Survey, QuestionOption, SurveyAnswer, SurveyQuestion

admin.site.register(Survey)
admin.site.register(QuestionOption)
admin.site.register(SurveyAnswer)
admin.site.register(SurveyQuestion)
