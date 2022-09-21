from django.contrib import messages
from django.shortcuts import render, redirect
from . models import Attendance
from main.models import Member, Space, Leader
from main.views import is_leader_authorised


def attendance(request, code):
    if is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        members = Member.objects.filter(space__code=code)

        return render(request, 'attendance/attendance.html', {'members': members, 'space': space, 'leader': Leader.objects.get(space=space)})


def createRecord(request, code):
    if is_leader_authorised(request, code):
        if request.method == 'POST':
            date = request.POST['dateCreate']
            space = Space.objects.get(code=code)
            members = Member.objects.filter(space__code=code)
            # check if attendance record already exists for the date
            if Attendance.objects.filter(date=date, space=space).exists():
                return render(request, 'attendance/attendance.html', {'code': code, 'members': members, 'space': space, 'leader': Leader.objects.get(space=space), 'error': "Attendance record already exists for the date " + date})
            else:
                for member in members:
                    attendance = Attendance(
                        member=member, space=space, date=date, status=False)
                    attendance.save()

                messages.success(
                    request, 'Attendance record created successfully for the date ' + date)
                return redirect('/attendance/' + str(code))
        else:
            return redirect('/attendance/' + str(code))
    else:
        return redirect('std_login')


def loadAttendance(request, code):
    if is_leader_authorised(request, code):
        if request.method == 'POST':
            date = request.POST['date']
            space = Space.objects.get(code=code)
            members = Member.objects.filter(space__code=code)
            attendance = Attendance.objects.filter(space=space, date=date)
            # check if attendance record exists for the date
            if attendance.exists():
                return render(request, 'attendance/attendance.html', {'code': code, 'members': members, 'space': space, 'leader': Leader.objects.get(space=space), 'attendance': attendance, 'date': date})
            else:
                return render(request, 'attendance/attendance.html', {'code': code, 'members': members, 'space': space, 'leader': Leader.objects.get(space=space), 'error': 'Could not load. Attendance record does not exist for the date ' + date})

    else:
        return redirect('std_login')


def submitAttendance(request, code):
    if is_leader_authorised(request, code):
        try:
            members = Member.objects.filter(space__code=code)
            space = Space.objects.get(code=code)
            if request.method == 'POST':
                date = request.POST['datehidden']
                for member in members:
                    attendance = Attendance.objects.get(
                        member=member, space=space, date=date)
                    if request.POST.get(str(member.member_id)) == '1':
                        attendance.status = True
                    else:
                        attendance.status = False
                    attendance.save()
                messages.success(request, 'Attendance record saved for ' + date)
                return redirect('/attendance/' + str(code))
            else:
                return render(request, 'attendance/attendance.html', {'code': code, 'members': members, 'space': space, 'leader': Leader.objects.get(space=space)})
        except:
            return render(request, 'attendance/attendance.html', {'code': code, 'error': "Error! could not save", 'members': members, 'space': space, 'leader': Leader.objects.get(space=space)})
