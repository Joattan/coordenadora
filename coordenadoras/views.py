from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from .models import CandidataCoordenadora
from .forms import CandidataRegistrationForm
from .services import get_address_by_cep, get_name_by_cpf

# --- Public Views ---

class CadastroCandidataView(CreateView):
    model = CandidataCoordenadora
    form_class = CandidataRegistrationForm
    template_name = 'coordenadoras/cadastro.html'
    success_url = reverse_lazy('coordenadoras:sucesso')

    def form_valid(self, form):
        # O status inicial já é PENDENTE por padrão no model
        return super().form_valid(form)

def cadastro_sucesso(request):
    return render(request, 'coordenadoras/sucesso.html')

def api_cep_lookup(request):
    cep = request.GET.get('cep')
    if cep:
        result = get_address_by_cep(cep)
        return JsonResponse(result)
    return JsonResponse({"success": False, "error": "CEP não fornecido"})

def api_cpf_lookup(request):
    cpf = request.GET.get('cpf')
    if cpf:
        result = get_name_by_cpf(cpf)
        return JsonResponse(result)
    return JsonResponse({"success": False, "error": "CPF não fornecido"})


# --- Admin Views ---

class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class CandidataListView(AdminStaffRequiredMixin, ListView):
    model = CandidataCoordenadora
    template_name = 'coordenadoras/admin_list.html'
    context_object_name = 'candidatas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        nome = self.request.GET.get('nome')
        cpf = self.request.GET.get('cpf')
        
        if status:
            queryset = queryset.filter(status=status)
        if nome:
            queryset = queryset.filter(nome_completo__icontains=nome)
        if cpf:
            queryset = queryset.filter(cpf__contains=cpf)
            
        return queryset

class CandidataDetailView(AdminStaffRequiredMixin, DetailView):
    model = CandidataCoordenadora
    template_name = 'coordenadoras/admin_detail.html'
    context_object_name = 'candidata'

class CandidataUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = CandidataCoordenadora
    form_class = CandidataRegistrationForm # Reutilizamos o form de cadastro
    template_name = 'coordenadoras/admin_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('coordenadoras:admin_detail', kwargs={'pk': self.object.pk})

def admin_excluir_candidata(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Não autorizado"}, status=403)
    
    candidata = get_object_or_404(CandidataCoordenadora, pk=pk)
    candidata.delete()
    return redirect('coordenadoras:admin_list')

def admin_atualizar_status(request, pk):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Não autorizado"}, status=403)
    
    if request.method == 'POST':
        candidata = get_object_or_404(CandidataCoordenadora, pk=pk)
        novo_status = request.POST.get('status')
        observacao = request.POST.get('observacao')
        
        # Se aprovado, cria o usuário para acesso
        if novo_status == 'APROVADO' and candidata.status != 'APROVADO':
            from django.contrib.auth.models import User
            import re
            
            cpf_clean = re.sub(r'\D', '', candidata.cpf)
            username = cpf_clean
            password = cpf_clean[:6] # 6 primeiros números
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, 
                    password=password,
                    first_name=candidata.nome_completo.split()[0]
                )
                user.save()

        if novo_status in dict(CandidataCoordenadora.STATUS_CHOICES):
            candidata.status = novo_status
            candidata.observacao_aprovacao = observacao
            candidata.save()
            return redirect('coordenadoras:admin_detail', pk=pk)
            
    return redirect('coordenadoras:admin_list')
