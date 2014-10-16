from datetime import datetime
from django.db import models


TEXT = 1
RADIO = 2
ENUM = 3

QUESTION_TYPES = (
    (TEXT, 'Text'),
    (RADIO, 'Radio'),
    (ENUM, 'Enumerated'),
)


class Survey(models.Model):
    """A group of questions, along with meta data about its gathering."""
    canonical_buildings = models.ManyToManyField(
        'seed.CanonicalBuilding',
        through="SurveyBuilding",
        related_name='surveys',
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s' % self.pk


class SurveyBuilding(models.Model):
    """through table to capture the building's survey non-question data"""
    canonical_building = models.ForeignKey(
        'seed.CanonicalBuilding', related_name='survey_buildings'
    )
    survey = models.ForeignKey(
        'Survey', related_name='survey_buildings'
    )
    date_collected = models.DateField(
        default=datetime.now, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)
    completion_time = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['survey', 'canonical_building']
        unique_together = ('canonical_building', 'survey')

    def __unicode__(self):
        return u"{0} - {1}".format(self.canonical_building, self.survey)


class SurveyQuestion(models.Model):
    """Definition of a survey question, including answer type, and options."""
    survey = models.ForeignKey(
        Survey, related_name='questions', null=True, blank=True
    )
    question = models.TextField()
    question_type = models.IntegerField(
        max_length=3, default=TEXT, choices=QUESTION_TYPES
    )

    def __unicode__(self):
        return u'%s - %s - %s' % (
            self.pk, self.question, self.get_question_type_display()
        )


class QuestionOption(models.Model):
    """What kinds of enumerated answers are possible."""
    question = models.ForeignKey(
        SurveyQuestion, related_name='question_options'
    )
    option = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s - %s - %s' % (
            self.pk, self.question, self.option
        )


class SurveyAnswer(models.Model):
    """Answer to a question, whether it's boolean or textual."""
    canonical_building = models.ForeignKey(
        'seed.CanonicalBuilding', related_name='survey_answers'
    )
    question = models.ForeignKey(SurveyQuestion, related_name='+')
    # Some questions are open ended, some are boolean in nature.
    # Just capture one or the other in this row.
    answer = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s - %s - %s' % (
            self.pk, self.question, self.answer
        )
