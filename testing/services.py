from django.db import connection
import datetime


def update_results():
    print("UPDATING...")


class News:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.text = kwargs.get('text')
        self.date = kwargs.get('date_create')
        self.title = kwargs.get('title')
        self.slug = kwargs.get('slug')


class Review:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.text = kwargs.get('text')
        self.date = kwargs.get('date')
        self.participant_id = kwargs.get('participant_id')
        self.participant_name = self.get_participant_name()

    def get_participant_name(self):
        return self.participant_id


def get_news_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM contesttest.post ORDER BY date_created")
        news_list = {}
        news = []
        for row in cursor.fetchall():
            news_one = News(id=row[0], text=row[1], date_create=row[2], slug=row[3], title=row[4])
            news.append(news_one)

        news_list['news_list'] = news
        return news_list


def get_one_news(slug):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM contesttest.post WHERE slug='{slug}'")
        news = cursor.fetchone()
        news = News(id=news[0], text=news[1], date_create=news[2], slug=news[3], title=news[4])
        return news


def get_reviews_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM contesttest.review WHERE is_approved=true ORDER BY date")
        review_list = {}
        reviews = []
        for row in cursor.fetchall():
            review = Review(id=row[0], text=row[1], date_create=row[2], participant_id=row[4])
            reviews.append(review)

        review_list['reviews_list'] = reviews
        return review_list


def create_review(user_id, text):
    date = datetime.datetime.now()
    is_approved = False
    with connection.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO contesttest.review (text, date, is_approved, participant_id) VALUES ('{text}', '{date}', '{is_approved}', '{user_id}')")


def get_available_quiz(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT grade_id FROM contesttest.profile "
            f"JOIN contesttest.participant ON contesttest.profile.participant_id=contesttest.participant.id "
            f"WHERE contesttest.participant.id='{user_id}'"
        )
        try:
            grade_id = cursor.fetchone()[0]
        except TypeError:
            return None
    print(grade_id)
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.category.test_url "
            f"FROM contesttest.category "
            f"JOIN contesttest.session ON contesttest.category.session_id=contesttest.session.id "
            f"WHERE CURRENT_TIMESTAMP > contesttest.session.date_started "
            f"and CURRENT_TIMESTAMP < contesttest.session.date_finished and contesttest.category.grade_id='{grade_id}'"
        )
        try:
            data = cursor.fetchone()[0]
            return data
        except TypeError:
            return None


def create_profile(user_id, grade_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO contesttest.profile "
            f"(is_participation_paid, is_email_confirmed, participant_id, grade_id) "
            f"VALUES ('false', 'true', '{user_id}', '{grade_id}') "
        )


def set_user_grade(user_id, grade_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.profile.id "
            f"FROM contesttest.profile "
            f"JOIN contesttest.participant ON contesttest.participant.id=contesttest.profile.participant_id "
            f"WHERE contesttest.participant.id='{user_id}'"
        )
        profile_id = cursor.fetchone()
        if not profile_id:
            create_profile(user_id, grade_id)
        else:
            cursor.execute(
                f"UPDATE contesttest.profile SET grade_id='{grade_id}' WHERE contesttest.profile.participant_id='{user_id}';")


def get_user_by_email(email):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.participant.id "
            f"FROM contesttest.participant "
            f"WHERE contesttest.participant.email='{email}'"
        )
        user_id = cursor.fetchone()
        if user_id:
            return user_id[0]
        else:
            return None


def save_result(category_id, answers_url):
    from .result_handler import get_by_url
    results = get_by_url(answers_url)
    with connection.cursor() as cursor:
        for result in results:
            participant_id = get_user_by_email(result)
            cursor.execute(
                f"INSERT INTO contesttest.result (score, category_id, participant_id) VALUES ('{results[result]}', '{category_id}', '{participant_id}')")


def get_old_categories_results():
    """
    Get all old (previous) categories without any result saved.
    """
    is_over = False
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.category.answers_url, contesttest.category.id "
            f"FROM contesttest.session "
            f"JOIN contesttest.category ON contesttest.session.id=contesttest.category.session_id "
            f"WHERE contesttest.session.date_finished < CURRENT_TIMESTAMP AND contesttest.category.id NOT IN (SELECT category_id FROM contesttest.result); "
        )
        data = cursor.fetchall()

        for i in data:
            if i[0] and i[1]:
                save_result(i[1], i[0])

    return is_over


# def get_previous_category():
#     # get the current day of the year
#     doy = datetime.datetime.today().timetuple().tm_yday
#
#     # "day of year" ranges for the northern hemisphere
#     spring = range(80, 172)
#     summer = range(172, 264)
#     fall = range(264, 355)
#     # winter = everything else
#
#     if doy in spring:
#         season = 'Весняна'
#     elif doy in summer:
#         season = 'Літня'
#     elif doy in fall:
#         season = 'Осіння'
#     else:
#         season = 'Зимова'
#
#     prev_seasons = {
#         'Весняна': 'Зимова',
#         'Зимова': 'Осіння',
#         'Осіння': 'Літня',
#         'Літня': 'Весняна',
#     }
#     print(prev_seasons[season])
#     with connection.cursor() as cursor:
#         cursor.execute(
#             f"SELECT contesttest.session.id, contesttest.category.id, contesttest.session.name, contesttest.session.date_finished "
#             f"FROM contesttest.session "
#             f"JOIN contesttest.category ON contesttest.session.id=contesttest.category.session_id "
#             f"WHERE contesttest.session.date_finished < CURRENT_TIMESTAMP AND date_part('year', contesttest.session.date_finished) = date_part('year', CURRENT_DATE) "
#             f"AND contesttest.session.name='{prev_seasons[season]}'"
#         )
#
#         print(cursor.fetchall())


def get_last_categories():

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT contesttest.category.id, contesttest.category.grade_id "
            "FROM contesttest.category "
            "JOIN contesttest.session ON contesttest.category.session_id=contesttest.session.id "
            "ORDER BY contesttest.session.date_finished"
        )
        data = cursor.fetchall()
    last_category_for_grade = {

    }
    for i in data:
        last_category_for_grade[i[1]] = i[0]

    print(last_category_for_grade)


