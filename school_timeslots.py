#! /usr/bin/python3 -u

import json
import sys
import random

# hardcoded
teachers = []
teachers.append({'name' : "Hélio Loureiro", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Luciana Amora Doce", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 3})
teachers.append({'name' : "Richard Stallman", 'dow' : [2, 3], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 2})
teachers.append({'name' : "Linus Torvalds", 'dow' : [3, 5], 'class' : [8, 9], 'period' : [3, 4, 5, 6], 'fixed' : False, 'nr' : 2})
teachers.append({'name' : "John Maddog Hall", 'dow' : [2, 3, 5], 'class' : [8, 9], 'period' : [3, 4, 5, 6], 'fixed' : False, 'nr' : 2})
teachers.append({'name' : "Diego Neves", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Mirian Retka", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Mariele", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Aprigio Simões", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Nilo Menezes", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
teachers.append({'name' : "Ingo Hoffman", 'dow' : [2, 3, 4, 5, 6], 'class' : [6, 7, 8, 9], 'period' : [1, 2, 3, 4, 5, 6], 'fixed' : False, 'nr' : 5})
# not random
teachers. append({'name' : "Tempo livre 2", 'dow' : [2], 'class' : [6, 7, 8, 9], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Tempo livre 3", 'dow' : [3], 'class' : [8, 9], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Tempo livre 4", 'dow' : [4], 'class' : [6, 7, 8], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Tempo livre 5", 'dow' : [5], 'class' : [6, 7], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Tempo livre 6", 'dow' : [6], 'class' : [6, 7, 8, 9], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Educação física 3/5", 'dow' : [3], 'class' : [8, 9], 'period' : [5], 'fixed' : True})
teachers. append({'name' : "Educação física 3/6", 'dow' : [3], 'class' : [6, 7], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Educação física 5/5", 'dow' : [5], 'class' : [6, 7], 'period' : [5], 'fixed' : True})
teachers. append({'name' : "Educação física 5/6", 'dow' : [5], 'class' : [8, 9], 'period' : [6], 'fixed' : True})
teachers. append({'name' : "Avaliação", 'dow' : [6], 'class' : [6, 7, 8, 9], 'period' : [4, 5], 'fixed' : True})

def error(msg):
    print("ERROR: %s" % msg)

class TimeSlot():
    def __init__(self):
        day_of_week = [2, 3, 4, 5, 6]
        periods = [1, 2, 3, 4, 5, 6]
        school_classes = [6, 7, 8, 9]
        self.timeslot = {}
        for day in day_of_week:
            self.timeslot[day] = {}
            for period in periods:
                self.timeslot[day][period] = {}
                for that_class in school_classes:
                    self.timeslot[day][period][that_class] = None
        self.class_counter = {}

    def SetFixedSlots(self):
        for teacher in teachers:
            if teacher['fixed'] is not True:
                continue
            name = teacher['name']
            day_of_week = teacher['dow']
            classes = teacher['class']
            periods = teacher['period']
            for day in day_of_week:
                for cl in classes:
                    for period in periods:
                        if self.timeslot[day][period][cl] is not None:
                            error("Somethig got nasty.  Slot already taken.")
                            continue
                        self.timeslot[day][period][cl] = {'name' : name }

    def getSlot(self, day, clas, slot):
        return self.timeslot[day][slot][clas]

    def setSlot(self, day, clas, slot, teacher):
        if self.getSlot(day, clas, slot) is None:
            self.timeslot[day][slot][clas]['name'] = teacher
        else:
            raise("Teacher error: slot taken")

    def setTeacherCounter(self, teacher, clas):
        if not teacher in self.class_counter:
            self.class_counter = { teacher : { clas : 1 } }
        elif not clas in self.class_counter[teacher]:
            self.class_counter[teacher] = { clas : 1 }
        else:
            self.class_counter[teacher][clas] += 1


    def getTeacherCounter(self, teacher, clas):
        if teacher in self.class_counter:
            if clas in self.class_counter[teacher]:
                return self.class_counter[teacher][clas]
        return 0

    def getNotFixedTeachers(self):
        all_teachers = []
        for teacher in teachers:
            if teacher['fixed'] is False:
                all_teachers.append(teacher['name'])
        return all_teachers

    def getTeacherData(self, teacher_name):
        for teacher in teachers:
            if teacher['name'] == teacher_name:
                return teacher
        return None

    def hasDayFree(self, teacher_data, day):
        if day in teacher_data['dow']:
            return True
        return False

    def hasClass(self, teacher_data, clas):
        if clas in teacher_data['class']:
            return True
        return False

    def hasPeriod(self, teacher_data, period):
        if period in teacher_data['period']:
            return True
        return False

    def hasAvailableTime(self, teacher_data, clas, counter):
        # {'name' : "Joselito", 'dow' : [2, 3, 5], 'class' : [8, 9], 'period' : [3, 4, 5, 6], 'fixed' : False, 'nr' : 2}
        amount_classes = teacher_data['nr']
        teacher_name = teacher_data['name']
        current_amount = self.getTeacherCounter(teacher_name, clas)
        if current_amount < amount_classes:
            return True
        else:
            return False

    def isAssignedSameTime(self, teacher, day, period):
        #self.timeslot[day][period][clas] = {'name' : teacher }
        for clas in self.timeslot[day][period]:
            if self.timeslot[day][period][clas] is None:
                continue
            try:
                if self.timeslot[day][period][clas]['name'] == teacher:
                    return True
            except:
                pass
        return False

    def getFreeTeacher(self, day, period, clas, teachers_list):
        teacher = None
        while teacher is None:
            lottery = random.randint(0, len(teachers_list) - 1)
            possible_teacher = teachers_list[lottery]
            teacher_data = self.getTeacherData(possible_teacher)
            if not self.hasDayFree(teacher_data, day):
                continue
            if not self.hasClass(teacher_data, clas):
                continue
            if not self.hasPeriod(teacher_data, period):
                continue
            counter = self.getTeacherCounter(possible_teacher, clas)
            if not self.hasAvailableTime(teacher_data, clas, counter):
                continue
            if self.isAssignedSameTime(possible_teacher, day, period):
                continue
            self.setTeacherCounter(possible_teacher, clas)
            teacher = possible_teacher
        return teacher

    def SetTeachers(self):
        teachers_list = self.getNotFixedTeachers()
        for day in self.timeslot.keys():
            for period in self.timeslot[day].keys():
                for clas in self.timeslot[day][period].keys():
                    try:
                        if self.timeslot[day][period][clas]['name'] is not None:
                            continue
                    except:
                        pass
                    teacher = self.getFreeTeacher(day, period, clas, teachers_list)
                    self.timeslot[day][period][clas] = {'name' : teacher }

    def Build(self):
        self.SetFixedSlots()
        self.SetTeachers()

    def Print(self, data=None):
        if data is None:
            data = self.timeslot
        print(json.dump(data, sys.stdout, indent=True, ensure_ascii=False, sort_keys=True))
        #pass

def main():
    ts = TimeSlot()
    ts.Build()
    ts.Print()

if __name__ == '__main__':
    main()
