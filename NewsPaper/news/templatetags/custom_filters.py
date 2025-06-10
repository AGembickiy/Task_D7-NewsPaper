from django import template

register = template.Library()

@register.filter(name='censor')
def censor(value):
    variants = ['mat', 'abc', 'dolor', 'no', 'vel']  # непристойные выражения
    strk = value.split()
    for i in strk:
        if i in variants:
            strk[strk.index(i)] = f'{i[0]}{'*'*(len(i) - 1)}'
    return ' '.join(strk)


