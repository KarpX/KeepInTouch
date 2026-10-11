from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("contacts:contact_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("contacts:contact_list")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
