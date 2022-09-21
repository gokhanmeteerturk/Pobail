import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Member, Space, Announcement, Report, Submission, Coupon, Leader, Branch
from django.template.defaulttags import register
from django.db.models import Count, Q
from django.http import HttpResponseRedirect


def is_member_authorised(request, code):
    space = Space.objects.get(code=code)
    if request.session.get('member_id') and space in Member.objects.get(member_id=request.session['member_id']).space.all():
        return True
    else:
        return False


def is_leader_authorised(request, code):
    if request.session.get('leader_id') and code in Space.objects.filter(leader_id=request.session['leader_id']).values_list('code', flat=True):
        return True
    else:
        return False


# Login page for both member and leader
def std_login(request):
    try:
        # If the user is already logged in, redirect to the space page
        if request.session.get('member_id'):
            return redirect('/my/')
        elif request.session.get('leader_id'):
            return redirect('/leaderSpaces/')
        else:
            # If the user is not logged in, display the login page
            if request.method == 'POST':
                id = request.POST["id"]
                password = (request.POST["password"])
                try:
                    # Checks if id matches any member, if no match found, checks if id matches any leader
                    if Member.objects.filter(member_id=id).exists():
                        member = Member.objects.get(member_id=id)
                        if str(member.member_id) == id and str(member.password) == password:

                            request.session['member_id'] = id
                            return redirect('mySpaces')
                        else:
                            # id matches but member password is wrong
                            messages.error(
                                request, 'Incorrect password. Please try again.', extra_tags='alert')
                            return redirect('std_login')

                    else:
                        # Checks if id matches any leader
                        if Leader.objects.filter(leader_id=id).exists():
                            leader = Leader.objects.get(leader_id=id)
                            if str(leader.leader_id) == id and str(leader.password) == password:
                                request.session['leader_id'] = id
                                return redirect('leaderSpaces')

                            else:
                                # id matches but leader password is wrong
                                messages.error(
                                    request, 'Incorrect password. Please try again.', extra_tags='alert')
                                return redirect('std_login')
                        else:
                            # id does not match any member or leader
                            messages.error(
                                request, 'Incorrect user id. Please try again.', extra_tags='alert')
                            return redirect('std_login')
                except:
                    # id does not match any member or leader
                    messages.error(
                        request, 'Invalid login credentials.', extra_tags='alert')
                    return redirect('std_login')

            else:
                return render(request, 'login_page.html')
    except:
        return render(request, 'error.html')


# Clears the session on logout
def std_logout(request):
    request.session.flush()
    return redirect('std_login')


# Display all spaces (member view)
def mySpaces(request):
    try:
        if request.session.get('member_id'):
            member = Member.objects.get(
                member_id=request.session['member_id'])
            spaces = member.space.all()
            leader = member.space.all().values_list('leader_id', flat=True)

            context = {
                'spaces': spaces,
                'member': member,
                'leader': leader
            }

            return render(request, 'main/mySpaces.html', context)
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Display all spaces (leader view)
def leaderSpaces(request):
    try:
        if request.session['leader_id']:
            leader = Leader.objects.get(
                leader_id=request.session['leader_id'])
            spaces = Space.objects.filter(
                leader_id=request.session['leader_id'])
            # Member count of each space to show on the leader page
            memberCount = Space.objects.all().annotate(member_count=Count('members'))

            memberCountDict = {}

            for space in memberCount:
                memberCountDict[space.code] = space.member_count

            @register.filter
            def get_item(dictionary, space_code):
                return dictionary.get(space_code)

            context = {
                'spaces': spaces,
                'leader': leader,
                'memberCount': memberCountDict
            }

            return render(request, 'main/leaderSpaces.html', context)

        else:
            return redirect('std_login')
    except:

        return redirect('std_login')


# Particular space page (member view)
def space_page(request, code):
    try:
        space = Space.objects.get(code=code)
        if is_member_authorised(request, code):
            try:
                announcements = Announcement.objects.filter(space_code=space)
                reports = Report.objects.filter(
                    space_code=space.code)
                coupons = Coupon.objects.filter(space_code=space.code)

            except:
                announcements = None
                reports = None
                coupons = None

            context = {
                'space': space,
                'announcements': announcements,
                'reports': reports[:3],
                'coupons': coupons,
                'member': Member.objects.get(member_id=request.session['member_id'])
            }

            return render(request, 'main/space.html', context)

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Particular space page (leader view)
def space_page_leader(request, code):
    space = Space.objects.get(code=code)
    if request.session.get('leader_id'):
        try:
            announcements = Announcement.objects.filter(space_code=space)
            reports = Report.objects.filter(
                space_code=space.code)
            coupons = Coupon.objects.filter(space_code=space.code)
            memberCount = Member.objects.filter(space=space).count()

        except:
            announcements = None
            reports = None
            coupons = None

        context = {
            'space': space,
            'announcements': announcements,
            'reports': reports[:3],
            'coupons': coupons,
            'leader': Leader.objects.get(leader_id=request.session['leader_id']),
            'memberCount': memberCount
        }

        return render(request, 'main/leader_space.html', context)
    else:
        return redirect('std_login')


def error(request):
    return render(request, 'error.html')


# Display user profile(member & leader)
def profile(request, id):
    try:
        if request.session['member_id'] == id:
            member = Member.objects.get(member_id=id)
            return render(request, 'main/profile.html', {'member': member})
        else:
            return redirect('std_login')
    except:
        try:
            if request.session['leader_id'] == id:
                leader = Leader.objects.get(leader_id=id)
                return render(request, 'main/leader_profile.html', {'leader': leader})
            else:
                return redirect('std_login')
        except:
            return render(request, 'error.html')


def addAnnouncement(request, code):
    if is_leader_authorised(request, code):
        if request.method == 'POST' and request.POST['title'] and request.POST['description']:
            if request.FILES.get('file'):
                Announcement.objects.create(
                    space_code=Space.objects.get(code=code),
                    title=request.POST['title'],
                    description=request.POST['description'],
                    file=request.FILES['file']
                )
            else:
                Announcement.objects.create(
                    space_code=Space.objects.get(code=code),
                    title=request.POST['title'],
                    description=request.POST['description']
                )

            messages.success(request, 'Announcement posted successfully.')
            return redirect('/leader/' + str(code))
        else:
            return render(request, 'main/announcement.html', {'space': Space.objects.get(code=code), 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
    else:
        return redirect('std_login')


def deleteAnnouncement(request, code, id):
    if is_leader_authorised(request, code):
        try:
            announcement = Announcement.objects.get(space_code=code, id=id)
            announcement.delete()
            messages.warning(request, 'Announcement deleted successfully.')
            return redirect('/leader/' + str(code))
        except:
            return redirect('/leader/' + str(code))
    else:
        return redirect('std_login')


def editAnnouncement(request, code, id):
    if is_leader_authorised(request, code):
        announcement = Announcement.objects.get(space_code_id=code, id=id)
        context = {
            'announcement': announcement,
            'space': Space.objects.get(code=code),
            'leader': Leader.objects.get(leader_id=request.session['leader_id'])
        }
        return render(request, 'main/update-announcement.html', context)
    else:
        return redirect('std_login')


def updateAnnouncement(request, code, id):
    if is_leader_authorised(request, code):
        try:
            announcement = Announcement.objects.get(space_code_id=code, id=id)
            announcement.title = request.POST['title']
            announcement.description = request.POST['description']
            if request.FILES.get('file'):
                announcement.file = request.FILES['file']
            announcement.save()
            messages.info(request, 'Announcement updated successfully.')
            return redirect('/leader/' + str(code))
        except:
            return redirect('/leader/' + str(code))

    else:
        return redirect('std_login')


def addReport(request, code):
    if is_leader_authorised(request, code):
        if request.method == 'POST' and request.POST['title'] and request.POST['content']:
            try:
                space = Space.objects.get(code=code)
                space_code = space
                title = request.POST['title']
                description = request.POST['content']
                deadline = request.POST['datetime']
                marks = request.POST['marks']
                file = request.FILES['file']
                report = Report(space_code=space_code, title=title,
                                        description=description, deadline=deadline, marks=marks, file=file)

                report.save()
                messages.success(request, 'Report ' +
                                 report.title + ' posted successfully.')
                return redirect('/leader/' + str(code))
            except:

                return render(request, 'main/report.html', {'space': Space.objects.get(code=code), 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})

        else:
            return render(request, 'main/report.html', {'space': Space.objects.get(code=code), 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
    else:
        return redirect('std_login')


def reportPage(request, code, id):
    space = Space.objects.get(code=code)
    if is_member_authorised(request, code):
        report = Report.objects.get(space_code=space.code, id=id)
        try:

            submission = Submission.objects.get(report=report, member=Member.objects.get(
                member_id=request.session['member_id']))

            context = {
                'report': report,
                'space': space,
                'submission': submission,
                'time': datetime.datetime.now(),
                'member': Member.objects.get(member_id=request.session['member_id']),
                'spaces': Member.objects.get(member_id=request.session['member_id']).space.all()
            }

            return render(request, 'main/report-portal.html', context)

        except:
            submission = None

        context = {
            'report': report,
            'space': space,
            'submission': submission,
            'time': datetime.datetime.now(),
            'member': Member.objects.get(member_id=request.session['member_id']),
            'spaces': Member.objects.get(member_id=request.session['member_id']).space.all()
        }

        return render(request, 'main/report-portal.html', context)
    else:

        return redirect('std_login')


def allReports(request, code):
    if is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        reports = Report.objects.filter(space_code=space)
        memberCount = Member.objects.filter(space=space).count()

        context = {
            'reports': reports,
            'space': space,
            'leader': Leader.objects.get(leader_id=request.session['leader_id']),
            'memberCount': memberCount

        }
        return render(request, 'main/all-reports.html', context)
    else:
        return redirect('std_login')


def allReportsSTD(request, code):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        reports = Report.objects.filter(space_code=space)
        context = {
            'reports': reports,
            'space': space,
            'member': Member.objects.get(member_id=request.session['member_id']),

        }
        return render(request, 'main/all-reports-std.html', context)
    else:
        return redirect('std_login')


def addSubmission(request, code, id):
    try:
        space = Space.objects.get(code=code)
        if is_member_authorised(request, code):
            # check if report is open
            report = Report.objects.get(space_code=space.code, id=id)
            if report.deadline < datetime.datetime.now():

                return redirect('/report/' + str(code) + '/' + str(id))

            if request.method == 'POST' and request.FILES['file']:
                report = Report.objects.get(
                    space_code=space.code, id=id)
                submission = Submission(report=report, member=Member.objects.get(
                    member_id=request.session['member_id']), file=request.FILES['file'],)
                submission.status = 'Submitted'
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                report = Report.objects.get(
                    space_code=space.code, id=id)
                submission = Submission.objects.get(report=report, member=Member.objects.get(
                    member_id=request.session['member_id']))
                context = {
                    'report': report,
                    'space': space,
                    'submission': submission,
                    'time': datetime.datetime.now(),
                    'member': Member.objects.get(member_id=request.session['member_id']),
                    'spaces': Member.objects.get(member_id=request.session['member_id']).space.all()
                }

                return render(request, 'main/report-portal.html', context)
        else:
            return redirect('std_login')
    except:
        return HttpResponseRedirect(request.path_info)


def viewSubmission(request, code, id):
    space = Space.objects.get(code=code)
    if is_leader_authorised(request, code):
        try:
            report = Report.objects.get(space_code_id=code, id=id)
            submissions = Submission.objects.filter(
                report_id=report.id)

            context = {
                'space': space,
                'submissions': submissions,
                'report': report,
                'totalMembers': len(Member.objects.filter(space=space)),
                'leader': Leader.objects.get(leader_id=request.session['leader_id']),
                'spaces': Space.objects.filter(leader_id=request.session['leader_id'])
            }

            return render(request, 'main/report-view.html', context)

        except:
            return redirect('/leader/' + str(code))
    else:
        return redirect('std_login')


def gradeSubmission(request, code, id, sub_id):
    try:
        space = Space.objects.get(code=code)
        if is_leader_authorised(request, code):
            if request.method == 'POST':
                report = Report.objects.get(space_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    report_id=report.id)
                submission = Submission.objects.get(
                    report_id=id, id=sub_id)
                submission.marks = request.POST['marks']
                if request.POST['marks'] == 0:
                    submission.marks = 0
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                report = Report.objects.get(space_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    report_id=report.id)
                submission = Submission.objects.get(
                    report_id=id, id=sub_id)

                context = {
                    'space': space,
                    'submissions': submissions,
                    'report': report,
                    'totalMembers': len(Member.objects.filter(space=space)),
                    'leader': Leader.objects.get(leader_id=request.session['leader_id']),
                    'spaces': Space.objects.filter(leader_id=request.session['leader_id'])
                }

                return render(request, 'main/report-view.html', context)

        else:
            return redirect('std_login')
    except:
        return redirect('/error/')


def addSpaceCoupon(request, code):
    if is_leader_authorised(request, code):
        if request.method == 'POST' and request.POST['title'] and request.POST['content']:
            try:
                space = Space.objects.get(code=code)
                space_coupon = Coupon(space_code=space, title=request.POST['title'],
                                           description=request.POST['content'], file=request.FILES['file'])
                space_coupon.save()
                messages.success(request, 'New space coupon added')
                return redirect('/leader/' + str(code))
            except:
                return render(request, 'main/space-coupon.html', {'space': Space.objects.get(code=code), 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
        else:
            return render(request, 'main/space-coupon.html', {'space': Space.objects.get(code=code), 'leader': Leader.objects.get(leader_id=request.session['leader_id'])})
    else:
        return redirect('std_login')


def deleteSpaceCoupon(request, code, id):
    if is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        space_coupon = Coupon.objects.get(space_code=space, id=id)
        space_coupon.delete()
        messages.warning(request, 'Space coupon deleted')
        return redirect('/leader/' + str(code))
    else:
        return redirect('std_login')


def spaces(request):
    if request.session.get('member_id') or request.session.get('leader_id'):

        spaces = Space.objects.all()
        if request.session.get('member_id'):
            member = Member.objects.get(
                member_id=request.session['member_id'])
        else:
            member = None
        if request.session.get('leader_id'):
            leader = Leader.objects.get(
                leader_id=request.session['leader_id'])
        else:
            leader = None

        enrolled = member.space.all() if member else None
        accessed = Space.objects.filter(
            leader_id=leader.leader_id) if leader else None

        context = {
            'leader': leader,
            'spaces': spaces,
            'member': member,
            'enrolled': enrolled,
            'accessed': accessed
        }

        return render(request, 'main/all-spaces.html', context)

    else:
        return redirect('std_login')


def branches(request):
    if request.session.get('member_id') or request.session.get('leader_id'):
        branches = Branch.objects.all()
        if request.session.get('member_id'):
            member = Member.objects.get(
                member_id=request.session['member_id'])
        else:
            member = None
        if request.session.get('leader_id'):
            leader = Leader.objects.get(
                leader_id=request.session['leader_id'])
        else:
            leader = None
        context = {
            'leader': leader,
            'member': member,
            'deps': branches
        }

        return render(request, 'main/branches.html', context)

    else:
        return redirect('std_login')


def access(request, code):
    if request.session.get('member_id'):
        space = Space.objects.get(code=code)
        member = Member.objects.get(member_id=request.session['member_id'])
        if request.method == 'POST':
            if (request.POST['key']) == str(space.memberKey):
                member.space.add(space)
                member.save()
                return redirect('/my/')
            else:
                messages.error(request, 'Invalid key')
                return HttpResponseRedirect(request.path_info)
        else:
            return render(request, 'main/access.html', {'space': space, 'member': member})

    else:
        return redirect('std_login')


def search(request):
    if request.session.get('member_id') or request.session.get('leader_id'):
        if request.method == 'GET' and request.GET['q']:
            q = request.GET['q']
            spaces = Space.objects.filter(Q(code__icontains=q) | Q(
                name__icontains=q) | Q(leader__name__icontains=q))

            if request.session.get('member_id'):
                member = Member.objects.get(
                    member_id=request.session['member_id'])
            else:
                member = None
            if request.session.get('leader_id'):
                leader = Leader.objects.get(
                    leader_id=request.session['leader_id'])
            else:
                leader = None
            enrolled = member.space.all() if member else None
            accessed = Space.objects.filter(
                leader_id=leader.leader_id) if leader else None

            context = {
                'spaces': spaces,
                'leader': leader,
                'member': member,
                'enrolled': enrolled,
                'accessed': accessed,
                'q': q
            }
            return render(request, 'main/search.html', context)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('std_login')


def changePasswordPrompt(request):
    if request.session.get('member_id'):
        member = Member.objects.get(member_id=request.session['member_id'])
        return render(request, 'main/changePassword.html', {'member': member})
    elif request.session.get('leader_id'):
        leader = Leader.objects.get(leader_id=request.session['leader_id'])
        return render(request, 'main/changePasswordLeader.html', {'leader': leader})
    else:
        return redirect('std_login')


def changePhotoPrompt(request):
    if request.session.get('member_id'):
        member = Member.objects.get(member_id=request.session['member_id'])
        return render(request, 'main/changePhoto.html', {'member': member})
    elif request.session.get('leader_id'):
        leader = Leader.objects.get(leader_id=request.session['leader_id'])
        return render(request, 'main/changePhotoLeader.html', {'leader': leader})
    else:
        return redirect('std_login')


def changePassword(request):
    if request.session.get('member_id'):
        member = Member.objects.get(
            member_id=request.session['member_id'])
        if request.method == 'POST':
            if member.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                member.password = request.POST['newPassword']
                member.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/profile/' + str(member.member_id))
            else:
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePassword/')
        else:
            return render(request, 'main/changePassword.html', {'member': member})
    else:
        return redirect('std_login')


def changePasswordLeader(request):
    if request.session.get('leader_id'):
        leader = Leader.objects.get(
            leader_id=request.session['leader_id'])
        if request.method == 'POST':
            if leader.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                leader.password = request.POST['newPassword']
                leader.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/leaderProfile/' + str(leader.leader_id))
            else:
                print('error')
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePasswordLeader/')
        else:
            print(leader)
            return render(request, 'main/changePasswordLeader.html', {'leader': leader})
    else:
        return redirect('std_login')


def changePhoto(request):
    if request.session.get('member_id'):
        member = Member.objects.get(
            member_id=request.session['member_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                member.photo = request.FILES['photo']
                member.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/profile/' + str(member.member_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhoto/')
        else:
            return render(request, 'main/changePhoto.html', {'member': member})
    else:
        return redirect('std_login')


def changePhotoLeader(request):
    if request.session.get('leader_id'):
        leader = Leader.objects.get(
            leader_id=request.session['leader_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                leader.photo = request.FILES['photo']
                leader.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/leaderProfile/' + str(leader.leader_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhotoLeader/')
        else:
            return render(request, 'main/changePhotoLeader.html', {'leader': leader})
    else:
        return redirect('std_login')


def guestMember(request):
    request.session.flush()
    try:
        member = Member.objects.get(name='Guest Member')
        request.session['member_id'] = str(member.member_id)
        return redirect('mySpaces')
    except:
        return redirect('std_login')


def guestLeader(request):
    request.session.flush()
    try:
        leader = Leader.objects.get(name='Guest Leader')
        request.session['leader_id'] = str(leader.leader_id)
        return redirect('leaderSpaces')
    except:
        return redirect('std_login')
