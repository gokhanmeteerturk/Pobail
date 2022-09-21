import datetime
from django.shortcuts import redirect, render
from talk.models import LeaderTalk, MemberTalk
from main.models import Member, Leader, Space
from main.views import is_leader_authorised, is_member_authorised
from itertools import chain

# Create your views here.


''' We have two different user models.
    That's why we are filtering the talks based on the user type and then combining them.'''


def context_list(space):
    try:
        memberDis = MemberTalk.objects.filter(space=space)
        leaderDis = LeaderTalk.objects.filter(space=space)
        talks = list(chain(memberDis, leaderDis))
        talks.sort(key=lambda x: x.sent_at, reverse=True)

        for dis in talks:
            if dis.__class__.__name__ == 'MemberTalk':
                dis.author = Member.objects.get(member_id=dis.sent_by_id)
            else:
                dis.author = Leader.objects.get(leader_id=dis.sent_by_id)
    except:

        talks = []

    return talks


def talk(request, code):
    if is_member_authorised(request, code):
        space = Space.objects.get(code=code)
        member = Member.objects.get(member_id=request.session['member_id'])
        talks = context_list(space)
        context = {
            'space': space,
            'member': member,
            'talks': talks,
        }
        return render(request, 'talk/talk.html', context)

    elif is_leader_authorised(request, code):
        space = Space.objects.get(code=code)
        leader = Leader.objects.get(leader_id=request.session['leader_id'])
        talks = context_list(space)
        context = {
            'space': space,
            'leader': leader,
            'talks': talks,
        }
        return render(request, 'talk/talk.html', context)
    else:
        return redirect('std_login')


def send(request, code, std_id):
    if is_member_authorised(request, code):
        if request.method == 'POST':
            content = request.POST['content']
            space = Space.objects.get(code=code)
            member = Member.objects.get(member_id=std_id)
            try:
                MemberTalk.objects.create(
                    content=content,
                    space=space,
                    sent_by=member,
                    sent_at=datetime.datetime.now()
                )
                return redirect('talk', code=code)
            except:
                return redirect('talk', code=code)

    else:
        return render(request, 'error.html')


def send_fac(request, code, fac_id):
    if is_leader_authorised(request, code):
        if request.method == 'POST':
            content = request.POST['content']
            space = Space.objects.get(code=code)
            try:
                leader = Leader.objects.get(leader_id=fac_id)
                LeaderTalk.objects.create(
                    content=content,
                    space=space,
                    sent_by=leader,
                    sent_at=datetime.datetime.now()
                )
                return redirect('talk', code=code)
            except:
                return redirect('talk', code=code)
    else:
        return render(request, 'error.html')
