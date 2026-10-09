from django import forms
from .models import Faq

class FaqForm(forms.ModelForm):
    class Meta:
        model = Faq
        fields = ['project', 'question', 'answer', 'question_en', 'answer_en', 'question_pt', 'answer_pt',
                  'order', 'is_published']
        labels = {
            'project': 'Proyecto',
            'question': 'Pregunta',
            'answer': 'Respuesta',
            'question_en': 'Pregunta (inglés)',
            'answer_en': 'Respuesta (inglés)',
            'question_pt': 'Pregunta (portugués)',
            'answer_pt': 'Respuesta (portugués)',
            'order': 'Orden',
            'is_published': 'Publicada',
        }
        help_texts = {
            'project': 'Dejalo vacío para una pregunta general (se muestra en la página de inicio).',
            'is_published': 'Si no está marcada, la pregunta no se muestra en la web.',
        }
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'question_en': forms.TextInput(attrs={'class': 'form-control'}),
            'answer_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'question_pt': forms.TextInput(attrs={'class': 'form-control'}),
            'answer_pt': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].empty_label = 'General (página de inicio)'

    def clean(self):
        cleaned_data = super().clean()
        ## A translation is optional, but half of one would show a question without its answer (or vice versa)
        for lang, name in (('en', 'inglés'), ('pt', 'portugués')):
            question, answer = cleaned_data.get(f'question_{lang}'), cleaned_data.get(f'answer_{lang}')
            if question and not answer:
                self.add_error(f'answer_{lang}', f'Completá la respuesta en {name} o borrá la pregunta.')
            elif answer and not question:
                self.add_error(f'question_{lang}', f'Completá la pregunta en {name} o borrá la respuesta.')
        return cleaned_data
