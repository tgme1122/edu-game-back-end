# import random
# from faker import Faker
# from uuid import uuid4
#
# from app.core.database import SessionLocal
# # from app.models.category import Category
# # from app.models.course import Course
# # from app.models.lesson import Lesson
# # from app.models.assignment import Assignment
#
# fake = Faker()
#
#
# def run():
#     db = SessionLocal()
#
#     CATEGORY_COUNT = 5
#     COURSE_PER_CAT = 5
#     LESSON_PER_COURSE = 5
#     ASSIGN_PER_LESSON = 2
#
#     for _ in range(CATEGORY_COUNT):
#         category = Category(
#             id=uuid4(),
#             name=fake.unique.word(),
#             description=fake.text(max_nb_chars=120),
#             icon="icon.png",
#         )
#         db.add(category)
#         db.flush()
# 
#         for _ in range(COURSE_PER_CAT):
#             course = Course(
#                 id=uuid4(),
#                 category_id=category.id,
#                 title=fake.sentence(nb_words=4),
#                 description=fake.text(max_nb_chars=200),
#                 image="course.jpg",
#                 level=random.choice(["beginner", "intermediate", "advanced"]),
#                 price=random.randint(0, 200),
#                 duration=random.randint(1, 50),
#                 rating=random.randint(1, 5),
#             )
#             db.add(course)
#             db.flush()
#
#             for i in range(LESSON_PER_COURSE):
#                 lesson = Lesson(
#                     id=uuid4(),
#                     course_id=course.id,
#                     title=fake.sentence(nb_words=5),
#                     description=fake.text(max_nb_chars=200),
#                     order=i + 1,
#                     is_free=(i == 0),  # 1-lesson free bo'lsin
#                     video_url="https://youtu.be/W5LPcpIRLzs?si=HQuVh_NxM_R02bu4",
#                     duration_sec=random.randint(300, 2000),
#                 )
#                 db.add(lesson)
#                 db.flush()
#
#                 for j in range(ASSIGN_PER_LESSON):
#                     assignment = Assignment(
#                         id=uuid4(),
#                         lesson_id=lesson.id,
#                         title=fake.sentence(nb_words=5),
#                         description=fake.text(max_nb_chars=200),
#                         order=j + 1,
#                         max_score=100,
#                         is_required=True,
#                     )
#                     db.add(assignment)
#
#     db.commit()
#     db.close()
#     print("Small demo data generated ✅")
#
#
# if __name__ == "__main__":
#     run()
