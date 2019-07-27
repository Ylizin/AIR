from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import View
from user.forms import UserForm

# 注册视图
class RegisterView(View):
    form_class = UserForm  # 上文自定义的表单
    template_name = 'user/register.html'

    # 显示空表单
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # 处理POST表单数据
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            # 保存到数据库中
            user.save()
            # 注册成功之后 跳转到成功页面
            return render(request, 'user/register_success.html', {'form': form})
        return render(request, self.template_name, {'form': form})

# class LoginView(View):
#     pass

# class LogoutView(View):
#     pass

    