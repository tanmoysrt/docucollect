from datetime import datetime
import random
import string
import os
import shutil
import pandas as pd

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from documentCollector.settings import BASE_DIR, SECURITY_KEY_REPORT
from studentportal import models
from studentportal.utils import send_forget_password_mail, generate_filename_for_course, \
    generate_filename_for_hackathon, generate_filename_for_internship, generate_filename_for_placement, \
    generate_filename_for_docs


def login_page(request):
    data = {
        "title": "Login Now",
        "dontshownav": True
    }
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        email_id = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(email=email_id, password=password)
        if user:
            login(user=user, request=request)
            return redirect("/")
        else:
            data["error"] = "Incorrect e-mail or password"
    return render(request, "studentportal/login.html", data)


def register_page(request):
    data = {
        "years": models.YEARS,
        "title": "Register Now",
        "dontshownav": True
    }
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email_id = request.POST["email_id"]
        phone_no = request.POST["phone_no"]
        roll_no = request.POST["roll_no"]
        graduation_year = request.POST["graduation_year"]
        year = request.POST["year"]
        password = request.POST["password"]
        if first_name == "" or last_name == "" or email_id == "" or len(phone_no) != 10 or len(roll_no) != 12 or \
                len(graduation_year) != 4 or year == "" or password == "":
            data["error"] = "Fill the form correctly please"
        else:
            try:
                with transaction.atomic():
                    auth_profile = models.StudentAuthProfile.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=email_id
                    )
                    auth_profile.set_password(password)
                    auth_profile.save()
                    personal_profile = models.StudentPersonalProfile.objects.create(
                        user=auth_profile,
                        roll_no=roll_no,
                        phone_no=phone_no,
                        year=year,
                        graduation_year=graduation_year
                    )
                    login(user=auth_profile, request=request)
                    return redirect("/")
            except:
                data["error"] = "Unexpected Error occured"
    return render(request, "studentportal/register.html", data)


def forget_password_page(request):
    data = {
        "dontshownav": True
    }
    if request.method == "POST":
        try:
            email = request.POST["email"]
            account = models.StudentAuthProfile.objects.get(email=email)
            if account is not None:
                password = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
                account.set_password(password)
                account.save()
                send_forget_password_mail(email=account.email, name=account.get_full_name(), password=password)
                data["success"] = "Password has been reset and sent to your e-mail id"
            else:
                raise Exception("Not found account")
        except:
            data["error"] = "Failed to reset password ! Check mail id and retry"
    return render(request, "studentportal/forget_password.html", data)


@login_required(login_url='/login')
def dashboard_page(request):
    data = {
        "name": request.user.get_full_name(),
        "email": request.user.email,
        "title": "Dashboard"
    }
    profile = models.StudentPersonalProfile.objects.get(user__id=request.user.id)
    data["roll_no"] = profile.roll_no
    data["phone_no"] = profile.phone_no
    data["year"] = profile.get_year_display()
    data["graduation_year"] = profile.graduation_year

    return render(request, "studentportal/dashboard.html", data)


@login_required(login_url='/login')
def profile_page(request):
    successMsg = ""
    errorMsg = ""
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        roll_no = request.POST["roll_no"]
        graduation_year = request.POST["graduation_year"]
        year = request.POST["year"]
        if first_name == "" or last_name == "" or len(roll_no) != 12 or len(graduation_year) != 4 or year == "":
            errorMsg = "Fill the form correctly please"
        else:
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            profile = models.StudentPersonalProfile.objects.get(user__id=user.id)
            profile.roll_no = roll_no
            profile.graduation_year = graduation_year
            profile.year = year
            profile.save()
            successMsg = "Profile updated successfully !"

    data = {
        "title": "Personal Profile",
        "years": models.YEARS,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
    }
    if successMsg:
        data["success"] = successMsg
    if errorMsg:
        data["error"] = errorMsg
    profile = models.StudentPersonalProfile.objects.get(user__id=request.user.id)
    data["roll_no"] = profile.roll_no
    data["phone_no"] = profile.phone_no
    data["year"] = profile.year
    data["graduation_year"] = profile.graduation_year

    return render(request, "studentportal/profile.html", data)


@login_required(login_url='/login')
def internship_list_page(request):
    data = {
        "title": "Internships Record",
        "internships": models.JobProfile.objects.filter(type="internship")
    }
    return render(request, "studentportal/internship_list.html", data)


@login_required(login_url='/login')
def placement_list_page(request):
    data = {
        "title": "Placements Record",
        "placements": models.JobProfile.objects.filter(type="placement")
    }
    return render(request, "studentportal/placement_list.html", data)


@login_required(login_url='/login')
def hackathon_list_page(request):
    data = {
        "title": "Hackathons Record",
        "hackathons": models.HackathonProfile.objects.filter()
    }
    return render(request, "studentportal/hackathon_list.html", data)


@login_required(login_url='/login')
def online_course_list_page(request):
    data = {
        "title": "Courses Record",
        "courses": models.OnlineCoursesProfile.objects.filter()
    }
    return render(request, "studentportal/onlinecourse_list.html", data)


@login_required(login_url='/login')
def other_docs_list_page(request):
    data = {
        "title": "Other Documents Record",
        "docs": models.OtherDocuments.objects.all()
    }
    return render(request, "studentportal/otherdocs_list.html", data)

def generate_random_filename(filename):
    extension = str(filename).split(".")[-1]
    random_name = str(random.randint(1111111111111111, 9999999999999999))
    final_random_name = random_name + "." + extension
    return final_random_name


def upload_file(file):
    fs = FileSystemStorage(location='media/')
    filename = fs.save(generate_random_filename(file.name), file)
    return fs.generate_filename(filename)


@login_required(login_url='/login')
def add_placement_page(request):
    data = {
        "title": "Add Placement Record",
        "months": models.MONTHS
    }
    # type -> placement
    if request.method == "POST" and request.FILES and request.FILES["document"]:
        file = request.FILES["document"]
        company = request.POST["company"]
        month = request.POST["month"]
        year = request.POST["year"]

        filename = upload_file(file)
        models.JobProfile.objects.create(
            document=filename,
            type="placement",
            year=year,
            month=month,
            duration_months=0,
            company=company,
            user_id=request.user.id
        )
        return redirect(reverse("student_placement_list_page"))
    # company, month, year, document

    return render(request, "studentportal/add_placement.html", data)


@login_required(login_url='/login')
def add_internship_page(request):
    data = {
        "title": "Add Internship Record",
        "months": models.MONTHS
    }
    # type -> placement
    if request.method == "POST" and request.FILES and request.FILES["document"]:
        file = request.FILES["document"]
        company = request.POST["company"]
        month = request.POST["month"]
        year = request.POST["year"]
        duration = request.POST["duration"]

        filename = upload_file(file)
        models.JobProfile.objects.create(
            document=filename,
            type="internship",
            year=year,
            month=month,
            duration_months=duration,
            company=company,
            user_id=request.user.id
        )
        return redirect(reverse("student_internship_list_page"))
    # company, month, year, document

    return render(request, "studentportal/add_internship.html", data)


@login_required(login_url='/login')
def add_hackathon_page(request):
    data = {
        "title": "Add Hackathon Record",
        "certificate_types": models.HACKATHON_CERTIFICATE_TYPE,
        "months": models.MONTHS
    }

    if request.method == "POST" and request.FILES and request.FILES["document"]:
        file = request.FILES["document"]
        certificate_type = request.POST["certificate_type"]
        organizer = request.POST["organizer"]
        title = request.POST["title"]
        month = request.POST["month"]
        year = request.POST["year"]

        filename = upload_file(file)

        models.HackathonProfile.objects.create(
            document=filename,
            title=title,
            year=year,
            month=month,
            certificate_type=certificate_type,
            organizer=organizer,
            user_id=request.user.id
        )
        return redirect(reverse("student_hackathon_list_page"))
    # organizer, certificate_type, month, year, document
    return render(request, "studentportal/add_hackathon.html", data)


@login_required(login_url='/login')
def add_online_course_page(request):
    data = {
        "title": "Add Courses Record",
        "months": models.MONTHS
    }

    if request.method == "POST" and request.FILES and request.FILES["document"]:
        file = request.FILES["document"]
        title = request.POST["title"]
        issued_by = request.POST["issued_by"]
        description = request.POST["description"]
        year = request.POST["year"]

        filename = upload_file(file)

        models.OnlineCoursesProfile.objects.create(
            document=filename,
            year=year,
            title=title,
            issued_by=issued_by,
            description=description,
            user_id=request.user.id
        )
        return redirect(reverse("student_online_course_list_page"))
    # title, issued_by, description, year, document
    return render(request, "studentportal/add_online_course.html", data)

@login_required(login_url='/login')
def add_other_docs_page(request):
    data = {
        "title": "Add Other Documents",
    }

    if request.method == "POST" and request.FILES and request.FILES["document"]:
        file = request.FILES["document"]
        title = request.POST["title"]
        description = request.POST["description"]

        filename = upload_file(file)

        models.OtherDocuments.objects.create(
            document=filename,
            title=title,
            description=description,
            user_id=request.user.id
        )
        return redirect(reverse("student_other_docs_list_page"))
    # title, description, document
    return render(request, "studentportal/add_other_docs.html", data)


@login_required(login_url='/login')
def download_file(request):
    filename = request.GET.get("filename", "unnamed.pdf")
    source = request.GET.get("source", "-1")
    if source == "-1" or source == "":
        return HttpResponse("File not found or you have not accesss", status=404)
    file = open("media/" + source, "rb")
    return FileResponse(file, as_attachment=True, filename=filename)


@login_required(login_url='/login')
def delete_record(request):
    record_type = request.GET.get("type", "-1")
    record_id = request.GET.get("id", "-1")
    if record_type == "" or record_type == "-1" or record_id == "-1" or record_id == "":
        return HttpResponse("Cant delete", status=400)
    if record_type == "internship":
        tmp = models.JobProfile.objects.get(type="internship", id=record_id)
        try:
            os.remove(os.path.join(os.path.join(BASE_DIR, "media"), tmp.document))
        except:
            pass
        tmp.delete()
        return redirect(reverse("student_internship_list_page"))
    elif record_type == "placement":
        tmp = models.JobProfile.objects.get(type="placement", id=record_id)
        try:
            os.remove(os.path.join(os.path.join(BASE_DIR, "media"), tmp.document))
        except:
            pass
        tmp.delete()
        return redirect(reverse("student_placement_list_page"))
    elif record_type == "hackathon":
        tmp = models.HackathonProfile.objects.get(id=record_id)
        try:
            os.remove(os.path.join(os.path.join(BASE_DIR, "media"), tmp.document))
        except:
            pass
        tmp.delete()
        return redirect(reverse("student_hackathon_list_page"))
    elif record_type == "course":
        tmp = models.OnlineCoursesProfile.objects.get(id=record_id)
        try:
            os.remove(os.path.join(os.path.join(BASE_DIR, "media"), tmp.document))
        except:
            pass
        tmp.delete()
        return redirect(reverse("student_online_course_list_page"))
    elif record_type == "other":
        tmp = models.OtherDocuments.objects.get(id=record_id)
        try:
            os.remove(os.path.join(os.path.join(BASE_DIR, "media"), tmp.document))
        except:
            pass
        tmp.delete()
        return redirect(reverse("student_other_docs_list_page"))
    return HttpResponse("Cant delete", status=400)


def download_report(request):
    key = request.GET["key"]
    if key != SECURITY_KEY_REPORT:
        return HttpResponse("Bye", status=500)
    source = request.GET.get("source", "-1")
    if source == "-1" or source == "":
        return HttpResponse("File not found or you have not accesss", status=404)
    file = open("reports/" + source, "rb")
    return FileResponse(file, as_attachment=True, filename="report.zip")


def generate_report(request):
    key = request.GET["key"]
    if key != SECURITY_KEY_REPORT:
        return HttpResponse("Bye", status=500)
    users = models.StudentAuthProfile.objects.filter(is_superuser=False)
    TMP_FOLDER = "tmp_"+str(random.randint(111111111111111111, 999999999999999999))
    FINAL_PATH = os.path.join(BASE_DIR, TMP_FOLDER)
    MEDIA_PATH = os.path.join(BASE_DIR, "media")
    # Delete folder
    if os.path.exists(path=FINAL_PATH):
        shutil.rmtree(FINAL_PATH)
    # Create folder
    os.mkdir(FINAL_PATH)
    # Iterate
    for user in users:
        user_folder_path = os.path.join(FINAL_PATH, f'{user.get_full_name().replace(" ", "_")}_{user.personal_profile.roll_no}')
        # Create folder user
        os.mkdir(user_folder_path)
        # Build path for different type
        user_folder_path__internship = os.path.join(user_folder_path, "internship")
        user_folder_path__placement = os.path.join(user_folder_path, "placement")
        user_folder_path__hackathon = os.path.join(user_folder_path, "hackathon")
        user_folder_path__course = os.path.join(user_folder_path, "course")
        user_folder_path__docs = os.path.join(user_folder_path, "docs")
        # Objects
        internships = user.job_profile.filter(type="internship")
        placements = user.job_profile.filter(type="placement")
        hackathons = user.hackathon_profile.all()
        courses = user.online_courses_profile.all()
        docs = user.other_documents.all()
        
        # Save files
        if len(internships) > 0:
            os.mkdir(user_folder_path__internship)
            for internship in internships:
                shutil.copy(os.path.join(MEDIA_PATH, internship.document), os.path.join(user_folder_path__internship, generate_filename_for_internship(internship)))

        if len(placements) > 0:
            os.mkdir(user_folder_path__placement)
            for placement in placements:
                shutil.copy(os.path.join(MEDIA_PATH, placement.document), os.path.join(user_folder_path__placement, generate_filename_for_placement(placement)))

        if len(hackathons) > 0:
            os.mkdir(user_folder_path__hackathon)
            for hackathon in hackathons:
                shutil.copy(os.path.join(MEDIA_PATH, hackathon.document),
                            os.path.join(user_folder_path__hackathon, generate_filename_for_hackathon(hackathon)))

        if len(courses) > 0:
            os.mkdir(user_folder_path__course)
            for course in courses:
                shutil.copy(os.path.join(MEDIA_PATH, course.document),
                            os.path.join(user_folder_path__course, generate_filename_for_course(course)))

        if len(docs) > 0:
            os.mkdir(user_folder_path__docs)
            for doc in docs:
                shutil.copy(os.path.join(MEDIA_PATH, doc.document),
                            os.path.join(user_folder_path__docs, generate_filename_for_docs(doc)))

    compressedFilePath = os.path.join(os.path.join(BASE_DIR, "reports"), TMP_FOLDER)
    shutil.make_archive(compressedFilePath, "zip", FINAL_PATH, '.')
    # final_file = open(compressedFilePath+".zip", "rb")
    shutil.rmtree(FINAL_PATH)
    # return FileResponse(final_file, as_attachment=True, filename="report.zip")
    return redirect(f"/report/download/?source={TMP_FOLDER}.zip&key={key}")


def generate_report_v2(request):
    key = request.GET["key"]
    if key != SECURITY_KEY_REPORT:
        return HttpResponse("Bye", status=500)
    users = models.StudentAuthProfile.objects.filter(is_superuser=False)
    TMP_FOLDER = "tmp_" + str(random.randint(111111111111111111, 999999999999999999))
    FINAL_PATH = os.path.join(BASE_DIR, TMP_FOLDER)
    MEDIA_PATH = os.path.join(BASE_DIR, "media")
    # Delete folder
    if os.path.exists(path=FINAL_PATH):
        shutil.rmtree(FINAL_PATH)
    # Create folder
    os.mkdir(FINAL_PATH)

    # Init sub-folders
    internship_folder = os.path.join(FINAL_PATH, "internship")
    placement_folder = os.path.join(FINAL_PATH, "placement")
    hackathon_folder = os.path.join(FINAL_PATH, "hackathon")
    course_folder = os.path.join(FINAL_PATH, "course")
    other_docs_folder = os.path.join(FINAL_PATH, "other_docs")

    # Create sub-folders
    os.mkdir(internship_folder)
    os.mkdir(placement_folder)
    os.mkdir(hackathon_folder)
    os.mkdir(course_folder)
    os.mkdir(other_docs_folder)

    # Init dataframes
    internships_dataframe = pd.DataFrame(["Year", "Roll No", "Name", "E-mail Id", "Phone No", "Company", "Duration [In months]", "Received on"])
    placement_dataframe =   pd.DataFrame(["Year", "Roll No", "Name", "E-mail Id", "Phone No", "Company", "Received on"])
    hackathon_dataframe =   pd.DataFrame(["Year", "Roll No", "Name", "E-mail Id", "Phone No", "Hackathon Name", "Organized by", "Rank", "Received on"])
    course_dataframe =      pd.DataFrame(["Year", "Roll No", "Name", "E-mail Id", "Phone No", "Course Name", "Issued By", "Description", "Received on"])
    other_docs_dataframe =  pd.DataFrame(["Year", "Roll No", "Name", "E-mail Id", "Phone No", "Title", "Description"])


    # Iterate
    for user in users:
        user_folder_name = f'{user.get_full_name().replace(" ", "_")}_{user.personal_profile.roll_no}'

        # Create folder user
        # Build path for different type
        user_folder_path__internship = os.path.join(internship_folder, user_folder_name)
        user_folder_path__placement = os.path.join(placement_folder, user_folder_name)
        user_folder_path__hackathon = os.path.join(hackathon_folder, user_folder_name)
        user_folder_path__course = os.path.join(course_folder, user_folder_name)
        user_folder_path__docs = os.path.join(other_docs_folder, user_folder_name)

        # Objects
        internships = user.job_profile.filter(type="internship")
        placements = user.job_profile.filter(type="placement")
        hackathons = user.hackathon_profile.all()
        courses = user.online_courses_profile.all()
        docs = user.other_documents.all()


        # Save files
        if len(internships) > 0:
            os.mkdir(user_folder_path__internship)
            for internship in internships:
                internships_dataframe.loc[len(internships_dataframe.index)]  = [user.personal_profile.get_year_display(), user.personal_profile.roll_no, user.get_full_name(), user.email, user.personal_profile.phone_no, internship.company, internship.duration_months, f"{internship.get_month_display()} {internship.year}"]
                shutil.copy(os.path.join(MEDIA_PATH, internship.document),
                            os.path.join(user_folder_path__internship, generate_filename_for_internship(internship)))


        if len(placements) > 0:
            os.mkdir(user_folder_path__placement)
            for placement in placements:
                placement_dataframe.loc[len(placement_dataframe.index)]  = [user.personal_profile.get_year_display(), user.personal_profile.roll_no, user.get_full_name(), user.email, user.personal_profile.phone_no, placement.company, f"{placement.get_month_display()} {placement.year}"]
                shutil.copy(os.path.join(MEDIA_PATH, placement.document),
                            os.path.join(user_folder_path__placement, generate_filename_for_placement(placement)))

        if len(hackathons) > 0:
            os.mkdir(user_folder_path__hackathon)
            for hackathon in hackathons:
                hackathon_dataframe.loc[len(hackathon_dataframe.index)]  = [user.personal_profile.get_year_display(), user.personal_profile.roll_no, user.get_full_name(), user.email, user.personal_profile.phone_no, hackathon.title, hackathon.organizer, hackathon.get_certificate_type_display(), f"{hackathon.get_month_display()} {hackathon.year}"]
                shutil.copy(os.path.join(MEDIA_PATH, hackathon.document),
                            os.path.join(user_folder_path__hackathon, generate_filename_for_hackathon(hackathon)))

        if len(courses) > 0:
            os.mkdir(user_folder_path__course)
            for course in courses:
                course_dataframe.loc[len(course_dataframe.index)] = [user.personal_profile.get_year_display(),
                                                                           user.personal_profile.roll_no,
                                                                           user.get_full_name(), user.email,
                                                                           user.personal_profile.phone_no,
                                                                           course.title, course.issued_by,
                                                                           course.description,
                                                                           f"{course.year}"]
                shutil.copy(os.path.join(MEDIA_PATH, course.document),
                            os.path.join(user_folder_path__course, generate_filename_for_course(course)))

        if len(docs) > 0:
            os.mkdir(user_folder_path__docs)
            for doc in docs:
                other_docs_dataframe.loc[len(other_docs_dataframe.index)] = [user.personal_profile.get_year_display(),
                                                                           user.personal_profile.roll_no,
                                                                           user.get_full_name(), user.email,
                                                                           user.personal_profile.phone_no,
                                                                           doc.title, doc.description]
                shutil.copy(os.path.join(MEDIA_PATH, doc.document),
                            os.path.join(user_folder_path__docs, generate_filename_for_docs(doc)))

    compressedFilePath = os.path.join(os.path.join(BASE_DIR, "reports"), TMP_FOLDER)
    shutil.make_archive(compressedFilePath, "zip", FINAL_PATH, '.')
    # final_file = open(compressedFilePath+".zip", "rb")
    shutil.rmtree(FINAL_PATH)

    # Generate python excel
    report_excel_path = os.path.join(FINAL_PATH, "report.xlsx")
    writer = pd.ExcelWriter(report_excel_path, engine='xlsxwriter')
    internships_dataframe.to_excel(writer, sheet_name="Internship")
    placement_dataframe.to_excel(writer, sheet_name="Placement")
    hackathon_dataframe.to_excel(writer, sheet_name="Hackathon")
    course_dataframe.to_excel(writer, sheet_name="Course")
    other_docs_dataframe.to_excel(writer, sheet_name="Other Docs")
    writer.save()

    return redirect(f"/report/download/?source={TMP_FOLDER}.zip&key={key}")

def download_backup(request):
    key = request.GET["key"]
    if key != SECURITY_KEY_REPORT:
        return HttpResponse("Bye", status=500)
    source = request.GET.get("source", "-1")
    if source == "-1" or source == "":
        return HttpResponse("File not found or you have not accesss", status=404)
    file = open("backup/" + source, "rb")
    time = datetime.now()
    date = time.strftime("%d-%m-%Y")
    return FileResponse(file, as_attachment=True, filename=f"backup_{date}.zip")


def generate_backup(request):
    key = request.GET["key"]
    if key != SECURITY_KEY_REPORT:
        return HttpResponse("Bye", status=500)

    TMP_FOLDER = "tmp_"+str(random.randint(111111111111111111, 999999999999999999))
    FINAL_PATH = os.path.join(BASE_DIR, TMP_FOLDER)
    MEDIA_PATH = os.path.join(BASE_DIR, "media")
    # Delete folder
    if os.path.exists(path=FINAL_PATH):
        shutil.rmtree(FINAL_PATH)
    # Create folder
    os.mkdir(FINAL_PATH)
    # Copy files
    shutil.copytree(MEDIA_PATH, os.path.join(FINAL_PATH, "media"))
    shutil.copyfile(os.path.join(BASE_DIR, "db.sqlite3"), os.path.join(FINAL_PATH, "db.sqlite3"))
    # Compress
    compressedFilePath = os.path.join(os.path.join(BASE_DIR, "backup"), TMP_FOLDER)
    shutil.make_archive(compressedFilePath, "zip", FINAL_PATH, '.')
    # Delete folder
    shutil.rmtree(FINAL_PATH)
    return redirect(f"/backup/download/?source={TMP_FOLDER}.zip&key={key}")
