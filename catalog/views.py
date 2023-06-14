from django.shortcuts import render, redirect
from . import models
from . import handlers

# Create your views here.


def hello_world_text(request):
    # показ контента html файла
    return render(request, 'index.html')


def about_page(request):
    return render(request, 'about.html')


# получаем все данные о котигориях из базы
def main_page(request):
    all_categories = models.Category.objects.all()
    all_products = models.Product.objects.all()

    # получить переменную из фронт части, если он есть
    search_value_from_front = request.GET.get('pr')
    if search_value_from_front:
        all_products = models.Product.objects.filter(name__contains=search_value_from_front)
    # передача переменных из бэка на фронт

    context = {'all_categories': all_categories, 'all_products': all_products}
    return render(request, 'index.html', context)


# получить продукты из конкретной категории
def get_category_products(request, pk):
    #   получить все товары из конкретной категории
    exact_category_products = models.Product.objects.filter(category_name__id=pk)
    # передача переменных из бэка на фронт
    context = {'category_products': exact_category_products}
    #   указать html
    return render(request, 'category.html', context)


def get_product(request, name, pk):
    exact_product = models.Product.objects.get(name=name, id=pk)
    context = {'product': exact_product}
    return render(request, 'product.html', context)
# функция добавлени продукта в корзину


def add_pr_to_cart(request, pk):
    # получить выбранное количество продукта из front части
    quantity = request.POST.get('pr_count')
    # находим сам продукт
    product_to_cart = models.Product.objects.get(id=pk)
    # добавление данных
    models.UserCart.objects.create(user_id=request.user.id, user_product=product_to_cart,
                                   user_product_quantity=quantity)

    return redirect('/')


def print_cart(request):
    product_from_cart = models.UserCart.objects.filter(user_id=request.user.id)
    context = {'cart_products': product_from_cart}
    return render(request, 'printcart.html', context)


# оформляем заказ
def complete_order(request):
    # вызываем корзину пользователя
    user_cart = models.UserCart.objects.filter(user_id=request.user.id)
    # собираем сообщение бота для админа
    if request.method == 'POST':
        result_message = 'Новый заказ(из Сайта)\n\n'
        total = 0
    #  Счетчик для подсчета итога корзины
        for cart in user_cart:
            result_message += f'Название товара: {cart.user_product}\n' \
                          f'количество: {cart.user_product_quantity}\n'
            total += cart.user_product.price * cart.user_product_quantity
        result_message += f'\n\nИтог: {total}'
        handlers.bot.send_message(-1001964021020, result_message)
        user_cart.delete()
        return redirect('/')
    return render(request, ' user_cart.html', {'user_cart': user_cart})


def delete_from_user_cart(request, pk):
    product_to_delete = models.Product.objects.get(id=pk)
    models.UserCart.objects.filter(user_id=request.user.id, user_product=product_to_delete).delete()
    return redirect('/cart')
