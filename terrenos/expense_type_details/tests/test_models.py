import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from expense_type_details.models import ExpenseTypeDetail


@pytest.mark.django_db
class TestExpenseTypeDetailModel:
    """Test cases for ExpenseTypeDetail model"""
    
    def test_create_expense_type_detail_with_all_fields(self):
        """Test creating expense type detail with all fields"""
        expense = ExpenseTypeDetail.objects.create(
            description='Test expense',
            notes='Test notes'
        )
        
        assert expense.description == 'Test expense'
        assert expense.notes == 'Test notes'
        assert expense.id is not None
        
    def test_create_expense_type_detail_with_minimal_fields(self):
        """Test creating expense type detail with only required fields"""
        expense = ExpenseTypeDetail.objects.create()
        
        assert expense.description is None
        assert expense.notes is None
        assert expense.id is not None
        
    def test_create_expense_type_detail_with_blank_fields(self):
        """Test creating expense type detail with blank fields"""
        expense = ExpenseTypeDetail.objects.create(
            description='',
            notes=''
        )
        
        assert expense.description == ''
        assert expense.notes == ''
        
    def test_create_expense_type_detail_with_null_fields(self):
        """Test creating expense type detail with null fields"""
        expense = ExpenseTypeDetail.objects.create(
            description=None,
            notes=None
        )
        
        assert expense.description is None
        assert expense.notes is None
        
    def test_expense_type_detail_str_representation(self):
        """Test string representation of expense type detail"""
        expense = ExpenseTypeDetail.objects.create(
            description='Test description',
            notes='Test notes'
        )
        
        expected_str = "Detalle de Tipo de Gasto: Test description (Test notes)"
        assert str(expense) == expected_str
        
    def test_expense_type_detail_str_with_none_values(self):
        """Test string representation with None values"""
        expense = ExpenseTypeDetail.objects.create(
            description=None,
            notes=None
        )
        
        expected_str = "Detalle de Tipo de Gasto: None (None)"
        assert str(expense) == expected_str
        
    def test_expense_type_detail_str_with_empty_values(self):
        """Test string representation with empty values"""
        expense = ExpenseTypeDetail.objects.create(
            description='',
            notes=''
        )
        
        expected_str = "Detalle de Tipo de Gasto:  ()"
        assert str(expense) == expected_str
        
    def test_expense_type_detail_meta_verbose_name(self):
        """Test model meta verbose name"""
        assert ExpenseTypeDetail._meta.verbose_name == "Detalle de Tipo de Gasto"
        
    def test_expense_type_detail_meta_verbose_name_plural(self):
        """Test model meta verbose name plural"""
        assert ExpenseTypeDetail._meta.verbose_name_plural == "Detalles de Tipos de Gasto"
        
    def test_expense_type_detail_meta_ordering(self):
        """Test model meta ordering"""
        assert ExpenseTypeDetail._meta.ordering == ['description']
        
    def test_expense_type_detail_ordering_in_queryset(self):
        """Test that objects are ordered by description"""
        ExpenseTypeDetail.objects.create(description='Z expense', notes='Z notes')
        ExpenseTypeDetail.objects.create(description='A expense', notes='A notes')
        ExpenseTypeDetail.objects.create(description='M expense', notes='M notes')
        
        expenses = list(ExpenseTypeDetail.objects.all())
        descriptions = [expense.description for expense in expenses]
        
        assert descriptions == ['A expense', 'M expense', 'Z expense']
        
    def test_expense_type_detail_field_types(self):
        """Test that fields have correct types"""
        expense = ExpenseTypeDetail.objects.create(
            description='Test',
            notes='Test notes'
        )
        
        description_field = expense._meta.get_field('description')
        notes_field = expense._meta.get_field('notes')
        
        assert description_field.__class__.__name__ == 'TextField'
        assert notes_field.__class__.__name__ == 'TextField'
        
    def test_expense_type_detail_field_options(self):
        """Test field options (blank=True, null=True)"""
        description_field = ExpenseTypeDetail._meta.get_field('description')
        notes_field = ExpenseTypeDetail._meta.get_field('notes')
        
        assert description_field.blank is True
        assert description_field.null is True
        assert notes_field.blank is True
        assert notes_field.null is True
        
    def test_expense_type_detail_update(self):
        """Test updating expense type detail"""
        expense = ExpenseTypeDetail.objects.create(
            description='Original description',
            notes='Original notes'
        )
        
        expense.description = 'Updated description'
        expense.notes = 'Updated notes'
        expense.save()
        
        updated_expense = ExpenseTypeDetail.objects.get(id=expense.id)
        assert updated_expense.description == 'Updated description'
        assert updated_expense.notes == 'Updated notes'
        
    def test_expense_type_detail_delete(self):
        """Test deleting expense type detail"""
        expense = ExpenseTypeDetail.objects.create(
            description='To be deleted',
            notes='Delete me'
        )
        expense_id = expense.id
        
        expense.delete()
        
        with pytest.raises(ExpenseTypeDetail.DoesNotExist):
            ExpenseTypeDetail.objects.get(id=expense_id)
            
    def test_expense_type_detail_count(self):
        """Test counting expense type details"""
        initial_count = ExpenseTypeDetail.objects.count()
        
        ExpenseTypeDetail.objects.create(description='First', notes='First notes')
        ExpenseTypeDetail.objects.create(description='Second', notes='Second notes')
        
        assert ExpenseTypeDetail.objects.count() == initial_count + 2