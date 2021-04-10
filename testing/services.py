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
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT participant.last_name, participant.first_name, participant.middle_name "
                           f"FROM contesttest.review "
                           f"JOIN contesttest.participant ON contesttest.review.participant_id=contesttest.participant.id "
                           f"WHERE contesttest.participant.id='{self.participant_id}'")
            name = cursor.fetchall()
        if name:
            name = name[0]
        else:
            return ''
        return ' '.join(name)


def get_news_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM contesttest.post ORDER BY date_created DESC")
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
        cursor.execute("SELECT * FROM contesttest.review WHERE is_approved=true ORDER BY date DESC")
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


def check_participant_session_unique(user_id, category_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT session_id FROM contesttest.category WHERE contesttest.category.id='{category_id}'"
        )
        data = cursor.fetchone()
        try:
            session_id = data[0]
        except (TypeError, IndexError):
            return None

        cursor.execute(
            f"SELECT contesttest.result.id FROM contesttest.result "
            f"JOIN contesttest.category ON contesttest.category.id=contesttest.result.category_id "
            f"WHERE contesttest.category.session_id='{session_id}' AND contesttest.result.participant_id='{user_id}'"
        )

        data = cursor.fetchall()
        try:
            if len(data) > 0:
                return False
            else:
                return True
        except TypeError:
            return True


def save_result(category_id, answers_url):
    from .result_handler import get_by_url
    results = get_by_url(answers_url)
    with connection.cursor() as cursor:
        for result in results:
            participant_id = get_user_by_email(result)
            if participant_id is not None and check_participant_session_unique(participant_id,
                                                                               category_id):  # Some user used different emails for registration and test - participant = None
                cursor.execute(
                    f"INSERT INTO contesttest.result (score, category_id, participant_id) VALUES ('{results[result]}', '{category_id}', '{participant_id}')")


def save_old_categories_results():
    """
    Get all old (previous) categories without any result saved and save it.
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


class Result:
    def __init__(self, **kwargs):
        self.first_name = kwargs.get('first_name')
        self.middle_name = kwargs.get('middle_name')
        self.last_name = kwargs.get('last_name')
        self.score = kwargs.get('score')
        self.grade = kwargs.get('grade')


def get_grade_name_by_id(id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.grade.grade FROM contesttest.grade WHERE id='{id}'"
        )
        data = cursor.fetchone()
        if data:
            return data[0]
        else:
            return None


def get_result_for_category(category_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT contesttest.participant.first_name, contesttest.participant.middle_name, contesttest.participant.last_name, contesttest.result.score, contesttest.result.category_id, contesttest.result.participant_id FROM contesttest.result "
            f"JOIN contesttest.participant ON contesttest.result.participant_id=contesttest.participant.id "
            f"WHERE contesttest.result.category_id='{category_id}'"
        )
        return cursor.fetchall()


def get_result_for_last_categories():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT contesttest.category.id, contesttest.category.grade_id "
            "FROM contesttest.category "
            "JOIN contesttest.session ON contesttest.category.session_id=contesttest.session.id "
            "ORDER BY contesttest.session.date_finished DESC"
        )
        data = cursor.fetchall()
    last_category_for_grade = {

    }
    for i in data:
        # grade_id : category_id
        last_category_for_grade[i[1]] = i[0]
    result_list = {
        # grade : result list
    }

    for grade in last_category_for_grade:
        result_for_grade = []
        result_info = get_result_for_category(last_category_for_grade[grade])
        for i in result_info:
            result_for_grade.append(Result(first_name=i[0], middle_name=i[1], last_name=i[2], score=i[3],
                                           grade=get_grade_name_by_id(grade)))
        result_list[grade] = result_for_grade
    return result_list


def get_user_grade(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT grade.grade FROM contesttest.grade "
            f"JOIN contesttest.profile ON contesttest.profile.grade_id=contesttest.grade.id "
            f"WHERE contesttest.profile.participant_id='{user_id}'"
        )

        data = cursor.fetchone()

        if data:
            return data[0]
        else:
            return None
