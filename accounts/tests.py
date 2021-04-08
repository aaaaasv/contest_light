from django.test import TestCase
from django.db import connection, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from accounts import services


class TestAuth(TestCase):

    def setUp(self):
        self.signup_data = {
            'email': '0192391293@gmail.com',
            'password1': 'hellothere_1',
            'password2': 'hellothere_1',
            'first_name': 'test_name',
            'middle_name': 'test_second_name',
            'last_name': 'test_last_name',
            'phone_number': '38102300123',
            'city': 'Київ',
            'region': 'Київська',
            'study': 'study school for test',
        }

        self.email = "test_email@example.comf"
        self.password = "zzsdabcdef12_"
        self.user_id = 1234
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO contesttest.participant (id, email, password, last_name, first_name, middle_name, address, "
                f"city_id, region_id, phone_number, study, date_joined) VALUES ('{self.user_id}','{self.email}', '{make_password(self.password)}', 'TestLan', "
                f"'TestF', "
                f"'TestM', 'asldl', '1', '1', '1231283', 'aksdlasdk', CURRENT_TIMESTAMP)")

    def test_check_email_unique_not(self):
        email = '00000001xyz@gmail.com'
        is_unique = services.check_email_unique(email)
        self.assertFalse(is_unique)

    def test_check_email_unique_yes(self):
        email = '00000001xyzakdskdaksdkadk@gmail.com'
        is_unique = services.check_email_unique(email)
        self.assertTrue(is_unique)

    def test_user_signup_success(self):
        signup_data = {
            'email': '0192391293@gmail.com',
            'password1': 'hellothere_1',
            'password2': 'hellothere_1',
            'first_name': 'test_name',
            'middle_name': 'test_second_name',
            'last_name': 'test_last_name',
            'phone_number': '38102300123',
            'city': 'Київ',
            'region': 'Київська',
            'study': 'study school for test',
        }

        services.register_user(signup_data)

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM contesttest.participant """
                f"WHERE email='{signup_data['email']}'"
            )
            data = cursor.fetchall()
        self.assertEqual(len(data), 1)

        # print(connection.settings_dict['NAME'])

    def test_user_signup_fail_email(self):
        signup_data = self.signup_data
        signup_data['email'] = '123@g'
        with self.assertRaises(ValidationError):
            services.register_user(signup_data)

    def test_user_signup_fail_passwords_different(self):
        signup_data = self.signup_data
        signup_data['password1'] = 'abaklsdkasd'
        signup_data['password2'] = 'aklsdkaslkdasld'
        with self.assertRaises(ValidationError, msg="Passwords are different"):
            services.register_user(signup_data)

    def test_user_signup_fail_password_simple(self):
        signup_data = self.signup_data
        signup_data['password1'] = '12345'
        signup_data['password2'] = '12345'
        with self.assertRaises(ValidationError):
            services.register_user(signup_data)

    def test_user_login_success(self):
        is_logged, user_id = services.login_user({'email': self.email, 'password': self.password})

        self.assertTrue(is_logged)
        self.assertEqual(self.user_id, user_id)

    def test_user_login_fail(self):
        is_logged, user_id = services.login_user({'email': self.email, 'password': 'incorrect_password'})

        self.assertFalse(is_logged)
        self.assertIsNone(user_id)
