import subprocess
import traceback
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from gitthesis.forms import CommentForm
from .models import *
from django.contrib.auth.models import User
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.files.storage import default_storage
import json
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.db import models
from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from django_tex.core import compile_template_to_pdf
from django_tex.shortcuts import render_to_pdf
from django_tex.response import PDFResponse
from django.views.decorators.http import require_POST
import shutil
import time
import logging
from git_thesis.settings import LATEX_INTERPRETER, LATEX_INTERPRETER_OPTIONS


def section_versions(request, section_id):
    # Ambil section berdasarkan ID
    section = Section.objects.get(id=section_id)

    latest_version = SectionVersion.objects.filter(section_id=section_id).order_by('-created_at').first()
    section_versions = SectionVersion.objects.filter(section_id=section_id).exclude(id=latest_version.id).order_by('-created_at')
    
    for version in section_versions:
        # Ambil 10 kata terakhir
        words = version.content.split()  
        last_10_words = ' '.join(words[-5:]) 
        version.short_content = last_10_words

    # Render halaman untuk menampilkan versi-section
    return render(request, 'section_versions.html', {  
        'section': section,
        'section_versions': section_versions
    })

def compare_versions(request, section_id, version_id):
    # Ambil section berdasarkan ID
    section = get_object_or_404(Section, id=section_id)

    # Ambil versi yang dipilih dan versi terbaru
    selected_version = get_object_or_404(SectionVersion, id=version_id, section_id=section_id)
    latest_version = SectionVersion.objects.filter(section_id=section_id).order_by('-created_at').first()

    # Render halaman perbandingan versi
    return render(request, 'compare_versions.html', {
        'section': section,
        'selected_version': selected_version,
        'latest_version': latest_version
    })

def apply_version(request, section_id):
    if request.method == "POST":
        selected_version_id = request.POST.get("selected_version_id")
        section = get_object_or_404(Section, id=section_id)
        selected_version = get_object_or_404(SectionVersion, id=selected_version_id)

        # Update section content and title
        section.title = selected_version.title
        section.content = selected_version.content
        section.save()

        SectionVersion.objects.create(
            section=section,
            title=section.title,
            content=section.content,
            created_at=timezone.now()  
        )

        # Redirect to project detail page
        return redirect('project_detail', project_id=section.project.id)  
    return redirect('compare_versions')


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    images = project.images.all().order_by('-created_at') 
    sections = project.sections.all().order_by('position')
    
    # Mengambil komentar untuk section pertama (atau section aktif)
    section_id = request.GET.get('section_id', sections.first().id)  
    section = get_object_or_404(Section, id=section_id)
    
    # Ambil komentar untuk section yang dipilih
    comments = Comment.objects.filter(section=section).values('id', 'user__username', 'content', 'is_solved')
    form = CommentForm()
    
    section_versions = SectionVersion.objects.filter(section__project=project).order_by('-created_at')[:1]
    
    return render(request, 'project.html', {
        'project': project, 'images': images, 'sections': sections, 'comments' : comments, 'form' : form, 'section_versions': section_versions,})


def home(request):
    
    search_query = request.GET.get('search', '')
    
    projects = Project.objects.filter(
        Q(owner=request.user)
        | Q(collaborator__user=request.user, collaborator__is_accepted=True)
    ).distinct()
    
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |  
            Q(collaborator__user__username__icontains=search_query) 
        ).distinct()

    collaborators = (
        User.objects.filter(
            Q(owned_projects__in=projects)
            | Q(collaborator__project__in=projects, collaborator__is_accepted=True)
        )
        .exclude(id=request.user.id)
        .distinct()
    )

    invitations = Collaborator.objects.filter(user=request.user, is_accepted=False)

    context = {
        "projects": projects,
        "collaborators": collaborators,
        "invitations": invitations,
        "search_query": search_query,
    }

    return render(request, "home.html", context)


def landing(request):

    if request.user.is_authenticated:    
        return redirect("home")
    
    return render(request, "landing.html")

logger = logging.getLogger(__name__)

def generate_pdf(request, file_path):
    try:
        logger.info(f"Starting PDF generation for file: {file_path}")
        
        # Directory for output PDF (media/tex_file)
        pdf_output_dir = os.path.join(settings.MEDIA_ROOT, 'tex_file')
        os.makedirs(pdf_output_dir, exist_ok=True)

        # Copy project_images directory
        images_dir = os.path.join(pdf_output_dir, 'images')
        project_images_dir = os.path.join(settings.MEDIA_ROOT, 'project_images')
        
        # Remove existing images directory if exists
        if os.path.exists(images_dir):
            shutil.rmtree(images_dir)
        
        # Copy the project_images directory
        shutil.copytree(project_images_dir, images_dir)
        logger.info(f"Copied project_images to: {images_dir}")
        
        # Define PDF file name and source path based on the .tex file
        pdf_filename = os.path.basename(file_path).replace('.tex', '.pdf')
        pdf_source_path = os.path.join(os.path.dirname(file_path), pdf_filename)

        logger.info(f"Using LATEX_INTERPRETER: {settings.LATEX_INTERPRETER}")
        logger.info(f"Current working directory: {os.path.dirname(file_path)}")

        # Run pdflatex in the same directory as the .tex file
        process = subprocess.run(
            [settings.LATEX_INTERPRETER, '-interaction=nonstopmode', '-shell-escape', file_path],
            cwd=os.path.dirname(file_path),
            capture_output=True,
            text=True
        )
        
        # Log output for debugging
        logger.error(f"pdflatex stdout: {process.stdout}")
        logger.error(f"pdflatex stderr: {process.stderr}")
        
        # Define the destination path for the PDF
        pdf_dest_path = os.path.join(pdf_output_dir, pdf_filename)

        # Move the generated PDF to media/tex_file if it exists
        if os.path.exists(pdf_source_path):
            shutil.move(pdf_source_path, pdf_dest_path)
            logger.info(f"PDF moved to: {pdf_dest_path}")

            # Create URL for PDF that can be accessed
            pdf_url = request.build_absolute_uri('/media/tex_file/' + pdf_filename)
            return JsonResponse({'pdf_url': pdf_url})  # Return the URL to the PDF
            
        else:
            logger.error(f"PDF file not found at source: {pdf_source_path}")
            return JsonResponse({'error': "PDF generation failed"}, status=500)
            
    except subprocess.CalledProcessError as e:
        logger.error(f"pdflatex error: {e.stderr}")
        return JsonResponse({'error': f"Error generating PDF: {e.stderr}"}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500)


logger = logging.getLogger(__name__)

def create_tex_file(request, project_id):
    if request.method == "POST":
        try:
            latex_contents = request.POST.getlist('latex_content')  # Ambil semua konten dari section
            
            project = get_object_or_404(Project, id=project_id)

            if not latex_contents:
                return JsonResponse({'error': "Konten LaTeX tidak boleh kosong."}, status=400)

            # Gabungkan semua konten menjadi satu string
            combined_latex_content = "\n\n".join(latex_contents)

            # Tambahkan template minimal LaTeX
            if '\\documentclass' not in combined_latex_content:
                combined_latex_content = f""""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{graphicx}}
\\graphicspath{{./images/}}
\\begin{{document}}
{combined_latex_content}
\\end{{document}}
"""""

            # Ensure the tex_file directory exists in media
            tex_dir = os.path.join(settings.MEDIA_ROOT, 'tex_file')
            os.makedirs(tex_dir, exist_ok=True)

            # Hapus file .tex dan .pdf yang ada
            for file in os.listdir(tex_dir):
                file_path = os.path.join(tex_dir, file)
                if file.endswith(('.tex', '.pdf', '.log', '.aux')):
                    os.remove(file_path)

            # Buat nama file unik
            project_name = project.name
            file_name = f'{project_name}_{int(time.time())}.tex'
            full_file_path = os.path.join(tex_dir, file_name)

            # Tulis konten LaTeX ke dalam file .tex
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(combined_latex_content)

            # Generate PDF dan kembalikan URL PDF
            pdf_response = generate_pdf(request, full_file_path)

            return pdf_response  # Kembalikan respons PDF

        except Exception as e:
            logger.error(f"Error in create_tex_file: {str(e)}")
            return JsonResponse({'error': f"Error creating TeX file: {str(e)}"}, status=500)

    return render(request, 'project_detail')



logger = logging.getLogger(__name__)


def generate_combined_pdf(request, project_id):
    logger.info("Starting generate_combined_pdf for project_id: %s", project_id)
    
    # Directory for output PDF (media/tex_file)
    pdf_output_dir = os.path.join(settings.MEDIA_ROOT, 'tex_file')
    os.makedirs(pdf_output_dir, exist_ok=True)

    # Copy project_images directory
    images_dir = os.path.join(pdf_output_dir, 'images')
    project_images_dir = os.path.join(settings.MEDIA_ROOT, 'project_images')
    
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)
    
    try:
        # Log request body for debugging
        logger.debug("Request body: %s", request.body.decode('utf-8'))
        
        # Get project
        project = get_object_or_404(Project, id=project_id)
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
            sections_content = data.get('sections', [])
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", str(e))
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        
        # Validate sections content
        if not sections_content:
            return JsonResponse({"error": "No sections content provided."}, status=400)
    
        
        # Create unique filename
        timestamp = int(time.time())
        filename = f'project_{project_id}_{timestamp}.tex'
        tex_path = os.path.join(settings.MEDIA_ROOT, 'tex_file', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(tex_path), exist_ok=True)
        
        # Create URL for the PDF
        pdf_filename = os.path.basename(tex_path).replace('.tex', '.pdf')
        pdf_url = f'/media/tex_file/{pdf_filename}'
        logger.info("Successfully generated PDF, returning URL: %s", pdf_url)
        return JsonResponse({"pdf_url": pdf_url})
        
    except Exception as e:
        logger.error("Unexpected error in generate_combined_pdf: %s\n%s", str(e), traceback.format_exc())
        return JsonResponse({"error": f"An error occurred during PDF generation: {str(e)}"}, status=500)
    

logger = logging.getLogger(__name__)

@csrf_exempt
def update_section_content(request, project_id, section_id):
    if request.method == "POST":
        logger.info(f"Updating section {section_id} for project {project_id}")
        
        data = json.loads(request.body)
        content = data.get("content", "")
        
        try:
            section = Section.objects.get(id=section_id, project_id=project_id)
            section.content = content
            section.save()
            
            SectionVersion.objects.create(
                section=section,
                title=section.title,  
                content=content,  
            )
            
            logger.info(f"Section {section_id} updated successfully.")
            return JsonResponse({"success": True, "message": "Section updated successfully"})
        except Section.DoesNotExist:
            logger.error(f"Section {section_id} not found for project {project_id}.")
            return JsonResponse({"success": False, "message": "Section not found"}, status=404)
    
    logger.error("Invalid request method.")
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


@csrf_exempt  # Only use this if necessary (for debugging or non-logged in user requests)
def update_section_order(request, project_id):
    try:
        data = json.loads(request.body)
        sections = data.get('sections', [])
        
        for section_data in sections:
            section_id = section_data.get('id')
            new_position = section_data.get('position')
            
            if section_id and new_position:
                section = Section.objects.get(id=section_id)
                section.position = new_position
                section.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    


@login_required
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            section_id = request.POST.get('section_id')
            if section_id:
                comment.section_id = section_id
                comment.user = request.user
                comment.save()

                # Mengembalikan response JSON dengan pesan sukses dan detail komentar
                return JsonResponse({
                    'success': True,
                    'message': "Komentar berhasil ditambahkan!",
                    'comment': {
                        'id': comment.id,
                        'user': comment.user.username,
                        'content': comment.content,
                        'is_solved': comment.is_solved
                    }
                })
            else:
                return JsonResponse({'success': False, 'message': "Section ID tidak valid."})
        else:
            return JsonResponse({'success': False, 'message': "Form tidak valid.", 'errors': form.errors})
    return JsonResponse({'success': False, 'message': "Metode tidak valid."})

    

@require_http_methods(["GET"])
def get_comments(request, section_id):
    try:
        section = get_object_or_404(Section, id=section_id)
        comments = Comment.objects.filter(section=section).select_related('user').order_by('created_at')
        
        comments_data = [{
            'id': comment.id,
            'user': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'is_solved':comment.is_solved
            
        } for comment in comments]
        
        return JsonResponse({
            'status': 'success',
            'comments': comments_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
        

@require_POST
def mark_solved(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.is_solved = True  # Asumsi bahwa field is_solved ada di model Comment
        comment.save()
        return JsonResponse({'status': 'success'})
    except Comment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Komentar tidak ditemukan'})
        


def get_section_versions(request, section_id):
    # Ambil riwayat perubahan untuk section yang dipilih
    section_versions = SectionVersion.objects.filter(section_id=section_id).order_by('-created_at')[:1]

    # Menyiapkan data untuk dikirim sebagai respons JSON
    versions_data = [
        {
            'title': version.title,
            'created_at': version.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for version in section_versions
    ]

    return JsonResponse({'section_versions': versions_data})




@method_decorator(csrf_exempt, name="dispatch")
class AddSectionView(View):
    def post(self, request):
        data = json.loads(request.body)
        title = data.get("title")
        project_id = data.get("project_id")  # Mengambil project_id dari request

        # Validasi input
        if not title:
            return JsonResponse({"success": False, "error": "Title is required"}, status=400)

        if not project_id:
            return JsonResponse({"success": False, "error": "Project ID is required"}, status=400)

        try:
            # Dapatkan objek Project yang sesuai
            project = Project.objects.get(id=project_id)

            # Cari nilai position terbesar pada project tersebut
            max_position = project.sections.aggregate(max_position=models.Max('position'))['max_position']
            print(f"Max position for project {project_id}: {max_position}")  # Debugging log

            if max_position is None:
                max_position = 0  # Jika tidak ada section, mulai dari 0
            else:
                max_position += 1  # Tambah 1 dari nilai position terbesar

            # Buat Section baru dengan position baru
            section = Section.objects.create(project=project, title=title, position=max_position)

            SectionVersion.objects.create(
                section=section,
                title=section.title,
                content=section.content  
            )

            # Mengembalikan ID section yang baru dibuat
            return JsonResponse({"success": True, "section_id": section.id, "position": section.position}, status=201)
        except Project.DoesNotExist:
            return JsonResponse({"success": False, "error": "Project not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
 
        
@method_decorator(csrf_exempt, name="dispatch")
class UpdateSectionTitleView(View):
    def post(self, request, section_id):
        data = json.loads(request.body)
        title = data.get("title")

        try:
            section = Section.objects.get(id=section_id)
            section.title = title
            section.save()

            SectionVersion.objects.create(
                section=section,
                title=section.title,
                content=section.content  
            )
            
            return JsonResponse({"success": True})
        except Section.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Section not found"}, status=404
            )


@csrf_protect 
def upload_image(request, project_id):
    if request.method == "POST":
        # Cek jika project dengan ID yang diberikan ada
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Project not found"}, status=404
            )

        if "image" in request.FILES:
            image = request.FILES["image"]

            # Ambil ekstensi file
            ext = os.path.splitext(image.name)[1]

            # Buat nama file yang unik
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")  # Format timestamp
            unique_filename = f"{project_id}_{timestamp}{ext}"

            # Simpan file image dengan nama unik
            file_name = default_storage.save(f"project_images/{unique_filename}", image)

            # Simpan data ke database
            ProjectImage.objects.create(project=project, image=file_name)

            return JsonResponse(
                {"success": True, "message": "Image uploaded successfully"}
            )
        else:
            return JsonResponse(
                {"success": False, "message": "No image file provided"}, status=400
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=405
    )

@login_required
@require_http_methods(["DELETE"])
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    section.delete()
    return JsonResponse({'status': 'success'}, status=200)


@login_required
@require_http_methods(["DELETE"])
def delete_image(request, image_id):
    # Mencari gambar berdasarkan ID
    image = get_object_or_404(ProjectImage, id=image_id)

    original_image_path = image.image.path
    filename = os.path.basename(original_image_path)

    tex_file_dir = os.path.join(settings.MEDIA_ROOT, 'tex_file')
    symlink_images_dir = os.path.join(tex_file_dir, 'images')
    symlink_image_path = os.path.join(symlink_images_dir, filename)
    
    # Menghapus gambar dari database
    image.delete()
    image_path = image.image.path
    if os.path.exists(image_path):
        os.remove(image_path)

    if os.path.exists(symlink_image_path):
            os.remove(symlink_image_path)
            logger.info(f"Deleted symlink/copied image: {symlink_image_path}")
    
    # Mengembalikan respons sukses
    return JsonResponse({'status': 'success'}, status=200)


@login_required
def profile(request):
    projects = Project.objects.filter(owner=request.user)[:3]
    Contributedprojects = Project.objects.filter(collaborators=request.user).exclude(owner=request.user)[:3]

    all_projects = Project.objects.filter(owner=request.user)
    all_contributed_projects = Project.objects.filter(collaborators=request.user)

    projectcount = all_projects.union(all_contributed_projects).count()

    networks = (
    User.objects.filter(
        Q(owned_projects__in=projects) & Q(collaborator__is_accepted=True)  # Pemilik proyek yang menerima user sebagai collaborator
        | Q(collaborator__project__in=projects, collaborator__is_accepted=True)  # Kolaborator di proyek user
    )
    .exclude(id=request.user.id)  # Mengecualikan user auth
    .distinct()
    )

    networks = (
        User.objects.filter(
            Q(projects__collaborator__project__in=all_projects)
            | Q(
                collaborator__project__in=all_contributed_projects,
                collaborator__is_accepted=True,
            )
        )
        .exclude(id=request.user.id)
        .distinct()
    )

    networkscount = networks.count()

    return render(
        request,
        "profile.html",
        {
            "user": request.user,
            "projects": projects,
            "contributedprojects": Contributedprojects,
            "projectcount": projectcount,
            "networkscount": networkscount,
        },
    )


@login_required
def upload_profile_image(request):
    if request.method == "POST":
        # Check if the user has a UserProfile instance
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Get the uploaded file from the request
        profile_picture = request.FILES.get("profile_picture")

        if profile_picture:
            # Check if there is an existing profile picture and delete it
            if user_profile.profile_picture:
                # Construct the full file path
                old_picture_path = os.path.join(
                    settings.MEDIA_ROOT, str(user_profile.profile_picture)
                )
                if os.path.isfile(old_picture_path):
                    os.remove(old_picture_path)  # Delete the old profile picture

            # Update the profile picture
            user_profile.profile_picture = profile_picture
            user_profile.save()
            messages.success(request, "Profile picture updated successfully!")
        else:
            messages.error(
                request, "No image selected. Please choose an image to upload."
            )

        return redirect("profile")

    return render(request, "profile.html")


def myprojects(request):
    search_query = request.GET.get('search', '')

    projects = Project.objects.filter(
        Q(owner=request.user) | 
        Q(collaborator__user=request.user, collaborator__is_accepted=True)
    ).distinct()

    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | 
            Q(collaborator__user__username__icontains=search_query)
        ).distinct()

    filter_option = request.GET.get("filter", "all")
    if filter_option == "mine":
        projects = projects.filter(owner=request.user)
    elif filter_option == "collaborating":
        projects = projects.filter(collaborator__user=request.user)

    order_option = request.GET.get("order", "latest")
    if order_option == "latest":
        projects = projects.order_by("-created_at")
    else:
        projects = projects.order_by("created_at")

    return render(request, "myprojects.html", {"projects": projects, "search_query": search_query})


@login_required
def inbox(request):
    invitations = Collaborator.objects.filter(user=request.user, is_accepted=False)

    return render(
        request,
        "inbox.html",
        {
            "invitations": invitations,
        },
    )


@login_required
def accept_invitation(request, invitation_id):
    try:
        invitation = Collaborator.objects.get(
            id=invitation_id, user=request.user, is_accepted=False
        )
        invitation.is_accepted = True
        invitation.save()
        messages.success(request, "Invitation accepted!")
    except Collaborator.DoesNotExist:
        messages.error(request, "Invitation not found or already accepted.")

    return redirect("inbox")


@login_required
def reject_invitation(request, invitation_id):
    try:
        invitation = Collaborator.objects.get(id=invitation_id, user=request.user)
        invitation.delete()
        messages.success(request, "Invitation rejected successfully.")
    except Collaborator.DoesNotExist:
        messages.error(
            request, "Invitation not found or you don't have permission to reject it."
        )

    return redirect("inbox")


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        return HttpResponseForbidden("You are not allowed to delete this project.")

    project.delete()
    messages.success(request, "Project has been deleted successfully.")

    return redirect("myprojects")


@login_required
def project_settings(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        return HttpResponseForbidden("You are not allowed to edit this project.")

    if request.method == "POST":
        collaborators_emails = request.POST.get("collaborators")
        if collaborators_emails:
            emails = [email.strip() for email in collaborators_emails.split(",")]

            current_collaborators = project.collaborator_set.all()
            current_collaborator_emails = current_collaborators.values_list(
                "user__email", flat=True
            )

            for collaborator in current_collaborators:
                if not collaborator.is_accepted:
                    collaborator.delete()

            if request.user not in [c.user for c in current_collaborators]:
                Collaborator.objects.create(
                    project=project,
                    user=request.user,
                    invited_at=timezone.now(),
                    is_accepted=True,
                )

            for email in emails:
                if email in current_collaborator_emails:
                    messages.warning(
                        request, f"User with email '{email}' already has an invitation."
                    )
                    continue

                try:
                    user = User.objects.get(email=email)
                    if user != request.user:
                        if user.email not in current_collaborator_emails:
                            Collaborator.objects.create(
                                project=project,
                                user=user,
                                invited_at=timezone.now(),
                                is_accepted=False,
                            )
                        else:
                            messages.warning(
                                request,
                                f"User with email '{email}' is already a collaborator.",
                            )
                    else:
                        messages.warning(
                            request, "You cannot invite yourself as a collaborator."
                        )
                except User.DoesNotExist:
                    messages.warning(
                        request, f"User with email '{email}' does not exist."
                    )

        messages.success(request, "Collaborators updated successfully!")
        return redirect("project_settings", project_id=project.id)

    all_collaborators = project.collaborator_set.all()
    collaboratorsAccepted = all_collaborators.filter(is_accepted=True)

    return render(
        request,
        "project_settings.html",
        {
            "project": project,
            "all_collaborators": all_collaborators,
            "collaboratorsAccepted": collaboratorsAccepted,
        },
    )


@login_required
def remove_collaborator(request, project_id, collaborator_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        return HttpResponseForbidden(
            "You are not allowed to remove collaborators from this project."
        )

    try:
        collaborator = Collaborator.objects.get(
            id=collaborator_id, project=project, is_accepted=True
        )

        if collaborator.user == project.owner:
            messages.error(request, "You cannot remove the project owner.")
            return redirect("project_settings", project_id=project.id)

        collaborator.delete()

        messages.success(
            request,
            f"Collaborator {collaborator.user.username} has been removed successfully.",
        )
    except Collaborator.DoesNotExist:
        messages.error(
            request,
            "Collaborator not found or they haven't accepted the invitation yet.",
        )

    return redirect("project_settings", project_id=project.id)


@login_required
def notifications_count(request):
    if request.user.is_authenticated:
        count = Collaborator.objects.filter(
            user=request.user, is_accepted=False
        ).count()
        return {"invitations_count": count}
    return {"invitations_count": 0}


@login_required
def create_project(request):
    if request.method == "POST":
        project_name = request.POST.get("projectName")
        collaborator_emails = request.POST.get("collaborators")

        if not project_name:
            messages.error(request, "Project name is required.")
            return render(
                request,
                "createproject.html",
                {"messages": messages.get_messages(request)},
            )

        if len(project_name) > 255:
            messages.error(request, "Project name cannot exceed 255 characters.")
            return render(
                request,
                "createproject.html",
                {"messages": messages.get_messages(request)},
            )

        project = Project.objects.create(
            name=project_name,
            owner=request.user,
            created_at=timezone.now(),
        )

        Collaborator.objects.create(
            project=project,
            user=request.user,
            invited_at=timezone.now(),
            is_accepted=True,
        )

        if collaborator_emails:
            emails = collaborator_emails.split(",")
            for email in emails:
                email = email.strip()
                try:
                    user = User.objects.get(email=email)
                    if user != request.user:
                        Collaborator.objects.create(
                            project=project,
                            user=user,
                            invited_at=timezone.now(),
                            is_accepted=False,
                        )
                    else:
                        messages.warning(
                            request, "You cannot invite yourself as a collaborator."
                        )
                except User.DoesNotExist:
                    messages.warning(
                        request, f"User with email '{email}' does not exist."
                    )

        messages.success(
            request, "Project created successfully! Invitations sent to collaborators."
        )
        return redirect("create_project")

    return render(request, "createproject.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = {}

        # Validasi username
        if not username:
            errors["username"] = "Username is required"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists"

        # Validasi email
        if not email:
            errors["email"] = "Email is required"
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors["email"] = "Email already exists"
            except ValidationError:
                errors["email"] = "Enter a valid email address"

        # Validasi password
        if not password1 or not password2:
            errors["password"] = "Password is required"
        elif password1 != password2:
            errors["password"] = "Passwords do not match"
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                errors["password"] = list(e.messages)

        if errors:
            return JsonResponse({"success": False, "error": errors})

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password1),
        )

        return JsonResponse({"success": True})

    return render(request, "landing.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "error": "Invalid username or password."}
            )

    return render(request, "landing.html")


def custom_logout(request):
    logout(request)
    return redirect("landing")