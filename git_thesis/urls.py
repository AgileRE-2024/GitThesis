from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from gitthesis import views
from gitthesis.views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("home/", home, name="home"),
    path('profile/', views.profile, name='profile'),
    path("myprojects/", myprojects, name='myprojects'),
    path('myprojects/project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('myprojects/section-versions/<int:section_id>/', views.section_versions, name='section_versions'),
    path('myprojects/compare-versions/<int:section_id>/<int:version_id>/', views.compare_versions, name='compare_versions'),
    path('apply_version/<int:section_id>/', views.apply_version, name='apply_version'),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", custom_logout, name="logout"),
    path("myprojects/createnewproject/", create_project, name="create_project"),
    path("myprojects/project/<int:project_id>/settings/", project_settings, name="project_settings"),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('inbox/', inbox, name='inbox'),
    path('accept_invitation/<int:invitation_id>/', accept_invitation, name='accept_invitation'),
    path('reject_invitation/<int:invitation_id>/', reject_invitation, name='reject_invitation'),
    path('project/<int:project_id>/remove-collaborator/<int:collaborator_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('upload-profile-image/', upload_profile_image, name='upload_profile_image'),
    path('project/<int:project_id>/upload_image/', upload_image, name='upload_image'),
    path('update-section-title/<int:section_id>/', UpdateSectionTitleView.as_view(), name='update_section_title'),
    path('add-section/', AddSectionView.as_view(), name='add_section'),
    path('delete-section/<int:section_id>/', views.delete_section, name='delete_section'),
    path('project/<int:project_id>/update-section-order/', update_section_order, name='update_section_order'),
    path('project/<int:project_id>/update-section/<int:section_id>/', update_section_content, name='update_section_content'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('create-tex/<int:project_id>/', views.create_tex_file, name='create_tex_project'),
    path('project/<int:project_id>/generate-combined-pdf/', views.generate_combined_pdf, name='generate_combined_pdf'),
    path('myprojects/add_comment/', views.add_comment, name='add_comment'),
    path('myprojects/get_comments/<int:section_id>/', views.get_comments, name='get_comments'),
    path('get_section_versions/<int:section_id>/', views.get_section_versions, name='get_section_versions'),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
