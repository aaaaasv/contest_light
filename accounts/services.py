from django.db import connection
import datetime

from django.contrib.auth.hashers import make_password, check_password


def get_or_create_city(city_name):
    with connection.cursor() as cursor:
        city_id = cursor.execute(f"SELECT id FROM contesttest.city WHERE name='{city_name}'")
        if city_id is None:
            cursor.execute(f"INSERT INTO contesttest.city (name) VALUES ('{city_name}')")
            cursor.execute(f"SELECT id FROM contesttest.city WHERE name='{city_name}'")
            city_id = cursor.fetchone()[0]
    return city_id


def get_or_create_region(region_name):
    with connection.cursor() as cursor:
        region_id = cursor.execute(f"SELECT id FROM contesttest.region WHERE name='{region_name}'")
        if region_id is None:
            cursor.execute(f"INSERT INTO contesttest.region (name) VALUES ('{region_name}')")
            cursor.execute(f"SELECT id FROM contesttest.region WHERE name='{region_name}'")
            region_id = cursor.fetchone()[0]
    return region_id


def check_email_unique(email):
    return True


def register_user(register_data):
    email = register_data.get('email')
    if not check_email_unique(email):
        return 'user with this email is already has an account'
    password1 = register_data.get('password1')
    password2 = register_data.get('password2')
    if password1 != password2:
        return 'passwords are different'

    last_name = register_data.get('last_name')
    first_name = register_data.get('first_name')
    middle_name = register_data.get('middle_name')

    address = register_data.get('address')
    city = register_data.get('city')
    city = get_or_create_city(city)
    region = register_data.get('region')
    region = get_or_create_region(region)
    phone_number = register_data.get('phone_number')
    study = register_data.get('study')

    date_joined = datetime.datetime.now()

    password1 = make_password(password1)

    with connection.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO contesttest.participant (email, password, last_name, first_name, middle_name, address, city_id, region_id, phone_number, study, date_joined) VALUES ('{email}', '{password1}', '{last_name}', '{first_name}', '{middle_name}', '{address}', '{city}', '{region}', '{phone_number}', '{study}', '{date_joined}')")


def login_user(login_data):
    email = login_data.get('email')
    password = login_data.get('password')

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT password FROM contesttest.participant WHERE email='{email}'")
        db_password = cursor.fetchone()[0]
        if check_password(password, db_password):
            print("ITS A MATCH!", password, db_password)
            return True
        else:
            print("IST NOT A MATCH", make_password(password), db_password)