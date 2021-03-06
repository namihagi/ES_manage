from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from .models import CustomUserModel, TagModel, HistoryModel
from django.urls import reverse_lazy
from django.views import View
from .forms import HistoryCreateForm, TagCreateForm, UpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class SignupView(View):
    '''サインアップ'''

    def get(self, request, *args, **kwargs):
        return render(request, 'history/signup.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']

        # ユーザーを追加
        try:
            CustomUserModel.objects.get(username=username)
            return render(request, 'history/signup.html', {'error': 'このユーザー名は既に登録されています．'})
        except:
            user = CustomUserModel.objects.create_user(username, '', password)
            # 新しいユーザーが作成されたタイミングで並び順モデルに新しいデータを追加
            # HowtoOrder.objects.create(user_name=username)
            return redirect('login')


class LoginView(View):
    '''ログイン'''

    def get(self, request, *args, **kwargs):
        return render(request, 'history/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list', username=username)
        else:
            return redirect('login')


def logoutfunc(request):
    logout(request)
    return redirect('login')


class HistoryCreateView(View):

    def get(self, request, *args, **kwargs):
        login_username = request.user.username
        print(login_username)
        tags = TagModel.objects.filter(username=login_username)
        print(len(tags))
        context = {
            'form': HistoryCreateForm(),
            'login_username': login_username,
            'tags': tags,
            # タグの数に応じてpost画面のタグの表示数を変更，タグが10個以上の場合はスクロール
            'len_tags': min(len(tags), 10),
        }
        return render(request, 'history/create_post.html', context)

    def post(self, request, *args, **kwargs):
        login_username = request.user.username
        request_copy = request.POST.copy()
        request_copy['question'] = request_copy['question'].rstrip().lstrip()
        request_copy['answer'] = request_copy['answer'].rstrip().lstrip()
        request_copy['char_num'] = len(request_copy['answer'])
        form = HistoryCreateForm(request_copy)
        if form.is_valid():
            form.save()
            print('ok')
            return redirect('list', username=login_username)
        else:
            print('failed')
            return redirect('create_his')


# class Userlist(ListView):
#     model = HistoryModel
#     slug_field = "username"
#     slug_url_kwarg = "username"
#     template_name = 'history/list.html'

#     def get_object(self):
#         object = get_object_or_404(HistoryModel, username=self.kwargs.get("username"))
#         if self.request.user.username == object.username:
#             return object
#         else:
#             print("you are not the owner!!")


class HistoryListView(ListView):
    # memo LoginRequiredMixinとListViewの順番を入れ替えるとうまくいかない
    '''タスクの一覧を表示'''

    def get(self, request, username):
        # ログイン中のユーザー名を取得
        login_username = request.user.username
        # username = self.kwargs['username']

        # ゆーざーDBに登録されていないユーザ名がリクエストされることも想定される
        # この方法がベストかはわからないがとりあえず．
        # ユーザーが存在していないとき
        if CustomUserModel.objects.filter(username=username).count() == 0:
            context = {
                'username': username,
                'login_username': login_username,
            }
            return render(request, 'history/list_not_exist.html', context)

        # ログインしていない人のポストを見るときには制限をかける
        # ログインしているとき
        if login_username == username:
            histories = HistoryModel.objects.filter(username=username)

            context = {
                'username': username,
                'histories': histories,
                'login_username': login_username
            }
            return render(request, 'history/list.html', context)

        # ログインしていないとき
        else:
            # memo:カンマで区切るとAND検索
            histories = HistoryModel.objects.filter(username=username, open_info='public')
            context = {
                'username': username,
                'histories': histories,
                'login_username': login_username,
            }
            return render(request, 'history/list_not_login.html', context)


class HistoryDetailView(DetailView):
    '''タスクの詳細を表示'''
    template_name = 'history/detail_his.html'
    model = HistoryModel


# class TodoDeleteView(DeleteView):
#     '''タスクを削除'''
#     template_name = 'history/delete_post.html'
#     model = HistoryModel
#     success_url = reverse_lazy('list')

class HistroyUpdateView(View):
    '''ポストを修正'''

    def get(self, request, pk, *args, **kwargs):
        login_username = request.user.username
        post = HistoryModel.objects.get(pk=pk)
        form = UpdateForm(instance=post)
        tags = TagModel.objects.filter(username=login_username)
        print(post)
        context = {
            'form': form,
            'login_username': login_username,
            'tags': tags,
            # タグの数に応じてpost画面のタグの表示数を変更，タグが10個以上の場合はスクロール
            'len_tags': min(len(tags), 10),
        }
        return render(request, 'history/update_post.html', context)

    def post(self, request, pk, *args, **kwargs):
        login_username = request.user.username
        post = HistoryModel.objects.get(pk=pk)
        form = UpdateForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('list', username=login_username)
        else:
            return redirect('update')


class TagCreateView(View):
    def get(self, request, *args, **kwargs):
        login_username = request.user.username
        context = {
            'form': TagCreateForm(),
            'username': login_username,
        }
        return render(request, 'history/create_tag.html', context)

    def post(self, request, *args, **kwargs):
        login_username = request.user.username
        form = TagCreateForm(request.POST)
        if form.is_valid():
            form.save()
            print('ok')
            return redirect('list', username=login_username)
        else:
            print('failed')
            return redirect('create_his')
