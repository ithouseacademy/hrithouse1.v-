from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm
from .models import *


class UserLoginForm(forms.Form):
    """Foydalanuvchi login qilish formasi"""
    username = forms.CharField(
        max_length=150,
        label="Login",
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2001FF] focus:border-transparent',
            'placeholder': 'Loginingizni kiriting'
        })
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2001FF] focus:border-transparent',
            'placeholder': 'Parolingizni kiriting'
        })
    )


class UserEditForm(forms.ModelForm):
    """Foydalanuvchi loginini o'zgartirish formasi"""
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2001FF] focus:border-transparent',
                'placeholder': 'Yangi login'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2001FF] focus:border-transparent',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'username': 'Yangi login',
            'email': 'Email',
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Bu login allaqachon mavjud!")
        return username


class XodimTahrirlashForm(forms.ModelForm):
    """Xodim ma'lumotlarini tahrirlash formasi"""
    # User modeliga tegishli maydonlar
    username = forms.CharField(max_length=150, label="Login", required=False)
    password = forms.CharField(widget=forms.PasswordInput, label="Yangi parol", required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Parolni tasdiqlang", required=False)
    
    # Xodim ma'lumotlari
    ism = forms.CharField(max_length=100, label="Ism")
    familya = forms.CharField(max_length=100, label="Familiya")
    telefon = forms.CharField(max_length=20, label="Telefon")
    rasm = forms.ImageField(label="Rasm", required=False)
    
    # Ballar va pullar (to'g'ridan-to'g'ri tahrirlash uchun)
    bonus_ball = forms.IntegerField(label="Bonus ball", required=False, initial=0)
    bonus_pul = forms.DecimalField(label="Bonus pul (so'm)", max_digits=12, decimal_places=2, required=False, initial=0)
    jarima_ball = forms.IntegerField(label="Jarima ball", required=False, initial=0)
    jarima_pul = forms.DecimalField(label="Jarima pul (so'm)", max_digits=12, decimal_places=2, required=False, initial=0)
    
    # O'zgartirish sababi
    ozgartirish_sababi = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                         label="O'zgartirish sababi", required=True,
                                         help_text="Nima uchun o'zgartirish kiritayotganingizni yozing")
    
    class Meta:
        model = Xodim
        fields = ['ism', 'familya', 'telefon', 'rasm', 'bonus_ball', 'bonus_pul', 'jarima_ball', 'jarima_pul']
    
    def __init__(self, *args, **kwargs):
        self.xodim = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.xodim and self.xodim.user:
            # User ma'lumotlarini formaga qo'shish
            self.fields['username'].initial = self.xodim.user.username
            self.fields['username'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Parol berilgan bo'lsa, tasdiqlashni tekshirish
        if password and password != password_confirm:
            self.add_error('password_confirm', "Parollar bir-biriga mos kelmadi!")
        
        # Username berilgan bo'lsa, unikal ekanligini tekshirish
        username = cleaned_data.get('username')
        if username and self.xodim and self.xodim.user:
            if User.objects.exclude(pk=self.xodim.user.pk).filter(username=username).exists():
                self.add_error('username', "Bu login allaqachon mavjud!")
        
        return cleaned_data
    
    def save(self, commit=True):
        xodim = super().save(commit=False)
        
        # User ma'lumotlarini yangilash
        if xodim.user:
            user = xodim.user
            username = self.cleaned_data.get('username')
            if username:
                user.username = username
            
            password = self.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            if commit:
                user.save()
        
        if commit:
            xodim.save()
            
            # O'zgartirish tarixiga yozish
            OzgartirishTarixi.objects.create(
                xodim=xodim,
                admin=self.initial.get('admin', None),
                sabab=self.cleaned_data.get('ozgartirish_sababi', ''),
                eski_bonus_ball=self.initial.get('eski_bonus_ball', xodim.bonus_ball),
                eski_bonus_pul=self.initial.get('eski_bonus_pul', xodim.bonus_pul),
                eski_jarima_ball=self.initial.get('eski_jarima_ball', xodim.jarima_ball),
                eski_jarima_pul=self.initial.get('eski_jarima_pul', xodim.jarima_pul),
                yangi_bonus_ball=xodim.bonus_ball,
                yangi_bonus_pul=xodim.bonus_pul,
                yangi_jarima_ball=xodim.jarima_ball,
                yangi_jarima_pul=xodim.jarima_pul
            )
        
        return xodim


class XodimForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Parol', required=False)
    
    class Meta:
        model = Xodim
        fields = ['ism', 'familya', 'telefon', 'rasm']
    
    def save(self, commit=True):
        # User yaratish yoki mavjudini olish
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')
        
        user, created = User.objects.get_or_create(username=username)
        if password:
            user.set_password(password)
            user.save()
        
        # Xodim yaratish
        xodim = super().save(commit=False)
        xodim.user = user
        
        if commit:
            xodim.save()
        
        return xodim


class BonusRecordForm(forms.ModelForm):
    class Meta:
        model = BonusRecord
        fields = ['xodim', 'sabab', 'izoh']
        widgets = {
            'izoh': forms.Textarea(attrs={'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.sabab:
            instance.pul_miqdori = instance.sabab.pul_miqdori
            instance.ball_miqdori = instance.sabab.ball_miqdori
        
        if commit:
            instance.save()
        return instance


class JarimaRecordForm(forms.ModelForm):
    class Meta:
        model = JarimaRecord
        fields = ['xodim', 'sabab', 'izoh']
        widgets = {
            'izoh': forms.Textarea(attrs={'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.sabab:
            instance.pul_miqdori = instance.sabab.pul_miqdori
            instance.ball_miqdori = instance.sabab.ball_miqdori
        
        if commit:
            instance.save()
        return instance


class XodimRasmForm(forms.ModelForm):
    class Meta:
        model = Xodim
        fields = ['rasm']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price_points', 'stock', 'is_coming_soon', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-xl'}),
            'category': forms.Select(attrs={'class': 'w-full p-3 border rounded-xl'}),
            'price_points': forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-xl'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-xl'}),
        }
        labels = {
            'name': 'Mahsulot nomi',
            'description': 'Tavsif',
            'image': 'Rasm',
            'category': 'Kategoriya',
            'price_points': 'Narxi (ball)',
            'stock': 'Ombordagi soni',
            'is_coming_soon': 'Tez orada',
            'is_active': 'Aktiv',
        }


class OrderRejectForm(forms.Form):
    reject_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-3 border rounded-xl'}),
        label="Rad etish sababi",
        required=True
    )