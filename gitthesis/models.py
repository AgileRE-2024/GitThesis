from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Project(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_projects"
    )
    collaborators = models.ManyToManyField(
        User,
        through="Collaborator",
        related_name="projects",
    )

    def get_all_sections_content(self):
        """
        Mengambil konten dari semua section dalam proyek ini.
        """
        sections = self.sections.all()
        combined_content = "\n\n".join([section.content for section in sections])
        return combined_content

    def __str__(self):
        return f"{self.name} (Updated: {self.updated_at})"


class Section(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=255, default="Untitled Section") 
    content = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        ordering = ['position']

    def save_new_version(self):
        """
        Save changes as a new version in the SectionVersion model.
        """
        new_version = SectionVersion.objects.create(
            section=self,
            title=self.title, 
            content=self.content,
        )
        return new_version

    def get_history(self):
        """
        Retrieve the entire history of changes for this section.
        """
        return SectionVersion.objects.filter(section=self).order_by("-created_at")

    def apply_version(self, version_id):
        """
        Apply a previous version to the current section and save it as a new version.
        """
        try:
            old_version = SectionVersion.objects.get(id=version_id, section=self)
            # Apply the old version's content
            self.content = old_version.content
            # Save this as a new version
            self.save_new_version()
            # Save section with updated content
            self.save()

            # Update the project updated_at timestamp
            self.project.updated_at = timezone.now()
            self.project.save()

            return True
        except SectionVersion.DoesNotExist:
            return False

    def __str__(self):
        return f"Section of {self.project.name} (Created: {self.created_at})"


class SectionVersion(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="versions"
    )
    title = models.CharField(max_length=255, default="Untitled Section")
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Version of Section {self.section.id} (Created: {self.created_at})"


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="project_images/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for {self.project.name} (Uploaded: {self.created_at})"


class Collaborator(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} on {self.project.name} (Accepted: {self.is_accepted})"


class Comment(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on Section {self.section.id} (Created: {self.created_at})"


class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=Project)
def create_default_sections(sender, instance, created, **kwargs):
    if created:
        # Buat section default
        sections = [
            {"title": "Cover", "content": r"""\documentclass{article}
\usepackage{graphicx}
\graphicspath{{./images/}}
\title{Project Document}

\begin{document}
\maketitle
"""}, 
            {"title": "Kata Pengantar", "content": "Ini adalah kata pengantar"},
            {"title": "Bab 1: Pendahuluan", "content": "Ini adalah bab pendahuluan"},
            {"title": "Bab 2: Tinjauan Pustaka", "content": "Ini adalah tinjauan pustaka"},
            {"title": "Bab 3: Metodologi", "content": "Ini adalah metodologi penelitian"},
            {"title": "Bab 4: Pembahasan", "content": "Ini adalah pembahasan"},
            {"title": "Kesimpulan dan Saran", "content": "\end{document}"},
        ]

        # Mengatur posisi awal
        position = 0

        # Buat setiap section dengan position bertambah secara otomatis
        for section_data in sections:
            Section.objects.create(
                project=instance,
                title=section_data["title"],
                content=section_data["content"],
                position=position
            )
            position += 1  # Naikkan posisi untuk section berikutnya
