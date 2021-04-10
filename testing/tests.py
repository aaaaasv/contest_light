from django.test import TestCase
from django.db import connection
from django.contrib.auth.hashers import make_password

from . import services


class TestQuiz(TestCase):
    def setUp(self):
        self.user_email = '0192391293@gmail.com'
        signup_data = {
            'email': self.user_email,
            'password1': 'hellothere_1',
            'password2': 'hellothere_1',
            'first_name': 'test_name',
            'middle_name': 'test_second_name',
            'last_name': 'test_last_name',
            'phone_number': '38102300123',
            'address': 'aksdlkasd',
            'city': '1',
            'region': '1',
            'study': 'study school for test',
        }
        self.user_id = 1412
        self.grade_id = 1283
        self.grade = '123 клас'
        with connection.cursor() as cursor:  # create participant
            cursor.execute(
                f"INSERT INTO contesttest.participant (id, email, password, last_name, first_name, middle_name, address, "
                f"city_id, region_id, phone_number, study, date_joined) VALUES ('{self.user_id}','{signup_data['email']}', '{make_password(signup_data['password1'])}', '{signup_data['last_name']}', "
                f"'{signup_data['first_name']}', "
                f"'{signup_data['middle_name']}', '{signup_data['address']}', '{signup_data['city']}', '{signup_data['region']}', '{signup_data['phone_number']}', '{signup_data['study']}', CURRENT_TIMESTAMP)")

        with connection.cursor() as cursor:  # create grade
            cursor.execute(
                f"INSERT INTO contesttest.grade "
                f"(id, grade) "
                f"VALUES ('{self.grade_id}', '{self.grade}') "
            )
        with connection.cursor() as cursor:  # create user profile
            cursor.execute(
                f"INSERT INTO contesttest.profile "
                f"(is_participation_paid, is_email_confirmed, participant_id, grade_id) "
                f"VALUES ('false', 'true', '{self.user_id}', '{self.grade_id}') "
            )

        self.not_finished_session_id = 142
        with connection.cursor() as cursor:  # available session
            cursor.execute(
                f"INSERT INTO contesttest.session "
                f"(id, name, date_started, date_finished) "
                f"VALUES ('{self.not_finished_session_id}','Test sessi1on', CURRENT_TIMESTAMP - interval '2 day', CURRENT_TIMESTAMP + interval '2 day')"
            )
        self.finished_session_id = 1283

        with connection.cursor() as cursor:  # not available (old) session
            cursor.execute(
                f"INSERT INTO contesttest.session "
                f"(id, name, date_started, date_finished) "
                f"VALUES ('{self.finished_session_id}','Test sessi1on', CURRENT_TIMESTAMP - interval '10 days', CURRENT_TIMESTAMP - interval '5 days')"
            )
        self.available_category_id = 8412
        with connection.cursor() as cursor:  # available category
            cursor.execute(
                f"INSERT INTO contesttest.category "
                f"(id, grade_id, session_id, test_url, answers_url) "
                f"VALUES ('{self.available_category_id}','{self.grade_id}', '{self.not_finished_session_id}', 'test_available_url_test', 'answer_url_answer' )"
            )

        with connection.cursor() as cursor:  # finished category
            cursor.execute(
                f"INSERT INTO contesttest.category "
                f"(grade_id, session_id, test_url, answers_url) "
                f"VALUES ('{self.grade_id}', '{self.finished_session_id}', 'test_not_available_url_test', 'answer_url_answer' )"
            )

    def test_get_available_quiz_success(self):
        categories = services.get_available_quiz(self.user_id)
        self.assertEqual(categories, 'test_available_url_test')

    def test_get_grade_name_by_id(self):
        self.assertEqual(services.get_grade_name_by_id(self.grade_id), self.grade)

    def test_get_user_grade(self):
        self.assertEqual(services.get_user_grade(self.user_id), self.grade)

    def test_get_user_by_email(self):
        self.assertEqual((services.get_user_by_email(self.user_email)), self.user_id)

    def test_check_participant_session_is_unique(self):
        self.assertTrue(services.check_participant_session_unique(self.user_id, self.available_category_id))

    def test_check_participant_session_not_unique(self):
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO contesttest.result "
                f"(category_id, participant_id, score) "
                f"VALUES ('{self.available_category_id}', '{self.user_id}', 123)"
            )
        self.assertFalse(services.check_participant_session_unique(self.user_id, self.available_category_id))

