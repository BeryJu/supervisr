from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .views.common import index as common_index
from .forms.account import AuthenticationForm

def login(req):
    if req.method == 'POST':
        form = AuthenticationForm(req.POST)
        if form.is_valid():
            return redirect(reverse(common_index))
    else:
        form = NameForm()
    return render(req, 'account/login.html', { 'form': form })
