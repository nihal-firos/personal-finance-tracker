from django import forms
from .models import Transaction, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'date']

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Add Tailwind classes to inputs
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            })

        # Initially empty until type is selected
        self.fields['category'].queryset = Category.objects.none()
        self.fields['category'].empty_label = "Select a category (choose type first)"

        # Check for POST data
        if 'type' in self.data:
            type_value = self.data.get('type')
            self.fields['category'].queryset = Category.objects.filter(type=type_value)
        elif self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(type=self.instance.type)



class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400'})

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            })