from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth, ExtractWeek
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta

from .models import User, Category, Expense
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    CategorySerializer,
    ExpenseSerializer,
    ExpenseCreateSerializer,
    CategoryBreakdownSerializer,
    AggregationSerializer,
    MonthlySpendSerializer,
    WeeklySpendSerializer,
)

class APIResponse:
    @staticmethod
    def success(data=None, message=None, count=None):
        response = {"success": True}
        if message:
            response["message"] = message
        if data is not None:
            response["data"] = data
        if count is not None:
            response["count"] = count
        return Response(response)

    @staticmethod
    def error(message, errors=None):
        response = {"success": False, "message": message}
        if errors:
            response["errors"] = errors
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return APIResponse.error("Registration failed", serializer.errors)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            from django.contrib.auth import authenticate

            user = authenticate(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return APIResponse.success(
                    message="Login successful",
                    data={
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                )
            return APIResponse.error("Invalid credentials")
        return APIResponse.error("Validation failed", serializer.errors)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return APIResponse.success(message="Logged out successfully")
        except Exception:
            return APIResponse.success(message="Logged out successfully")


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return CategorySerializer
        return CategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "date"]
    pagination_class = None

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user).select_related(
            "category", "user"
        )

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        category_id = self.request.query_params.get("category")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, count=queryset.count())

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return APIResponse.success(message="Expense deleted successfully")
        except Exception as e:
            return APIResponse.error(str(e))

    @action(detail=False, methods=["get"])
    def total(self, request):
        queryset = self.get_queryset()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        aggregates = queryset.aggregate(total_amount=Sum("amount"), count=Count("id"))

        return APIResponse.success(
            data={
                "total_amount": float(aggregates["total_amount"] or 0),
                "count": aggregates["count"] or 0,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    @action(detail=False, methods=["get"])
    def monthly(self, request):
        queryset = self.get_queryset()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        monthly_data = (
            queryset.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total_amount=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        result = []
        for item in monthly_data:
            month_date = timezone.datetime(2024, item["month"], 1)
            result.append(
                {
                    "month": month_date.strftime("%B %Y"),
                    "total_amount": float(item["total_amount"]),
                    "count": item["count"],
                }
            )

        return APIResponse.success(data=result)

    @action(detail=False, methods=["get"])
    def weekly(self, request):
        queryset = self.get_queryset()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        weekly_data = (
            queryset.annotate(week=ExtractWeek("date"))
            .values("week")
            .annotate(total_amount=Sum("amount"), count=Count("id"))
            .order_by("week")
        )

        result = []
        for item in weekly_data:
            result.append(
                {
                    "week": item["week"],
                    "total_amount": float(item["total_amount"]),
                    "count": item["count"],
                }
            )

        return APIResponse.success(data=result)

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        queryset = self.get_queryset()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        total_amount = queryset.aggregate(Sum("amount"))["amount__sum"] or 0

        category_data = (
            queryset.values("category__id", "category__name")
            .annotate(total_amount=Sum("amount"), count=Count("id"))
            .order_by("-total_amount")
        )

        result = []
        for item in category_data:
            percentage = (
                (float(item["total_amount"]) / float(total_amount) * 100)
                if total_amount > 0
                else 0
            )
            result.append(
                {
                    "category_id": item["category__id"],
                    "category_name": item["category__name"] or "Uncategorized",
                    "total_amount": float(item["total_amount"]),
                    "count": item["count"],
                    "percentage": round(percentage, 2),
                }
            )

        return APIResponse.success(data=result)
