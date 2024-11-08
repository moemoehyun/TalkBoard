# myapp/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("半角英語、半角数字、特殊文字のどれかを2種類以上使い、８文字以上である必要があります")
            )

        has_letter = bool(re.search(r'[A-Za-z]', password))
        has_number = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+]', password))

        conditions_met = sum([has_letter, has_number, has_special])
        if conditions_met < 2:
            raise ValidationError(
                _("半角英語、半角数字、特殊文字のどれかを2種類以上使い、８文字以上である必要があります")
            )

    def get_help_text(self):
        return _("パスワードは半角英語、半角数字、特殊文字のどれかを2種類以上使い、８文字以上である必要があります。")
