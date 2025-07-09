import pytest
from django.test import TestCase
from expense_type_details.forms import ExpenseTypeDetailForm
from expense_type_details.models import ExpenseTypeDetail


@pytest.mark.django_db
class TestExpenseTypeDetailForm:
    """Test cases for ExpenseTypeDetailForm"""
    
    def test_form_with_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'description': 'Test expense description',
            'notes': 'Test notes'
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['description'] == 'Test expense description'
        assert form.cleaned_data['notes'] == 'Test notes'
        
    def test_form_with_empty_data(self):
        """Test form with empty data"""
        form_data = {}
        form = ExpenseTypeDetailForm(data=form_data)
        
        # Form should be valid since all fields are optional
        assert form.is_valid()
        
    def test_form_with_empty_strings(self):
        """Test form with empty strings"""
        form_data = {
            'description': '',
            'notes': ''
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['description'] == ''
        assert form.cleaned_data['notes'] == ''
        
    def test_form_with_only_description(self):
        """Test form with only description field"""
        form_data = {
            'description': 'Only description',
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['description'] == 'Only description'
        
    def test_form_with_only_notes(self):
        """Test form with only notes field"""
        form_data = {
            'notes': 'Only notes',
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['notes'] == 'Only notes'
        
    def test_form_save_creates_new_object(self):
        """Test that form save creates new object"""
        form_data = {
            'description': 'New expense',
            'notes': 'New notes'
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        expense = form.save()
        
        assert expense.id is not None
        assert expense.description == 'New expense'
        assert expense.notes == 'New notes'
        
    def test_form_save_updates_existing_object(self):
        """Test that form save updates existing object"""
        # Create existing object
        expense = ExpenseTypeDetail.objects.create(
            description='Original description',
            notes='Original notes'
        )
        
        # Update with form
        form_data = {
            'description': 'Updated description',
            'notes': 'Updated notes'
        }
        form = ExpenseTypeDetailForm(data=form_data, instance=expense)
        
        assert form.is_valid()
        updated_expense = form.save()
        
        assert updated_expense.id == expense.id
        assert updated_expense.description == 'Updated description'
        assert updated_expense.notes == 'Updated notes'
        
    def test_form_fields_configuration(self):
        """Test form field configuration"""
        form = ExpenseTypeDetailForm()
        
        # Check that the form has the correct fields
        assert 'description' in form.fields
        assert 'notes' in form.fields
        assert len(form.fields) == 2
        
    def test_form_field_labels(self):
        """Test form field labels"""
        form = ExpenseTypeDetailForm()
        
        assert form.fields['description'].label == 'Descripción'
        assert form.fields['notes'].label == 'Notas'
        
    def test_form_field_widgets(self):
        """Test form field widgets"""
        form = ExpenseTypeDetailForm()
        
        # Check widget types
        assert form.fields['description'].widget.__class__.__name__ == 'TextInput'
        assert form.fields['notes'].widget.__class__.__name__ == 'TextInput'
        
        # Check widget attributes
        assert 'form-control' in form.fields['description'].widget.attrs['class']
        assert 'form-control' in form.fields['notes'].widget.attrs['class']
        
    def test_form_meta_model(self):
        """Test form meta model"""
        form = ExpenseTypeDetailForm()
        assert form._meta.model == ExpenseTypeDetail
        
    def test_form_meta_fields(self):
        """Test form meta fields"""
        form = ExpenseTypeDetailForm()
        assert form._meta.fields == ['description', 'notes']
        
    def test_form_with_long_text(self):
        """Test form with long text data"""
        long_text = 'A' * 1000  # 1000 character string
        form_data = {
            'description': long_text,
            'notes': long_text
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['description'] == long_text
        assert form.cleaned_data['notes'] == long_text
        
    def test_form_with_special_characters(self):
        """Test form with special characters"""
        special_text = 'Test with special chars: áéíóú ñ @#$%^&*()_+-=[]{}|;:,.<>?'
        form_data = {
            'description': special_text,
            'notes': special_text
        }
        form = ExpenseTypeDetailForm(data=form_data)
        
        assert form.is_valid()
        assert form.cleaned_data['description'] == special_text
        assert form.cleaned_data['notes'] == special_text
        
    def test_form_initial_data(self):
        """Test form with initial data"""
        initial_data = {
            'description': 'Initial description',
            'notes': 'Initial notes'
        }
        form = ExpenseTypeDetailForm(initial=initial_data)
        
        assert form.initial['description'] == 'Initial description'
        assert form.initial['notes'] == 'Initial notes'
        
    def test_form_bound_vs_unbound(self):
        """Test bound vs unbound forms"""
        # Unbound form
        unbound_form = ExpenseTypeDetailForm()
        assert not unbound_form.is_bound
        
        # Bound form
        bound_form = ExpenseTypeDetailForm(data={'description': 'test'})
        assert bound_form.is_bound