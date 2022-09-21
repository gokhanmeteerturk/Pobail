import datetime
from django.shortcuts import render, redirect
from .models import Quiz, Question, MemberAnswer
from main.models import Member, Space, Leader
from main.views import is_leader_authorised, is_member_authorised
from django.contrib import messages


def quiz(request, code):
    try:
        space = Space.objects.get(code=code)
        if is_leader_authorised(request, code):
            if request.method == 'POST':
                title = request.POST.get('title')
                description = request.POST.get('description')
                start = request.POST.get('start')
                end = request.POST.get('end')
                publish_status = request.POST.get('checkbox')
                quiz = Quiz(title=title, description=description, start=start,
                            end=end, publish_status=publish_status, space=space)
                quiz.save()
                return redirect('addQuestion', code=code, quiz_id=quiz.id)
            else:
                return render(request, 'quiz/quiz.html', {'space': space, 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def addQuestion(request, code, quiz_id):
    try:
        space = Space.objects.get(code=code)
        if is_leader_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                question = request.POST.get('question')
                option1 = request.POST.get('option1')
                option2 = request.POST.get('option2')
                option3 = request.POST.get('option3')
                option4 = request.POST.get('option4')
                answer = request.POST.get('answer')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question = Question(question=question, option1=option1, option2=option2,
                                    option3=option3, option4=option4, answer=answer, quiz=quiz, marks=marks, explanation=explanation)
                question.save()
                messages.success(request, 'Question added successfully')
            else:
                return render(request, 'quiz/addQuestion.html', {'space': space, 'quiz': quiz, 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
            if 'saveOnly' in request.POST:
                return redirect('allQuizzes', code=code)
            return render(request, 'quiz/addQuestion.html', {'space': space, 'quiz': quiz, 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def allQuizzes(request, code):
    if is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        quizzes = Quiz.objects.filter(space=space)
        for quiz in quizzes:
            quiz.total_questions = Question.objects.filter(quiz=quiz).count()
            if quiz.start < datetime.datetime.now():
                quiz.started = True
            else:
                quiz.started = False
            quiz.save()
        return render(request, 'quiz/allQuizzes.html', {'space': space, 'quizzes': quizzes, 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
    else:
        return redirect('std_login')


# REFACTOR THIS
def myQuizzes(request, code):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        quizzes = Quiz.objects.filter(space=space)
        member = Member.objects.get(member_id=request.session['member_id'])
        # check if that member has already attempted this quiz
        for quiz in quizzes:
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=quiz)
            if member_answers.count() > 0:
                quiz.attempted = True
            else:
                quiz.attempted = False

        active_quizzes = []
        previous_quizzes = []

        for quiz in quizzes:
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=quiz)
            if quiz.end < datetime.datetime.now() or member_answers.count() > 0:
                previous_quizzes.append(quiz)
            else:
                active_quizzes.append(quiz)

        for previousQuiz in previous_quizzes:
            total_marks_obtained = 0
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=previousQuiz)

            for member_answer in member_answers:
                total_marks_obtained += member_answer.question.marks if member_answer.answer == member_answer.question.answer else 0
            previousQuiz.total_marks_obtained = total_marks_obtained

            previousQuiz.total_marks = 0
            for question in previousQuiz.question_set.all():
                previousQuiz.total_marks += question.marks

            try:
                previousQuiz.percentage = (
                    total_marks_obtained / previousQuiz.total_marks) * 100
                previousQuiz.percentage = round(previousQuiz.percentage, 2)
            except ZeroDivisionError:
                previousQuiz.percentage = 0

        for previousQuiz in previous_quizzes:
            previousQuiz.total_questions = Question.objects.filter(
                quiz=previousQuiz).count()
        for activeQuiz in active_quizzes:
            activeQuiz.total_questions = Question.objects.filter(
                quiz=activeQuiz).count()

        return render(request, 'quiz/myQuizzes.html', {'space': space, 'quizzes': quizzes, 'active_quizzes': active_quizzes, 'previous_quizzes': previous_quizzes, 'member': member})
    else:
        return redirect('std_login')


def startQuiz(request, code, quiz_id):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        total_questions = questions.count()

        marks = 0
        for question in questions:
            marks += question.marks
        quiz.total_marks = marks

        return render(request, 'quiz/portalStdNew.html', {'space': space, 'quiz': quiz, 'questions': questions, 'total_questions': total_questions, 'member': Member.objects.get(member_id=request.session['member_id'])})
    else:
        return redirect('std_login')


def memberAnswer(request, code, quiz_id):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        member = Member.objects.get(member_id=request.session['member_id'])

        for question in questions:
            answer = request.POST.get(str(question.id))
            member_answer = MemberAnswer(member=member, quiz=quiz, question=question,
                                           answer=answer, marks=question.marks if answer == question.answer else 0)
            # prevent duplicate answers & multiple attempts
            try:
                member_answer.save()
            except:
                redirect('myQuizzes', code=code)
        return redirect('myQuizzes', code=code)
    else:
        return redirect('std_login')


def quizResult(request, code, quiz_id):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        try:
            member = Member.objects.get(
                member_id=request.session['member_id'])
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=quiz)
            total_marks_obtained = 0
            for member_answer in member_answers:
                total_marks_obtained += member_answer.question.marks if member_answer.answer == member_answer.question.answer else 0
            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = 0
            for question in questions:
                quiz.total_marks += question.marks
            quiz.percentage = (total_marks_obtained / quiz.total_marks) * 100
            quiz.percentage = round(quiz.percentage, 2)
        except:
            quiz.total_marks_obtained = 0
            quiz.total_marks = 0
            quiz.percentage = 0

        for question in questions:
            member_answer = MemberAnswer.objects.get(
                member=member, question=question)
            question.member_answer = member_answer.answer

        member_answers = MemberAnswer.objects.filter(
            member=member, quiz=quiz)
        for member_answer in member_answers:
            quiz.time_taken = member_answer.created_at - quiz.start
            quiz.time_taken = quiz.time_taken.total_seconds()
            quiz.time_taken = round(quiz.time_taken, 2)
            quiz.submission_time = member_answer.created_at.strftime(
                "%a, %d-%b-%y at %I:%M %p")
        return render(request, 'quiz/quizResult.html', {'space': space, 'quiz': quiz, 'questions': questions, 'member': member})
    else:
        return redirect('std_login')


# REFACTOR THIS
def quizSummary(request, code, quiz_id):
    if is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)

        questions = Question.objects.filter(quiz=quiz)
        time = datetime.datetime.now()
        total_members = Member.objects.filter(space=space).count()
        for question in questions:
            question.A = MemberAnswer.objects.filter(
                question=question, answer='A').count()
            question.B = MemberAnswer.objects.filter(
                question=question, answer='B').count()
            question.C = MemberAnswer.objects.filter(
                question=question, answer='C').count()
            question.D = MemberAnswer.objects.filter(
                question=question, answer='D').count()
        # members who have attempted the quiz and their marks
        members = Member.objects.filter(space=space)
        for member in members:
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=quiz)
            total_marks_obtained = 0
            for member_answer in member_answers:
                total_marks_obtained += member_answer.question.marks if member_answer.answer == member_answer.question.answer else 0
            member.total_marks_obtained = total_marks_obtained

        if request.method == 'POST':
            quiz.publish_status = True
            quiz.save()
            return redirect('quizSummary', code=code, quiz_id=quiz.id)
        # check if member has attempted the quiz
        for member in members:
            if MemberAnswer.objects.filter(member=member, quiz=quiz).count() > 0:
                member.attempted = True
            else:
                member.attempted = False
        for member in members:
            member_answers = MemberAnswer.objects.filter(
                member=member, quiz=quiz)
            for member_answer in member_answers:
                member.submission_time = member_answer.created_at.strftime(
                    "%a, %d-%b-%y at %I:%M %p")

        context = {'space': space, 'quiz': quiz, 'questions': questions, 'time': time, 'total_members': total_members,
                   'members': members, 'leader': Leader.objects.get(leader_id=request.session['leader_id'])}
        return render(request, 'quiz/quizSummaryLeader.html', context)

    else:
        return redirect('std_login')
