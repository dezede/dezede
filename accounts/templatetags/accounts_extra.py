from django.template import Library


register = Library()


@register.simple_tag
def hsv_to_hex(h, s, v):
    """
    >>> print(hsv_to_hex(0, 0, 0))
    #000000
    >>> print(hsv_to_hex(0, 0, 1))
    #FFFFFF
    >>> print(hsv_to_hex(0, 1, 1))
    #FF0000
    >>> print(hsv_to_hex(120, 1, 1))
    #00FF00
    >>> print(hsv_to_hex(240, 1, 1))
    #0000FF
    >>> print(hsv_to_hex(60, 1, 1))
    #FFFF00
    >>> print(hsv_to_hex(180, 1, 1))
    #00FFFF
    >>> print(hsv_to_hex(300, 1, 1))
    #FF00FF
    >>> print(hsv_to_hex(0, 0, .75))
    #C0C0C0
    >>> print(hsv_to_hex(0, 0, .5))
    #808080
    >>> print(hsv_to_hex(0, 1, .5))
    #800000
    >>> print(hsv_to_hex(60, 1, .5))
    #808000
    >>> print(hsv_to_hex(120, 1, .5))
    #008000
    >>> print(hsv_to_hex(300, 1, .5))
    #800080
    >>> print(hsv_to_hex(180, 1, .5))
    #008080
    >>> print(hsv_to_hex(240, 1, .5))
    #000080
    >>> print(hsv_to_hex(220, .95, 1))
    #0C5DFF
    """
    # Implementation of http://www.rapidtables.com/convert/color/hsv-to-rgb.htm
    h %= 360

    if not (0 <= s <= 1 and 0 <= v <= 1):
        raise ValueError('`s` and `v` must be between 0 and 1.')

    c = v * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = v - c
    if 0 <= h < 60:
        t = c, x, 0
    elif 60 <= h < 120:
        t = x, c, 0
    elif 120 <= h < 180:
        t = 0, c, x
    elif 180 <= h < 240:
        t = 0, x, c
    elif 240 <= h < 300:
        t = x, 0, c
    elif 300 <= h < 360:
        t = c, 0, x
    else:
        raise ValueError('`h` should be between 0 and 359.')
    r2, g2, b2 = t
    r, g, b = r2 + m, g2 + m, b2 + m

    def to_hex(color):
        return hex(int(min(255, color * 256)))[2:].upper().zfill(2)

    return '#' + to_hex(r) + to_hex(g) + to_hex(b)
