from difflib import SequenceMatcher
import logging
from venv import logger
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
    content = models.TextField(default="", null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['position']

    def save_new_version(self, user=None):
        """
        Save changes as a new version in the SectionVersion model.
        """
        
        if not user:
            raise ValueError("User must be provided when saving a new version.")
        
        self.save()
            
        new_version = SectionVersion.objects.create(
            section=self,
            title=self.title, 
            content=self.content,
            updated_by=user
        )
        print(f"New version created with content: {self.content}")
        
        # Tandai untuk melewati perhitungan kontribusi
        new_version._skip_contribution_calculation = True
        new_version.save()  # Menyimpan versi baru tanpa menghitung kontribusi

        if self.get_history().count() > 1:
            previous_version = self.get_history()[1]  # Ambil versi sebelumnya
            print(f"Previous version content: {previous_version.content}")
            new_version.calculate_contribution(previous_version)  # Hitung kontribusi berdasarkan versi sebelumnya
        
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


logger = logging.getLogger(__name__)

class SectionVersion(models.Model):
    section = models.ForeignKey(
        "Section", on_delete=models.CASCADE, related_name="versions"
    )
    title = models.CharField(max_length=255, default="Untitled Section")
    content = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="versions_updated", null=True
    )
    characters_added = models.IntegerField(default=0)
    characters_removed = models.IntegerField(default=0)

    def calculate_contribution(self, previous_version):
        if previous_version:
            print(f"Calculating contribution between {previous_version.id} and {self.id}")
        else:
            print("Previous version is None, skipping calculation.")
            
        previous_content = previous_version.content or ""
        current_content = self.content or ""

        print(f"Previous content length: {len(previous_content)}")
        print(f"Current content length: {len(current_content)}")
        
        added = 0 
        removed = 0

        matcher = SequenceMatcher(None, previous_content, current_content)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            print(f"Tag: {tag}, Previous: {previous_content[i1:i2]}, Current: {current_content[j1:j2]}")
            if tag == "insert":
                added += len(current_content[j1:j2])
            elif tag == "delete":
                removed += len(previous_content[i1:i2])

        self.characters_added = added
        self.characters_removed = removed

        print(f"Final Added: {self.characters_added}, Final Removed: {self.characters_removed}")

        
    def save(self, *args, **kwargs):
        logger.debug(f"Saving SectionVersion: {self.pk}")  # Ini log yang ada
        logger.debug(f"SectionVersion ID: {self.id}")  # Tambahkan log ini untuk memeriksa ID
        
        skip_contribution_calculation = getattr(self, '_skip_contribution_calculation', False)

        if not skip_contribution_calculation:
            if self.pk and self.section.versions.exists():
                previous_version = self.section.versions.exclude(pk=self.pk).order_by("-created_at").first()
                if previous_version:
                    self.calculate_contribution(previous_version)
                else:
                    print("No previous version to calculate contribution.")
        
        if hasattr(self, '_skip_contribution_calculation'):
            del self._skip_contribution_calculation

        super().save(*args, **kwargs) 



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
    is_solved = models.BooleanField(default=False)
    solved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="solved_comments")
    solved_at = models.DateTimeField(null=True, blank=True)

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
            section = Section.objects.create(
                project=instance,
                title=section_data["title"],
                content=section_data["content"],
                position=position
            )
            position += 1  

            section_version= SectionVersion.objects.create(
                section=section,
                title=section.title,
                content=section.content,
                created_at=timezone.now()
            )
            
            previous_version = SectionVersion.objects.filter(section=section).exclude(id=section_version.id).order_by('-created_at').first()
            if previous_version:
                section_version.calculate_contribution(previous_version)

        # Anda bisa menambahkan log jika perlu untuk memastikan bahwa section dan version telah dibuat
        print(f"Default sections created for project {instance.id}")
