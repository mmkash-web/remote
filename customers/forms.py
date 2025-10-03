"""
Forms for customer management.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field
from .models import Customer
from routers.models import Router
from profiles.models import Profile


class CustomerForm(forms.ModelForm):
    """
    Form for creating and updating customers.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Customer login password"
    )
    
    class Meta:
        model = Customer
        fields = [
            'username', 'password', 'full_name', 'email', 'phone_number',
            'router', 'profile', 'notes', 'send_notifications'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'customer1'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254712345678'}),
            'router': forms.Select(attrs={'class': 'form-control'}),
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'send_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to show only active routers and profiles
        self.fields['router'].queryset = Router.objects.filter(is_active=True)
        self.fields['profile'].queryset = Profile.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('password', css_class='form-group col-md-6 mb-3'),
            ),
            'full_name',
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('router', css_class='form-group col-md-6 mb-3'),
                Column('profile', css_class='form-group col-md-6 mb-3'),
            ),
            'notes',
            Field('send_notifications', wrapper_class='form-check'),
            Div(
                Submit('submit', 'Save Customer', css_class='btn btn-primary'),
                css_class='text-right mt-3'
            )
        )


class CustomerQuickEditForm(forms.ModelForm):
    """
    Quick edit form for common customer updates.
    """
    class Meta:
        model = Customer
        fields = ['profile', 'is_active', 'notes']
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile'].queryset = Profile.objects.filter(is_active=True)


class CustomerExtendForm(forms.Form):
    """
    Form for extending customer subscription.
    """
    EXTEND_OPTIONS = [
        ('profile', 'Use profile duration'),
        ('custom', 'Custom duration'),
    ]
    
    extend_option = forms.ChoiceField(
        choices=EXTEND_OPTIONS,
        widget=forms.RadioSelect,
        initial='profile'
    )
    custom_days = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of days'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        extend_option = cleaned_data.get('extend_option')
        custom_days = cleaned_data.get('custom_days')
        
        if extend_option == 'custom' and not custom_days:
            raise forms.ValidationError("Please specify the number of days for custom extension.")
        
        return cleaned_data

