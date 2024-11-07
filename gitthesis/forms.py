from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Hanya ambil field content untuk form
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tulis komentar di sini...',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        # Misalnya, Anda dapat menambahkan atribut tambahan atau melakukan penyesuaian lainnya di sini
        self.fields['content'].label = 'Komentar' 
