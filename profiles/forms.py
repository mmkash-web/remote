"""
Forms for profile management.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field
from .models import Profile


class ProfileForm(forms.ModelForm):
    """
    Form for creating and updating profiles.
    """
    class Meta:
        model = Profile
        fields = [
            'name', 'description', 'download_speed', 'upload_speed',
            'data_limit_mb', 'duration_value', 'duration_unit',
            'price', 'currency', 'is_active', 'is_public'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1GB Daily'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'download_speed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5M'}),
            'upload_speed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5M'}),
            'data_limit_mb': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Leave empty for unlimited'}),
            'duration_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_unit': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'KES'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8 mb-3'),
                Column('currency', css_class='form-group col-md-4 mb-3'),
            ),
            'description',
            Row(
                Column('download_speed', css_class='form-group col-md-6 mb-3'),
                Column('upload_speed', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('data_limit_mb', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('duration_value', css_class='form-group col-md-6 mb-3'),
                Column('duration_unit', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('price', css_class='form-group col-md-6 mb-3'),
                Column(
                    Field('is_active', wrapper_class='form-check'),
                    Field('is_public', wrapper_class='form-check'),
                    css_class='form-group col-md-6 mb-3'
                ),
            ),
            Div(
                Submit('submit', 'Save Profile', css_class='btn btn-primary'),
                css_class='text-right mt-3'
            )
        )

