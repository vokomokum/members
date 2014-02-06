from __future__ import unicode_literals

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid.url import route_url
from pyramid.view import view_config

import os
import base64

from members.utils.security import get_member
from members.utils.security import authenticated_user
from members.utils.md5crypt import md5crypt
from members.views.base import BaseView


@view_config(renderer='../templates/base.pt', route_name='login')
@view_config(renderer='../templates/base.pt',
             context='pyramid.exceptions.Forbidden')
class Login(BaseView):

    def __call__(self):
        self.logged_in = False
        referrer = self.request.url
        try: # to protect tests from failing, as this is not critical
            login_url = route_url('login', self.request)
            if referrer == login_url:
                referrer = '/' # never use the login form itself as came_from
        except:
            pass
        message = ''
        if 'form.submitted' in self.request.params:
            login = self.request.params['login']
            passwd = self.request.params['passwd']
            member = get_member(login)
            if member:
                # jim uses encrypted pwd as salt
                enc_pwd = md5crypt(str(passwd), str(member.mem_enc_pwd))
                if (member.mem_enc_pwd and str(member.mem_enc_pwd) == enc_pwd):
                    if member.mem_active:
                        self.logged_in = True
                        member.mem_cookie = base64.urlsafe_b64encode(os.urandom(24))
                        member.mem_ip = self.request.client_addr
                        headers = remember(self.request, member.mem_id)
                        return HTTPFound(location = self.came_from, headers = headers)
                    else:
                        message += 'Login denied because the account of {} has been '\
                                   ' set to inactive.'.format(member)
                        if member.balance < 0:
                            message += ' One possible reason for deactivation is'\
                                       ' that the account balance is EUR {}. Please'\
                                       ' transfer the missing amount to Vokomokum,'\
                                       ' account no. 78.68.29.109, t.p.v. Amsterdam'\
                                       ' (be sure to include your member number)'\
                                       ' and contact finance@vokomokum.nl to report'\
                                       ' that you have paid.'\
                                        .format(member.balance)   
                        else:
                            message += ' Please contact membership@vokomokum.nl.' 
                else:
                    message += ' The password is not correct.'
            else:
                message += ' Member not found. '
            message += ' The Login failed.'

        return dict(msg = message,
                    url = self.request.application_url + '/login')


@view_config(renderer='../templates/base.pt', route_name='logout')
class Logout(BaseView):

    def __call__(self):
        m = get_member(self.request.cookies.get("Mem"))
        m.mem_cookie = ""
        headers = forget(self.request)
        return HTTPFound(location = route_url('home', self.request),
                         headers = headers)


@view_config(renderer='json', route_name='userinfo')
def userinfo(request):
    '''
    This view is used from outside apps (currently: vers foodcoop) to check
    if a user is logged in here. If (s)he is, we return some info.
    '''
    member = authenticated_user(request)
    if not member:
        return dict(error='Could not authenticate member.') 
    return dict(user_id=member.mem_id, given_name=member.mem_fname,
                middle_name=member.mem_prefix, family_name=member.mem_lname,
                email=member.mem_email)
