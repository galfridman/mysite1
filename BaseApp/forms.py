from django.forms import Select
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget
import pytz

__author__ = 'Gal'
from . import models as m
from django import forms
import datetime
from django.forms import widgets


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First name')
    last_name = forms.CharField(max_length=30, label='Last name')
    info = forms.CharField(max_length=30, label='info')

    def signup(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        profile = m.AppUser()
        profile.user = user
        profile.info = self.cleaned_data['info']
        profile.save()
        user.profile = profile
        user.save()


class AppUserForm(forms.ModelForm):
    class Meta:
        model = m.AppUser
        fields = [
            'birthdate',
            'image',
            'gender',
        ]
        widgets = {
        }


class BusinessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })
        self.fields['image'].widget.attrs.update({
            'required': False
        })

    class Meta:
        model = m.Business
        fields = [
            'name',
            'description',
            'category',
            'image',
            'email',
        ]
        widgets = {
        }


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Post content',
            'required': True,
        })
        self.fields['audience'].widget.attrs.update({
            'class': 'form-control',
        })

    class Meta:
        model = m.BasePost
        fields = [
            'text',
            'is_important',
            'audience',
        ]
        widgets = {
        }


class CatalogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })

    class Meta:
        model = m.Catalog
        fields = [
            'name',
            'description',
            'image',
        ]
        widgets = {
        }


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })

    class Meta:
        model = m.Item
        fields = [
            'name',
            'description',
            'image',
            'is_available',
            'price',
        ]
        widgets = {
        }


class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })

    class Meta:
        model = m.Service
        fields = [
            'name',
            'description',
            'image',
            'duration',
            'price',
        ]
        widgets = {
        }


class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })
        self.fields['street_name'].widget.attrs.update({
            'id': 'route'
        })
        self.fields['street_number'].widget.attrs.update({
            'id': 'street_number'
        })
        self.fields['state'].widget.attrs.update({
            'id': 'administrative_area_level_1'
        })
        self.fields['zip_code'].widget.attrs.update({
            'id': 'postal_code'
        })
        self.fields['country'].widget.attrs.update({
            'id': 'country'
        })
        self.fields['city'].widget.attrs.update({
            'id': 'locality'
        })

    class Meta:
        model = m.Address
        fields = [
            'street_name',
            'street_number',
            'city',
            'state',
            'zip_code',
            'country',
        ]
        widgets = {
        }


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })
        self.fields['phone'].widget.attrs.update({
            'data-inputmask': '"mask": "(999) 999-9999"',
            'data-mask': True,
        })
        self.fields['picking_time'].widget.attrs.update({
            'class': 'form-control timepicker',
            'required': False,

        })

    class Meta:
        model = m.Order
        fields = [
            'type',
            'picking_time',
            'phone',
        ]

        widgets = {
            # 'picking_time': forms.TextInput(attrs={'class': 'timepicker'})
        }


class DisputeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })

    class Meta:
        model = m.Dispute
        fields = [
            'topic',
            'description',
        ]


class BaseBenefitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                # 'placeholder': field,
                'required': True,
            })
        self.fields['starting_date'].widget.attrs.update({
            # 'class': 'form-control',
            'type': "date"
        })
        self.fields['ending_date'].widget.attrs.update({
            # 'class': 'form-control',
            'type': 'date',
        })

    class Meta:
        model = m.BaseBenefit
        fields = [
            'title',
            'text',
            'starting_date',
            'ending_date',
            'type',
        ]

    def clean_starting_date(self):
        date = self.cleaned_data['starting_date']
        utc = pytz.UTC
        date_now = utc.localize(datetime.datetime.today())
        if date < date_now:
            raise forms.ValidationError("The date cannot be in the past!")
        return date

    def clean_ending_date(self):
        starting_date = self.cleaned_data['starting_date']
        date = self.cleaned_data['ending_date']
        if date < starting_date:
            raise forms.ValidationError("The ending date cannot be lower then the starting date!")
        return date


class TicketBenefitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
                'id': field,
            })

    class Meta:
        model = m.TicketBenefit
        fields = [
            'required_punches',
            'reward_type',
        ]


class FriendBenefitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
                'id': field,
            })

    class Meta:
        model = m.FriendBenefit
        fields = [
            'required_friends',
            'reward_type',
        ]


class DiscountBenefitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'rows': '1',
                'placeholder': field,
                'required': True,
            })

    class Meta:
        model = m.DiscountBenefit
        fields = [
            'discount_type',
            'discount_percentage',
        ]

