from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Review, ReviewImage


class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews with rating."""
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    title = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Give your review a title (e.g., "Amazing product!")',
            'id': 'review-title',
        })
    )
    
    comment = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your detailed experience with this product...',
            'rows': 5,
            'id': 'review-comment',
        })
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
    
    def clean_rating(self):
        """Validate that rating is between 1 and 5."""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Please select a rating between 1 and 5 stars.')
        if not rating:
            raise forms.ValidationError('Please select at least one star rating.')
        return rating
    
    def clean_title(self):
        """Validate title is not empty."""
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError('Please provide a review title.')
        if len(title.strip()) < 5:
            raise forms.ValidationError('Review title must be at least 5 characters long.')
        return title.strip()
    
    def clean_comment(self):
        """Validate comment is substantive."""
        comment = self.cleaned_data.get('comment')
        if not comment or not comment.strip():
            raise forms.ValidationError('Please write a review.')
        if len(comment.strip()) < 20:
            raise forms.ValidationError('Review must be at least 20 characters long.')
        return comment.strip()


class ReviewImageForm(forms.ModelForm):
    """Form for uploading review images."""
    
    class Meta:
        model = ReviewImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)',
                'maxlength': '200'
            })
        }
