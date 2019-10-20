from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import VendorForm, VendorFormBBox
from accounts.models import Vendor


@login_required
def dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('setup_start')
    return render(request, 'users/dashboard.html', {})


@login_required
def setup_start(request):
    return render(request, 'users/setup_start.html', {})


@login_required
def setup_step1(request):
    if request.method == 'GET':
        try:
            form = VendorForm(instance=request.user.vendor)
        except AttributeError:
            form = VendorForm()
        return render(request, 'users/setup_step1.html', {'vendor_form': form})
    else:
        try:
            form = VendorForm(request.POST, request.FILES, instance=request.user.vendor)
        except AttributeError:
            form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            vendor.extract_pdf_img()
            return redirect('setup_step2')
        else:
            return render(request, 'users/setup_step1.html', {'vendor_form': form})


@login_required
def setup_step2(request):
    vendor = request.user.vendor
    if request.method == 'GET':

        form = VendorFormBBox(instance=vendor)
        return render(request, 'users/setup_step2.html', {'form': form, 'vendor': vendor})
    else:
        form = VendorFormBBox(request.POST, instance=vendor)
        vendor = form.save()
        return redirect('setup_complete')


@login_required
def setup_complete(request):
    vendor = request.user.vendor
    return render(request, 'users/setup_complete.html', {'vendor': vendor})


@login_required
def dashboard_payments(request):
    vendor = request.user.vendor
    return render(request, 'users/setup_complete.html', {'vendor': vendor})
