from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .models import Article, Category, Tag, BugReport

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    """Форма для обновления профиля с валидацией уникальности и полей"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'nickname']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text=_("Select relevant tags for this article.")
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'excerpt', 'content',
            'meta_description', 'meta_keywords',
            'featured_image', 'featured_image_alt',
            'category', 'tags', 'is_featured', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter article title')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL slug (auto-generated from title)')
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Brief description of the article')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'id': 'id_content_editor'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SEO meta description (max 160 characters)')
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SEO keywords separated by commas')
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured_image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Alt text for featured image')
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
        # Make slug field optional for creation
        self.fields['slug'].required = False
        
        # Hide publication controls for non-content managers
        if self.user and not (self.user.is_superuser or 
                            self.user.roles.filter(scope='content').exists()):
            # Remove fields that only content managers should see
            if 'is_featured' in self.fields:
                del self.fields['is_featured']
            if 'order' in self.fields:
                del self.fields['order']
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        # Auto-generate slug from title if not provided
        if not slug and title:
            slug = slugify(title)
        
        # Check for uniqueness, excluding current instance
        if slug:
            qs = Article.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_('Article with this slug already exists.'))
        
        return slug
    
    def clean_meta_description(self):
        meta_description = self.cleaned_data.get('meta_description')
        if meta_description and len(meta_description) > 160:
            raise forms.ValidationError(_('Meta description must be 160 characters or less.'))
        return meta_description


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Category name')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL slug (auto-generated from name)')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Category description')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#007bff'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        if slug:
            qs = Category.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_('Category with this slug already exists.'))
        
        return slug


class TagForm(forms.ModelForm):
    """Form for creating and editing tags."""
    
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tag name')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL slug (auto-generated from name)')
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        if slug:
            qs = Tag.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_('Tag with this slug already exists.'))
        
        return slug


class ArticleSearchForm(forms.Form):
    """Form for searching articles."""
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles...'),
            'type': 'search'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_('All categories'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label=_('All tags'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    published_only = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=_('Published articles only')
    )


class ArticlePublishForm(forms.Form):
    """Simple form for publishing/unpublishing articles."""
    
    action = forms.ChoiceField(
        choices=[
            ('publish', _('Publish')),
            ('unpublish', _('Unpublish'))
        ],
        widget=forms.HiddenInput()
    )

class BugReportForm(forms.ModelForm):
    class Meta:
        model = BugReport
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Кратко опишите проблему'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Подробное описание'}),
        }