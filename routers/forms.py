"""
Forms for router management.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div
from .models import Router


class RouterForm(forms.ModelForm):
    """
    Form for creating and updating routers.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Router admin password"
    )
    
    class Meta:
        model = Router
        fields = ['name', 'description', 'vpn_ip', 'api_port', 'username', 'password', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Router1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vpn_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10.10.0.2'}),
            'api_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'admin'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('vpn_ip', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('password', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('api_port', css_class='form-group col-md-6 mb-3'),
                Column('is_active', css_class='form-group col-md-6 mb-3'),
            ),
            'description',
            Div(
                Submit('submit', 'Save Router', css_class='btn btn-primary'),
                css_class='text-right mt-3'
            )
        )


class RouterTestForm(forms.Form):
    """
    Form for testing router connection.
    """
    router_id = forms.UUIDField(widget=forms.HiddenInput())

