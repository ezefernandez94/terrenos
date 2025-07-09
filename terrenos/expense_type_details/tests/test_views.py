import pytest
from django.test import Client
from django.urls import reverse
from django.http import Http404
from expense_type_details.models import ExpenseTypeDetail
from expense_type_details.forms import ExpenseTypeDetailForm


@pytest.mark.django_db
class TestExpenseTypeDetailViews:
    """Test cases for ExpenseTypeDetail views"""
    
    def test_index_view_get(self, client):
        """Test index view GET request"""
        # Create some test data
        ExpenseTypeDetail.objects.create(description='First expense', notes='First notes')
        ExpenseTypeDetail.objects.create(description='Second expense', notes='Second notes')
        
        # Make request - assuming URL pattern name is 'expense_type_details:index'
        response = client.get('/expense_type_details/')  # Adjust URL as needed
        
        assert response.status_code == 200
        assert 'expense_type_details' in response.context
        assert len(response.context['expense_type_details']) == 2
        
    def test_index_view_empty_queryset(self, client):
        """Test index view with no expenses"""
        response = client.get('/expense_type_details/')  # Adjust URL as needed
        
        assert response.status_code == 200
        assert 'expense_type_details' in response.context
        assert len(response.context['expense_type_details']) == 0
        
    def test_detail_view_existing_expense(self, client, expense_type_detail):
        """Test detail view for existing expense"""
        url = f'/expense_type_details/{expense_type_detail.id}/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'expense_type_detail' in response.context
        assert response.context['expense_type_detail'] == expense_type_detail
        
    def test_detail_view_nonexistent_expense(self, client):
        """Test detail view for non-existent expense"""
        url = '/expense_type_details/999999/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 404
        
    def test_create_view_get(self, client):
        """Test create view GET request (function-based view)"""
        response = client.get('/expense_type_details/create/')  # Adjust URL as needed
        
        assert response.status_code == 200
        assert b'Create a New Expense' in response.content
        
    def test_edit_view_get(self, client, expense_type_detail):
        """Test edit view GET request"""
        url = f'/expense_type_details/{expense_type_detail.id}/edit/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert isinstance(response.context['form'], ExpenseTypeDetailForm)
        assert response.context['form'].instance == expense_type_detail
        
    def test_edit_view_post_valid_data(self, client, expense_type_detail):
        """Test edit view POST request with valid data"""
        url = f'/expense_type_details/{expense_type_detail.id}/edit/'  # Adjust URL as needed
        data = {
            'description': 'Updated description',
            'notes': 'Updated notes'
        }
        response = client.post(url, data)
        
        assert response.status_code == 200
        
        # Check that the object was updated
        updated_expense = ExpenseTypeDetail.objects.get(id=expense_type_detail.id)
        assert updated_expense.description == 'Updated description'
        assert updated_expense.notes == 'Updated notes'
        
    def test_edit_view_post_invalid_data(self, client, expense_type_detail):
        """Test edit view POST request with invalid data"""
        url = f'/expense_type_details/{expense_type_detail.id}/edit/'  # Adjust URL as needed
        # Since all fields are optional, we need to test with actual invalid data
        # For this model, all data is valid, so we'll test form rendering
        response = client.post(url, {})
        
        assert response.status_code == 200
        assert 'form' in response.context
        
    def test_edit_view_nonexistent_expense(self, client):
        """Test edit view for non-existent expense"""
        url = '/expense_type_details/999999/edit/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 404
        
    def test_delete_view_get(self, client, expense_type_detail):
        """Test delete view GET request"""
        url = f'/expense_type_details/{expense_type_detail.id}/delete/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'expense_type_detail' in response.context
        assert response.context['expense_type_detail'] == expense_type_detail
        
    def test_delete_view_post(self, client, expense_type_detail):
        """Test delete view POST request"""
        expense_id = expense_type_detail.id
        url = f'/expense_type_details/{expense_id}/delete/'  # Adjust URL as needed
        
        response = client.post(url)
        
        assert response.status_code == 200
        assert b'Expense deleted successfully' in response.content
        
        # Check that the object was deleted
        assert not ExpenseTypeDetail.objects.filter(id=expense_id).exists()
        
    def test_delete_view_nonexistent_expense(self, client):
        """Test delete view for non-existent expense"""
        url = '/expense_type_details/999999/delete/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestExpenseTypeDetailCreateView:
    """Test cases for ExpenseTypeDetailCreateView (Class-based view)"""
    
    def test_create_view_get(self, client):
        """Test create view GET request"""
        url = '/expense_type_details/create_cbv/'  # Adjust URL for CBV as needed
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert isinstance(response.context['form'], ExpenseTypeDetailForm)
        
    def test_create_view_post_valid_data(self, client):
        """Test create view POST request with valid data"""
        url = '/expense_type_details/create_cbv/'  # Adjust URL for CBV as needed
        data = {
            'description': 'New expense description',
            'notes': 'New expense notes'
        }
        
        initial_count = ExpenseTypeDetail.objects.count()
        response = client.post(url, data)
        
        # Should redirect to success URL
        assert response.status_code == 302
        assert ExpenseTypeDetail.objects.count() == initial_count + 1
        
        # Check created object
        created_expense = ExpenseTypeDetail.objects.latest('id')
        assert created_expense.description == 'New expense description'
        assert created_expense.notes == 'New expense notes'
        
    def test_create_view_post_empty_data(self, client):
        """Test create view POST request with empty data"""
        url = '/expense_type_details/create_cbv/'  # Adjust URL for CBV as needed
        data = {}
        
        initial_count = ExpenseTypeDetail.objects.count()
        response = client.post(url, data)
        
        # Should still succeed since all fields are optional
        assert response.status_code == 302
        assert ExpenseTypeDetail.objects.count() == initial_count + 1


@pytest.mark.django_db
class TestExpenseDeleteView:
    """Test cases for ExpenseDeleteView (Class-based view)"""
    
    def test_delete_cbv_get(self, client, expense_type_detail):
        """Test delete CBV GET request"""
        url = f'/expense_type_details/{expense_type_detail.id}/delete_cbv/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 200
        assert response.context['object'] == expense_type_detail
        
    def test_delete_cbv_post(self, client, expense_type_detail):
        """Test delete CBV POST request"""
        expense_id = expense_type_detail.id
        url = f'/expense_type_details/{expense_id}/delete_cbv/'  # Adjust URL as needed
        
        response = client.post(url)
        
        # Should redirect to success URL
        assert response.status_code == 302
        assert not ExpenseTypeDetail.objects.filter(id=expense_id).exists()
        
    def test_delete_cbv_nonexistent_expense(self, client):
        """Test delete CBV for non-existent expense"""
        url = '/expense_type_details/999999/delete_cbv/'  # Adjust URL as needed
        response = client.get(url)
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestViewsIntegration:
    """Integration tests for view interactions"""
    
    def test_create_edit_delete_workflow(self, client):
        """Test complete workflow: create -> edit -> delete"""
        # Create
        create_url = '/expense_type_details/create_cbv/'  # Adjust URL as needed
        create_data = {
            'description': 'Workflow test expense',
            'notes': 'Workflow test notes'
        }
        response = client.post(create_url, create_data)
        assert response.status_code == 302
        
        # Get created object
        expense = ExpenseTypeDetail.objects.get(description='Workflow test expense')
        
        # Edit
        edit_url = f'/expense_type_details/{expense.id}/edit/'  # Adjust URL as needed
        edit_data = {
            'description': 'Updated workflow expense',
            'notes': 'Updated workflow notes'
        }
        response = client.post(edit_url, edit_data)
        assert response.status_code == 200
        
        # Verify edit
        updated_expense = ExpenseTypeDetail.objects.get(id=expense.id)
        assert updated_expense.description == 'Updated workflow expense'
        
        # Delete
        delete_url = f'/expense_type_details/{expense.id}/delete/'  # Adjust URL as needed
        response = client.post(delete_url)
        assert response.status_code == 200
        
        # Verify deletion
        assert not ExpenseTypeDetail.objects.filter(id=expense.id).exists()
        
    def test_index_view_with_multiple_expenses(self, client, multiple_expense_type_details):
        """Test index view with multiple expenses"""
        response = client.get('/expense_type_details/')  # Adjust URL as needed
        
        assert response.status_code == 200
        assert len(response.context['expense_type_details']) == 3
        
        # Check ordering (should be by description)
        expenses = response.context['expense_type_details']
        descriptions = [expense.description for expense in expenses]
        assert descriptions == ['First expense', 'Second expense', 'Third expense']

