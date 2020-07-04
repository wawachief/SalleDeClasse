#!/usr/bin/env python
# encoding: utf-8
# Généré par Mocodo 2.3.7 le Sat, 04 Jul 2020 10:57:44

from __future__ import division
from math import hypot

import time, codecs

(width,height) = (520,142)
cx = {
    u"Students":   98,
    u"Desks"   :  268,
    u"Courses" :  430,
}
cy = {
    u"Students":   71,
    u"Desks"   :   71,
    u"Courses" :   71,
}
colors = {
    u"annotation_color"                : '#8c510a',
    u"annotation_text_color"           : '#f5f5f5',
    u"association_attribute_text_color": '#000000',
    u"association_cartouche_color"     : '#dfc27d',
    u"association_cartouche_text_color": '#000000',
    u"association_color"               : '#f6e8c3',
    u"association_stroke_color"        : '#bf812d',
    u"background_color"                : '#f5f5f5',
    u"card_text_color"                 : '#01665e',
    u"entity_attribute_text_color"     : '#000000',
    u"entity_cartouche_color"          : '#80cdc1',
    u"entity_cartouche_text_color"     : '#000000',
    u"entity_color"                    : '#c7eae5',
    u"entity_stroke_color"             : '#35978f',
    u"leg_stroke_color"                : '#bf812d',
    u"transparent_color"               : 'none',
}
card_max_width = 23
card_max_height = 14
card_margin = 5
arrow_width = 12
arrow_half_height = 6
arrow_axis = 8
card_baseline = 3

def cmp(x, y):
    return (x > y) - (x < y)

def offset(x, y):
    return (x + card_margin, y - card_baseline - card_margin)

def line_intersection(ex, ey, w, h, ax, ay):
    if ax == ex:
        return (ax, ey + cmp(ay, ey) * h)
    if ay == ey:
        return (ex + cmp(ax, ex) * w, ay)
    x = ex + cmp(ax, ex) * w
    y = ey + (ay-ey) * (x-ex) / (ax-ex)
    if abs(y-ey) > h:
        y = ey + cmp(ay, ey) * h
        x = ex + (ax-ex) * (y-ey) / (ay-ey)
    return (x, y)

def straight_leg_factory(ex, ey, ew, eh, ax, ay, aw, ah, cw, ch):
    
    def card_pos(twist, shift):
        compare = (lambda x1_y1: x1_y1[0] < x1_y1[1]) if twist else (lambda x1_y1: x1_y1[0] <= x1_y1[1])
        diagonal = hypot(ax-ex, ay-ey)
        correction = card_margin * 1.4142 * (1 - abs(abs(ax-ex) - abs(ay-ey)) / diagonal) - shift
        (xg, yg) = line_intersection(ex, ey, ew, eh + ch, ax, ay)
        (xb, yb) = line_intersection(ex, ey, ew + cw, eh, ax, ay)
        if compare((xg, xb)):
            if compare((xg, ex)):
                if compare((yb, ey)):
                    return (xb - correction, yb)
                return (xb - correction, yb + ch)
            if compare((yb, ey)):
                return (xg, yg + ch - correction)
            return (xg, yg + correction)
        if compare((xb, ex)):
            if compare((yb, ey)):
                return (xg - cw, yg + ch - correction)
            return (xg - cw, yg + correction)
        if compare((yb, ey)):
            return (xb - cw + correction, yb)
        return (xb - cw + correction, yb + ch)
    
    def arrow_pos(direction, ratio):
        (x0, y0) = line_intersection(ex, ey, ew, eh, ax, ay)
        (x1, y1) = line_intersection(ax, ay, aw, ah, ex, ey)
        if direction == "<":
            (x0, y0, x1, y1) = (x1, y1, x0, y0)
        (x, y) = (ratio * x0 + (1 - ratio) * x1, ratio * y0 + (1 - ratio) * y1)
        return (x, y, x1 - x0, y0 - y1)
    
    straight_leg_factory.card_pos = card_pos
    straight_leg_factory.arrow_pos = arrow_pos
    return straight_leg_factory


def curved_leg_factory(ex, ey, ew, eh, ax, ay, aw, ah, cw, ch, spin):
    
    def bisection(predicate):
        (a, b) = (0, 1)
        while abs(b - a) > 0.0001:
            m = (a + b) / 2
            if predicate(bezier(m)):
                a = m
            else:
                b = m
        return m
    
    def intersection(left, top, right, bottom):
       (x, y) = bezier(bisection(lambda p: left <= p[0] <= right and top <= p[1] <= bottom))
       return (int(round(x)), int(round(y)))
    
    def card_pos(shift):
        diagonal = hypot(ax-ex, ay-ey)
        correction = card_margin * 1.4142 * (1 - abs(abs(ax-ex) - abs(ay-ey)) / diagonal)
        (top, bot) = (ey - eh, ey + eh)
        (TOP, BOT) = (top - ch, bot + ch)
        (lef, rig) = (ex - ew, ex + ew)
        (LEF, RIG) = (lef - cw, rig + cw)
        (xr, yr) = intersection(LEF, TOP, RIG, BOT)
        (xg, yg) = intersection(lef, TOP, rig, BOT)
        (xb, yb) = intersection(LEF, top, RIG, bot)
        if spin > 0:
            if (yr == BOT and xr <= rig) or (xr == LEF and yr >= bot):
                return (max(x for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if y >= bot) - correction + shift, bot + ch)
            if (xr == RIG and yr >= top) or yr == BOT:
                return (rig, min(y for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if x >= rig) + correction + shift)
            if (yr == TOP and xr >= lef) or xr == RIG:
                return (min(x for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if y <= top) + correction + shift - cw, TOP + ch)
            return (LEF, max(y for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if x <= lef) - correction + shift + ch)
        if (yr == BOT and xr >= lef) or (xr == RIG and yr >= bot):
            return (min(x for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if y >= bot) + correction + shift - cw, bot + ch)
        if xr == RIG or (yr == TOP and xr >= rig):
            return (rig, max(y for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if x >= rig) - correction + shift + ch)
        if yr == TOP or (xr == LEF and yr <= top):
            return (max(x for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if y <= top) - correction + shift, TOP + ch)
        return (LEF, min(y for (x, y) in ((xr, yr), (xg, yg), (xb, yb)) if x <= lef) + correction + shift)
    
    def arrow_pos(direction, ratio):
        t0 = bisection(lambda p: abs(p[0] - ax) > aw or abs(p[1] - ay) > ah)
        t3 = bisection(lambda p: abs(p[0] - ex) < ew and abs(p[1] - ey) < eh)
        if direction == "<":
            (t0, t3) = (t3, t0)
        tc = t0 + (t3 - t0) * ratio
        (xc, yc) = bezier(tc)
        (x, y) = derivate(tc)
        if direction == "<":
            (x, y) = (-x, -y)
        return (xc, yc, x, -y)
    
    diagonal = hypot(ax - ex, ay - ey)
    (x, y) = line_intersection(ex, ey, ew + cw / 2, eh + ch / 2, ax, ay)
    k = (cw *  abs((ay - ey) / diagonal) + ch * abs((ax - ex) / diagonal))
    (x, y) = (x - spin * k * (ay - ey) / diagonal, y + spin * k * (ax - ex) / diagonal)
    (hx, hy) = (2 * x - (ex + ax) / 2, 2 * y - (ey + ay) / 2)
    (x1, y1) = (ex + (hx - ex) * 2 / 3, ey + (hy - ey) * 2 / 3)
    (x2, y2) = (ax + (hx - ax) * 2 / 3, ay + (hy - ay) * 2 / 3)
    (kax, kay) = (ex - 2 * hx + ax, ey - 2 * hy + ay)
    (kbx, kby) = (2 * hx - 2 * ex, 2 * hy - 2 * ey)
    bezier = lambda t: (kax*t*t + kbx*t + ex, kay*t*t + kby*t + ey)
    derivate = lambda t: (2*kax*t + kbx, 2*kay*t + kby)
    
    curved_leg_factory.points = (ex, ey, x1, y1, x2, y2, ax, ay)
    curved_leg_factory.card_pos = card_pos
    curved_leg_factory.arrow_pos = arrow_pos
    return curved_leg_factory


def upper_round_rect(x, y, w, h, r):
    return " ".join([str(x) for x in ["M", x + w - r, y, "a", r, r, 90, 0, 1, r, r, "V", y + h, "h", -w, "V", y + r, "a", r, r, 90, 0, 1, r, -r]])

def lower_round_rect(x, y, w, h, r):
    return " ".join([str(x) for x in ["M", x + w, y, "v", h - r, "a", r, r, 90, 0, 1, -r, r, "H", x + r, "a", r, r, 90, 0, 1, -r, -r, "V", y, "H", w]])

def arrow(x, y, a, b):
    c = hypot(a, b)
    (cos, sin) = (a / c, b / c)
    return " ".join([str(x) for x in [ "M", x, y, "L", x + arrow_width * cos - arrow_half_height * sin, y - arrow_half_height * cos - arrow_width * sin, "L", x + arrow_axis * cos, y - arrow_axis * sin, "L", x + arrow_width * cos + arrow_half_height * sin, y + arrow_half_height * cos - arrow_width * sin, "Z"]])

def safe_print_for_PHP(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("utf8"))


lines = '<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
lines += '\n\n<svg width="%s" height="%s" view_box="0 0 %s %s"\nxmlns="http://www.w3.org/2000/svg"\nxmlns:link="http://www.w3.org/1999/xlink">' % (width,height,width,height)
lines += u'\\n\\n<desc>Généré par Mocodo 2.3.7 le %s</desc>' % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
lines += '\n\n<rect id="frame" x="0" y="0" width="%s" height="%s" fill="%s" stroke="none" stroke-width="0"/>' % (width,height,colors['background_color'] if colors['background_color'] else "none")

lines += u"""\n\n<!-- Entity Students -->"""
(x,y) = (cx[u"Students"],cy[u"Students"])
lines += u"""\n<g id="entity-Students">""" % {}
lines += u"""\n	<g id="frame-Students">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="26" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -56+x, 'y': -44+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="62" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -56+x, 'y': -18.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="88" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -56+x, 'y': -44+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -56+x, 'y0': -18+y, 'x1': 56+x, 'y1': -18+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">Students</text>""" % {'x': -34+x, 'y': -25.4+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">IdStudent</text>""" % {'x': -51+x, 'y': 0.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -51+x, 'y0': 3.0+y, 'x1': 26+x, 'y1': 3.0+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">StdFirstname</text>""" % {'x': -51+x, 'y': 18.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">StdLastname</text>""" % {'x': -51+x, 'y': 36.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Desks -->"""
(x,y) = (cx[u"Desks"],cy[u"Desks"])
lines += u"""\n<g id="entity-Desks">""" % {}
lines += u"""\n	<g id="frame-Desks">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="26" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -62+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="98" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -36.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="124" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -48+x, 'y': -62+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -48+x, 'y0': -36+y, 'x1': 48+x, 'y1': -36+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">Desks</text>""" % {'x': -22+x, 'y': -43.4+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">IdDesk</text>""" % {'x': -43+x, 'y': -17.4+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -43+x, 'y0': -15.0+y, 'x1': 9+x, 'y1': -15.0+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">DeskRow</text>""" % {'x': -43+x, 'y': 0.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">DeskCol</text>""" % {'x': -43+x, 'y': 18.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">#IdStudent</text>""" % {'x': -43+x, 'y': 36.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">#IdCourse</text>""" % {'x': -43+x, 'y': 54.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Courses -->"""
(x,y) = (cx[u"Courses"],cy[u"Courses"])
lines += u"""\n<g id="entity-Courses">""" % {}
lines += u"""\n	<g id="frame-Courses">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="26" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -35+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="44" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -9.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="70" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -48+x, 'y': -35+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -48+x, 'y0': -9+y, 'x1': 48+x, 'y1': -9+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">Courses</text>""" % {'x': -30+x, 'y': -16.4+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">IdCourse</text>""" % {'x': -43+x, 'y': 9.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -43+x, 'y0': 12.0+y, 'x1': 25+x, 'y1': 12.0+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Courier New" font-size="14">CourseName</text>""" % {'x': -43+x, 'y': 27.6+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}
(fs,ps) = (min([(-1, -1), (1, -1), (-1, 1), (1, 1)], key=lambda fs_ps: abs(cx[u"Desks"]+48*fs_ps[0] - cx[u"Students"]-56*fs_ps[1])))
(xf,yf,xp,yp) = (cx[u"Desks"]+48*fs,cy[u"Desks"]+32.0,cx[u"Students"]+56*ps,cy[u"Students"]+-4.0)
lines += u"""\n<path d="M%(x0)s %(y0)s C %(x1)s %(y1)s %(x2)s %(y2)s %(x3)s %(y3)s" fill="none" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': xf, 'y0': yf, 'x1': xf+(xp-xf)/2 if fs != ps else xf+56*fs, 'y1': yf+(yp-yf)/2, 'x2': xf+(xp-xf)/3 if fs != ps else xp+56*ps, 'y2': yp, 'x3': xp, 'y3': yp, 'stroke_color': colors['leg_stroke_color']}
path = arrow(xp,yp,ps,0)
lines += u"""\n<path d="%(path)s" fill="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'stroke_color': colors['leg_stroke_color']}
lines += u"""\n<circle cx="%(cx)s" cy="%(cy)s" r="1.5" stroke="%(stroke_color)s" stroke-width="1.5" fill="%(color)s"/>""" % {'cx': xf, 'cy': yf, 'stroke_color': colors['leg_stroke_color'], 'color': colors['leg_stroke_color']}
(fs,ps) = (min([(1, 1), (-1, 1), (1, -1), (-1, -1)], key=lambda fs_ps: abs(cx[u"Desks"]+48*fs_ps[0] - cx[u"Courses"]-48*fs_ps[1])))
(xf,yf,xp,yp) = (cx[u"Desks"]+48*fs,cy[u"Desks"]+50.0,cx[u"Courses"]+48*ps,cy[u"Courses"]+5.0)
lines += u"""\n<path d="M%(x0)s %(y0)s C %(x1)s %(y1)s %(x2)s %(y2)s %(x3)s %(y3)s" fill="none" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': xf, 'y0': yf, 'x1': xf+(xp-xf)/2 if fs != ps else xf+56*fs, 'y1': yf+(yp-yf)/2, 'x2': xf+(xp-xf)/3 if fs != ps else xp+56*ps, 'y2': yp, 'x3': xp, 'y3': yp, 'stroke_color': colors['leg_stroke_color']}
path = arrow(xp,yp,ps,0)
lines += u"""\n<path d="%(path)s" fill="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'stroke_color': colors['leg_stroke_color']}
lines += u"""\n<circle cx="%(cx)s" cy="%(cy)s" r="1.5" stroke="%(stroke_color)s" stroke-width="1.5" fill="%(color)s"/>""" % {'cx': xf, 'cy': yf, 'stroke_color': colors['leg_stroke_color'], 'color': colors['leg_stroke_color']}
lines += u'\n</svg>'

with codecs.open("mocodo_notebook/sandbox.svg", "w", "utf8") as f:
    f.write(lines)
safe_print_for_PHP(u'Fichier de sortie "mocodo_notebook/sandbox.svg" généré avec succès.')