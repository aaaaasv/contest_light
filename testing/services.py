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
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.category.url "
            f"FROM contesttest.category "
            f"JOIN contesttest.session ON contesttest.category.session_id=contesttest.session.id "
            f"WHERE CURRENT_TIMESTAMP > contesttest.session.date_started "
            f"and CURRENT_TIMESTAMP < contesttest.session.date_finished and contesttest.category.grade_id='{grade_id}'"
        )
        try:
            return cursor.fetchone()[0]
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
            print('updating...')
