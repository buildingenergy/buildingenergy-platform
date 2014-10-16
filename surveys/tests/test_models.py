from django.test import TestCase

from seed.models import CanonicalBuilding

from surveys.models import (
    Survey,
    SurveyQuestion,
    SurveyAnswer,
    SurveyBuilding,
)


class TestSurveyModels(TestCase):

    def setUp(self):
        super(TestSurveyModels, self).setUp()
        self.can = CanonicalBuilding.objects.create()

    def test_survey_structure(self):
        """Make sure that questions, answers and surveys are linked up."""
        s = Survey.objects.create()
        SurveyBuilding.objects.create(survey=s, canonical_building=self.can)

        q = SurveyQuestion.objects.create(
            survey=s, question='Database?'
        )

        a = SurveyAnswer.objects.create(
            canonical_building=self.can,
            question=q,
        )

        self.assertEqual(self.can.survey_answers.first(), a)
