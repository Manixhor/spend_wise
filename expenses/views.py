from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Expense
from .serializers import ExpenseSerializer


# GET all expenses
@api_view(['GET'])
def get_expenses(request):
    expenses = Expense.objects.all().order_by('-created_at')
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


# POST new expense
@api_view(['POST'])
def add_expense(request):
    serializer = ExpenseSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)


# DELETE expense
@api_view(['DELETE'])
def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    return Response({"message": "Deleted"})


# UPDATE expense
@api_view(['PUT'])
def update_expense(request, id):
    expense = Expense.objects.get(id=id)
    serializer = ExpenseSerializer(expense, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)