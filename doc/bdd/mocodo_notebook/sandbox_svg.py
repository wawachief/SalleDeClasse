#!/usr/bin/env python
# encoding: utf-8
# Généré par Mocodo 2.3.7 le Mon, 06 Jul 2020 10:55:03

from __future__ import division
from math import hypot

import time, codecs

(width,height) = (697,411)
cx = {
    u"Students"     :   83,
    u"sitsAt"       :  237,
    u"Desks"        :  371,
    u"belongs to"   :  498,
    u"Courses"      :  637,
    u"IsIn"         :  237,
    u"Groups"       :  371,
    u"IsAbout"      :  637,
    u"HasAttributes":   83,
    u"StdAttrs"     :  237,
    u"Topics"       :  498,
    u"Attributes"   :   83,
    u"IsOfType"     :  237,
    u"AttrTypes"    :  371,
}
cy = {
    u"Students"     :   64,
    u"sitsAt"       :   64,
    u"Desks"        :   64,
    u"belongs to"   :   64,
    u"Courses"      :   64,
    u"IsIn"         :  173,
    u"Groups"       :  173,
    u"IsAbout"      :  173,
    u"HasAttributes":  264,
    u"StdAttrs"     :  264,
    u"Topics"       :  264,
    u"Attributes"   :  364,
    u"IsOfType"     :  364,
    u"AttrTypes"    :  364,
}
shift = {
    u"sitsAt,Students"         :    0,
    u"sitsAt,Desks"            :    0,
    u"belongs to,Courses"      :    0,
    u"belongs to,Desks"        :    0,
    u"IsIn,Students"           :    0,
    u"IsIn,Groups"             :    0,
    u"IsAbout,Courses"         :    0,
    u"IsAbout,Topics"          :    0,
    u"HasAttributes,StdAttrs"  :    0,
    u"HasAttributes,Students"  :    0,
    u"HasAttributes,Attributes":    0,
    u"HasAttributes,Topics"    :    0,
    u"IsOfType,AttrTypes"      :    0,
    u"IsOfType,Attributes"     :    0,
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
card_max_width = 20
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

lines += u"""\n\n<!-- Association sitsAt -->"""
(x,y) = (cx[u"sitsAt"],cy[u"sitsAt"])
(ex,ey) = (cx[u"Students"],cy[u"Students"])
leg=straight_leg_factory(ex,ey,51,55,x,y,36,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(True,shift[u"sitsAt,Students"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">0,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Desks"],cy[u"Desks"])
leg=straight_leg_factory(ex,ey,39,47,x,y,36,29,18+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"sitsAt,Desks"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,1</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-sitsAt">""" % {}
path = upper_round_rect(-36+x,-29+y,72,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-36+x,-1.0+y,72,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="72" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -36+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -36+x, 'y0': -1+y, 'x1': 36+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">sitsAt</text>""" % {'x': -29+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Association belongs to -->"""
(x,y) = (cx[u"belongs to"],cy[u"belongs to"])
(ex,ey) = (cx[u"Courses"],cy[u"Courses"])
leg=straight_leg_factory(ex,ey,51,38,x,y,58,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"belongs to,Courses"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Desks"],cy[u"Desks"])
leg=straight_leg_factory(ex,ey,39,47,x,y,58,29,18+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"belongs to,Desks"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,1</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-belongs to">""" % {}
path = upper_round_rect(-58+x,-29+y,116,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-58+x,-1.0+y,116,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="116" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -58+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -58+x, 'y0': -1+y, 'x1': 58+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">belongs to</text>""" % {'x': -51+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Association IsIn -->"""
(x,y) = (cx[u"IsIn"],cy[u"IsIn"])
(ex,ey) = (cx[u"Students"],cy[u"Students"])
leg=straight_leg_factory(ex,ey,51,55,x,y,25,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsIn,Students"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Groups"],cy[u"Groups"])
leg=straight_leg_factory(ex,ey,48,38,x,y,25,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsIn,Groups"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-IsIn">""" % {}
path = upper_round_rect(-25+x,-29+y,50,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-25+x,-1.0+y,50,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="50" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -25+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -25+x, 'y0': -1+y, 'x1': 25+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">IsIn</text>""" % {'x': -18+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Association IsAbout -->"""
(x,y) = (cx[u"IsAbout"],cy[u"IsAbout"])
(ex,ey) = (cx[u"Courses"],cy[u"Courses"])
leg=straight_leg_factory(ex,ey,51,38,x,y,43,29,18+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsAbout,Courses"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,1</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Topics"],cy[u"Topics"])
leg=straight_leg_factory(ex,ey,45,38,x,y,43,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsAbout,Topics"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-IsAbout">""" % {}
path = upper_round_rect(-43+x,-29+y,86,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-43+x,-1.0+y,86,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="86" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -43+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -43+x, 'y0': -1+y, 'x1': 43+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">IsAbout</text>""" % {'x': -36+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Association HasAttributes -->"""
(x,y) = (cx[u"HasAttributes"],cy[u"HasAttributes"])
(ex,ey) = (cx[u"StdAttrs"],cy[u"StdAttrs"])
leg=straight_leg_factory(ex,ey,50,38,x,y,74,29,18+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"HasAttributes,StdAttrs"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,1</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Students"],cy[u"Students"])
leg=straight_leg_factory(ex,ey,51,55,x,y,74,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(True,shift[u"HasAttributes,Students"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Attributes"],cy[u"Attributes"])
leg=straight_leg_factory(ex,ey,58,38,x,y,74,29,20+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"HasAttributes,Attributes"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">N,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Topics"],cy[u"Topics"])
leg=straight_leg_factory(ex,ey,45,38,x,y,74,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"HasAttributes,Topics"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-HasAttributes">""" % {}
path = upper_round_rect(-74+x,-29+y,148,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-74+x,-1.0+y,148,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="148" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -74+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -74+x, 'y0': -1+y, 'x1': 74+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">HasAttributes</text>""" % {'x': -67+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Association IsOfType -->"""
(x,y) = (cx[u"IsOfType"],cy[u"IsOfType"])
(ex,ey) = (cx[u"AttrTypes"],cy[u"AttrTypes"])
leg=straight_leg_factory(ex,ey,56,38,x,y,48,29,19+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsOfType,AttrTypes"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,N</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
(ex,ey) = (cx[u"Attributes"],cy[u"Attributes"])
leg=straight_leg_factory(ex,ey,58,38,x,y,48,29,18+2*card_margin,14+2*card_margin)
lines += u"""\n<line x1="%(ex)s" y1="%(ey)s" x2="%(ax)s" y2="%(ay)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'ex': ex, 'ey': ey, 'ax': x, 'ay': y, 'stroke_color': colors['leg_stroke_color']}
(tx,ty)=offset(*leg.card_pos(False,shift[u"IsOfType,Attributes"]))
lines += u"""\n<text x="%(tx)s" y="%(ty)s" fill="%(text_color)s" font-family="Futura" font-size="11">1,1</text>""" % {'tx': tx, 'ty': ty, 'text_color': colors['card_text_color']}
lines += u"""\n<g id="association-IsOfType">""" % {}
path = upper_round_rect(-48+x,-29+y,96,28,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_cartouche_color'], 'stroke_color': colors['association_cartouche_color']}
path = lower_round_rect(-48+x,-1.0+y,96,30,14)
lines += u"""\n	<path d="%(path)s" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'path': path, 'color': colors['association_color'], 'stroke_color': colors['association_color']}
lines += u"""\n	<rect x="%(x)s" y="%(y)s" width="96" height="58" fill="%(color)s" rx="14" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -48+x, 'y': -29+y, 'color': colors['transparent_color'], 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -48+x, 'y0': -1+y, 'x1': 48+x, 'y1': -1+y, 'stroke_color': colors['association_stroke_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">IsOfType</text>""" % {'x': -41+x, 'y': -7.7+y, 'text_color': colors['association_cartouche_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Students -->"""
(x,y) = (cx[u"Students"],cy[u"Students"])
lines += u"""\n<g id="entity-Students">""" % {}
lines += u"""\n	<g id="frame-Students">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -51+x, 'y': -55+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="80" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -51+x, 'y': -25.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="110" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -51+x, 'y': -55+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -51+x, 'y0': -25+y, 'x1': 51+x, 'y1': -25+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Students</text>""" % {'x': -43+x, 'y': -33.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdStudent</text>""" % {'x': -43+x, 'y': -7.9+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -43+x, 'y0': -5+y, 'x1': 17+x, 'y1': -5+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">StdFirstname</text>""" % {'x': -43+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">StdLastname</text>""" % {'x': -43+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">OrderKey</text>""" % {'x': -43+x, 'y': 43.0+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Desks -->"""
(x,y) = (cx[u"Desks"],cy[u"Desks"])
lines += u"""\n<g id="entity-Desks">""" % {}
lines += u"""\n	<g id="frame-Desks">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="78" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -39+x, 'y': -47+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="78" height="64" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -39+x, 'y': -17.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="78" height="94" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -39+x, 'y': -47+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -39+x, 'y0': -17+y, 'x1': 39+x, 'y1': -17+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Desks</text>""" % {'x': -27+x, 'y': -25.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdDesk</text>""" % {'x': -31+x, 'y': 0.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -31+x, 'y0': 3+y, 'x1': 14+x, 'y1': 3+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">DeskRow</text>""" % {'x': -31+x, 'y': 17.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">DeskCol</text>""" % {'x': -31+x, 'y': 34.0+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Courses -->"""
(x,y) = (cx[u"Courses"],cy[u"Courses"])
lines += u"""\n<g id="entity-Courses">""" % {}
lines += u"""\n	<g id="frame-Courses">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -51+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -51+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="102" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -51+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -51+x, 'y0': -8+y, 'x1': 51+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Courses</text>""" % {'x': -39+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdCourse</text>""" % {'x': -43+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -43+x, 'y0': 12+y, 'x1': 16+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">CourseName</text>""" % {'x': -43+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Groups -->"""
(x,y) = (cx[u"Groups"],cy[u"Groups"])
lines += u"""\n<g id="entity-Groups">""" % {}
lines += u"""\n	<g id="frame-Groups">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -48+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="96" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -48+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -48+x, 'y0': -8+y, 'x1': 48+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Groups</text>""" % {'x': -34+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdGroup</text>""" % {'x': -40+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -40+x, 'y0': 12+y, 'x1': 14+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">GroupName</text>""" % {'x': -40+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity StdAttrs -->"""
(x,y) = (cx[u"StdAttrs"],cy[u"StdAttrs"])
lines += u"""\n<g id="entity-StdAttrs">""" % {}
lines += u"""\n	<g id="frame-StdAttrs">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="100" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -50+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="100" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -50+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="100" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -50+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -50+x, 'y0': -8+y, 'x1': 50+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">StdAttrs</text>""" % {'x': -42+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdStdAttr</text>""" % {'x': -42+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -42+x, 'y0': 12+y, 'x1': 17+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">StdAttrValue</text>""" % {'x': -42+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Topics -->"""
(x,y) = (cx[u"Topics"],cy[u"Topics"])
lines += u"""\n<g id="entity-Topics">""" % {}
lines += u"""\n	<g id="frame-Topics">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="90" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -45+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="90" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -45+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="90" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -45+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -45+x, 'y0': -8+y, 'x1': 45+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Topics</text>""" % {'x': -30+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdTopic</text>""" % {'x': -37+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -37+x, 'y0': 12+y, 'x1': 11+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">TopicName</text>""" % {'x': -37+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity Attributes -->"""
(x,y) = (cx[u"Attributes"],cy[u"Attributes"])
lines += u"""\n<g id="entity-Attributes">""" % {}
lines += u"""\n	<g id="frame-Attributes">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="116" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -58+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="116" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -58+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="116" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -58+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -58+x, 'y0': -8+y, 'x1': 58+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">Attributes</text>""" % {'x': -50+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdAttr</text>""" % {'x': -50+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -50+x, 'y0': 12+y, 'x1': -11+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">AttrName</text>""" % {'x': -50+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}

lines += u"""\n\n<!-- Entity AttrTypes -->"""
(x,y) = (cx[u"AttrTypes"],cy[u"AttrTypes"])
lines += u"""\n<g id="entity-AttrTypes">""" % {}
lines += u"""\n	<g id="frame-AttrTypes">""" % {}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="30" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -56+x, 'y': -38+y, 'color': colors['entity_cartouche_color'], 'stroke_color': colors['entity_cartouche_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="46" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="0"/>""" % {'x': -56+x, 'y': -8.0+y, 'color': colors['entity_color'], 'stroke_color': colors['entity_color']}
lines += u"""\n		<rect x="%(x)s" y="%(y)s" width="112" height="76" fill="%(color)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x': -56+x, 'y': -38+y, 'color': colors['transparent_color'], 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n		<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1.5"/>""" % {'x0': -56+x, 'y0': -8+y, 'x1': 56+x, 'y1': -8+y, 'stroke_color': colors['entity_stroke_color']}
lines += u"""\n	</g>""" % {}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Copperplate" font-size="18">AttrTypes</text>""" % {'x': -47+x, 'y': -16.7+y, 'text_color': colors['entity_cartouche_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">IdAttrType</text>""" % {'x': -48+x, 'y': 9.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n	<line x1="%(x0)s" y1="%(y0)s" x2="%(x1)s" y2="%(y1)s" stroke="%(stroke_color)s" stroke-width="1"/>""" % {'x0': -48+x, 'y0': 12+y, 'x1': 22+x, 'y1': 12+y, 'stroke_color': colors['entity_attribute_text_color']}
lines += u"""\n	<text x="%(x)s" y="%(y)s" fill="%(text_color)s" font-family="Gill Sans" font-size="15">AttrTypeName</text>""" % {'x': -48+x, 'y': 26.1+y, 'text_color': colors['entity_attribute_text_color']}
lines += u"""\n</g>""" % {}
lines += u'\n</svg>'

with codecs.open("mocodo_notebook/sandbox.svg", "w", "utf8") as f:
    f.write(lines)
safe_print_for_PHP(u'Fichier de sortie "mocodo_notebook/sandbox.svg" généré avec succès.')