from django import forms
from .models import CandidataCoordenadora
from .services import validate_cpf

class CandidataRegistrationForm(forms.ModelForm):
    class Meta:
        model = CandidataCoordenadora
        fields = [
            'cpf', 'nome_completo', 'email', 'foto', 'cep', 'rua', 'numero', 
            'complemento', 'bairro', 'cidade', 'estado', 'empresa_anterior', 
            'empresa_outra', 'media_ganhos', 'quantidade_consultoras', 
            'documento_rg_cnh', 'documento_cpf', 'comprovante_endereco', 
            'comprovante_ganhos'
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00', 'data-mask': '000.000.000-00'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'data-mask': '00000-000'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'empresa_anterior': forms.Select(attrs={'class': 'form-select'}),
            'empresa_outra': forms.TextInput(attrs={'class': 'form-control'}),
            'media_ganhos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade_consultoras': forms.NumberInput(attrs={'class': 'form-control'}),
            'documento_rg_cnh': forms.FileInput(attrs={'class': 'form-control'}),
            'documento_cpf': forms.FileInput(attrs={'class': 'form-control'}),
            'comprovante_endereco': forms.FileInput(attrs={'class': 'form-control'}),
            'comprovante_ganhos': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not validate_cpf(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf

    def clean(self):
        cleaned_data = super().clean()
        empresa_anterior = cleaned_data.get('empresa_anterior')
        empresa_outra = cleaned_data.get('empresa_outra')

        if empresa_anterior == 'OUTRAS' and not empresa_outra:
            self.add_error('empresa_outra', "Por favor, informe qual a outra empresa.")
        
        return cleaned_data
