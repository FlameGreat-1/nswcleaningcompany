  from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from .validators import (
    validate_quote_status_transition, validate_postcode, validate_phone_number,
    validate_ndis_participant_number, validate_file_size, validate_file_type,
    validate_quote_pricing, validate_urgency_level, validate_room_count
)
from .utils import calculate_quote_pricing, validate_quote_data
from services.models import Service, ServiceAddOn

User = get_user_model()


class QuoteForm(forms.ModelForm):
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        help_text="Select your preferred service date"
    )
    
    preferred_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False,
        help_text="Select your preferred service time"
    )
    
    class Meta:
        model = Quote
        fields = [
            'service', 'cleaning_type', 'property_address', 'suburb', 
            'postcode', 'state', 'number_of_rooms', 'square_meters',
            'urgency_level', 'preferred_date', 'preferred_time',
            'special_requirements', 'access_instructions'
        ]
        
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'cleaning_type': forms.Select(attrs={'class': 'form-control'}),
            'property_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter property address'}),
            'suburb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter suburb'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter postcode'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'number_of_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'square_meters': forms.NumberInput(attrs={'class': 'form-control', 'min': '10', 'max': '10000'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'access_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        
        if self.user and not self.user.is_staff:
            self.fields['service'].queryset = self.fields['service'].queryset.filter(
                is_public=True
            )
    
    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if postcode:
            validate_postcode(postcode)
        return postcode
    
    def clean_number_of_rooms(self):
        rooms = self.cleaned_data.get('number_of_rooms')
        if rooms:
            validate_room_count(rooms)
        return rooms
    
    def clean_urgency_level(self):
        urgency = self.cleaned_data.get('urgency_level')
        if urgency:
            validate_urgency_level(urgency)
        return urgency
    
    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < timezone.now().date():
            raise ValidationError("Preferred date cannot be in the past")
        return preferred_date
    
    def clean(self):
        cleaned_data = super().clean()
        
        validation_errors = validate_quote_data(cleaned_data)
        if validation_errors:
            for error in validation_errors:
                self.add_error(None, error)
        
        return cleaned_data


class NDISQuoteForm(QuoteForm):
    ndis_participant_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter NDIS participant number'}),
        help_text="Enter your NDIS participant number"
    )
    
    plan_manager_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan manager name'})
    )
    
    plan_manager_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan manager contact'})
    )
    
    support_coordinator_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Support coordinator name'})
    )
    
    support_coordinator_contact = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Support coordinator contact'})
    )
    
    class Meta(QuoteForm.Meta):
        fields = QuoteForm.Meta.fields + [
            'ndis_participant_number', 'plan_manager_name', 'plan_manager_contact',
            'support_coordinator_name', 'support_coordinator_contact'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ndis_participant_number'].required = True
    
    def clean_ndis_participant_number(self):
        participant_number = self.cleaned_data.get('ndis_participant_number')
        if participant_number:
            validate_ndis_participant_number(participant_number)
        return participant_number
    
    def clean_plan_manager_contact(self):
        contact = self.cleaned_data.get('plan_manager_contact')
        if contact:
            validate_phone_number(contact)
        return contact
    
    def clean_support_coordinator_contact(self):
        contact = self.cleaned_data.get('support_coordinator_contact')
        if contact:
            validate_phone_number(contact)
        return contact


class QuoteUpdateForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            'cleaning_type', 'property_address', 'suburb', 'postcode', 'state',
            'number_of_rooms', 'square_meters', 'urgency_level', 'preferred_date',
            'preferred_time', 'special_requirements', 'access_instructions'
        ]
        
        widgets = {
            'cleaning_type': forms.Select(attrs={'class': 'form-control'}),
            'property_address': forms.TextInput(attrs={'class': 'form-control'}),
            'suburb': forms.TextInput(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'number_of_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'square_meters': forms.NumberInput(attrs={'class': 'form-control', 'min': '10', 'max': '10000'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'preferred_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'special_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'access_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.status not in ['draft', 'submitted']:
            for field in self.fields:
                self.fields[field].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.instance and self.instance.status not in ['draft', 'submitted']:
            raise ValidationError("Cannot update quote with current status")
        
        return cleaned_data


class QuoteStatusForm(forms.ModelForm):
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Required when rejecting a quote"
    )
    
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Internal notes for staff"
    )
    
    class Meta:
        model = Quote
        fields = ['status', 'assigned_to', 'rejection_reason', 'admin_notes']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_staff=True, is_active=True
        )
        
        if self.instance:
            current_status = self.instance.status
            valid_transitions = self.get_valid_status_transitions(current_status)
            
            self.fields['status'].choices = [
                (status, label) for status, label in Quote.STATUS_CHOICES
                if status in valid_transitions
            ]
    
    def get_valid_status_transitions(self, current_status):
        transitions = {
            'draft': ['submitted'],
            'submitted': ['under_review', 'rejected'],
            'under_review': ['approved', 'rejected'],
            'approved': ['converted', 'expired', 'cancelled'],
            'rejected': [],
            'expired': [],
            'converted': [],
            'cancelled': []
        }
        return transitions.get(current_status, [])
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'rejected' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting a quote")
        
        if self.instance:
            try:
                validate_quote_status_transition(self.instance.status, status, self.user)
            except ValidationError as e:
                raise ValidationError(str(e))
        
        return cleaned_data


class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = [
            'service', 'addon', 'item_type', 'name', 'description',
            'quantity', 'unit_price', 'is_optional', 'is_taxable', 'display_order'
        ]
        
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'addon': forms.Select(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'is_optional': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }
    
    def __init__(self, *args, **kwargs):
        self.quote = kwargs.pop('quote', None)
        super().__init__(*args, **kwargs)
        
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['addon'].queryset = ServiceAddOn.objects.filter(is_active=True)
        self.fields['addon'].required = False
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")
        return quantity
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price and unit_price <= 0:
            raise ValidationError("Unit price must be greater than 0")
        return unit_price
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.quote and self.quote.status not in ['draft', 'submitted']:
            raise ValidationError("Cannot add/edit items for quote with current status")
        
        return cleaned_data

class QuoteAttachmentForm(forms.ModelForm):
    class Meta:
        model = QuoteAttachment
        fields = [
            'file', 'attachment_type', 'title', 'description', 
            'is_public', 'display_order'
        ]
        
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'}),
            'attachment_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Attachment title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }
    
    def __init__(self, *args, **kwargs):
        self.quote = kwargs.pop('quote', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            validate_file_size(file)
            validate_file_type(file)
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.quote and self.quote.status in ['expired', 'cancelled', 'converted']:
            raise ValidationError("Cannot add attachments to quote with current status")
        
        return cleaned_data


class QuoteRevisionForm(forms.ModelForm):
    class Meta:
        model = QuoteRevision
        fields = ['changes_summary', 'reason', 'previous_price', 'new_price']
        
        widgets = {
            'changes_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'previous_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'new_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }
    
    def __init__(self, *args, **kwargs):
        self.quote = kwargs.pop('quote', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.quote:
            self.fields['previous_price'].initial = self.quote.final_price
    
    def clean_new_price(self):
        new_price = self.cleaned_data.get('new_price')
        if new_price and new_price <= 0:
            raise ValidationError("New price must be greater than 0")
        return new_price
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.quote and self.quote.status not in ['draft', 'submitted', 'under_review']:
            raise ValidationError("Cannot create revision for quote with current status")
        
        return cleaned_data


class QuoteTemplateForm(forms.ModelForm):
    class Meta:
        model = QuoteTemplate
        fields = [
            'name', 'description', 'cleaning_type', 'default_service',
            'default_urgency_level', 'is_active', 'is_ndis_template'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cleaning_type': forms.Select(attrs={'class': 'form-control'}),
            'default_service': forms.Select(attrs={'class': 'form-control'}),
            'default_urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_ndis_template': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['default_service'].queryset = Service.objects.filter(is_active=True)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            existing = QuoteTemplate.objects.filter(name=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("A template with this name already exists")
        return name


class QuoteSearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search quotes by number, client name, or address...'
        })
    )
    
    status = forms.MultipleChoiceField(
        choices=Quote.STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    cleaning_type = forms.MultipleChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    urgency_level = forms.MultipleChoiceField(
        choices=Quote.URGENCY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    is_ndis_client = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    postcode = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postcode'})
    )
    
    state = forms.ChoiceField(
        choices=[('', 'All States')] + Quote.STATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    price_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Min price'})
    )
    
    price_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Max price'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        required=False,
        empty_label="All Staff",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("Date from cannot be later than date to")
        
        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')
        
        if price_min and price_max and price_min > price_max:
            raise ValidationError("Minimum price cannot be greater than maximum price")
        
        return cleaned_data


class QuoteCalculatorForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True, is_public=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the service you need"
    )
    
    cleaning_type = forms.ChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Type of cleaning required"
    )
    
    number_of_rooms = forms.IntegerField(
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
        help_text="Number of rooms to be cleaned"
    )
    
    square_meters = forms.IntegerField(
        min_value=10,
        max_value=10000,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '10', 'max': '10000'}),
        help_text="Total area in square meters (optional)"
    )
    
    urgency_level = forms.ChoiceField(
        choices=Quote.URGENCY_CHOICES,
        initial=2,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="How urgent is this service?"
    )
    
    postcode = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter postcode'}),
        help_text="Property postcode for travel calculation"
    )
    
    addons = forms.ModelMultipleChoiceField(
        queryset=ServiceAddOn.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select additional services"
    )
    
    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if postcode:
            validate_postcode(postcode)
        return postcode


class BulkQuoteOperationForm(forms.Form):
    OPERATION_CHOICES = [
        ('approve', 'Approve Selected Quotes'),
        ('reject', 'Reject Selected Quotes'),
        ('cancel', 'Cancel Selected Quotes'),
        ('assign', 'Assign Selected Quotes'),
        ('export', 'Export Selected Quotes')
    ]
    
    operation = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quote_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        required=False,
        empty_label="Select staff member",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Required when rejecting quotes"
    )
    
    def clean_quote_ids(self):
        quote_ids = self.cleaned_data.get('quote_ids')
        if quote_ids:
            try:
                quote_id_list = quote_ids.split(',')
                return [id.strip() for id in quote_id_list if id.strip()]
            except:
                raise ValidationError("Invalid quote IDs format")
        return []
    
    def clean(self):
        cleaned_data = super().clean()
        operation = cleaned_data.get('operation')
        assigned_to = cleaned_data.get('assigned_to')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if operation == 'assign' and not assigned_to:
            raise ValidationError("Staff member must be selected for assignment operation")
        
        if operation == 'reject' and not rejection_reason:
            raise ValidationError("Rejection reason is required for reject operation")
        
        return cleaned_data


class QuoteExportForm(forms.Form):
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ]
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        initial='csv',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quote_ids = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Leave empty to export all quotes"
    )
    
    status_filter = forms.MultipleChoiceField(
        choices=Quote.STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    include_items = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_attachments = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_quote_ids(self):
        quote_ids = self.cleaned_data.get('quote_ids')
        if quote_ids:
            try:
                quote_id_list = quote_ids.split(',')
                return [id.strip() for id in quote_id_list if id.strip()]
            except:
                raise ValidationError("Invalid quote IDs format")
        return []

class QuoteReportForm(forms.Form):
    REPORT_TYPE_CHOICES = [
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('analytics', 'Analytics Report'),
        ('conversion', 'Conversion Report')
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV')
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        initial='summary',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        initial='pdf',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    filter_status = forms.MultipleChoiceField(
        choices=Quote.STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    filter_cleaning_type = forms.MultipleChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be later than end date")
        
        return cleaned_data


class QuoteAnalyticsForm(forms.Form):
    GROUP_BY_CHOICES = [
        ('status', 'By Status'),
        ('cleaning_type', 'By Cleaning Type'),
        ('urgency', 'By Urgency Level'),
        ('month', 'By Month'),
        ('state', 'By State')
    ]
    
    group_by = forms.ChoiceField(
        choices=GROUP_BY_CHOICES,
        initial='status',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    include_ndis = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_general = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be later than end date")
        
        include_ndis = cleaned_data.get('include_ndis')
        include_general = cleaned_data.get('include_general')
        
        if not include_ndis and not include_general:
            raise ValidationError("At least one client type must be included")
        
        return cleaned_data


class QuoteAssignmentForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        empty_label="Select staff member",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assignment_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        help_text="Optional notes for the assigned staff member"
    )
    
    notify_assignee = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send notification email to assigned staff member"
    )


class QuoteApprovalForm(forms.Form):
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text="When should this quote expire? (Leave empty for default 30 days)"
    )
    
    approval_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        help_text="Optional approval notes"
    )
    
    notify_client = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send approval notification to client"
    )
    
    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError("Expiry date must be in the future")
        return expires_at


class QuoteRejectionForm(forms.Form):
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Please provide a reason for rejection"
    )
    
    notify_client = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send rejection notification to client"
    )
    
    offer_alternative = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Offer to create an alternative quote"
    )


class QuoteDuplicateForm(forms.Form):
    new_cleaning_type = forms.ChoiceField(
        choices=Quote.CLEANING_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Change cleaning type for the duplicate (optional)"
    )
    
    new_urgency_level = forms.ChoiceField(
        choices=Quote.URGENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Change urgency level for the duplicate (optional)"
    )
    
    include_items = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Include quote items in the duplicate"
    )
    
    include_attachments = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Include public attachments in the duplicate"
    )


class QuoteNotificationForm(forms.Form):
    NOTIFICATION_TYPE_CHOICES = [
        ('submitted', 'Quote Submitted'),
        ('approved', 'Quote Approved'),
        ('rejected', 'Quote Rejected'),
        ('expired', 'Quote Expired'),
        ('reminder', 'Expiry Reminder'),
        ('custom', 'Custom Message')
    ]
    
    RECIPIENT_TYPE_CHOICES = [
        ('client', 'Client Only'),
        ('staff', 'Staff Only'),
        ('both', 'Client and Staff')
    ]
    
    quote_id = forms.UUIDField(
        widget=forms.HiddenInput()
    )
    
    notification_type = forms.ChoiceField(
        choices=NOTIFICATION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    custom_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text="Required for custom notifications"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        notification_type = cleaned_data.get('notification_type')
        custom_message = cleaned_data.get('custom_message')
        
        if notification_type == 'custom' and not custom_message:
            raise ValidationError("Custom message is required for custom notifications")
        
        return cleaned_data


class QuoteConversionForm(forms.Form):
    conversion_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Notes about the conversion to job"
    )
    
    scheduled_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Scheduled service date"
    )
    
    scheduled_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Scheduled service time"
    )
    
    notify_client = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send conversion notification to client"
    )
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now().date():
            raise ValidationError("Scheduled date cannot be in the past")
        return scheduled_date


class QuoteFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Quote.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    cleaning_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Quote.CLEANING_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    urgency_level = forms.ChoiceField(
        choices=[('', 'All Urgency Levels')] + Quote.URGENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_ndis = forms.ChoiceField(
        choices=[('', 'All Clients'), ('true', 'NDIS Only'), ('false', 'General Only')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_active=True),
        required=False,
        empty_label="All Staff",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_range = forms.ChoiceField(
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class QuotePricingForm(forms.Form):
    base_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True})
    )
    
    extras_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    travel_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True})
    )
    
    urgency_surcharge = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True})
    )
    
    discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    def clean_extras_cost(self):
        extras_cost = self.cleaned_data.get('extras_cost')
        if extras_cost and extras_cost < 0:
            raise ValidationError("Extras cost cannot be negative")
        return extras_cost
    
    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount and discount_amount < 0:
            raise ValidationError("Discount amount cannot be negative")
        return discount_amount


class QuoteFormMixin:
    def add_form_errors(self, form, errors):
        for error in errors:
            form.add_error(None, error)
    
    def get_form_initial_data(self, quote=None):
        if quote:
            return {
                'service': quote.service,
                'cleaning_type': quote.cleaning_type,
                'property_address': quote.property_address,
                'suburb': quote.suburb,
                'postcode': quote.postcode,
                'state': quote.state,
                'number_of_rooms': quote.number_of_rooms,
                'square_meters': quote.square_meters,
                'urgency_level': quote.urgency_level,
                'preferred_date': quote.preferred_date,
                'preferred_time': quote.preferred_time,
                'special_requirements': quote.special_requirements,
                'access_instructions': quote.access_instructions
            }
        return {}
    
    def validate_form_permissions(self, form, user, quote=None):
        if quote and quote.status not in ['draft', 'submitted'] and not user.is_staff:
            form.add_error(None, "You cannot modify this quote")
            return False
        return True


def get_quote_form_class(quote_type='general', user=None):
    if quote_type == 'ndis':
        return NDISQuoteForm
    elif quote_type == 'calculator':
        return QuoteCalculatorForm
    elif quote_type == 'update':
        return QuoteUpdateForm
    elif quote_type == 'status':
        return QuoteStatusForm
    else:
        return QuoteForm


def validate_quote_form_data(form_data, quote=None):
    errors = []
    
    if quote and quote.status not in ['draft', 'submitted']:
        errors.append("Cannot modify quote with current status")
    
    validation_errors = validate_quote_data(form_data)
    errors.extend(validation_errors)
    
    return errors

