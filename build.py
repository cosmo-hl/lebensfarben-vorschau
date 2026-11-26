#!/usr/bin/env python3
"""Baut die statische Vorschau von Lebensfarben nach dist/.

Aufruf: python3 build.py   (Bilder vorher mit scripts/images.py nach site/img/ holen)
Alle Seiten sind für Suchmaschinen gesperrt (noindex, robots.txt), weil es eine Vorschau ist.
"""
import json, pathlib, shutil, re, html
import markdown

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / 'site'
DIST = ROOT / 'dist'
LIVE = 'https://www.lebensfarben.net/'  # spätere Adresse, nur für Strukturdaten

NAV = [
    ('wofuer/', 'Wofür'),
    ('somatic-experiencing/', 'Somatic Experiencing'),
    ('angebot/', 'Angebot & Preise'),
    ('ueber-mich/', 'Über mich'),
    ('kunst/', 'Kunst'),
    ('kontakt/', 'Kontakt'),
]

PHONE = '0163 583 7997'
PHONE_TEL = '+491635837997'
MAIL = 'mail@kristindamaschke.de'
WA = 'https://wa.me/491635837997'
IG_PRAXIS = 'https://www.instagram.com/lebensfarben_psychotherapie/'
IG_ART = 'https://www.instagram.com/kristindamaschke_art/'
OSM = 'https://www.openstreetmap.org/search?query=L%C3%BCbsche%20Stra%C3%9Fe%2071%2C%2023966%20Wismar'

ARROW = '<span class="arrow" aria-hidden="true">→</span>'


def rel(depth):
    return '../' * depth


def img(r, name, alt, w=None, h=None, sizes='100vw', cls='', loading='lazy', pos=None):
    """Bild mit srcset (800/1600 px). Dateien entstehen in scripts/images.py."""
    style = f' style="object-position:{pos}"' if pos else ''
    wh = f' width="{w}" height="{h}"' if w and h else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{r}img/{name}-1600.jpg" srcset="{r}img/{name}-800.jpg 800w, {r}img/{name}-1600.jpg 1600w" '
            f'sizes="{sizes}" alt="{html.escape(alt)}"{wh} loading="{loading}" decoding="async"{style}>')


def btn_kontakt(r, text='Kennenlernen vereinbaren', cls='btn'):
    return f'<a class="{cls}" href="{r}kontakt/">{text} {ARROW}</a>'


# ---------------------------------------------------------------- Strukturdaten
def ld_base():
    person = {
        '@type': 'Person', '@id': LIVE + '#kristin',
        'name': 'Kristin Damaschke', 'givenName': 'Kristin', 'familyName': 'Damaschke',
        'jobTitle': 'Heilpraktikerin für Psychotherapie und Kunsttherapeutin (M.A.)',
        'description': 'Traumasensible, körperorientierte Begleitung mit Somatic Experiencing (in Ausbildung) und Kunsttherapie in Wismar und online. Für Erwachsene, die schon viel verstanden haben und trotzdem immer wieder von alten Gefühlen und Mustern eingeholt werden.',
        'url': LIVE + 'ueber-mich/',
        'worksFor': {'@id': LIVE + '#praxis'},
        'hasCredential': [
            {'@type': 'EducationalOccupationalCredential', 'credentialCategory': 'Erlaubnis nach dem Heilpraktikergesetz', 'name': 'Heilpraktikerin für Psychotherapie (2018)'},
            {'@type': 'EducationalOccupationalCredential', 'credentialCategory': 'degree', 'name': 'Master of Arts Intermediale Kunsttherapie', 'recognizedBy': {'@type': 'CollegeOrUniversity', 'name': 'MSH Medical School Hamburg'}},
            {'@type': 'EducationalOccupationalCredential', 'credentialCategory': 'Weiterbildung', 'name': 'Somatic Experiencing® nach Peter A. Levine (in Ausbildung seit 2023)'},
        ],
        'alumniOf': [{'@type': 'CollegeOrUniversity', 'name': 'MSH Medical School Hamburg'}, {'@type': 'CollegeOrUniversity', 'name': 'HAW Hamburg'}],
        'knowsAbout': ['Somatic Experiencing', 'Traumasensible Begleitung', 'Nervensystemregulation', 'Kunsttherapie', 'Intermediale Kunsttherapie', 'Stressfolgen und Erschöpfung', 'Wiederkehrende emotionale Muster', 'Psychotherapie nach dem Heilpraktikergesetz'],
        'knowsLanguage': 'de',
        'sameAs': [IG_PRAXIS, IG_ART],
    }
    praxis = {
        '@type': 'ProfessionalService', '@id': LIVE + '#praxis',
        'name': 'Lebensfarben · Kristin Damaschke',
        'alternateName': 'Praxis Lebensfarben Wismar',
        'description': 'Praxis für körperorientierte Begleitung (Somatic Experiencing), Psychotherapie nach dem Heilpraktikergesetz und Kunsttherapie in Wismar und online. Selbstzahlerpraxis, Termine nach Vereinbarung.',
        'url': LIVE, 'email': MAIL, 'telephone': PHONE_TEL,
        'image': LIVE + 'img/raum-1600.jpg',
        'founder': {'@id': LIVE + '#kristin'},
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Lübsche Straße 71', 'postalCode': '23966', 'addressLocality': 'Wismar', 'addressRegion': 'Mecklenburg-Vorpommern', 'addressCountry': 'DE'},
        'areaServed': [{'@type': 'City', 'name': n} for n in ['Wismar', 'Schwerin', 'Lübeck']] + [{'@type': 'AdministrativeArea', 'name': 'Nordwestmecklenburg'}, {'@type': 'Country', 'name': 'Deutschland (online)'}],
        'priceRange': '90–120 € je 50 Minuten',
        'paymentAccepted': 'Überweisung, bar',
        'currenciesAccepted': 'EUR',
        'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Angebote', 'itemListElement': [
            {'@type': 'Offer', 'price': '90', 'priceCurrency': 'EUR', 'itemOffered': {'@type': 'Service', 'name': 'Einzelsitzung Psychotherapie (HeilprG), traumasensibel und körperorientiert', 'description': '50 Minuten, in Wismar oder online.'}},
            {'@type': 'Offer', 'price': '90', 'priceCurrency': 'EUR', 'itemOffered': {'@type': 'Service', 'name': 'Einzelsitzung Nervensystemregulation (Anti-Stress)', 'description': '50 Minuten, auch bei Neurodivergenz.'}},
            {'@type': 'Offer', 'price': '120', 'priceCurrency': 'EUR', 'itemOffered': {'@type': 'Service', 'name': 'Einzelsitzung Coaching', 'description': '50 Minuten.'}},
            {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': 'Kunsttherapeutische Selbsterfahrungsgruppe', 'description': 'Termine werden auf der Seite angekündigt.'}},
        ]},
        'sameAs': [IG_PRAXIS],
    }
    return [person, praxis]


def ld_page(slug, title, desc, crumbs=None, extra=None):
    graph = ld_base()
    url = LIVE + slug
    graph.append({'@type': 'WebSite', '@id': LIVE + '#website', 'url': LIVE, 'name': 'Lebensfarben · Kristin Damaschke', 'inLanguage': 'de-DE', 'publisher': {'@id': LIVE + '#praxis'}})
    graph.append({'@type': 'WebPage', '@id': url + '#seite', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'de-DE', 'isPartOf': {'@id': LIVE + '#website'}, 'about': {'@id': LIVE + '#praxis'}})
    if crumbs:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Start', 'item': LIVE},
            {'@type': 'ListItem', 'position': 2, 'name': crumbs, 'item': url}]})
    if extra:
        graph.extend(extra)
    return {'@context': 'https://schema.org', '@graph': graph}


# ---------------------------------------------------------------- Rahmen
def layout(slug, title, desc, body, active=None, crumbs=None, extra_ld=None):
    depth = slug.count('/')
    r = '/lebensfarben-vorschau/' if slug == '404' else rel(depth)
    full_title = title if slug == '' else f'{title} · Kristin Damaschke · Lebensfarben Wismar'
    nav = ''.join(
        f'<li><a href="{r}{h}"{" aria-current=\"page\"" if active == h else ""}>{l}</a></li>' for h, l in NAV)
    ld = json.dumps(ld_page(slug, title, desc, crumbs, extra_ld), ensure_ascii=False, separators=(',', ':'))
    year = 2026
    return f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive, noimageindex">
<meta name="googlebot" content="noindex, nofollow">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#2f4a40">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{r}fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}style.css">
<script type="application/ld+json">{ld}</script>
<script>document.documentElement.classList.add('js');</script>
</head>
<body>
<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
<div class="preview-bar"><div class="wrap"><span><strong>Vorschau</strong> · Entwurf für eine neue Seite von Kristin Damaschke. Texte sind Vorschläge.</span><span><a href="{r}konzept/">Analyse und Konzept</a> · <a href="https://www.lebensfarben.net/" rel="nofollow">Aktuelle Seite</a></span></div></div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{r or './'}"><span class="brand-name">Kristin Damaschke</span><span class="brand-sub"><b>Lebensfarben</b><span class="brand-sub-more"> · Somatic Experiencing</span></span><span class="visually-hidden">, zur Startseite</span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="hauptmenue"><span>Menü</span><span class="bars" aria-hidden="true"></span></button>
    <nav class="main-nav" id="hauptmenue" aria-label="Hauptmenü"><ul>{nav}<li class="nav-cta"><a href="{r}kontakt/#kennenlernen">Kennenlernen</a></li></ul></nav>
  </div>
</header>
<main id="inhalt" tabindex="-1">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-name">Kristin Damaschke · Lebensfarben</p>
        <p>Heilpraktikerin für Psychotherapie und Kunsttherapeutin (M.A.)<br>Somatic Experiencing® in Ausbildung</p>
        <address>Lübsche Straße 71 · 23966 Wismar<br>und ein ruhiger Praxisraum bei Wismar · auch online</address>
      </div>
      <div>
        <p class="footer-title">Kontakt</p>
        <ul>
          <li><a href="tel:{PHONE_TEL}">Telefon {PHONE}</a></li>
          <li><a href="{WA}">WhatsApp schreiben</a></li>
          <li><a href="mailto:{MAIL}">{MAIL}</a></li>
          <li><a href="{IG_PRAXIS}">Instagram</a></li>
        </ul>
      </div>
      <div>
        <p class="footer-title">Mehr</p>
        <ul>
          <li><a href="{r}fragen/">Häufige Fragen</a></li>
          <li><a href="{r}kunsttherapie/">Kunsttherapie</a></li>
          <li><a href="{r}impressum/">Impressum</a></li>
          <li><a href="{r}datenschutz/">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom"><span>© {year} Kristin Damaschke · Lebensfarben</span><span>Fotos: Kristin Damaschke, Alexander Tiffert, Alexander Henke (Unsplash)</span></div>
  </div>
</footer>
<script>
(function(){{
  var root=document.documentElement,header=document.querySelector('.site-header');
  function setH(){{if(header)root.style.setProperty('--header-h',header.offsetHeight+'px');}}
  setH();addEventListener('resize',setH);
  function onScroll(){{if(header)header.classList.toggle('is-scrolled',scrollY>8);}}
  onScroll();addEventListener('scroll',onScroll,{{passive:true}});
  var btn=document.querySelector('.menu-toggle'),nav=document.getElementById('hauptmenue');
  if(btn&&nav){{
    var set=function(o){{btn.setAttribute('aria-expanded',String(o));nav.classList.toggle('is-open',o);document.body.style.overflow=o?'hidden':'';setH();}};
    btn.addEventListener('click',function(){{set(btn.getAttribute('aria-expanded')!=='true');}});
    document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&btn.getAttribute('aria-expanded')==='true'){{set(false);btn.focus();}}}});
  }}
  var items=document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches){{items.forEach(function(el){{el.classList.add('is-in');}});}}
  else{{var io=new IntersectionObserver(function(es){{es.forEach(function(en){{if(en.isIntersecting){{en.target.classList.add('is-in');io.unobserve(en.target);}}}});}},{{rootMargin:'0px 0px -8% 0px',threshold:.08}});items.forEach(function(el){{io.observe(el);}});}}
}})();
</script>
</body>
</html>
'''


def page_head(r, eyebrow, h1, lead, crumb=None):
    c = f'<p class="crumbs"><a href="{r}">Start</a> / {crumb}</p>' if crumb else ''
    return f'''<section class="page-head"><div class="wrap">{c}<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p></div></section>'''


def closing(r, h='Lernen wir uns <em>kennen</em>.', p='Ein erstes Gespräch am Telefon dauert etwa 15 Minuten. Sie erzählen kurz, was Sie bewegt, und wir klären, ob meine Arbeit zu Ihnen passt. Ganz ohne Verpflichtung.'):
    return f'''<section class="closing center"><div class="wrap"><div class="closing-card"><span class="duo-blob duo-blob--c" aria-hidden="true"></span><h2>{h}</h2><p>{p}</p><div class="cta-row">{btn_kontakt(r, cls='btn btn--light')}<a class="btn btn--ghost btn--on-dark" href="{WA}">WhatsApp schreiben</a></div></div></div></section>'''


PAGES = {}


def page(slug):
    def deco(fn):
        PAGES[slug] = fn
        return fn
    return deco


# ---------------------------------------------------------------- Startseite
@page('')
def start():
    r = ''
    body = f'''
<section class="hero"><div class="wrap">
  <div class="hero-grid">
    <div class="hero-text">
      <p class="eyebrow">Somatic Experiencing® in Wismar und online</p>
      <h1>Raum für das, was Worte <em>nicht</em> erreichen.</h1>
      <p class="lead">Sie haben schon viel verstanden. Und trotzdem holen alte Gefühle und Muster Sie immer wieder ein? Mit Somatic Experiencing beziehen wir den Körper ein, dort, wo alte Reaktionen gespeichert sind. In Ihrem Tempo, in kleinen, sicheren Schritten.</p>
      <div class="cta-row">{btn_kontakt(r)}<a class="btn btn--ghost" href="somatic-experiencing/">Was ist Somatic Experiencing?</a></div>
      <p class="hero-aside"><strong>Kristin Damaschke</strong> · Somatic Experiencing® in Ausbildung · Heilpraktikerin für Psychotherapie · Kunsttherapeutin (M.A.) · viele Jahre Erfahrung in Kliniken</p>
    </div>
    <div class="duo" role="group" aria-label="Weite und Raum: Dünen an der Ostsee und der Praxisraum mit Blick nach draußen">
      <span class="duo-blob duo-blob--a" aria-hidden="true"></span>
      <span class="duo-blob duo-blob--b" aria-hidden="true"></span>
      <figure class="duo-weite">{img(r, 'weite', 'Dünengras vor der Ostsee unter weitem Himmel', 1600, 1310, '(min-width: 1100px) 440px, 75vw', loading='eager')}</figure>
      <figure class="duo-raum">{img(r, 'raum', 'Heller Praxisraum mit Sesseln, Sofa und Blick aus dem Fenster ins Grüne', 1200, 1600, '(min-width: 1100px) 300px, 50vw', loading='eager')}</figure>
      <p class="duo-caption"><span>Weite</span> <i aria-hidden="true">&amp;</i> <span>Raum</span></p>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head reveal"><p class="eyebrow">Wofür</p><h2>Vielleicht erkennen Sie sich <em>wieder</em></h2><p class="lead muted">Viele, die zu mir kommen, stehen mitten im Leben. Sie sind beruflich erfolgreich, reflektiert, oft therapieerfahren. Und merken doch: Etwas in mir reagiert schneller, als ich denken kann.</p></div>
  <ul class="cards">
    <li class="card reveal"><p class="quote-line">„Ich weiß, woher es kommt. Und trotzdem passiert es wieder.“</p><h3>Alte Muster, die wiederkehren</h3><p>Wenn Einsicht allein nicht reicht: Wir arbeiten dort, wo alte Reaktionen gespeichert sind: im Körper und im Nervensystem.</p><a class="more" href="wofuer/#muster">Mehr dazu {ARROW}</a></li>
    <li class="card reveal"><p class="quote-line">„Ich funktioniere. Aber ich komme nicht mehr zur Ruhe.“</p><h3>Stress und Erschöpfung</h3><p>Ein dauerhaft angespanntes Nervensystem kann lernen, wieder zwischen Anspannung und Entspannung zu pendeln.</p><a class="more" href="wofuer/#stress">Mehr dazu {ARROW}</a></li>
    <li class="card reveal"><p class="quote-line">„Darüber zu reden, war mir bisher zu viel.“</p><h3>Belastende Erfahrungen</h3><p>Traumasensibel heißt: Sie müssen nichts noch einmal durchleben. Wir gehen behutsam vor und bleiben bei dem, was Sie tragen können.</p><a class="more" href="wofuer/#trauma">Mehr dazu {ARROW}</a></li>
  </ul>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split">
    <div class="split-head reveal"><p class="eyebrow">Mein Ansatz</p><h2>Was hier anders ist als im <em>Gespräch</em> allein</h2><p class="kicker">Nicht noch einmal erzählen, sondern spüren, was sich verändern möchte.</p></div>
    <div class="reveal">
      <ul class="points">
        <li><strong>Der Körper spricht mit</strong>Mit Somatic Experiencing achten wir auf Empfindungen, Atem und Haltung. So kann sich lösen, was der Kopf längst verstanden hat.</li>
        <li><strong>Sicherheit zuerst</strong>Wir beginnen bei Ihren Kraftquellen und pendeln behutsam zwischen Belastendem und Stärkendem. Tempo und Tiefe bestimmen Sie.</li>
        <li><strong>Farbe, wo Worte fehlen</strong>Manchmal hilft ein Bild weiter, wo Sprache nicht hinreicht. Aus meiner Erfahrung als Kunsttherapeutin fließt das ein, wenn es passt. Malen können müssen Sie nicht.</li>
      </ul>
      <p style="margin-top:var(--s3)"><a class="more" href="somatic-experiencing/">Mehr über Somatic Experiencing {ARROW}</a></p>
    </div>
  </div>
</div></section>

<figure class="band contained">{img(r, 'art-erde', 'Aquarell von Kristin Damaschke in Ocker, Salbeigrün, Hellblau und Terrakotta', 1600, 850)}</figure>

<section class="section"><div class="wrap">
  <div class="split media-right">
    <div class="split-media portrait reveal"><figure>{img(r, 'kristin-lila', 'Kristin Damaschke in lila gemusterter Bluse, sie schaut ruhig und offen in die Kamera', 1600, 2000, '(min-width: 960px) 460px, 100vw')}</figure></div>
    <div class="reveal">
      <p class="eyebrow">Über mich</p>
      <h2>Ernstes darf auch <em>leicht</em> werden.</h2>
      <p class="lead">Ich bin Kristin Damaschke, Heilpraktikerin für Psychotherapie, Kunsttherapeutin und in Ausbildung zur Somatic-Experiencing-Practitioner. Seit 2021 lebe und arbeite ich bei Wismar.</p>
      <p>Auch wenn es um schwere Themen geht: In meinen Stunden darf gelacht werden. Leichtigkeit ist kein Gegensatz zu Tiefe, oft ist sie ein Zeichen, dass sich etwas löst.</p>
      <p>Viele Jahre habe ich in psychiatrischen und psychosomatischen Kliniken gearbeitet, unter anderem in den Sana Kliniken Lübeck und im Klinikum Schloss Lütgenhof. Dort habe ich erlebt, wie viel sich bewegt, wenn Menschen einen Zugang jenseits der Worte finden. Heute arbeite ich vor allem körperorientiert mit Somatic Experiencing.</p>
      <div class="cta-row"><a class="more" href="ueber-mich/">Mein Weg und meine Ausbildungen {ARROW}</a></div>
    </div>
  </div>
</div></section>

<section class="section sage"><div class="wrap">
  <div class="section-head reveal"><p class="eyebrow">Angebot</p><h2>Einzeln, in Wismar oder online</h2></div>
  <ul class="prices reveal">
    <li class="price"><span class="tag">50 Minuten</span><h3>Somatic Experiencing</h3><p class="amount">90 € <small>je Sitzung</small></p><p>Traumasensible, körperorientierte Einzelsitzungen (Psychotherapie nach dem Heilpraktikergesetz).</p></li>
    <li class="price"><span class="tag">50 Minuten</span><h3>Nervensystem­regulation</h3><p class="amount">90 € <small>je Sitzung</small></p><p>Anti-Stress-Begleitung, um wieder in Balance zu kommen. Auch bei Neurodivergenz.</p></li>
    <li class="price"><span class="tag">50 Minuten</span><h3>Coaching</h3><p class="amount">120 € <small>je Sitzung</small></p><p>Für berufliche und persönliche Fragen, mit Körper und Bild statt nur mit Strategie.</p></li>
  </ul>
  <p style="margin-top:var(--s3)"><a class="more" href="angebot/">Ablauf, Orte und Kosten {ARROW}</a></p>
</div></section>
{closing(r)}
'''
    return layout('', 'Kristin Damaschke · Lebensfarben · Körper- und Kunsttherapie in Wismar',
                  'Traumasensible, körperorientierte Begleitung mit Somatic Experiencing und Kunsttherapie in Wismar und online. Für Menschen, die schon viel verstanden haben und trotzdem von alten Mustern eingeholt werden.', body)


# ---------------------------------------------------------------- Wofür
@page('wofuer/')
def wofuer():
    r = '../'
    body = page_head(r, 'Wofür', 'Wenn Verstehen allein nicht mehr weiterhilft', 'Hier beschreibe ich, mit welchen Anliegen Menschen zu mir kommen. Vielleicht finden Sie sich in einem davon wieder, vielleicht in mehreren.', 'Wofür') + f'''
<section class="section white" id="muster"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Erstens</p><h2>Alte Muster, die immer wiederkommen</h2><p class="kicker">„Ich bin erwachsen, erfolgreich, reflektiert. Und in bestimmten Momenten fühle ich mich wieder wie damals.“</p></div>
    <div>
      <p>Vielleicht haben Sie schon eine oder mehrere Therapien gemacht. Sie kennen Ihre Geschichte und können gut darüber sprechen. Und trotzdem gibt es Situationen, in denen alte Gefühle Sie überrollen: Ohnmacht, Scham, Rückzug, Wut, das Gefühl, nicht genug zu sein.</p>
      <p>Das ist kein Zeichen, dass Sie etwas falsch machen. Viele dieser Reaktionen sind im Nervensystem und im Körper gespeichert, nicht im Verstand. Deshalb verändern sie sich oft erst, wenn auch der Körper eine neue Erfahrung machen darf.</p>
      <p><strong>Wie ich damit arbeite:</strong> Wir verlangsamen. Wir achten darauf, was im Körper geschieht, wenn ein altes Muster anklingt, und geben ihm Zeit, sich zu lösen. Bilder und Gestalten helfen, wo Worte fehlen.</p>
      <ul class="checks two">
        <li>wiederkehrende Gefühle von Ohnmacht oder Überforderung</li>
        <li>Muster in Beziehungen, die Sie längst durchschaut haben</li>
        <li>innere Antreiber: immer stark, immer perfekt sein</li>
        <li>das Gefühl, „neben sich“ zu stehen</li>
        <li>Lebensübergänge, Trennung, Verlust</li>
        <li>der Wunsch, sich selbst tiefer zu begegnen</li>
      </ul>
    </div>
  </div>
</div></section>

<section class="section" id="stress"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Zweitens</p><h2>Stress, Erschöpfung und ein Nervensystem im Dauerlauf</h2><p class="kicker">„Ich funktioniere, aber ich komme nicht mehr zur Ruhe.“</p></div>
    <div>
      <p>Dauerhafter Druck hinterlässt Spuren: Schlafprobleme, innere Unruhe, Gereiztheit, das Gefühl, nie ganz abschalten zu können. Manchmal folgt auf lange Anspannung eine bleierne Erschöpfung.</p>
      <p>In der Nervensystemregulation lernen Sie, Ihre Signale früher wahrzunehmen und Ihrem Körper zu helfen, wieder in einen Rhythmus von Anspannung und Erholung zu finden. Das ist praktisch, alltagsnah und braucht keine lange Vorgeschichte.</p>
      <ul class="checks two">
        <li>Stress und Anspannung</li><li>Vorbeugung von Burnout</li><li>Schlafprobleme</li><li>Ängste und Unruhe</li><li>Reizüberflutung, auch bei Neurodivergenz</li><li>Erschöpfung nach langen Belastungen</li>
      </ul>
    </div>
  </div>
</div></section>

<section class="section white" id="trauma"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Drittens</p><h2>Belastende und traumatische Erfahrungen</h2><p class="kicker">„Ich möchte das nicht alles noch einmal erzählen müssen.“</p></div>
    <div>
      <p>Das müssen Sie auch nicht. Traumasensibles Arbeiten heißt, dass wir zuerst Sicherheit und innere Stabilität aufbauen. Wir nähern uns dem Schweren nur so weit, wie es sich gut anfühlt, und kehren immer wieder zu dem zurück, was Sie stärkt.</p>
      <p>Somatic Experiencing wurde von Peter A. Levine für genau diese Arbeit entwickelt: Es hilft dem Körper, festgehaltene Stressreaktionen nach und nach zu lösen, ohne dass die Erinnerung im Mittelpunkt stehen muss.</p>
      <div class="note note--crisis"><p><strong>In einer akuten Krise</strong> bin ich nicht die richtige erste Adresse. Bitte wenden Sie sich an die Telefonseelsorge (0800 111 0 111, rund um die Uhr, kostenfrei), den ärztlichen Bereitschaftsdienst (116 117) oder im Notfall an den Notruf 112.</p></div>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap narrow center">
  <p class="pull">Sie müssen nicht wissen, welches Angebot das richtige ist. Das finden wir gemeinsam heraus.</p>
  <div class="cta-row">{btn_kontakt(r)}<a class="btn btn--ghost" href="../fragen/">Häufige Fragen</a></div>
</div></section>
'''
    return layout('wofuer/', 'Wofür: wenn alte Muster immer wiederkommen',
                  'Für Menschen, die schon viel verstanden haben und trotzdem von alten Gefühlen eingeholt werden, die unter Stress und Erschöpfung leiden oder belastende Erfahrungen behutsam bearbeiten möchten. Wismar und online.',
                  body, 'wofuer/', 'Wofür')


# ---------------------------------------------------------------- Somatic Experiencing
@page('somatic-experiencing/')
def se():
    r = '../'
    body = page_head(r, 'Somatic Experiencing® (SE)', 'Mit dem Körper lösen, was Worte oft <em>nicht</em> erreichen', 'Somatic Experiencing ist ein körperorientierter Ansatz zur Lösung von Stress- und Traumafolgen, entwickelt von Dr. Peter A. Levine. Er ist der Schwerpunkt meiner Arbeit.', 'Somatic Experiencing') + f'''
<figure class="band contained">{img(r, 'art-tuerkis', 'Aquarell von Kristin Damaschke in Türkis, Magenta und Rotbraun', 1600, 600)}</figure>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Worum es geht</p><h2>Wenn der Körper wieder zur Heimat wird</h2></div>
    <div>
      <p class="lead">Nach überwältigenden Erfahrungen bleibt das Nervensystem manchmal im Alarm. Der Körper reagiert, als wäre die Gefahr noch da, auch wenn der Verstand weiß, dass sie vorbei ist.</p>
      <p>Somatic Experiencing setzt genau hier an. Statt das Erlebte zu analysieren, richten wir die Aufmerksamkeit auf das, was jetzt im Körper spürbar ist: Atem, Wärme, Enge, Weite, Impulse. In kleinen Schritten pendeln wir zwischen dem, was belastet, und dem, was stärkt. So kann das Nervensystem seine natürliche Fähigkeit zur Selbstregulation wiederfinden.</p>
      <p>Viele Menschen beschreiben danach mehr Ruhe, mehr Lebendigkeit und das Gefühl, wieder bei sich anzukommen.</p>
    </div>
  </div>
</div></section>

<section class="section green"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Warum der Körper?</p><h2>Verstanden ist noch nicht <em>verändert</em></h2></div>
    <div>
      <p class="lead">Viele Menschen, die zu mir kommen, haben schon viel an sich gearbeitet. Sie können ihre Muster benennen. Trotzdem schlägt der Körper Alarm, bevor der Kopf eingreifen kann.</p>
      <p>Das liegt daran, dass Stress- und Schutzreaktionen nicht im Denken entstehen, sondern im Nervensystem. Somatic Experiencing arbeitet deshalb „von unten nach oben“: Wir geben dem Körper Gelegenheit, eine neue Erfahrung zu machen, etwa dass Anspannung kommen und wieder gehen darf. Das Verstehen, das Sie schon mitbringen, bekommt so ein Fundament.</p>
      <p>Das kann sich überraschend leicht anfühlen. Oft sind es kleine Momente: ein tieferer Atemzug, warme Hände, ein Lachen.</p>
    </div>
  </div>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Wobei es helfen kann</p><h2>Kleine Schritte, spürbare Wirkung</h2></div>
    <div>
      <ul class="checks two">
        <li>Stress und Anspannung</li><li>Verarbeitung belastender Erlebnisse</li><li>Ängste und Unruhe</li><li>wiederkehrende emotionale Muster</li><li>Erschöpfung und Burnout-Vorbeugung</li><li>Schlafprobleme</li><li>Gefühl von Taubheit oder Abgeschnittensein</li><li>Folgen von Unfällen, Operationen, Stürzen</li><li>mehr Körperwahrnehmung und Präsenz</li><li>innere Stabilität im Alltag</li>
      </ul>
      <p class="muted" style="margin-top:var(--s2)">Somatic Experiencing ersetzt keine ärztliche Diagnose oder Behandlung. Ob es für Ihr Anliegen passt, klären wir im Erstgespräch.</p>
      <h3 style="margin-top:var(--s4)">Und die Kunst?</h3>
      <p>Als Kunsttherapeutin habe ich gelernt, wie viel ein Bild sagen kann. Wenn es passt, lade ich Sie ein, etwas zu malen oder zu gestalten, um dem, was der Körper zeigt, eine Form zu geben. Ganz ohne Anspruch. <a href="../kunsttherapie/">Mehr dazu</a></p>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Ablauf</p><h2>So läuft eine Sitzung ab</h2></div>
    <div>
      <ol class="steps">
        <li><div><strong>Ankommen</strong>Wir beginnen mit dem, was gerade da ist. Sie sitzen bequem, wir sprechen kurz über Ihr Anliegen.</div></li>
        <li><div><strong>Spüren</strong>Ich lade Sie ein, wahrzunehmen, was im Körper geschieht. Sie bleiben dabei bekleidet und im Gespräch; Berührung gibt es nur, wenn Sie es ausdrücklich möchten.</div></li>
        <li><div><strong>Pendeln</strong>Wir wechseln behutsam zwischen Belastendem und Stärkendem, damit Ihr System nie überfordert wird.</div></li>
        <li><div><strong>Integrieren</strong>Zum Schluss nehmen wir uns Zeit, damit sich das Neue setzen kann, und schauen, was Sie in den Alltag mitnehmen.</div></li>
      </ol>
      <dl class="facts">
        <div><dt>Dauer</dt><dd>50 Minuten</dd></div>
        <div><dt>Ort</dt><dd>Praxisraum bei Wismar, Lübsche Straße 71 in Wismar oder online</dd></div>
        <div><dt>Kosten</dt><dd>90 € je Sitzung (Selbstzahlerleistung)</dd></div>
        <div><dt>Termine</dt><dd>nach Vereinbarung, auch samstags</dd></div>
        <div><dt>Meine Ausbildung</dt><dd>Somatic Experiencing® nach Dr. Peter A. Levine, bei Marinka Gattnar, seit 2023 (laufend).</dd></div>
      </dl>
    </div>
  </div>
</div></section>
{closing(r)}
'''
    return layout('somatic-experiencing/', 'Somatic Experiencing in Wismar',
                  'Somatic Experiencing (SE) nach Peter A. Levine in Wismar und online: körperorientierte Begleitung bei Stress, Traumafolgen und wiederkehrenden Mustern. Ablauf, Wirkung, Kosten.',
                  body, 'somatic-experiencing/', 'Somatic Experiencing')


# ---------------------------------------------------------------- Kunsttherapie
@page('kunsttherapie/')
def kunsttherapie():
    r = '../'
    body = page_head(r, 'Kunsttherapie', 'Farbe, wo Worte fehlen', 'Im Mittelpunkt meiner Arbeit steht der Körper. Manchmal kommt etwas dazu: Farbe, Papier, ein Bild. Als studierte Kunsttherapeutin lasse ich das einfließen, wenn es Ihnen hilft.', 'Kunsttherapie') + f'''
<figure class="band contained">{img(r, 'art-ocker', 'Aquarell von Kristin Damaschke mit Kreisen in Ocker, Rot und Türkis', 1600, 740)}</figure>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Worum es geht</p><h2>Innere Stärke durch die Verbindung zu sich selbst</h2></div>
    <div>
      <p class="lead">Gefühle, für die es keine Worte gibt, finden im Malen und Gestalten oft ganz selbstverständlich einen Ausdruck.</p>
      <p>Farben, Formen und Materialien machen innere Prozesse sichtbar, manchmal klarer als jedes Gespräch. Was auf dem Papier entsteht, können wir gemeinsam anschauen, verändern und neu ordnen. So wächst Abstand zu dem, was belastet, und Nähe zu dem, was trägt.</p>
      <p>Mein Verständnis ist humanistisch: Jeder Mensch trägt die Fähigkeit zur Selbstregulation und zum Wachsen in sich. Kreativität ist ein Weg, diese Fähigkeit wieder zu spüren.</p>
    </div>
  </div>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split media-right">
    <div class="split-media"><figure>{img(r, 'art-gruen', 'Aquarell von Kristin Damaschke in Ocker, Grün und Pink', 950, 1168, '(min-width: 960px) 460px, 100vw')}</figure></div>
    <div>
      <p class="eyebrow">Gut zu wissen</p>
      <h2>Sie müssen nicht malen können</h2>
      <p>Es geht nicht um schöne Bilder. Es geht um Ihren Ausdruck. Viele meiner Klientinnen und Klienten haben seit der Schulzeit keinen Pinsel mehr in der Hand gehabt, und genau das kann befreiend sein.</p>
      <p>Ich arbeite intermedial: Neben Malen und Zeichnen können auch Ton, Collage, Bewegung oder Schreiben eine Rolle spielen. In Einzelsitzungen ist das kein eigenes Programm, sondern eine Einladung innerhalb der körperorientierten Arbeit nach Somatic Experiencing: Ein Bild kann zeigen, was der Körper gerade erzählt.</p>
      <p><a class="more" href="../somatic-experiencing/">Zu Somatic Experiencing {ARROW}</a></p>
      <h3 style="margin-top:var(--s3)">Kunsttherapeutische Gruppe</h3>
      <p>In kleinen Gruppen erleben Sie Selbsterfahrung durch Gestalten, mit anderen und doch ganz bei sich. <strong>Aktuell sind keine Gruppentermine geplant.</strong> Wenn Sie Interesse haben, schreiben Sie mir gern; ich melde mich, sobald eine neue Gruppe startet.</p>
    </div>
  </div>
</div></section>
{closing(r)}
'''
    return layout('kunsttherapie/', 'Kunsttherapie in Wismar',
                  'Kunsttherapie in Wismar und online mit Kristin Damaschke, Kunsttherapeutin (M.A.): Inneres sichtbar machen durch Malen und Gestalten. Keine Vorkenntnisse nötig. Einzeln und in der Gruppe.',
                  body, 'kunsttherapie/', 'Kunsttherapie')


# ---------------------------------------------------------------- Angebot
@page('angebot/')
def angebot():
    r = '../'
    body = page_head(r, 'Angebot & Preise', 'Sicherheit und Ankommen', 'Einzelsitzungen in Wismar, in einem ruhigen Praxisraum bei Wismar oder online. Termine nach Vereinbarung, auch samstags.', 'Angebot &amp; Preise') + f'''
<section class="section" style="padding-top:0"><div class="wrap">
  <ul class="prices">
    <li class="price"><span class="tag">50 Minuten · 90 €</span><h3>Somatic Experiencing, traumasensibel und körperorientiert</h3><p>Psychotherapie nach dem Heilpraktikergesetz mit Somatic Experiencing im Mittelpunkt. Für alte Muster, belastende Erfahrungen und Lebenskrisen.</p><a class="more" href="../somatic-experiencing/">Zum Ansatz {ARROW}</a></li>
    <li class="price"><span class="tag">50 Minuten · 90 €</span><h3>Nervensystem­regulation (Anti-Stress)</h3><p>Praktische Begleitung, um Stress zu regulieren und wieder zur Ruhe zu kommen. Auch bei Neurodivergenz.</p><a class="more" href="../wofuer/#stress">Mehr dazu {ARROW}</a></li>
    <li class="price"><span class="tag">50 Minuten · 120 €</span><h3>Coaching</h3><p>Für berufliche und persönliche Fragen, Entscheidungen und Übergänge, mit Körper und Bild als Erkenntnisweg.</p><a class="more" href="../kontakt/">Anfragen {ARROW}</a></li>
  </ul>
  <p class="muted" style="margin-top:var(--s3)">Kunsttherapeutische Selbsterfahrungsgruppe: aktuell keine Termine. <a href="../kunsttherapie/">Mehr zur Gruppe</a></p>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Ablauf</p><h2>Vom ersten Kontakt bis zur ersten Sitzung</h2></div>
    <div>
      <ol class="steps">
        <li><div><strong>Kurz kennenlernen</strong>Sie rufen an oder schreiben per WhatsApp oder E-Mail. In einem kurzen Telefonat (etwa 15 Minuten) klären wir Ihr Anliegen und Ihre Fragen.</div></li>
        <li><div><strong>Erstgespräch</strong>In Wismar in der Lübschen Straße 71 oder online. Wir schauen gemeinsam, was Sie brauchen und wie wir arbeiten.</div></li>
        <li><div><strong>Begleitung</strong>Die weiteren Sitzungen finden meist in meinem ruhigen Praxisraum etwas außerhalb von Wismar statt, oder weiterhin online. Wie oft wir uns sehen, entscheiden wir gemeinsam.</div></li>
      </ol>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split media-right">
    <div class="split-media"><figure>{img(r, 'raum', 'Heller Praxisraum mit Sesseln, Sofa und Blick ins Grüne', 1200, 1600, '(min-width: 960px) 460px, 100vw')}<figcaption>Der Praxisraum bei Wismar</figcaption></figure></div>
    <div>
      <p class="eyebrow">Kosten</p>
      <h2>Was Sie zu den Kosten wissen sollten</h2>
      <p>Meine Leistungen sind <strong>Selbstzahlerleistungen</strong>. Die gesetzlichen Krankenkassen übernehmen die Kosten in der Regel nicht.</p>
      <p>Private Krankenversicherungen und private Zusatzversicherungen für Heilpraktikerleistungen erstatten Psychotherapie nach dem Heilpraktikergesetz teilweise. Bitte fragen Sie vorab bei Ihrer Versicherung nach; ich stelle Ihnen gern eine Rechnung nach dem Gebührenverzeichnis für Heilpraktiker (GebüH) aus.</p>
      <p>Der Vorteil: Sie brauchen keine Diagnose für die Kasse, es gibt keine langen Wartezeiten, und wir entscheiden selbst über Dauer und Häufigkeit.</p>
      <p class="muted">Abgesagte Termine bitte mindestens 24 Stunden vorher. <em>(Vorschlag, von Kristin zu bestätigen.)</em></p>
    </div>
  </div>
</div></section>

<section class="section sage"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Für wen</p><h2>Dieses Angebot richtet sich an Menschen, die …</h2></div>
    <div>
      <ul class="checks two">
        <li>innere Stabilität und Ruhe suchen</li><li>immer wieder von alten Gefühlen eingeholt werden</li><li>unter Stress, Druck oder Erschöpfung leiden</li><li>Burnout vorbeugen möchten</li><li>mit Ängsten oder Unruhe leben</li><li>Verlust, Trennung oder Krisen verarbeiten</li><li>belastende Erfahrungen behutsam bearbeiten möchten</li><li>sich selbst und ihren Körper besser verstehen wollen</li>
      </ul>
      <p style="margin-top:var(--s2)"><a class="more" href="../fragen/">Häufige Fragen {ARROW}</a></p>
    </div>
  </div>
</div></section>
{closing(r)}
'''
    return layout('angebot/', 'Angebot und Preise',
                  'Einzelsitzungen Psychotherapie (HeilprG) und Nervensystemregulation je 90 €, Coaching 120 €, jeweils 50 Minuten. In Wismar, bei Wismar und online. Ablauf, Kosten und Erstattung.',
                  body, 'angebot/', 'Angebot & Preise')


# ---------------------------------------------------------------- Über mich
@page('ueber-mich/')
def ueber():
    r = '../'
    body = page_head(r, 'Über mich', 'Kristin Damaschke', 'Künstlerin, Kunsttherapeutin und Heilpraktikerin für Psychotherapie. Geboren in Riesa, viele Jahre in Hamburg, seit 2021 zu Hause bei Wismar.', 'Über mich') + f'''
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="split">
    <div class="split-media portrait"><figure>{img(r, 'kristin-ruhig', 'Kristin Damaschke in rostroter Bluse, mit leichtem Lächeln', 1600, 2000, '(min-width: 960px) 460px, 100vw', loading='eager')}</figure></div>
    <div>
      <p class="eyebrow">Mein Weg</p>
      <h2>Von der Kunst zum Körper</h2>
      <p class="lead">Die Kunst war zuerst da. Sie hat mich gelehrt, dass sich Inneres zeigen will, auch ohne Worte.</p>
      <p>Aus dieser Erfahrung heraus habe ich Intermediale Kunsttherapie studiert und viele Jahre in Kliniken gearbeitet: in der Psychosomatik, in der Psychiatrie und mit Menschen nach großen Belastungen. Dort habe ich gesehen, wie viel sich verändert, wenn Menschen einen Zugang jenseits der Sprache finden.</p>
      <p>Mit der Zeit kam der Körper hinzu. Heute arbeite ich vor allem traumasensibel und körperorientiert mit Somatic Experiencing. Die Kunst ist geblieben: als eigener Raum für mich und als stiller Begleiter in meinen Stunden, wenn Worte nicht reichen.</p>
      <p class="pull" style="font-size:clamp(1.5rem,1.2rem + 1vw,2rem);margin-top:var(--s3)">„Alles ist Licht und Schatten, und es geht um den Tanz dazwischen.“</p>
    </div>
  </div>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Qualifikationen</p><h2>Ausbildungen</h2></div>
    <div>
      <ul class="timeline">
        <li><span class="when">seit 2023</span><span><strong>Somatic Experiencing® (SE)</strong> nach Dr. Peter A. Levine, Ausbildung bei Marinka Gattnar (laufend)</span></li>
        <li><span class="when">2018</span><span><strong>Heilpraktikerin für Psychotherapie</strong> (Erlaubnis nach dem Heilpraktikergesetz, Husum)</span></li>
        <li><span class="when">2015–2019</span><span><strong>Master of Arts Intermediale Kunsttherapie</strong>, MSH Medical School Hamburg</span></li>
        <li><span class="when">früher</span><span><strong>Diplom Medien und Information</strong> (Dipl. Medok.), HAW Hamburg</span></li>
      </ul>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Erfahrung</p><h2>Berufliche Stationen</h2></div>
    <div>
      <ul class="checks">
        <li>Sana Kliniken Lübeck</li>
        <li>Klinikum Schloss Lütgenhof: Stressfolgeerkrankungen, Psychosomatik, Personale Medizin</li>
        <li>Psychiatrische Tagesklinik Glückstadt (Klinikum Itzehoe)</li>
        <li>Vitanas Psychiatrisches Centrum Glückstadt</li>
        <li>Selbstständige Kunsttherapeutin in Wismar und Lübeck</li>
      </ul>
    </div>
  </div>
</div></section>

<section class="section sage" id="zuweisende"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Für Ärztinnen, Kliniken und Kolleginnen</p><h2>Auf einen Blick</h2></div>
    <div>
      <dl class="facts">
        <div><dt>Berufsbezeichnung</dt><dd>Heilpraktikerin für Psychotherapie (HeilprG); Kunsttherapeutin M.A.; keine approbierte Psychotherapeutin, keine Kassenzulassung</dd></div>
        <div><dt>Schwerpunkte</dt><dd>Traumasensible, körperorientierte Arbeit (Somatic Experiencing, in Ausbildung), Nervensystemregulation, Kunsttherapie</dd></div>
        <div><dt>Geeignet für</dt><dd>Erwachsene mit Stressfolgen, wiederkehrenden emotionalen Mustern, Ängsten, belastenden Erfahrungen; auch begleitend oder im Anschluss an eine Psychotherapie oder Klinik</dd></div>
        <div><dt>Nicht geeignet für</dt><dd>akute Suizidalität, akute Psychosen, akute Suchterkrankungen; hier bitte ärztliche oder klinische Versorgung</dd></div>
        <div><dt>Orte</dt><dd>Wismar (Lübsche Straße 71), Praxisraum bei Wismar, online</dd></div>
        <div><dt>Termine</dt><dd>in der Regel kurzfristig, nach Vereinbarung, auch samstags</dd></div>
        <div><dt>Kosten</dt><dd>Selbstzahlerleistung, 90 € je 50 Minuten</dd></div>
        <div><dt>Kontakt</dt><dd><a href="tel:{PHONE_TEL}">{PHONE}</a> · <a href="mailto:{MAIL}">{MAIL}</a></dd></div>
      </dl>
    </div>
  </div>
</div></section>
{closing(r)}
'''
    return layout('ueber-mich/', 'Über mich: Kristin Damaschke',
                  'Kristin Damaschke: Heilpraktikerin für Psychotherapie, Kunsttherapeutin (M.A., MSH Hamburg), Somatic Experiencing in Ausbildung. Klinische Erfahrung in Psychosomatik und Psychiatrie. Praxis in Wismar.',
                  body, 'ueber-mich/', 'Über mich')


# ---------------------------------------------------------------- Kunst
@page('kunst/')
def kunst():
    r = '../'
    body = page_head(r, 'Kunst', 'Kunst als Ursprung', 'Ein Teil meiner Geschichte, und ein Raum, der weiterhin wirkt.', 'Kunst') + f'''
<figure class="band contained">{img(r, 'art-blau', 'Aquarell von Kristin Damaschke in Blau, Grün und Rot', 1600, 700)}</figure>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Meine künstlerische Arbeit</p><h2>Art for Life</h2></div>
    <div>
      <p class="lead">Kunst begleitet mich seit vielen Jahren. Sie war der Anfang meines Weges zur Kunsttherapie.</p>
      <p>Meine Bilder entstehen meist abstrakt, in Aquarell und Acryl, mit Farben, die ineinanderfließen und sich begegnen. Heute liegt mein therapeutischer Schwerpunkt auf der körperorientierten, traumasensiblen Arbeit. Die Kunst bleibt mein eigener Raum und fließt vor allem in die Gruppenangebote ein.</p>
      <p>Mehr Bilder zeige ich auf <a href="{IG_ART}">Instagram</a> und auf meiner <a href="https://mail96198.wixsite.com/kristin-damaschke">Kunstseite</a>.</p>
    </div>
  </div>
</div></section>

<section class="section white"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Werke</p><h2>Auswahl</h2></div>
  <ul class="artgrid">
    <li>{img(r, 'art-erde', 'Aquarell in Ocker, Salbeigrün und Terrakotta', 1600, 850, '(min-width: 900px) 380px, 50vw')}</li>
    <li>{img(r, 'art-pink', 'Aquarell in Magenta, Türkis und Rotbraun', 950, 1332, '(min-width: 900px) 380px, 50vw')}</li>
    <li>{img(r, 'art-gruen', 'Aquarell in Ocker, Grün und Pink', 950, 1168, '(min-width: 900px) 380px, 50vw')}</li>
    <li>{img(r, 'art-ocker', 'Aquarell mit Kreisen in Ocker, Rot und Türkis', 1600, 740, '(min-width: 900px) 380px, 50vw')}</li>
    <li>{img(r, 'art-tuerkis', 'Aquarell in Türkis und Magenta', 1600, 600, '(min-width: 900px) 380px, 50vw')}</li>
    <li>{img(r, 'art-blau', 'Aquarell in Blau, Grün und Rot', 1600, 700, '(min-width: 900px) 380px, 50vw')}</li>
  </ul>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split-head"><p class="eyebrow">Ausstellungen</p><h2>Wo meine Bilder zu sehen waren</h2></div>
    <div>
      <h3>Gruppenausstellungen</h3>
      <ul class="timeline">
        <li><span class="when">2026</span><span>Spurensuche, Kunstraum K70, Lübeck</span></li>
        <li><span class="when">2026</span><span>Echoes of becoming, Atelier-Galerie Ralph Richter, Lübeck</span></li>
        <li><span class="when">2025</span><span>Creative Citizen Dialogue, Galleri Chapman, Karlskrona</span></li>
        <li><span class="when">2025</span><span>Begegnungen, Kunstraum K70, Lübeck</span></li>
        <li><span class="when">2021</span><span>Divulgarti Arte Italiana, Palazzo Divulgarti, Genua</span></li>
        <li><span class="when">2019</span><span>Little Treasures, Galerie di Marchi, Bologna</span></li>
        <li><span class="when">2015</span><span>Gallery Oliver Widmann, Oelkersallee, Hamburg</span></li>
      </ul>
      <h3 style="margin-top:var(--s4)">Einzelausstellungen</h3>
      <ul class="timeline">
        <li><span class="when">2021</span><span>Art For Life, Moritz Consulting, Potsdam</span></li>
        <li><span class="when">2020</span><span>Abstraktes, Galerie Cavissamba, Haselau</span></li>
        <li><span class="when">2020</span><span>Momente in Abstrakt, Elbmarschenhaus, Haseldorf</span></li>
        <li><span class="when">2019</span><span>SEIN, Kulturbotschaft, Hamburg</span></li>
        <li><span class="when">2018</span><span>Art For Life, VHS Halstenbek</span></li>
      </ul>
    </div>
  </div>
</div></section>

<section class="section white"><div class="wrap">
  <div class="section-head"><p class="eyebrow">Impressionen</p><h2>Aus Ausstellungen</h2></div>
  <ul class="gallery">
    <li><figure>{img(r, 'ausstellung-luebeck', 'Bilder von Kristin Damaschke in einem Galeriefenster in Lübeck, darin spiegeln sich Giebelhäuser', 1200, 1600, '(min-width: 900px) 280px, 50vw')}<figcaption>Lübeck</figcaption></figure></li>
    <li><figure>{img(r, 'ausstellung-wand', 'Abstrakte farbige Bilder an einer weißen Galeriewand', 1200, 1600, '(min-width: 900px) 280px, 50vw')}<figcaption>Galeriewand</figcaption></figure></li>
    <li><figure>{img(r, 'ausstellung-haengung', 'Hängung zweier Bilder in einer Ausstellung', 1200, 1600, '(min-width: 900px) 280px, 50vw')}<figcaption>Beim Hängen</figcaption></figure></li>
    <li><figure>{img(r, 'ausstellung-rot', 'Großformatige Bilder in Rot und Rosa in einem hellen Ausstellungsraum', 1600, 1067, '(min-width: 900px) 280px, 50vw')}<figcaption>Ausstellungsraum</figcaption></figure></li>
  </ul>
</div></section>
'''
    return layout('kunst/', 'Kunst und Ausstellungen',
                  'Abstrakte Malerei von Kristin Damaschke: Aquarell und Acryl, Einzel- und Gruppenausstellungen in Lübeck, Hamburg, Potsdam, Genua, Bologna und Karlskrona.',
                  body, 'kunst/', 'Kunst')


# ---------------------------------------------------------------- Fragen
FAQ = [
    ('Zur Person', [
        ('Sind Sie Psychotherapeutin?',
         '<p>Nein, nicht im Sinne des Psychotherapeutengesetzes. Ich bin <strong>Heilpraktikerin für Psychotherapie</strong>. Das heißt: Ich habe eine staatliche Erlaubnis, psychotherapeutisch zu arbeiten (nach dem Heilpraktikergesetz, seit 2018). Ich bin keine approbierte Psychologische Psychotherapeutin und habe keine Kassenzulassung.</p><p>Dazu bin ich studierte Kunsttherapeutin (M.A.) und in der Ausbildung zur Somatic-Experiencing-Practitioner. Viele Jahre habe ich in psychiatrischen und psychosomatischen Kliniken gearbeitet.</p>'),
        ('Ich habe schon Therapie gemacht. Was ist bei Ihnen anders?',
         '<p>In vielen Therapien steht das Gespräch im Mittelpunkt: verstehen, einordnen, erzählen. Das ist wertvoll. Manche Muster sitzen aber tiefer, im Nervensystem und im Körper. Dann kann man genau wissen, woher eine Reaktion kommt, und sie trotzdem nicht ändern.</p><p>Bei mir arbeiten wir zusätzlich mit dem Körper (Somatic Experiencing) und mit Bildern (Kunsttherapie). Viele erleben das als hilfreiche Ergänzung zu einer früheren Gesprächstherapie.</p>'),
        ('Was ist Somatic Experiencing?',
         '<p>Ein körperorientierter Ansatz zur Lösung von Stress- und Traumafolgen, entwickelt von Dr. Peter A. Levine. Wir achten auf Körperempfindungen und pendeln behutsam zwischen Belastendem und Stärkendem, damit das Nervensystem seine Selbstregulation wiederfindet. <a href="../somatic-experiencing/">Mehr dazu</a>.</p>'),
    ]),
    ('Zum Ablauf', [
        ('Wie beginne ich?',
         f'<p>Rufen Sie mich an ({PHONE}), schreiben Sie per WhatsApp oder E-Mail. In einem kurzen Telefonat klären wir Ihr Anliegen. Danach folgt ein Erstgespräch in Wismar oder online.</p>'),
        ('Muss ich über alles sprechen, was passiert ist?',
         '<p>Nein. Traumasensibel zu arbeiten bedeutet, dass Sie nichts im Detail erzählen oder noch einmal durchleben müssen. Wir gehen nur so weit, wie es sich sicher anfühlt.</p>'),
        ('Muss ich malen können?',
         '<p>Nein. In der Kunsttherapie geht es um Ausdruck, nicht um schöne Bilder. Vorkenntnisse sind nicht nötig.</p>'),
        ('Gibt es Körperkontakt?',
         '<p>Nur, wenn Sie es ausdrücklich möchten. Sie bleiben bekleidet, und Sie können jederzeit Stopp sagen.</p>'),
        ('Wie viele Sitzungen brauche ich?',
         '<p>Das ist sehr unterschiedlich. Manche Anliegen klären sich in wenigen Sitzungen, andere brauchen eine längere Begleitung. Wir besprechen das gemeinsam und überprüfen es regelmäßig.</p>'),
        ('Wo finden die Sitzungen statt?',
         '<p>Das Erstgespräch meist in Wismar (Lübsche Straße 71) oder online. Die weiteren Sitzungen finden in der Regel in meinem ruhigen Praxisraum etwas außerhalb von Wismar statt. Online-Sitzungen sind jederzeit möglich, auch für Menschen aus Schwerin, Lübeck oder weiter weg.</p>'),
    ]),
    ('Zu den Kosten', [
        ('Was kostet eine Sitzung?',
         '<p>Einzelsitzungen Psychotherapie und Nervensystemregulation kosten 90 € (50 Minuten), Coaching 120 € (50 Minuten).</p>'),
        ('Zahlt die Krankenkasse?',
         '<p>Gesetzliche Krankenkassen übernehmen die Kosten in der Regel nicht. Private Krankenversicherungen und private Zusatzversicherungen für Heilpraktikerleistungen erstatten oft einen Teil. Bitte klären Sie das vorab mit Ihrer Versicherung.</p>'),
        ('Gibt es Wartezeiten?',
         '<p>In der Regel kann ich kurzfristig Termine anbieten, auch samstags.</p>'),
    ]),
    ('Wenn es dringend ist', [
        ('Ich bin in einer akuten Krise. Was kann ich tun?',
         '<p>Bitte wenden Sie sich sofort an die Telefonseelsorge (0800 111 0 111 oder 0800 111 0 222, rund um die Uhr, kostenfrei), den ärztlichen Bereitschaftsdienst (116 117) oder im Notfall an den Notruf 112. Meine Praxis ist kein Krisendienst.</p>'),
    ]),
]


@page('fragen/')
def fragen():
    r = '../'
    groups = ''
    entities = []
    for title, qs in FAQ:
        items = ''.join(f'<details><summary>{q}</summary><div class="answer">{a}</div></details>' for q, a in qs)
        groups += f'<div class="faq-group"><h2>{title}</h2><div class="faq">{items}</div></div>'
        for q, a in qs:
            entities.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', a)}})
    body = page_head(r, 'Häufige Fragen', 'Ehrliche Antworten auf Ihre Fragen', 'Zu meiner Ausbildung, zum Ablauf und zu den Kosten. Wenn Ihre Frage fehlt, rufen Sie mich gern an.', 'Häufige Fragen') + f'''
<section class="section" style="padding-top:var(--s3)"><div class="wrap narrow">{groups}</div></section>
{closing(r)}
'''
    extra = [{'@type': 'FAQPage', '@id': LIVE + 'fragen/#faq', 'mainEntity': entities}]
    return layout('fragen/', 'Häufige Fragen',
                  'Heilpraktikerin oder Psychotherapeutin? Was ist anders als in der Gesprächstherapie? Was kostet es, zahlt die Kasse? Antworten von Kristin Damaschke, Lebensfarben Wismar.',
                  body, None, 'Häufige Fragen', extra)


# ---------------------------------------------------------------- Kontakt
@page('kontakt/')
def kontakt():
    r = '../'
    body = page_head(r, 'Kontakt', 'Schreiben Sie mir, oder rufen Sie an', 'Ich freue mich, von Ihnen zu hören. Wenn ich gerade in einer Sitzung bin, schreiben Sie mir gern eine SMS oder WhatsApp. Ich melde mich so bald wie möglich.', 'Kontakt') + f'''
<section class="section" style="padding-top:0" id="kennenlernen"><div class="wrap">
  <ul class="contact-ways">
    <li><a href="tel:{PHONE_TEL}"><span class="label">Telefon</span><span class="value">{PHONE}</span><span class="hint">Für ein erstes Kennenlernen, etwa 15 Minuten</span></a></li>
    <li><a href="{WA}"><span class="label">WhatsApp oder SMS</span><span class="value">{PHONE}</span><span class="hint">Schreiben Sie mir kurz, wann ich Sie erreiche</span></a></li>
    <li><a href="mailto:{MAIL}?subject=Anfrage%20Kennenlernen"><span class="label">E-Mail</span><span class="value">{MAIL}</span><span class="hint">Ich antworte in der Regel innerhalb von zwei Werktagen</span></a></li>
  </ul>
</div></section>

<section class="section white"><div class="wrap">
  <div class="split media-right">
    <div class="split-media portrait"><figure>{img(r, 'kristin-lachend', 'Kristin Damaschke lacht herzlich in die Kamera', 1600, 2000, '(min-width: 960px) 460px, 100vw')}</figure></div>
    <div>
      <p class="eyebrow">Praxis</p>
      <h2>Lebensfarben · Praxis für Somatic Experiencing</h2>
      <address><strong>Kristin Damaschke · Lebensfarben</strong><br>Lübsche Straße 71<br>23966 Wismar</address>
      <p style="margin-top:var(--s2)"><a class="more" href="{OSM}">Auf der Karte ansehen {ARROW}</a></p>
      <p>Das Erstgespräch findet meist hier in der Wismarer Altstadt statt. Die weiteren Sitzungen in einem ruhigen Praxisraum etwas außerhalb von Wismar; die genaue Adresse erhalten Sie mit der Terminbestätigung. Online-Sitzungen sind jederzeit möglich.</p>
      <dl class="facts">
        <div><dt>Termine</dt><dd>nach Vereinbarung, auch samstags</dd></div>
        <div><dt>Einzugsgebiet</dt><dd>Wismar, Nordwestmecklenburg, Schwerin, Lübeck und online</dd></div>
        <div><dt>Instagram</dt><dd><a href="{IG_PRAXIS}">Praxis</a> · <a href="{IG_ART}">Kunst</a></dd></div>
      </dl>
      <div class="note note--crisis" style="margin-top:var(--s3)"><p>In einer akuten Krise: Telefonseelsorge 0800 111 0 111 (rund um die Uhr, kostenfrei), ärztlicher Bereitschaftsdienst 116 117, Notruf 112.</p></div>
    </div>
  </div>
</div></section>
'''
    return layout('kontakt/', 'Kontakt',
                  'Kontakt zu Kristin Damaschke, Lebensfarben: Telefon und WhatsApp 0163 583 7997, E-Mail mail@kristindamaschke.de, Lübsche Straße 71, 23966 Wismar.',
                  body, 'kontakt/', 'Kontakt')


# ---------------------------------------------------------------- Rechtliches (Entwürfe)
@page('impressum/')
def impressum():
    r = '../'
    body = f'''<section class="page-head"><div class="wrap narrow"><p class="eyebrow">Rechtliches</p><h1>Impressum</h1></div></section>
<section class="section legal" style="padding-top:0"><div class="wrap narrow">
  <div class="note" style="margin-bottom:var(--s4)"><p><strong>Entwurf.</strong> Die aktuelle Seite hat kein Impressum. Bitte von Kristin prüfen und ergänzen (z. B. zuständige Aufsichtsbehörde, Berufsverband).</p></div>
  <h2>Angaben gemäß § 5 DDG</h2>
  <address>Kristin Damaschke<br>Lebensfarben<br>Lübsche Straße 71<br>23966 Wismar</address>
  <h2>Kontakt</h2>
  <p>Telefon: {PHONE}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>
  <h2>Berufsbezeichnung und berufsrechtliche Regelungen</h2>
  <p>Heilpraktikerin, beschränkt auf das Gebiet der Psychotherapie. Erlaubnis nach dem Heilpraktikergesetz (HeilprG), erteilt 2018 in Husum.<br>Zuständige Aufsichtsbehörde: [Gesundheitsamt Landkreis Nordwestmecklenburg, bitte prüfen]<br>Berufsrechtliche Regelungen: Heilpraktikergesetz und Durchführungsverordnung, abrufbar unter gesetze-im-internet.de.</p>
  <p>Kunsttherapeutin (M.A., Intermediale Kunsttherapie, MSH Medical School Hamburg).</p>
  <h2>Verantwortlich für den Inhalt</h2>
  <p>Kristin Damaschke, Anschrift wie oben.</p>
  <h2>Verbraucherstreitbeilegung</h2>
  <p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
  <h2>Bildnachweis</h2>
  <p>Kristin Damaschke, Alexander Tiffert, Alexander Henke (Unsplash).</p>
</div></section>'''
    return layout('impressum/', 'Impressum', 'Impressum von Lebensfarben, Kristin Damaschke, Wismar.', body)


@page('datenschutz/')
def datenschutz():
    r = '../'
    body = f'''<section class="page-head"><div class="wrap narrow"><p class="eyebrow">Rechtliches</p><h1>Datenschutz</h1></div></section>
<section class="section legal" style="padding-top:0"><div class="wrap narrow">
  <div class="note" style="margin-bottom:var(--s4)"><p><strong>Entwurf</strong> für eine Seite auf GitHub Pages ohne Cookies, Tracking oder Inhalte Dritter. Bitte vor einer Veröffentlichung prüfen lassen.</p></div>
  <h2>Verantwortliche</h2>
  <p>Kristin Damaschke, Lebensfarben, Lübsche Straße 71, 23966 Wismar, <a href="mailto:{MAIL}">{MAIL}</a>, {PHONE}.</p>
  <h2>Hosting</h2>
  <p>Diese Website wird bei GitHub Pages gehostet (GitHub Inc., 88 Colin P. Kelly Jr. St., San Francisco, CA 94107, USA). Beim Aufruf verarbeitet GitHub technisch notwendige Daten wie IP-Adresse, Zeitpunkt und aufgerufene Seite, um die Seite auszuliefern und vor Missbrauch zu schützen (Art. 6 Abs. 1 lit. f DSGVO). GitHub ist unter dem EU-US Data Privacy Framework zertifiziert.</p>
  <h2>Keine Cookies, kein Tracking</h2>
  <p>Diese Website setzt keine Cookies, verwendet keine Analysewerkzeuge und lädt keine Schriften oder Inhalte von anderen Servern.</p>
  <h2>Kontakt per Telefon, E-Mail oder WhatsApp</h2>
  <p>Wenn Sie mich kontaktieren, verarbeite ich Ihre Angaben, um Ihre Anfrage zu beantworten (Art. 6 Abs. 1 lit. b DSGVO). Gesundheitsdaten verarbeite ich nur mit Ihrer Einwilligung (Art. 9 Abs. 2 lit. a DSGVO). Bitte senden Sie über E-Mail oder WhatsApp keine ausführlichen Gesundheitsinformationen; das besprechen wir persönlich. Bei WhatsApp gelten zusätzlich die Datenschutzbestimmungen der WhatsApp Ireland Ltd.</p>
  <h2>Ihre Rechte</h2>
  <p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch. Sie können sich bei einer Datenschutzaufsichtsbehörde beschweren, z. B. beim Landesbeauftragten für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern.</p>
</div></section>'''
    return layout('datenschutz/', 'Datenschutz', 'Datenschutzerklärung von Lebensfarben, Kristin Damaschke, Wismar.', body)


# ---------------------------------------------------------------- Konzept (aus ANALYSE.md)
@page('konzept/')
def konzept():
    r = '../'
    md = (ROOT / 'ANALYSE.md').read_text(encoding='utf-8')
    md = md.split('\n', 1)[1]  # erste Überschrift wird zur H1 der Seite
    content = markdown.markdown(md, extensions=['tables', 'sane_lists'])
    content = content.replace('<h1>', '<h2>').replace('</h1>', '</h2>')
    sw = ''.join(f'<li><span style="background:{c}"></span>{n}<br>{c}</li>' for n, c in [('Waldgrün', '#2F4A40'), ('Salbei', '#DCE5DC'), ('Papier', '#F8F5EF'), ('Sand', '#E9DFCF'), ('Terrakotta', '#B5603F'), ('Text', '#26302C')])
    content = content.replace('<h2>4. Umzug', f'<ul class="swatches" aria-label="Farbpalette">{sw}</ul>\n<h2>4. Umzug', 1)
    body = f'''<section class="page-head"><div class="wrap"><p class="eyebrow">Für Kristin und Alexander · nicht Teil der späteren Seite</p><h1>Analyse, Konzept und Umzugsplan</h1><p class="lead">Wie die neue Lebensfarben-Seite entstanden ist, was sie anders macht und wie ein Umzug ohne Ranking-Verlust gelingt.</p></div></section>
<section class="section white"><div class="wrap"><div class="prose">{content}</div></div></section>'''
    return layout('konzept/', 'Analyse und Konzept', 'Analyse von lebensfarben.net aus fünf Rollen, Designkonzept und Umzugsplan.', body)


# ---------------------------------------------------------------- 404, robots, llms.txt
@page('404')
def notfound():
    body = '''<section class="page-head"><div class="wrap"><p class="eyebrow">Seite nicht gefunden</p><h1>Diese Seite gibt es nicht (mehr).</h1><p class="lead">Vielleicht hilft der Weg zurück zur <a href="/lebensfarben-vorschau/">Startseite</a>.</p></div></section>'''
    return layout('404', 'Seite nicht gefunden', 'Seite nicht gefunden.', body)


LLMS = f'''# Lebensfarben · Kristin Damaschke

> Praxis für traumasensible, körperorientierte Begleitung (Somatic Experiencing) und Kunsttherapie in Wismar (Mecklenburg-Vorpommern) und online. Kristin Damaschke ist Heilpraktikerin für Psychotherapie (Erlaubnis nach dem Heilpraktikergesetz, 2018) und Kunsttherapeutin (M.A. Intermediale Kunsttherapie, MSH Medical School Hamburg), in Ausbildung zur Somatic-Experiencing-Practitioner seit 2023. Sie ist keine approbierte Psychotherapeutin und hat keine Kassenzulassung; Selbstzahlerpraxis mit kurzfristigen Terminen.

## Für wen
- Erwachsene, oft beruflich erfolgreich und therapieerfahren, die ihre Muster verstehen und trotzdem immer wieder von alten Gefühlen eingeholt werden
- Menschen mit Stress, Erschöpfung, Schlafproblemen, Ängsten, Burnout-Gefahr, auch bei Neurodivergenz
- Menschen mit belastenden oder traumatischen Erfahrungen, die nicht alles noch einmal erzählen möchten
- Ergänzend zu oder im Anschluss an eine Gesprächspsychotherapie oder einen Klinikaufenthalt
- Nicht geeignet bei akuter Suizidalität, akuten Psychosen oder akuter Sucht

## Angebote und Preise (je 50 Minuten)
- Psychotherapie nach HeilprG, traumasensibel und körperorientiert: 90 €
- Nervensystemregulation (Anti-Stress): 90 €
- Coaching: 120 €
- Kunsttherapeutische Selbsterfahrungsgruppe: Termine nach Ankündigung

## Ort und Kontakt
- Lübsche Straße 71, 23966 Wismar; Praxisraum bei Wismar; online
- Einzugsgebiet: Wismar, Nordwestmecklenburg, Schwerin, Lübeck, online deutschlandweit
- Telefon/WhatsApp: {PHONE}; E-Mail: {MAIL}
- Termine nach Vereinbarung, auch samstags

## Erfahrung
- Sana Kliniken Lübeck; Klinikum Schloss Lütgenhof (Psychosomatik); Psychiatrische Tagesklinik Glückstadt; Vitanas Psychiatrisches Centrum Glückstadt

## Seiten
- [Wofür](wofuer/): Anliegen in der Sprache der Klientinnen
- [Somatic Experiencing](somatic-experiencing/)
- [Kunsttherapie](kunsttherapie/)
- [Angebot und Preise](angebot/)
- [Über mich](ueber-mich/)
- [Häufige Fragen](fragen/)
- [Kontakt](kontakt/)
'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#2f4a40"/><circle cx="26" cy="30" r="14" fill="#b5603f" opacity=".9"/><circle cx="38" cy="36" r="13" fill="#dce5dc" opacity=".85"/></svg>'''


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST)
    for slug, fn in PAGES.items():
        out = DIST / ('404.html' if slug == '404' else slug + 'index.html')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(fn(), encoding='utf-8')
    (DIST / 'robots.txt').write_text('# Vorschau: bitte nicht indexieren\nUser-agent: *\nDisallow: /\n', encoding='utf-8')
    (DIST / 'llms.txt').write_text(LLMS, encoding='utf-8')
    (DIST / 'favicon.svg').write_text(FAVICON, encoding='utf-8')
    (DIST / '.nojekyll').write_text('', encoding='utf-8')
    # Prüfung: jede Seite noindex, genau eine H1, lang=de
    errors = []
    for f in DIST.rglob('*.html'):
        t = f.read_text(encoding='utf-8')
        if 'name="robots" content="noindex' not in t: errors.append(f'{f}: noindex fehlt')
        if t.count('<h1') != 1: errors.append(f'{f}: {t.count("<h1")} H1')
        if '<html lang="de">' not in t: errors.append(f'{f}: lang fehlt')
        for m in re.findall(r'src="([^"]+)"', t):
            if m.startswith('http'): continue
            p = (f.parent / m).resolve()
            if not p.exists(): errors.append(f'{f.relative_to(DIST)}: fehlt {m}')
    if errors:
        print('\n'.join(sorted(set(errors))))
        raise SystemExit(1)
    print(f'{len(PAGES)} Seiten gebaut in {DIST}')


if __name__ == '__main__':
    main()
