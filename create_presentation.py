"""
FraudShield AI — Presentation PowerPoint (Francais, version simplifiee)
"""

import io
import math
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Couleurs ─────────────────────────────────────────────────────────────────
BG_DARK      = RGBColor(0x05, 0x08, 0x13)
BG_CARD      = RGBColor(0x08, 0x0E, 0x1F)
CYAN         = RGBColor(0x00, 0xF5, 0xFF)
CYAN_DARK    = RGBColor(0x06, 0xB6, 0xD4)
PURPLE       = RGBColor(0x7C, 0x3A, 0xED)
PURPLE_LIGHT = RGBColor(0xA8, 0x55, 0xF7)
FRAUD_RED    = RGBColor(0xFF, 0x2D, 0x55)
SAFE_GREEN   = RGBColor(0x00, 0xD6, 0x8F)
WARNING      = RGBColor(0xFF, 0xB8, 0x00)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
WHITE_60     = RGBColor(0x99, 0x9A, 0xA0)
CARD2        = RGBColor(0x0C, 0x12, 0x28)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H


# ── Helpers ──────────────────────────────────────────────────────────────────

def new_slide():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    # Barre verticale gauche (sera definie par chaque slide)
    return slide

def bar(slide, color):
    s = slide.shapes.add_shape(1, 0, 0, Inches(0.07), H)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()

def rect(slide, l, t, w, h, fill=None, border=None, bw=Pt(1)):
    s = slide.shapes.add_shape(1, l, t, w, h)
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if border:
        s.line.color.rgb = border; s.line.width = bw
    else:
        s.line.fill.background()
    return s

def txt(slide, text, l, t, w, h, size=Pt(14), bold=False,
        color=WHITE, align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = size
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.italic = italic
    return tb

def line(slide, l, t, length, color=CYAN, vertical=False):
    if vertical:
        s = slide.shapes.add_shape(1, l, t, Inches(0.02), length)
    else:
        s = slide.shapes.add_shape(1, l, t, length, Inches(0.02))
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background()

def section_header(slide, label, title, color):
    bar(slide, color)
    txt(slide, label, Inches(0.5), Inches(0.28), Inches(6), Inches(0.4),
        size=Pt(11), bold=True, color=color)
    txt(slide, title, Inches(0.5), Inches(0.75), Inches(12), Inches(0.75),
        size=Pt(38), bold=True, color=WHITE)
    line(slide, Inches(0.5), Inches(1.6), Inches(5), color=color)

def img_to_slide(slide, img, l, t, w, h):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    slide.shapes.add_picture(buf, l, t, w, h)

def card(slide, l, t, w, h, accent=None):
    rect(slide, l, t, w, h, fill=BG_CARD)
    if accent:
        rect(slide, l, t, Inches(0.06), h, fill=accent)


# ── Images 3D ────────────────────────────────────────────────────────────────

def globe_3d(size=500):
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy, r = size//2, size//2, size//2 - 18

    # Halo
    for i in range(35, 0, -1):
        a = int(70*(i/35)**2)
        draw.ellipse([cx-r-i*2, cy-r-i*2, cx+r+i*2, cy+r+i*2],
                     outline=(0,245,255,a), width=2)

    # Sphere
    for y in range(cy-r, cy+r+1):
        dy = y - cy
        if abs(dy) > r: continue
        dx = int(math.sqrt(r*r - dy*dy))
        t = (y-(cy-r))/(2*r)
        c = int(8+25*t)
        draw.line([(cx-dx,y),(cx+dx,y)], fill=(c,c+5,c+28,215))

    # Lignes latitude
    for lat in range(-75, 76, 20):
        lr = math.radians(lat)
        rz = r*math.sin(lr)
        screen_y = cy - int(rz)
        rx = int(math.sqrt(max(0, r*r - rz*rz)))
        ry = r*math.cos(lr)
        if rx > 2:
            draw.ellipse([cx-rx, screen_y-int(ry*0.28),
                          cx+rx, screen_y+int(ry*0.28)],
                         outline=(0,180,200,110), width=1)

    # Lignes longitude
    for lon in range(0, 180, 25):
        lr2 = math.radians(lon)
        pts = []
        for lat in range(-90, 91, 4):
            la = math.radians(lat)
            x3 = r*math.cos(la)*math.sin(lr2)
            y3 = r*math.sin(la)
            pts.append((int(cx+x3), int(cy-y3)))
        for i in range(len(pts)-1):
            draw.line([pts[i], pts[i+1]], fill=(0,190,210,90), width=1)

    # Equateur brillant
    draw.ellipse([cx-r, cy-int(r*0.22), cx+r, cy+int(r*0.22)],
                 outline=(0,245,255,200), width=2)

    # Noeuds lumineux
    for nx, ny in [(0.3,-0.5),(-0.5,0.2),(0.6,0.3),(-0.2,0.65),(0.1,-0.1)]:
        px, py2 = int(cx+nx*r), int(cy+ny*r)
        for gi in range(8,0,-2):
            draw.ellipse([px-gi,py2-gi,px+gi,py2+gi], fill=(0,245,255,int(140*(gi/8)**2)))
        draw.ellipse([px-3,py2-3,px+3,py2+3], fill=(255,255,255,230))

    draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline=(0,245,255,255), width=3)
    return img.filter(ImageFilter.GaussianBlur(0.4))


def pipeline_img(size=(1100, 300)):
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    W2, H2 = size

    steps = [
        ("1. Donnees",    (0,245,255),  "Collecte\n100K transac."),
        ("2. Validation", (255,184,0),  "Verification\nqualite"),
        ("3. Preparation",(168,85,247), "Nettoyage\n+ SMOTE"),
        ("4. Entrainement",(0,214,143), "XGBoost\nLightGBM"),
        ("5. Evaluation",  (0,245,255), "Mesure\nperformance"),
        ("6. Deploiement", (255,45,85), "Mise en\nproduction"),
    ]

    n = len(steps)
    bw = int(W2 / (n*1.6))
    gap = int(bw*0.6)
    bh = int(H2*0.72)
    total = n*bw + (n-1)*gap
    sx = (W2 - total)//2
    sy = (H2 - bh)//2

    for i, (label, col, desc) in enumerate(steps):
        x = sx + i*(bw+gap)
        d = 7

        dark = tuple(max(0,c//3) for c in col)
        draw.polygon([(x+bw,sy),(x+bw+d,sy-d),(x+bw+d,sy+bh-d),(x+bw,sy+bh)], fill=dark+(170,))
        draw.polygon([(x,sy+bh),(x+d,sy+bh-d),(x+bw+d,sy+bh-d),(x+bw,sy+bh)], fill=dark+(150,))

        for dy in range(bh):
            t = dy/bh
            r2=int(col[0]*(0.12+0.06*t)); g2=int(col[1]*(0.12+0.06*t)); b2=int(col[2]*(0.12+0.06*t))
            draw.line([(x,sy+dy),(x+bw,sy+dy)], fill=(r2,g2,b2,215))

        draw.rectangle([x,sy,x+bw,sy+bh], outline=col+(255,), width=2)

        # Numero
        cx2 = x + bw//2
        for gi in range(10,0,-3):
            draw.ellipse([cx2-gi,sy+10-gi,cx2+gi,sy+10+gi], fill=col+(int(100*(gi/10)**2),))
        draw.ellipse([cx2-8,sy+2,cx2+8,sy+18], fill=col+(255,))

        # Fleche
        if i < n-1:
            ax = x+bw+gap//2
            ay = sy+bh//2
            draw.line([(x+bw+2,ay),(ax+gap//2-2,ay)], fill=(0,245,255,190), width=2)
            draw.polygon([(ax+gap//2-2,ay-5),(ax+gap//2+6,ay),(ax+gap//2-2,ay+5)],
                         fill=(0,245,255,210))

    return img


def bar_chart_3d(size=(650, 320)):
    img = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    W2, H2 = size

    data = [
        ("Score F1",   0.923, (0,245,255)),
        ("Precision",  0.941, (168,85,247)),
        ("Rappel",     0.906, (0,214,143)),
        ("ROC-AUC",    0.987, (255,184,0)),
        ("AUC-PR",     0.951, (255,45,85)),
    ]

    bw = int(W2/(len(data)*2+1))
    d = 9
    ch = H2 - 70

    for i, (label, val, col) in enumerate(data):
        x = bw + i*(bw*2)
        bh = int(ch * val)
        y = 15 + (ch - bh)

        dark = tuple(max(0,c//3) for c in col)
        draw.polygon([(x+bw,y),(x+bw+d,y-d),(x+bw+d,H2-55-d),(x+bw,H2-55)], fill=dark+(170,))
        draw.polygon([(x,y),(x+d,y-d),(x+bw+d,y-d),(x+bw,y)],
                     fill=(min(255,col[0]+60),min(255,col[1]+60),min(255,col[2]+60),190))

        for dy in range(bh):
            t = dy/bh
            r2=int(col[0]*(0.18+0.55*t)); g2=int(col[1]*(0.18+0.55*t)); b2=int(col[2]*(0.18+0.55*t))
            draw.line([(x,y+dy),(x+bw,y+dy)], fill=(r2,g2,b2,215))

        draw.rectangle([x,y,x+bw,H2-55], outline=col+(255,), width=2)

        val_text = f"{val:.0%}"
        draw.rectangle([x-2,y-20,x+bw+2,y-4], fill=(8,14,31,180))
        draw.text((x+bw//2-14, y-18), val_text, fill=col+(255,))
        draw.text((x+bw//2-18, H2-48), label, fill=(170,180,195,200))

    for pct in [0.5, 1.0]:
        gy = 15 + int(ch*(1-pct))
        draw.line([(0,gy),(W2,gy)], fill=(255,255,255,18), width=1)

    return img


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDES
# ═══════════════════════════════════════════════════════════════════════════════

# ── Slide 1 : Titre ──────────────────────────────────────────────────────────
def slide_titre():
    slide = new_slide()

    # Grille de fond subtile
    for i in range(0, int(W), int(Inches(0.65))):
        s = slide.shapes.add_shape(1, i, 0, Pt(1), H)
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor(0x0A,0x10,0x22)
        s.line.fill.background()

    bar(slide, CYAN)

    # Globe 3D
    g = globe_3d(480)
    img_to_slide(slide, g, Inches(8.8), Inches(0.4), Inches(4.3), Inches(4.3))

    # Titre
    txt(slide, "FraudShield AI",
        Inches(0.6), Inches(1.3), Inches(7.8), Inches(1.3),
        size=Pt(60), bold=True, color=CYAN)

    txt(slide, "Detecter la fraude bancaire grace a l'intelligence artificielle",
        Inches(0.6), Inches(2.75), Inches(7.5), Inches(0.9),
        size=Pt(20), color=WHITE_60)

    line(slide, Inches(0.6), Inches(3.7), Inches(6.5))

    txt(slide, "Machine Learning  •  Traitement en temps reel  •  Tableau de bord interactif",
        Inches(0.6), Inches(3.95), Inches(9), Inches(0.5),
        size=Pt(14), color=CYAN_DARK)

    # Bas de page
    rect(slide, 0, Inches(6.85), W, Inches(0.65), fill=BG_CARD)
    txt(slide, "Projet de detection de fraude par carte bancaire  |  2025",
        Inches(0.5), Inches(6.92), Inches(12), Inches(0.45),
        size=Pt(12), color=WHITE_60)


# ── Slide 2 : C'est quoi le probleme ? ───────────────────────────────────────
def slide_probleme():
    slide = new_slide()
    section_header(slide, "LE PROBLEME", "Pourquoi detecter la fraude ?", FRAUD_RED)

    # Stats visuelles
    stats = [
        ("32 milliards $", "de pertes annuelles\nmondiales dues a la fraude", FRAUD_RED),
        ("1 transaction\nsur 50",   "est potentiellement\nfrauduleuse (2%)", WARNING),
        ("< 1 seconde",  "pour analyser\nchaque transaction", CYAN),
        ("Millions",     "de transactions\ntraitees par jour", PURPLE_LIGHT),
    ]

    for i, (val, desc, col) in enumerate(stats):
        x = Inches(0.4 + i*3.2)
        rect(slide, x, Inches(1.9), Inches(3.05), Inches(1.65), fill=BG_CARD)
        rect(slide, x, Inches(1.9), Inches(3.05), Inches(0.06), fill=col)
        txt(slide, val, x+Inches(0.12), Inches(2.08), Inches(2.8), Inches(0.7),
            size=Pt(22), bold=True, color=col, align=PP_ALIGN.CENTER)
        txt(slide, desc, x+Inches(0.08), Inches(2.82), Inches(2.88), Inches(0.65),
            size=Pt(12), color=WHITE_60, align=PP_ALIGN.CENTER)

    # Difficultes
    txt(slide, "Les defis principaux :",
        Inches(0.5), Inches(3.8), Inches(5), Inches(0.4),
        size=Pt(16), bold=True, color=WHITE)

    defis = [
        (FRAUD_RED,    "Tres peu de fraudes",     "Seulement 2% des transactions sont frauduleuses"),
        (WARNING,      "Rapidite exigee",          "La detection doit etre quasi instantanee"),
        (CYAN,         "Fraudes qui evoluent",     "Les techniques de fraude changent constamment"),
        (PURPLE_LIGHT, "Faux positifs couteux",    "Bloquer une vraie transaction nuit a l'experience client"),
    ]

    for i, (col, titre, desc) in enumerate(defis):
        x = Inches(0.5 + (i%2)*6.4)
        y = Inches(4.3 + (i//2)*1.0)
        card(slide, x, y, Inches(6.1), Inches(0.85), accent=col)
        txt(slide, titre, x+Inches(0.2), y+Inches(0.08), Inches(5.7), Inches(0.35),
            size=Pt(13), bold=True, color=col)
        txt(slide, desc, x+Inches(0.2), y+Inches(0.45), Inches(5.7), Inches(0.32),
            size=Pt(11), color=WHITE_60)


# ── Slide 3 : Notre solution ──────────────────────────────────────────────────
def slide_solution():
    slide = new_slide()
    section_header(slide, "LA SOLUTION", "Comment fonctionne FraudShield AI ?", CYAN)

    composants = [
        ("Intelligence\nArtificielle", CYAN, [
            "Modeles XGBoost et LightGBM",
            "Apprend a reconnaitre la fraude",
            "S'ameliore avec le temps",
        ]),
        ("Traitement\ndes donnees", PURPLE_LIGHT, [
            "100 000 transactions analysees",
            "13 caracteristiques par transaction",
            "Equilibrage des donnees (SMOTE)",
        ]),
        ("Suivi &\nSurveillance", SAFE_GREEN, [
            "MLflow : suivi des experiences",
            "Alertes si les resultats baissent",
            "Rapport de derive automatique",
        ]),
        ("Interface\nUtilisateur", WARNING, [
            "Tableau de bord en temps reel",
            "Alertes fraude instantanees",
            "Graphiques et statistiques",
        ]),
    ]

    for i, (titre, col, points) in enumerate(composants):
        x = Inches(0.35 + i*3.25)
        bh = Inches(4.9)
        rect(slide, x, Inches(1.85), Inches(3.1), bh, fill=BG_CARD)
        rect(slide, x, Inches(1.85), Inches(3.1), Inches(0.55), fill=col)

        txt(slide, titre, x+Inches(0.1), Inches(1.9), Inches(2.9), Inches(0.45),
            size=Pt(15), bold=True, color=BG_DARK, align=PP_ALIGN.CENTER)

        # Icone cercle
        s = slide.shapes.add_shape(9, x+Inches(1.2), Inches(2.6), Inches(0.7), Inches(0.7))
        s.fill.solid(); s.fill.fore_color.rgb = col
        s.line.fill.background()

        for j, pt in enumerate(points):
            py = Inches(3.55 + j*0.75)
            rect(slide, x+Inches(0.12), py, Inches(2.86), Inches(0.6), fill=CARD2)
            rect(slide, x+Inches(0.12), py, Inches(0.05), Inches(0.6), fill=col)
            txt(slide, pt, x+Inches(0.25), py+Inches(0.1), Inches(2.6), Inches(0.42),
                size=Pt(11), color=WHITE)


# ── Slide 4 : Les donnees ─────────────────────────────────────────────────────
def slide_donnees():
    slide = new_slide()
    section_header(slide, "LES DONNEES", "Ce qu'on analyse dans chaque transaction", WARNING)

    # Schema transaction
    txt(slide, "Exemple de transaction analysee :",
        Inches(0.5), Inches(1.85), Inches(6), Inches(0.4),
        size=Pt(15), bold=True, color=WHITE)

    champs = [
        ("Montant",               "750 EUR",      CYAN),
        ("Heure de la transaction","2h du matin",  FRAUD_RED),
        ("Jour de la semaine",    "Dimanche",      WARNING),
        ("Nombre de trans. / 1h", "5 transactions",PURPLE_LIGHT),
        ("Distance domicile",     "250 km",        FRAUD_RED),
        ("Score risque marchand", "0.85 / 1.0",    WARNING),
        ("Categorie marchand",    "Electronique",  CYAN),
        ("Type de carte",         "Credit",        SAFE_GREEN),
        ("Mode de saisie",        "En ligne",      PURPLE_LIGHT),
    ]

    for i, (champ, valeur, col) in enumerate(champs):
        col_idx = i % 3
        row_idx = i // 3
        x = Inches(0.5 + col_idx*4.2)
        y = Inches(2.45 + row_idx*0.85)

        rect(slide, x, y, Inches(4.0), Inches(0.72), fill=BG_CARD)
        rect(slide, x, y, Inches(0.06), Inches(0.72), fill=col)
        txt(slide, champ, x+Inches(0.15), y+Inches(0.07), Inches(2.2), Inches(0.28),
            size=Pt(10), color=WHITE_60)
        txt(slide, valeur, x+Inches(0.15), y+Inches(0.38), Inches(2.2), Inches(0.28),
            size=Pt(12), bold=True, color=col)

        # Indicateur fraude potentielle
        if col == FRAUD_RED:
            txt(slide, "! suspect",
                x+Inches(2.5), y+Inches(0.22), Inches(1.3), Inches(0.3),
                size=Pt(9), bold=True, color=FRAUD_RED, align=PP_ALIGN.RIGHT)

    # Note en bas
    rect(slide, Inches(0.5), Inches(5.55), Inches(12.3), Inches(0.65), fill=BG_CARD)
    rect(slide, Inches(0.5), Inches(5.55), Inches(12.3), Inches(0.04), fill=FRAUD_RED)
    txt(slide, "Dans cet exemple : heure inhabituelle (2h AM) + grande distance du domicile (250 km) + score marchand eleve = FRAUDE PROBABLE",
        Inches(0.65), Inches(5.65), Inches(12.0), Inches(0.45),
        size=Pt(11), color=WHITE_60)

    # Desequilibre des classes
    txt(slide, "Defi : 98% de transactions normales vs 2% de fraudes",
        Inches(0.5), Inches(6.35), Inches(8), Inches(0.4),
        size=Pt(13), bold=True, color=WARNING)

    for i, (label, pct, col) in enumerate([("Normales 98%", 0.98, SAFE_GREEN),("Fraudes 2%", 0.02, FRAUD_RED)]):
        bx = Inches(8.7 + i*2.0)
        rect(slide, bx, Inches(6.28), Inches(1.8), Inches(0.55), fill=BG_CARD)
        rect(slide, bx, Inches(6.28), Inches(1.8*pct), Inches(0.55), fill=col)
        txt(slide, label, bx+Inches(0.05), Inches(6.28), Inches(1.7), Inches(0.55),
            size=Pt(9), bold=True, color=BG_DARK if pct > 0.5 else col,
            align=PP_ALIGN.CENTER)


# ── Slide 5 : Le pipeline ML ──────────────────────────────────────────────────
def slide_pipeline():
    slide = new_slide()
    section_header(slide, "LE PIPELINE ML", "Les 6 etapes pour entrainer le modele", SAFE_GREEN)

    pipe = pipeline_img((1200, 280))
    img_to_slide(slide, pipe, Inches(0.3), Inches(1.85), Inches(12.7), Inches(3.3))

    descriptions = [
        "On collecte\n100 000 transactions\n(reelles ou simulees)",
        "On verifie que\nles donnees sont\ncorrectes et completes",
        "On equilibre\nles donnees pour\ncorriger le 2% vs 98%",
        "On entraine\ndeux algorithmes\nde Machine Learning",
        "On mesure\nla precision du\nmodele (F1, AUC...)",
        "Si ok, le modele\npasse en\nproduction",
    ]

    for i, desc in enumerate(descriptions):
        x = Inches(0.35 + i*2.18)
        rect(slide, x, Inches(5.25), Inches(2.05), Inches(1.05), fill=BG_CARD)
        txt(slide, desc, x+Inches(0.08), Inches(5.32), Inches(1.9), Inches(0.95),
            size=Pt(9), color=WHITE_60, align=PP_ALIGN.CENTER)

    txt(slide, "Tout ce processus est automatise et se relance chaque semaine automatiquement",
        Inches(0.5), Inches(6.5), Inches(12), Inches(0.4),
        size=Pt(12), color=CYAN, align=PP_ALIGN.CENTER)


# ── Slide 6 : Les modeles ML ──────────────────────────────────────────────────
def slide_modeles():
    slide = new_slide()
    section_header(slide, "LES MODELES", "Comment l'IA apprend a detecter la fraude", PURPLE_LIGHT)

    # Explication simple
    rect(slide, Inches(0.5), Inches(1.85), Inches(12.3), Inches(0.9), fill=BG_CARD)
    txt(slide, "Un modele de Machine Learning apprend a partir d'exemples passes (transactions frauduleuses et normales)\npour predire si une nouvelle transaction est suspecte ou non.",
        Inches(0.65), Inches(1.95), Inches(12.0), Inches(0.75),
        size=Pt(13), color=WHITE_60)

    # Deux modeles
    modeles = [
        ("XGBoost", CYAN, "Gradient Boosting", [
            ("Principe",       "Enchainement de petits arbres de decision"),
            ("Point fort",     "Tres performant sur les donnees tabulaires"),
            ("Gestion fraude", "Parametre scale_pos_weight=50 pour compenser le desequilibre"),
            ("Arret auto",     "S'arrete si pas d'amelioration au bout de 50 tours"),
        ]),
        ("LightGBM", PURPLE_LIGHT, "Light Gradient Boosting", [
            ("Principe",       "Variante plus rapide de XGBoost"),
            ("Point fort",     "Tres efficace sur les grands volumes de donnees"),
            ("Gestion fraude", "class_weight='balanced' pour les classes desequilibrees"),
            ("Arret auto",     "Meme mecanisme d'arret precoce"),
        ]),
    ]

    for mi, (nom, col, sous_titre, params) in enumerate(modeles):
        x = Inches(0.4 + mi*6.4)
        bh = Inches(4.7)
        rect(slide, x, Inches(2.9), Inches(6.1), bh, fill=BG_CARD)
        rect(slide, x, Inches(2.9), Inches(6.1), Inches(0.6), fill=col)

        txt(slide, nom, x+Inches(0.15), Inches(2.95), Inches(4), Inches(0.48),
            size=Pt(22), bold=True, color=BG_DARK)
        txt(slide, sous_titre, x+Inches(3.3), Inches(3.08), Inches(2.65), Inches(0.3),
            size=Pt(11), color=RGBColor(0x05,0x08,0x13), align=PP_ALIGN.RIGHT)

        for pi, (clef, valeur) in enumerate(params):
            py = Inches(3.65 + pi*0.82)
            rect(slide, x+Inches(0.12), py, Inches(5.86), Inches(0.7),
                 fill=CARD2 if pi%2==0 else BG_CARD)
            txt(slide, clef, x+Inches(0.22), py+Inches(0.08), Inches(1.8), Inches(0.28),
                size=Pt(10), color=WHITE_60)
            txt(slide, valeur, x+Inches(2.1), py+Inches(0.08), Inches(3.7), Inches(0.5),
                size=Pt(11), bold=False, color=col)

    # Lequel gagne ?
    rect(slide, Inches(0.5), Inches(6.9), Inches(12.3), Inches(0.45), fill=BG_CARD)
    rect(slide, Inches(0.5), Inches(6.9), Inches(12.3), Inches(0.04), fill=CYAN)
    txt(slide, "Le meilleur modele est automatiquement selectionne et mis en production si son Score F1 est superieur a 85%",
        Inches(0.65), Inches(6.97), Inches(12.0), Inches(0.35),
        size=Pt(11), color=WHITE_60)


# ── Slide 7 : Suivi avec MLflow ───────────────────────────────────────────────
def slide_mlflow():
    slide = new_slide()
    section_header(slide, "SUIVI DES EXPERIENCES", "MLflow : garder une trace de tout", CYAN)

    # Schema central simple
    etapes = [
        ("Lancer\nl'entrainement", CYAN),
        ("Enregistrer\nles resultats", PURPLE_LIGHT),
        ("Comparer\nles modeles", WARNING),
        ("Choisir\nle meilleur", SAFE_GREEN),
        ("Deployer\nen production", FRAUD_RED),
    ]

    bw = Inches(2.0)
    gap = Inches(0.25)
    total_w = len(etapes)*bw + (len(etapes)-1)*gap
    sx = (W - total_w)//2

    for i, (label, col) in enumerate(etapes):
        x = sx + i*(bw+gap)
        y = Inches(2.0)

        # Boite 3D simple (ombre)
        rect(slide, x+Inches(0.08), y+Inches(0.08), bw, Inches(1.4),
             fill=BG_CARD)
        rect(slide, x, y, bw, Inches(1.4), fill=BG_CARD, border=col, bw=Pt(2))
        rect(slide, x, y, bw, Inches(0.08), fill=col)

        txt(slide, str(i+1), x, y+Inches(0.2), bw, Inches(0.5),
            size=Pt(24), bold=True, color=col, align=PP_ALIGN.CENTER)
        txt(slide, label, x, y+Inches(0.75), bw, Inches(0.6),
            size=Pt(12), color=WHITE, align=PP_ALIGN.CENTER)

        if i < len(etapes)-1:
            ay = y + Inches(0.7)
            rect(slide, x+bw+Inches(0.02), ay, gap-Inches(0.04), Inches(0.04), fill=CYAN)

    # Ce que MLflow stocke
    txt(slide, "Ce que MLflow enregistre pour chaque experience :",
        Inches(0.5), Inches(3.65), Inches(9), Inches(0.4),
        size=Pt(15), bold=True, color=WHITE)

    elements = [
        (CYAN,         "Les parametres",   "Toutes les configurations du modele (ex: profondeur max = 6)"),
        (PURPLE_LIGHT, "Les metriques",    "Score F1, precision, rappel, courbe ROC..."),
        (SAFE_GREEN,   "Le modele sauve",  "Le fichier du modele entraine, pret a etre reutilise"),
        (WARNING,      "Les graphiques",   "Matrice de confusion, courbe ROC, importance des variables"),
    ]

    for i, (col, titre, desc) in enumerate(elements):
        x = Inches(0.5 + (i%2)*6.4)
        y = Inches(4.15 + (i//2)*0.95)
        card(slide, x, y, Inches(6.1), Inches(0.82), accent=col)
        txt(slide, titre, x+Inches(0.2), y+Inches(0.08), Inches(2.2), Inches(0.3),
            size=Pt(12), bold=True, color=col)
        txt(slide, desc, x+Inches(0.2), y+Inches(0.44), Inches(5.7), Inches(0.3),
            size=Pt(11), color=WHITE_60)


# ── Slide 8 : Resultats ───────────────────────────────────────────────────────
def slide_resultats():
    slide = new_slide()
    section_header(slide, "LES RESULTATS", "Performance du modele XGBoost champion", SAFE_GREEN)

    # Graphique barres 3D
    chart = bar_chart_3d((700, 310))
    img_to_slide(slide, chart, Inches(0.3), Inches(1.85), Inches(7.2), Inches(3.35))

    # Explication des metriques
    metriques = [
        ("Score F1",  "92.3%", CYAN,         "Equilibre entre precision et rappel"),
        ("Precision", "94.1%", PURPLE_LIGHT,  "9 alertes sur 10 sont de vraies fraudes"),
        ("Rappel",    "90.6%", SAFE_GREEN,    "9 fraudes sur 10 sont detectees"),
        ("ROC-AUC",   "98.7%", WARNING,       "Excellente discrimination global"),
        ("AUC-PR",    "95.1%", FRAUD_RED,     "Tres performant sur les cas rares"),
    ]

    for i, (nom, val, col, explication) in enumerate(metriques):
        x = Inches(7.7)
        y = Inches(1.85 + i*0.72)
        rect(slide, x, y, Inches(5.4), Inches(0.62), fill=BG_CARD)
        rect(slide, x, y, Inches(0.06), Inches(0.62), fill=col)
        txt(slide, nom, x+Inches(0.15), y+Inches(0.08), Inches(1.5), Inches(0.28),
            size=Pt(11), color=WHITE_60)
        txt(slide, val, x+Inches(1.75), y+Inches(0.05), Inches(0.9), Inches(0.42),
            size=Pt(18), bold=True, color=col, align=PP_ALIGN.CENTER)
        txt(slide, explication, x+Inches(2.75), y+Inches(0.15), Inches(2.5), Inches(0.28),
            size=Pt(9), color=WHITE_60)

    # Interpretation simple
    rect(slide, Inches(0.3), Inches(5.4), Inches(12.7), Inches(0.95), fill=BG_CARD)
    rect(slide, Inches(0.3), Inches(5.4), Inches(12.7), Inches(0.06), fill=SAFE_GREEN)
    txt(slide, "En clair : Sur 100 transactions frauduleuses, le modele en detecte 90.",
        Inches(0.5), Inches(5.52), Inches(12.3), Inches(0.35),
        size=Pt(14), bold=True, color=WHITE)
    txt(slide, "Et sur 100 alertes declenchees, 94 sont de vraies fraudes (tres peu de fausses alertes).",
        Inches(0.5), Inches(5.87), Inches(12.3), Inches(0.35),
        size=Pt(12), color=WHITE_60)

    # Seuil qualite
    rect(slide, Inches(0.3), Inches(6.55), Inches(12.7), Inches(0.75), fill=BG_CARD)
    txt(slide, "Seuil minimum requis pour mise en production : Score F1 >= 85%  →  Notre modele atteint 92.3%",
        Inches(0.5), Inches(6.65), Inches(12.2), Inches(0.5),
        size=Pt(13), color=CYAN, align=PP_ALIGN.CENTER)


# ── Slide 9 : Conclusion ─────────────────────────────────────────────────────
def slide_conclusion():
    slide = new_slide()

    # Grille
    for i in range(0, int(W), int(Inches(0.65))):
        s = slide.shapes.add_shape(1, i, 0, Pt(1), H)
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor(0x0A,0x10,0x22)
        s.line.fill.background()

    bar(slide, CYAN)

    # Globe
    g = globe_3d(380)
    img_to_slide(slide, g, Inches(9.3), Inches(0.3), Inches(3.7), Inches(3.7))

    txt(slide, "EN RESUME", Inches(0.5), Inches(0.28), Inches(5), Inches(0.4),
        size=Pt(11), bold=True, color=CYAN)
    txt(slide, "Ce que FraudShield AI accomplit",
        Inches(0.5), Inches(0.78), Inches(8.5), Inches(0.72),
        size=Pt(36), bold=True, color=WHITE)
    line(slide, Inches(0.5), Inches(1.58), Inches(5))

    points = [
        (CYAN,         "Un systeme complet de detection de fraude en temps reel"),
        (PURPLE_LIGHT, "Deux modeles IA entraines : XGBoost (F1=92%) et LightGBM"),
        (SAFE_GREEN,   "Pipeline automatise : de la donnee brute au modele en production"),
        (WARNING,      "Surveillance continue pour detecter si le modele se degrade"),
        (FRAUD_RED,    "Interface web pour visualiser les alertes et les statistiques"),
        (CYAN,         "Tout est tracable, reproductible et facile a mettre a jour"),
    ]

    for i, (col, texte) in enumerate(points):
        x = Inches(0.5)
        y = Inches(1.9 + i*0.78)
        rect(slide, x, y, Inches(8.6), Inches(0.65), fill=BG_CARD)
        rect(slide, x, y, Inches(0.06), Inches(0.65), fill=col)

        s = slide.shapes.add_shape(9, x+Inches(0.15), y+Inches(0.15),
                                   Inches(0.35), Inches(0.35))
        s.fill.solid(); s.fill.fore_color.rgb = col
        s.line.fill.background()

        txt(slide, texte, x+Inches(0.6), y+Inches(0.14), Inches(7.9), Inches(0.4),
            size=Pt(13), color=WHITE)

    # Stack technique en bas
    rect(slide, Inches(0.5), Inches(6.72), Inches(12.3), Inches(0.6), fill=BG_CARD)
    rect(slide, Inches(0.5), Inches(6.72), Inches(12.3), Inches(0.05), fill=CYAN)
    txt(slide, "Outils utilises : XGBoost  |  MLflow  |  Apache Airflow  |  FastAPI  |  Next.js  |  PostgreSQL  |  Docker",
        Inches(0.65), Inches(6.82), Inches(12.0), Inches(0.42),
        size=Pt(11), color=CYAN_DARK, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
#  GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

print("Generation de la presentation...")
slide_titre();    print("  [1/9] Titre")
slide_probleme(); print("  [2/9] Le probleme")
slide_solution(); print("  [3/9] La solution")
slide_donnees();  print("  [4/9] Les donnees")
slide_pipeline(); print("  [5/9] Le pipeline ML")
slide_modeles();  print("  [6/9] Les modeles")
slide_mlflow();   print("  [7/9] MLflow")
slide_resultats();print("  [8/9] Les resultats")
slide_conclusion();print("  [9/9] Conclusion")

OUT = r"c:\Users\Mellow\Desktop\FraudShield_AI_FR.pptx"
prs.save(OUT)
print(f"\nPresentation sauvegardee : {OUT}")
