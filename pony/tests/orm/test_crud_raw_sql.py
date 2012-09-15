import unittest
from pony.orm import *
from testutils import raises_exception

db = Database('sqlite', ':memory:')

class Student(db.Entity):
    name = Required(unicode)
    age = Optional(int)
    friends = Set("Student", reverse='friends')
    group = Required("Group")
    bio = Optional("Bio")

class Group(db.Entity):
    dept = Required(int)
    grad_year = Required(int)
    students = Set(Student)
    PrimaryKey(dept, grad_year)

class Bio(db.Entity):
    picture = Optional(buffer)
    desc = Required(unicode)
    Student = Required(Student)

db.generate_mapping(create_tables=True)    

class TestRawSql(unittest.TestCase):
    def setUp(self):
        rollback()
        db.execute('delete from Student')
        db.execute('delete from "Group"')
        db.insert('Group', dept=44, grad_year=1999)
        db.insert('Student', id=1, name='A', age=30, group_dept=44, group_grad_year=1999)
        db.insert('Student', id=2, name='B', age=25, group_dept=44, group_grad_year=1999)
        db.insert('Student', id=3, name='C', age=20, group_dept=44, group_grad_year=1999)
        commit()
        rollback()

    def test1(self):
        students = Student.fetch("select id, name, age, group_dept, group_grad_year from Student order by age")
        self.assertEquals(students, [Student[3], Student[2], Student[1]])

    def test2(self):
        students = Student.fetch("select id, age, group_dept from Student order by age")
        self.assertEquals(students, [Student[3], Student[2], Student[1]])

    @raises_exception(NameError, "Column x does not belong to entity Student")
    def test3(self):
        students = Student.fetch("select id, age, age*2 as x from Student order by age")
        self.assertEquals(students, [Student[3], Student[2], Student[1]])

    @raises_exception(TypeError, 'Positional argument must be lambda function or SQL select command. Got: 123')
    def test4(self):
        students = Student.fetch(123)

if __name__ == '__main__':
    unittest.main()        