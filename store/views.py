from django.db.models import Count 
from django.db.models import Sum
from rest_framework import generics
from rest_framework import status
from datetime import date
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import User, Product, Cart ,Order, OrderItem,Wishlist,PromoCode
from .serializers import RegisterSerializer, ProductSerializer, CartSerializer, OrderSerializer,WishlistSerializer
from rest_framework.permissions import AllowAny 

# ✅ Register view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# ✅ Product create view (Manager only)
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'manager':
            return Response({'error': 'Only store managers can add products.'}, status=403)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.role != 'manager':
            return Response({'error': 'Only store managers can update products.'}, status=403)
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=404)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        if request.user.role != 'manager':
            return Response({'error': 'Only store managers can delete products.'}, status=403)

        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({'message': 'Product deleted successfully.'}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=404)



class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')  # ⚠️ Make sure you're using 'product_id'
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=404)

        # Safely get the first cart item if it exists
        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        if cart_item:
            cart_item.quantity += int(quantity)
            cart_item.save()
        else:
            cart_item = Cart.objects.create(
                user=request.user,
                product=product,
                quantity=quantity
            )

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=201)





class ViewCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            item = Cart.objects.get(pk=pk, user=request.user)
            item.delete()
            return Response({"message": "Item removed from cart."}, status=204)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found in your cart."}, status=404)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        total = sum([item.product.price * item.quantity for item in cart_items], Decimal('0.00'))

        # Apply promo code if provided
        promo_code_input = request.data.get('promo_code')
        discount = Decimal('0.00')

        if promo_code_input:
            try:
                promo = PromoCode.objects.get(code=promo_code_input, active=True)
                if promo.expiry_date >= date.today():
                    discount = (Decimal(promo.discount_percentage) / 100) * total
                else:
                    return Response({'error': 'Promo code expired.'}, status=400)
            except PromoCode.DoesNotExist:
                return Response({'error': 'Invalid promo code.'}, status=400)

        final_total = total - discount

        # Create order
        order = Order.objects.create(user=request.user, total_amount=final_total)

        # Add items to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Clear cart
        cart_items.delete()

        # Respond with order details
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)


class FilteredProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        popular = self.request.query_params.get('popular')

        if category:
            queryset = queryset.filter(category__iexact=category)

        if popular == 'true':
            queryset = queryset.annotate(cart_count=Count('cart')).order_by('-cart_count')

        return queryset

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Wishlist.objects.get(user=request.user, product=serializer.validated_data['product'])
                return Response({'message': 'Product already in wishlist'}, status=400)
            except Wishlist.DoesNotExist:
                serializer.save(user=request.user)
                return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            item = Wishlist.objects.get(id=pk, user=request.user)
            item.delete()
            return Response({'message': 'Item removed from wishlist'}, status=204)
        except Wishlist.DoesNotExist:
            return Response({'error': 'Item not found in wishlist'}, status=404)


class SalesReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'manager':
            return Response({'error': 'Only managers can view sales report.'}, status=403)

        category = request.query_params.get('category')
        sort = request.query_params.get('sort')  # 'most' or 'least'

        queryset = Product.objects.all()

        if category:
            queryset = queryset.filter(category__iexact=category)

        # Annotate total quantity sold per product
        queryset = queryset.annotate(
            total_sold=Sum('orderitem__quantity')
        )

        # Sorting
        if sort == 'most':
            queryset = queryset.order_by('-total_sold')
        elif sort == 'least':
            queryset = queryset.order_by('total_sold')

        # Prepare response
        data = [
            {
                'product': product.name,
                'category': product.category,
                'total_sold': product.total_sold or 0
            }
            for product in queryset
        ]
        return Response(data)


class LowStockAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'manager':
            return Response({'error': 'Only store managers can view this'}, status=403)

        low_stock_products = Product.objects.filter(stock__lt=5)
        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)




