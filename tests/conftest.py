"""
Configuración global de pytest y fixtures compartidos.
"""

import os
from pathlib import Path

import pytest

# Establecer variables de entorno para tests antes de importar config
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token_12345")
os.environ.setdefault("ADMIN_USER_ID", "123456789")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("LOG_FORMAT", "text")


@pytest.fixture
def fixtures_dir() -> Path:
    """Directorio de fixtures para tests."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def real_pdf_files():
    """Rutas a los archivos PDF reales para tests."""
    test_dir = Path(__file__).parent
    return {
        "modificado_gallur_2026_01_03.pdf": test_dir / "pdf_examples" / "modificado_gallur_2026_01_03.pdf",
        "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf": test_dir / "pdf_examples" / "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf",
        "sub23_gallur_2026_01_24.pdf": test_dir / "pdf_examples" / "sub23_gallur_2026_01_24.pdf"
    }


@pytest.fixture
def real_calendar_html():
    """HTML real del calendario FAM para tests."""
    return """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es-es" lang="es-es" dir="ltr">

<head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Calendario de Competiciones - Federación de Atletismo de Madrid</title>
</head>

<body>
    <div class="main-content">
        <main class="content">
            <div class="container">
                <div class="col-md-12">
                    <h1>Calendario de Competiciones</h1>

                    <div class="article-content">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Competición</th>
                                    <th>Lugar</th>
                                    <th>Documentos</th>
                                    <th>Inscripciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>03/01/2026</td>
                                    <td>Copa Madrid - Reunión Gallur</td>
                                    <td>Pabellón Municipal de Gallur</td>
                                    <td><a href="/pdfs/modificado_gallur_2026_01_03.pdf" target="_blank">PDF</a></td>
                                    <td><a href="https://inscripciones.fam.es" target="_blank">Inscribirse</a></td>
                                </tr>
                                <tr>
                                    <td>17/01/2026 - 18/01/2026</td>
                                    <td>Copa Madrid Absoluta - Combinadas</td>
                                    <td>Pabellón Municipal de Gallur</td>
                                    <td><a href="/pdfs/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf" target="_blank">PDF</a></td>
                                    <td><a href="https://inscripciones.fam.es" target="_blank">Inscribirse</a></td>
                                </tr>
                                <tr>
                                    <td>24/01/2026</td>
                                    <td>Campeonato de Madrid Sub23</td>
                                    <td>Pabellón Municipal de Gallur</td>
                                    <td><a href="/pdfs/sub23_gallur_2026_01_24.pdf" target="_blank">PDF</a></td>
                                    <td><a href="https://inscripciones.fam.es" target="_blank">Inscribirse</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>"""


@pytest.fixture
def sample_calendar_html() -> str:
    """HTML de ejemplo del calendario FAM (versión simplificada)."""
    return """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es-es" lang="es-es" dir="ltr">

<head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script id="Cookiebot" src="https://consent.cookiebot.com/uc.js" data-cbid="a6d09ef1-4bc4-416d-9880-50394f268c59"
        data-blockingmode="auto" type="text/javascript"></script>
    <!-- head -->
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta name="keywords"
        content="Federación Atletismo Madrid, FAM, Atletismo, Atletismo Madrid, Federación Madrileña de Atletismo" />
    <meta name="author" content="Cesáreo Encinas" />
    <meta name="description" content="FAM. Web oficial de la Federación de Atletismo de Madrid" />
    <meta name="generator" content="Joomla! - Open Source Content Management" />
    <title>Calendario</title>
    <link href="/templates/shaper_helix3/images/favicon.ico" rel="shortcut icon" type="image/vnd.microsoft.icon" />
    <link
        href="//fonts.googleapis.com/css?family=Open+Sans:300,300italic,regular,italic,600,600italic,700,700italic,800,800italic&amp;subset=latin"
        rel="stylesheet" type="text/css" />
    <link href="/templates/shaper_helix3/css/bootstrap.min.css" rel="stylesheet" type="text/css" />
    <link href="/templates/shaper_helix3/css/font-awesome.min.css" rel="stylesheet" type="text/css" />
    <link href="/templates/shaper_helix3/css/legacy.css" rel="stylesheet" type="text/css" />
    <link href="/templates/shaper_helix3/css/template.css" rel="stylesheet" type="text/css" />
    <link href="/templates/shaper_helix3/css/presets/preset4.css" rel="stylesheet" type="text/css" class="preset" />
    <link href="/templates/shaper_helix3/css/frontend-edit.css" rel="stylesheet" type="text/css" />
    <style type="text/css">
        body.site {
            background-image: url(/templates/shaper_helix3/images/background-body.png);
            background-repeat: inherit;
            background-size: inherit;
            background-attachment: inherit;
            background-position: 50% 0;
        }

        body {
            font-family: Open Sans, sans-serif;
            font-weight: 300;
        }

        h1 {
            font-family: Open Sans, sans-serif;
            font-weight: 800;
        }

        h2 {
            font-family: Open Sans, sans-serif;
            font-weight: 600;
        }

        h3 {
            font-family: Open Sans, sans-serif;
            font-weight: normal;
        }

        h4 {
            font-family: Open Sans, sans-serif;
            font-weight: normal;
        }

        h5 {
            font-family: Open Sans, sans-serif;
            font-weight: 600;
        }

        h6 {
            font-family: Open Sans, sans-serif;
            font-weight: 600;
        }

        #sp-top-bar {
            background-color: #f4343c;
            color: #999999;
        }

        #sp-patrocinadores {
            margin: 20px 0px 20px 0px;
        }
    </style>
    <script src="/media/jui/js/jquery.min.js?afa80cf2cfac49911d57f057e1d58194" type="text/javascript"></script>
    <script src="/media/jui/js/jquery-noconflict.js?afa80cf2cfac49911d57f057e1d58194" type="text/javascript"></script>
    <script src="/media/jui/js/jquery-migrate.min.js?afa80cf2cfac49911d57f057e1d58194" type="text/javascript"></script>
    <script src="/media/system/js/caption.js?afa80cf2cfac49911d57f057e1d58194" type="text/javascript"></script>
    <script src="/templates/shaper_helix3/js/bootstrap.min.js" type="text/javascript"></script>
    <script src="/templates/shaper_helix3/js/jquery.sticky.js" type="text/javascript"></script>
    <script src="/templates/shaper_helix3/js/main.js" type="text/javascript"></script>
    <script src="/templates/shaper_helix3/js/frontend-edit.js" type="text/javascript"></script>
    <script type="text/javascript">
        jQuery(window).on('load', function () {
            new JCaption('img.caption');
        });
        var sp_preloader = '0';
        var sp_gotop = '1';
        var sp_offanimation = 'default';
    </script>
    <meta property="og:url" content="https://www.atletismomadrid.com/index.php" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Calendario" />
    <meta property="og:description" content="" />
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-29L66JYWVB"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-29L66JYWVB');
    </script>
</head>

<body
    class="site com-content view-article no-layout no-task itemid-111 es-es ltr  sticky-header layout-boxed off-canvas-menu-init">
    <div class="body-wrapper">
        <div class="body-innerwrapper">
            <section id="sp-top-bar">
                <div class="container">
                    <div class="row">
                        <div id="sp-top1" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <div class="sp-page-title">
                                    <div class="container"><a href="/"><img class="img_title_fam"
                                                src="/templates/shaper_helix3/images/fam_blanco.png" alt="" title=""
                                                width="180px" style="" /></a>
                                        <div class="title_h1_fam">
                                            <h1 style="text-align:center;">FEDERACIÓN DE ATLETISMO DE MADRID</h1>
                                        </div><a href="https://www.comunidad.madrid" target="_blank"><img
                                                class="img_title_cam" src="/templates/shaper_helix3/images/cam.png"
                                                alt="" title="" width="79px" style="" /></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <header id="sp-header">
                <div class="container">
                    <div class="row">
                        <div id="sp-menu" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <div class='sp-megamenu-wrapper'>
                                    <!--<div class='h2_menu_fam'><h2>FEDERACIÓN DE ATLETISMO DE MADRID</h2>-->
                                    <a id="offcanvas-toggler" class="visible-sm visible-xs"
                                        aria-label="Helix Megamenu Options" href="#"><i class="fa fa-bars"
                                            aria-hidden="true" title="Helix Megamenu Options"></i></a>
                                    <ul class="sp-megamenu-parent menu-fade hidden-sm hidden-xs">
                                        <li class="sp-menu-item sp-has-child"><a
                                                href="/index.php?option=com_content&amp;view=featured&amp;Itemid=101">Federación</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=category&amp;id=43&amp;Itemid=228">Órganos
                                                                de Gobierno y Representación</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/images/stories/ficheros/documentos/estatutos2019.pdf"
                                                                rel="noopener noreferrer" target="_blank">Estatutos</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=7921&amp;Itemid=212">Transparencia</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=2683&amp;Itemid=142">Contacto</a>
                                                        </li>
                                                        <li class="sp-menu-item sp-has-child"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=2730&amp;Itemid=141">Entrenadores
                                                                - EME</a>
                                                            <div class="sp-dropdown sp-dropdown-sub sp-menu-right"
                                                                style="width: 240px;">
                                                                <div class="sp-dropdown-inner">
                                                                    <ul class="sp-dropdown-items">
                                                                        <li class="sp-menu-item"><a
                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=2730&amp;Itemid=150">Presentación</a>
                                                                        </li>
                                                                        <li class="sp-menu-item"><a
                                                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=35&amp;Itemid=183">Bolsa
                                                                                de Trabajo</a></li>
                                                                        <li class="sp-menu-item"><a
                                                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=40&amp;Itemid=151">Formación</a>
                                                                        </li>
                                                                        <li class="sp-menu-item sp-has-child"><a
                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3177&amp;Itemid=153">Documentación</a>
                                                                            <div class="sp-dropdown sp-dropdown-sub sp-menu-right"
                                                                                style="width: 240px;">
                                                                                <div class="sp-dropdown-inner">
                                                                                    <ul class="sp-dropdown-items">
                                                                                        <li class="sp-menu-item"><a
                                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3408&amp;Itemid=155">Velocidad</a>
                                                                                        </li>
                                                                                        <li class="sp-menu-item"><a
                                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3409&amp;Itemid=156">Saltos</a>
                                                                                        </li>
                                                                                        <li class="sp-menu-item"><a
                                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3916&amp;Itemid=157">Marcha</a>
                                                                                        </li>
                                                                                    </ul>
                                                                                </div>
                                                                            </div>
                                                                        </li>
                                                                        <li class="sp-menu-item"><a
                                                                                href="/images/stories/ficheros/documentos/seguro/seguro_resp_civil_entrenadores.pdf"
                                                                                rel="noopener noreferrer"
                                                                                target="_blank">Seguro Resp. Civil</a>
                                                                        </li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </li>
                                                        <li class="sp-menu-item sp-has-child"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=252&amp;Itemid=147">Jueces</a>
                                                            <div class="sp-dropdown sp-dropdown-sub sp-menu-right"
                                                                style="width: 240px;">
                                                                <div class="sp-dropdown-inner">
                                                                    <ul class="sp-dropdown-items">
                                                                        <li class="sp-menu-item"><a
                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=6608&amp;Itemid=203">Jurados</a>
                                                                        </li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/images/stories/programas_comunidad_madrid.pdf">Programas
                                                                Comunidad de Madrid</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=category&amp;id=53&amp;Itemid=251">Subvenciones
                                                                y Ayudas</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=5906&amp;Itemid=265">Solicitud
                                                                de Certificados</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=4974&amp;Itemid=189">Calidad</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=4125&amp;Itemid=117">Instalaciones</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=1&amp;Itemid=118">Historia
                                                                FAM</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_weblinks&amp;view=categories&amp;id=0&amp;Itemid=234">Enlaces</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=5986&amp;Itemid=193">Elecciones</a>
                                                        </li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item sp-has-child"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=4130&amp;Itemid=120">Documentos</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=4130&amp;Itemid=122">Circulares</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=254&amp;Itemid=121">Licencias</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=7&amp;Itemid=123">Impresos</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=5&amp;Itemid=124">Estadística
                                                                de Licencias</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=6&amp;Itemid=125">Reglamentos</a>
                                                        </li>
                                                        <li class="sp-menu-item sp-has-child"><a
                                                                href="/index.php?option=com_content&amp;view=category&amp;id=52&amp;Itemid=248">Programas
                                                                deportivos</a>
                                                            <div class="sp-dropdown sp-dropdown-sub sp-menu-right"
                                                                style="width: 240px;">
                                                                <div class="sp-dropdown-inner">
                                                                    <ul class="sp-dropdown-items">
                                                                        <li class="sp-menu-item"><a
                                                                                href="/index.php?option=com_content&amp;view=article&amp;id=6217&amp;Itemid=199">Correr
                                                                                por Madrid</a></li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=9346&amp;Itemid=240"
                                                                rel="noopener noreferrer" target="_blank">Protocolo
                                                                Abusos Sexuales</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3400&amp;Itemid=126">Otros</a>
                                                        </li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item sp-has-child"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=8632&amp;Itemid=139">Tecnificación</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=12983&amp;Itemid=270">Tecnificación
                                                                2025</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=594&amp;Itemid=261">PROTAMA</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=8631&amp;Itemid=262">PROSEMA</a>
                                                        </li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item sp-has-child current-item active"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111">Calendario</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Pista%20Aire%20Libre">Calendario:
                                                                Aire Libre</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Pista%20Cubierta">Calendario:
                                                                Pista Cubierta</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Ruta">Calendario:
                                                                Ruta</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Marcha">Calendario:
                                                                Marcha</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Campo%20a%20traves">Calendario:
                                                                Campo a Través</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.atletismomadrid.com/index.php?option=com_content&view=article&id=3292&Itemid=111&tipo=Trail%20-%20Montaña">Calendario:
                                                                Trail - Montaña</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=4755&amp;Itemid=185">Carreras
                                                                Populares</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=10180&amp;Itemid=257">Circuito
                                                                Universitario Cross</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item sp-has-child"><a
                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=38&amp;Itemid=127">Noticias</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=39&amp;Itemid=128">Entrevistas</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.youtube.com/channel/UCq2TNbY1dpYLx4ov8y7hfMA/videos"
                                                                rel="noopener noreferrer" target="_blank">Videos</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=10679&amp;Itemid=168">Fotos</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://twitter.com/atletismomadrid"
                                                                rel="noopener noreferrer" target="_blank">Twitter</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.facebook.com/pages/Federacion-de-Atletismo-de-Madrid/511260275563407"
                                                                rel="noopener noreferrer" target="_blank">Facebook</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.instagram.com/federacion_atletismo_madrid/?hl=es"
                                                                rel="noopener noreferrer" target="_blank">Instragram</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://www.flickr.com/photos/atletismo_madrid/"
                                                                rel="noopener noreferrer" target="_blank">Flickr</a>
                                                        </li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item sp-has-child"><a
                                                href="https://atletismorfea.es/federaciones/ranking/mad">Estadistica</a>
                                            <div class="sp-dropdown sp-dropdown-main sp-menu-right"
                                                style="width: 240px;">
                                                <div class="sp-dropdown-inner">
                                                    <ul class="sp-dropdown-items">
                                                        <li class="sp-menu-item"><a
                                                                href="https://atletismorfea.es/federaciones/ranking/mad">Ranking
                                                                On-line</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=3265&amp;Itemid=133">Ranking
                                                                antiguos</a></li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=article&amp;id=9362&amp;Itemid=247">Records</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="/index.php?option=com_content&amp;view=category&amp;id=54&amp;Itemid=256">Historia</a>
                                                        </li>
                                                        <li class="sp-menu-item"><a
                                                                href="https://drive.google.com/drive/folders/1Wr99MmSj_7Ar1xW8TUGoH1VVqouy-zSJ?usp=drive_link"
                                                                rel="noopener noreferrer" target="_blank">Ranking FAM
                                                                (excel)</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </li>
                                        <li class="sp-menu-item"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=4131&amp;Itemid=144">Clubes</a>
                                        </li>
                                        <li class="sp-menu-item"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=12&amp;Itemid=140">Seguro</a>
                                        </li>
                                        <li class="sp-menu-item"><a
                                                href="/index.php?option=com_search&amp;view=search&amp;Itemid=170"><i
                                                    class="fa fa-search"></i></a></li>
                                    </ul> <!--</div>-->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>
            <section id="sp-enlaces-rfea">
                <div class="container">
                    <div class="row">
                        <div id="sp-top3" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <ul class="social-icons" style="float:left;">
                                    <li><a target="_blank"
                                            href="https://atletismorfea.es/user/login-registro"><i>Intranet RFEA (Call
                                                Room)</i></a></li>
                                </ul>
                                <ul class="social-icons" style="float:right;">
                                    <li><a target="_blank"
                                            href="https://whatsapp.com/channel/0029Vaz7Gp6GZNCzu8itU71E"><i>Canal
                                                WhatsApp FAM</i></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <section id="sp-main-body">
                <div class="container">
                    <div class="row">
                        <div id="sp-component" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <div id="system-message-container">
                                </div>
                                <form name='formulario1' method='post'
                                    action='index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111'>
                                    <label for="temporada" class="circulares_calendario_label">Temporada</label>
                                    <select name="temporada" class="circulares_calendario_label"
                                        onchange="enviar_formulario();">
                                        <option value='2027'>2027</option>
                                        <option value='2026' selected>2026</option>
                                        <option value='2025'>2025</option>
                                        <option value='2024'>2024</option>
                                        <option value='2023'>2023</option>
                                        <option value='2022'>2022</option>
                                        <option value='2021'>2021</option>
                                        <option value='2020'>2020</option>
                                        <option value='2019'>2018-2019</option>
                                        <option value='2018'>2017-2018</option>
                                        <option value='2017'>2016-2017</option>
                                        <option value='2016'>2015-2016</option>
                                        <option value='2015'>2014-2015</option>
                                        <option value='2014'>2013-2014</option>
                                        <option value='2013'>2012-2013</option>
                                        <option value='2012'>2011-2012</option>
                                        <option value='2011'>2010-2011</option>
                                        <option value='2010'>2009-2010</option>
                                        <option value='2009'>2008-2009</option>
                                        <option value='2008'>2007-2008</option>
                                        <option value='2007'>2006-2007</option>
                                    </select>
                                    <div class="calendario_retorno_carro"><br /></div>
                                    <label for="mes" class="circulares_calendario_label">Mes</label>
                                    <select name="mes" class="circulares_calendario_label"
                                        onchange="enviar_formulario();">
                                        <option value="1" selected="selected">Enero</option>
                                        <option value="2">Febrero</option>
                                        <option value="3">Marzo</option>
                                        <option value="4">Abril</option>
                                        <option value="5">Mayo</option>
                                        <option value="6">Junio</option>
                                        <option value="7">Julio</option>
                                        <option value="8">Agosto</option>
                                        <option value="9">Septiembre</option>
                                        <option value="10">Octubre</option>
                                        <option value="11">Noviembre</option>
                                        <option value="12">Diciembre</option>
                                    </select>
                                    <div class="calendario_retorno_carro"><br /></div>

                                    <label for="tipo" class="circulares_calendario_label">Tipo</label>
                                    <select name="tipo" size="1" class="circulares_calendario_label"
                                        onchange="enviar_formulario();">
                                        <option value="Todos" selected="selected">Todos</option>
                                        <option value="Pista Cubierta">Pista Cubierta</option>
                                        <option value="Pista Aire Libre">Pista Aire Libre</option>
                                        <option value="Campo a traves">Campo a traves</option>
                                        <option value="Ruta">Ruta</option>
                                        <option value="Marcha">Marcha</option>
                                        <option value="Trail - Montaña">Trail - Montaña</option>
                                        <option value="Jornada Tecnica">Jornada Tecnica</option>
                                        <option value="Jugando al Atletismo">Jugando al Atletismo</option>
                                        <option value="Otros">Otros</option>
                                    </select>

                                    <noscript>
                                        <input value="Filtrar" name="filtrar" type="submit"
                                            class="circulares_calendario_label">
                                    </noscript>

                                </form>

                                <script type="text/javascript">
                                    function enviar_formulario() {
                                        document.formulario1.submit()
                                    }
                                </script>

                                <br /><br />
                                <div id='calendario'>
                                    <table class='calendario'>
                                        <tr style='padding:2px;'>
                                            <th width='120px'>Fecha prueba</th>
                                            <th width='80px'>Límite inscripción</th>
                                            <th>Competición</th>
                                            <th width='200px'>Lugar</th>
                                            <th></th>
                                            <th></th>
                                            <th></th>
                                            <th width='60px'></th>
                                        </tr>
                                        <tr>
                                            <td align='right'>03.01 (S)</td>
                                            <td align='center'><b>28/12 (D)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13335&Itemid=250'>Reunión
                                                    FAM 13 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_gallur_2026_01_03.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.03_fam13.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.03_REUNION_FAM_13_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>03.01 (S)</td>
                                            <td align='center'><b>28/12 (D)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13572&Itemid=250'>Reunión
                                                    FAM 14 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_gallur_2026_01_03_2.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.03_fam14.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.03_REUNION_FAM_14_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>10.01 (S)</td>
                                            <td align='center'><b>06/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13601&Itemid=250'>Jornada
                                                    de Martillo Sub 16 y Sub 18</a></td>
                                            <td align='left'>Móstoles</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_martillo_mostoles_2026_01_10.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_martillo_mostoles_2026_01_10.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.10_JORNADA_MARTILLO_MOSTOLES.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>10.01 (S)</td>
                                            <td align='center'><b>06/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13317&Itemid=250'>Campeonato
                                                    de Madrid de Combinadas y 3.000m Máster - Control Pértiga Máster</a>
                                            </td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_combinadasmaster_gallur_2026_01_10.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.10_combinadas_marcha_master_gallur.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.10_CTO_MADRID_COMBINADAS_MARCHA_MASTER_PC_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>10.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13316&Itemid=250'>Campeonato
                                                    de Mundo de Campo a través</a></td>
                                            <td align='left'>Tallahasee (USA)</td>
                                            <td align='center'><a
                                                    href='https://worldathletics.org/competitions/world-athletics-cross-country-championships/tallahassee26'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>10.01 (S)</td>
                                            <td align='center'><b>28/12 (D)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13318&Itemid=250'>Campeonato
                                                    de Madrid de Clubes Absoluto PC</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><span class='reglamento_circular'><a
                                                        href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_copaabsoluta_gallur_2026_01_10.pdf?231357'
                                                        target='_blank' title='Reglamento'>regl.</a> / <a
                                                        href='images/stories/ficheros/circulares/2026/circular2026_01_estadillo_copa_abs_v3.pdf?231357'
                                                        target='_blank' title='Circular'>circ.</a></span></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.11_copa_abs.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.10_CTO_MADRID_CLUBES_ABSOLUTO_PC_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>11.01 (D)</td>
                                            <td align='center'><b>06/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13483&Itemid=250'>Jornada
                                                    de Menores 18 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_jornadamenores_gallur_2026_01_11.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.11_jornada_menores18_gallur.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.11_JORNADA_MENORES_18_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>11.01 (D)</td>
                                            <td align='center'><b>06/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13319&Itemid=250'>Campeonato
                                                    de Madrid de Campo a Través</a></td>
                                            <td align='left'>Valdemoro</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/Cto_absoluto_valdemoro_2026_01_11.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.11_valdemoro.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.11_CTO_MADRID_CROSS_VALDEMORO.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>11.01 (D)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13648&Itemid=250'>VI
                                                    Trofeo Amigos del Atletismo de Cross - Gran Premio Splendor</a></td>
                                            <td align='left'></td>
                                            <td></td>
                                            <td></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.11_CROSS_POPULAR_VALDEMORO.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>11.01 (D)</td>
                                            <td align='center'><b>06/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13579&Itemid=250'>Reunión
                                                    FAM 15 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_gallur_2026_01_11.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.11_fam15_gallur.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.11_REUNION_FAM_15_GALLUR.pdf'
                                                    target='_blank' title='Resultados'>resul.</a></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'><b>17/01 (S)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13546&Itemid=250'>Jornada
                                                    menores 19 Vicálvaro</a></td>
                                            <td align='left'>Vicálvaro</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_jornadamenores_vicálvaro_2026_01_17.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/Menores19_Competicion_InscripcionesComp_260115T154425.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13322&Itemid=250'>European
                                                    DNA Meeting -Clubes promoción mixto sub 18-sub 16</a></td>
                                            <td align='left'>Zaragoza</td>
                                            <td align='center'><a
                                                    href='https://atletismorfea.es/calendario/campeonato/european-dna-meeting-short-track-clubes-promocion-mixto-sub-18-sub-16-0'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13321&Itemid=250'>European
                                                    DNA Meeting-clubes sub 20 mixto</a></td>
                                            <td align='left'>Zaragoza</td>
                                            <td align='center'><a
                                                    href='https://atletismorfea.es/calendario/campeonato/european-dna-meeting-short-track-clubes-sub-20-mixto-0'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'><b>13/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13320&Itemid=250'>JDM
                                                    (1 Jornada Serie Básica)</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_JDM1basica_gallur2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.17_jdm_serie_basica.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17y18.01 (S-D)</td>
                                            <td align='center'><b>11/01 (D)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13323&Itemid=250'>Campeonato
                                                    de Madrid de Combinadas Absoluto, Sub 23 y Sub 20</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.17y18_combinadas_abs.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'><b>12/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13591&Itemid=250'>Jornada
                                                    de Lanzamiento de Jabalina</a></td>
                                            <td align='left'>Aluche</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_jabalina_aluche_2026_01_17.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.17_jabalina_aluche_v2.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'><b>15/01 (J)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13245&Itemid=250'>XXXVII
                                                    Cross del Rector UNED</a></td>
                                            <td align='left'>Ciudad Universitaria (Madrid)</td>
                                            <td align='center'><a
                                                    href='https://www.crossuniversitario.com/carreras/19-2025-2026/74-xxxvii-cross-del-rector-uned'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.17_cross_uned.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>17.01 (S)</td>
                                            <td align='center'><b>12/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13586&Itemid=250'>Reunión
                                                    FAM 16 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/FAM16_Competicion_InscripcionesComp_260115T154034.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>18.01 (D)</td>
                                            <td align='center'><b>12/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13325&Itemid=250'>Campeonato
                                                    de Madrid de Clubes de Marcha en Ruta</a></td>
                                            <td align='left'>Paracuellos de Jarama</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/ctomarchaclubes_ruta_paracuellos_2026_01_18.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.18_marcha.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Marcha'>M</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>18.01 (D)</td>
                                            <td align='center'><b>12/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13484&Itemid=250'>Jornada
                                                    de Menores 20 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_jornadamenores_gallur_2026_01_18.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.18_menores20_gallur.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>18.01 (D)</td>
                                            <td align='center'><b>12/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13587&Itemid=250'>Reunión
                                                    FAM 17 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center' style='background-color:#FFFF00;'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/FAM17_Competicion_InscripcionesComp_260115T154108.pdf?231357'
                                                    target='_blank' title='Inscritos'>insc.</a></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>22.01 (J)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13543&Itemid=250'>Campeonato
                                                    de Madrid Escolar de Campo a través</a></td>
                                            <td align='left'>Las Rozas</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/Campo a traves 2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13582&Itemid=250'>Jornada
                                                    menores 21 Alcorcón</a></td>
                                            <td align='left'>Alcorcón</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/jornadamenores_alcorcon_2026_01_24.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13589&Itemid=250'>Reunión
                                                    FAM 18 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/sub23_gallur_2026_01_24.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13327&Itemid=250'>Campeonato
                                                    de España de Selecciones Autonómicas sub 16, sub 18 e inclusivo
                                                    campo a través</a></td>
                                            <td align='left'>Almodovar del Rio</td>
                                            <td align='center'><a
                                                    href='https://atletismorfea.es/calendario/campeonato/campeonato-de-espana-de-selecciones-autonomicas-sub-16-sub-18-e-inclusivo-de-cam'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24y25.01 (S-D)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13328&Itemid=250'>Campeonato
                                                    de Madrid sub 23</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/sub23_gallur_2026_01_24.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'><b>20/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13326&Itemid=250'>JDM
                                                    1 Federados</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/JDM1federados_gallur2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13598&Itemid=250'>Campeonato
                                                    de Madrid de lanzamientos largos (disco Absoluto y sub 20)</a></td>
                                            <td align='left'>Aluche</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/ctodisco_aluche_2026_01_24.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>24.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13246&Itemid=250'>Cross
                                                    URJC 2025/2026</a></td>
                                            <td align='left'>Campus de Fuenlabrada</td>
                                            <td align='center'><a
                                                    href='https://www.crossuniversitario.com/carreras/19-2025-2026/75-cross-urjc-2025-2026'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13590&Itemid=250'>Reunión
                                                    FAM 19 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/sub23_gallur_2026_01_24.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'><b>22/01 (J)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13624&Itemid=250'>XL
                                                    Cross de Leganés 2026</a></td>
                                            <td align='left'>Parque Polvoranca (Leganés)</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/reglamento_cross_leganes_2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'><b>20/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13324&Itemid=250'>Campeonato
                                                    de Madrid Máster de Campo a Través</a></td>
                                            <td align='left'>Leganés</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/Cto_master_leganes_2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13329&Itemid=250'>Campeonato
                                                    de España de campo a través individual y Federaciones</a></td>
                                            <td align='left'>Almodovar del Rio</td>
                                            <td align='center'><a
                                                    href='https://atletismorfea.es/calendario/campeonato/campeonato-de-espana-campo-traves-individual-y-federaciones-5'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13632&Itemid=250'>Campeonato
                                                    de Madrid de lanzamientos largos (Disco sub 18)</a></td>
                                            <td align='left'>Aluche</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/ctodisco_aluche_2026_01_25.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr style='background:#EBFFAA;font-style:italic;'>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13330&Itemid=250'>Media
                                                    Maratón Ciudad de Getafe</a></td>
                                            <td align='left'>Getafe</td>
                                            <td align='center'><a href='https://mediadegetafe.com/es' target='_blank'
                                                    title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Ruta'>R</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>25.01 (D)</td>
                                            <td align='center'><b>19/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13485&Itemid=250'>Jornada
                                                    menores 22 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/jornadamenores_gallur_2026_01_25.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'><b>26/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13343&Itemid=250'>Campeonato
                                                    de Madrid de Marcha en ruta</a></td>
                                            <td align='left'>Móstoles</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/ctomarcha_ruta_mostoles_2026_01_31.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Marcha'>M</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'><b>26/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13332&Itemid=250'>Campeonato
                                                    de Madrid de lanzamientos largos máster martillo</a></td>
                                            <td align='left'>Vallehermoso</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/martillo_máster_vallehermoso2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'><b>27/01 (M)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13333&Itemid=250'>JDM
                                                    II Jornada básica</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/JDM2basica_gallur2026.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13247&Itemid=250'>XXII
                                                    Cross del Rector UCJC</a></td>
                                            <td align='left'>Campus UCJC (Villafranca del Castillo)</td>
                                            <td align='center'><a href='https://www.crossuniversitario.com/'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td></td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'><b>26/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13650&Itemid=250'>Campeonato
                                                    de Madrid lanzamientos largos jabalina sub 16</a></td>
                                            <td align='left'>Aluche</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/ctojabalina_aluche_2026_01_31.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Aire Libre'>AL</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13339&Itemid=250'>Cross
                                                    Villa de Parla Escolar (3ª Jornada)</a></td>
                                            <td align='left'>Parque de las Comunidades (Parla)</td>
                                            <td></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Campo a traves'>C</td>
                                        </tr>
                                        <tr>
                                            <td align='right'>31.01 (S)</td>
                                            <td align='center'><b>26/01 (L)</b></td>
                                            <td align='left'><a
                                                    href='index.php?option=com_content&view=article&id=13486&Itemid=250'>Reunión
                                                    FAM 20 Gallur</a></td>
                                            <td align='left'>Gallur</td>
                                            <td align='center'><a
                                                    href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/gallur_2026_01_31.pdf?231357'
                                                    target='_blank' title='Reglamento'>regl.</a></td>
                                            <td></td>
                                            <td></td>
                                            <td align='center' title='Pista Cubierta'>PC</td>
                                        </tr>
                                    </table>
                                </div><br /><a
                                    href='modules/mod_calendario/excel/calendario_excel.php?temporada=2026&Itemid=111'><span
                                        class='boton_descarga' style='float:left;margin-bottom:10px;'>Calendario de la
                                        Temporada en Excel</span></a><a href='https://atletismorfea.es/calendario'
                                    target='_blank'><span class='boton_descarga'
                                        style='float:right;margin-right:15px;'>Calendario RFEA</span></a>
                                <article class="item item-page" itemscope itemtype="http://schema.org/Article">
                                    <meta itemprop="inLanguage" content="es-ES" />
                                    <div class="entry-header has-post-format">


                                    </div>






                                    <div itemprop="articleBody">
                                    </div>






                                    <div class="article-footer-wrap">
                                        <div class="article-footer-top">













                                        </div>
                                    </div>

                                </article>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <section id="sp-patrocinadores">
                <div class="container">
                    <div class="row">
                        <div id="sp-user1" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <div class="sp-module ">
                                    <div class="sp-module-content">

                                        <div class="custom">
                                            <center>
                                                <img src="/templates/shaper_helix3/images/colaboradores2023.jpg"
                                                    width="912" height="78" alt="" title="" />
                                            </center>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <footer id="sp-footer">
                <div class="container">
                    <div class="row">
                        <div id="sp-footer1" class="col-sm-12 col-md-12">
                            <div class="sp-column ">
                                <ul class="sp-contact-info">
                                    <li><a target="_blank" href="https://twitter.com/AtletismoMadrid"
                                            aria-label="twitter" style="color:#999999"><i class="fa fa-twitter"></i></a>
                                    </li>
                                    <li><a target="_blank"
                                            href="https://www.instagram.com/federacion_atletismo_madrid/?hl=es"
                                            aria-label="twitter" style="color:#999999"><i
                                                class="fa fa-instagram"></i></a></li>
                                    <li class="sp-contact-phone"><i class="fa fa-phone" aria-hidden="true"></i> <a
                                            href="/index.php?option=com_content&amp;view=article&amp;id=2683&amp;Itemid=142">Contacto</a>
                                    </li>
                                    <li class="sp-contact-email"><i class="fa fa-envelope" aria-hidden="true"></i> <a
                                            href="mailto:fam@atletismomadrid.com">fam@atletismomadrid.com</a></li>
                                </ul><span class="sp-copyright">© 1916 - 2026 Federación de Atletismo de Madrid. Avda
                                    Salas de los Infantes, 1 - 28034 Madrid
                                    <br />
                                    <a href="/images/stories/ficheros/documentos/avisosLegales/AvisoLegal.pdf"
                                        target="_blank">Aviso legal</a>
                                    --
                                    <a href="/images/stories/ficheros/documentos/avisosLegales/PoliticaPrivacidad.pdf"
                                        target="_blank">Política de Privacidad</a>
                                    --
                                    <a href="/images/stories/ficheros/documentos/avisosLegales/CondicionesUso.pdf"
                                        target="_blank">Condiciones de uso</a>
                                    --
                                    <a href="/images/stories/ficheros/documentos/avisosLegales/PolíticaCookies.pdf"
                                        target="_blank">Política de Cookies</a></span>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        </div> <!-- /.body-innerwrapper -->
    </div> <!-- /.body-innerwrapper -->

    <!-- Off Canvas Menu -->
    <div class="offcanvas-menu">
        <a href="#" class="close-offcanvas" aria-label="Close"><i class="fa fa-remove" aria-hidden="true"
                title="HELIX_CLOSE_MENU"></i></a>
        <div class="offcanvas-inner">
            <div class="sp-module _menu">
                <h3 class="sp-module-title">Menu</h3>
                <div class="sp-module-content">
                    <ul class="nav menu">
                        <li class="item-101  deeper parent"><a
                                href="/index.php?option=com_content&amp;view=featured&amp;Itemid=101">
                                Federación</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-101"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-101">
                                <li class="item-228"><a
                                        href="/index.php?option=com_content&amp;view=category&amp;id=43&amp;Itemid=228">
                                        Órganos de Gobierno y Representación</a></li>
                                <li class="item-210"> <a href="/images/stories/ficheros/documentos/estatutos2019.pdf"
                                        rel="noopener noreferrer" target="_blank"> Estatutos</a></li>
                                <li class="item-212"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=7921&amp;Itemid=212">
                                        Transparencia</a></li>
                                <li class="item-142"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=2683&amp;Itemid=142">
                                        Contacto</a></li>
                                <li class="item-141  deeper parent"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=2730&amp;Itemid=141">
                                        Entrenadores - EME</a><span class="offcanvas-menu-toggler collapsed"
                                        data-toggle="collapse" data-target="#collapse-menu-141"><i
                                            class="open-icon fa fa-angle-down"></i><i
                                            class="close-icon fa fa-angle-up"></i></span>
                                    <ul class="collapse" id="collapse-menu-141">
                                        <li class="item-150"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=2730&amp;Itemid=150">
                                                Presentación</a></li>
                                        <li class="item-183"><a
                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=35&amp;Itemid=183">
                                                Bolsa de Trabajo</a></li>
                                        <li class="item-151"><a
                                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=40&amp;Itemid=151">
                                                Formación</a></li>
                                        <li class="item-153  deeper parent"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=3177&amp;Itemid=153">
                                                Documentación</a><span class="offcanvas-menu-toggler collapsed"
                                                data-toggle="collapse" data-target="#collapse-menu-153"><i
                                                    class="open-icon fa fa-angle-down"></i><i
                                                    class="close-icon fa fa-angle-up"></i></span>
                                            <ul class="collapse" id="collapse-menu-153">
                                                <li class="item-155"><a
                                                        href="/index.php?option=com_content&amp;view=article&amp;id=3408&amp;Itemid=155">
                                                        Velocidad</a></li>
                                                <li class="item-156"><a
                                                        href="/index.php?option=com_content&amp;view=article&amp;id=3409&amp;Itemid=156">
                                                        Saltos</a></li>
                                                <li class="item-157"><a
                                                        href="/index.php?option=com_content&amp;view=article&amp;id=3916&amp;Itemid=157">
                                                        Marcha</a></li>
                                            </ul>
                                        </li>
                                        <li class="item-188"> <a
                                                href="/images/stories/ficheros/documentos/seguro/seguro_resp_civil_entrenadores.pdf"
                                                rel="noopener noreferrer" target="_blank"> Seguro Resp. Civil</a></li>
                                    </ul>
                                </li>
                                <li class="item-147  deeper parent"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=252&amp;Itemid=147">
                                        Jueces</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                        data-target="#collapse-menu-147"><i class="open-icon fa fa-angle-down"></i><i
                                            class="close-icon fa fa-angle-up"></i></span>
                                    <ul class="collapse" id="collapse-menu-147">
                                        <li class="item-203"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=6608&amp;Itemid=203">
                                                Jurados</a></li>
                                    </ul>
                                </li>
                                <li class="item-268"> <a href="/images/stories/programas_comunidad_madrid.pdf">
                                        Programas Comunidad de Madrid</a></li>
                                <li class="item-251"><a
                                        href="/index.php?option=com_content&amp;view=category&amp;id=53&amp;Itemid=251">
                                        Subvenciones y Ayudas</a></li>
                                <li class="item-265"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=5906&amp;Itemid=265">
                                        Solicitud de Certificados</a></li>
                                <li class="item-189"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=4974&amp;Itemid=189">
                                        Calidad</a></li>
                                <li class="item-117"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=4125&amp;Itemid=117">
                                        Instalaciones</a></li>
                                <li class="item-118"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=1&amp;Itemid=118">
                                        Historia FAM</a></li>
                                <li class="item-234"><a
                                        href="/index.php?option=com_weblinks&amp;view=categories&amp;id=0&amp;Itemid=234">
                                        Enlaces</a></li>
                                <li class="item-193"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=5986&amp;Itemid=193">
                                        Elecciones</a></li>
                            </ul>
                        </li>
                        <li class="item-120  deeper parent"><a
                                href="/index.php?option=com_content&amp;view=article&amp;id=4130&amp;Itemid=120">
                                Documentos</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-120"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-120">
                                <li class="item-122"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=4130&amp;Itemid=122">
                                        Circulares</a></li>
                                <li class="item-121"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=254&amp;Itemid=121">
                                        Licencias</a></li>
                                <li class="item-123"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=7&amp;Itemid=123">
                                        Impresos</a></li>
                                <li class="item-124"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=5&amp;Itemid=124">
                                        Estadística de Licencias</a></li>
                                <li class="item-125"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=6&amp;Itemid=125">
                                        Reglamentos</a></li>
                                <li class="item-248  deeper parent"><a
                                        href="/index.php?option=com_content&amp;view=category&amp;id=52&amp;Itemid=248">
                                        Programas deportivos</a><span class="offcanvas-menu-toggler collapsed"
                                        data-toggle="collapse" data-target="#collapse-menu-248"><i
                                            class="open-icon fa fa-angle-down"></i><i
                                            class="close-icon fa fa-angle-up"></i></span>
                                    <ul class="collapse" id="collapse-menu-248">
                                        <li class="item-199"><a
                                                href="/index.php?option=com_content&amp;view=article&amp;id=6217&amp;Itemid=199">
                                                Correr por Madrid</a></li>
                                    </ul>
                                </li>
                                <li class="item-240"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=9346&amp;Itemid=240"
                                        target="_blank"> Protocolo Abusos Sexuales</a></li>
                                <li class="item-126"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=3400&amp;Itemid=126">
                                        Otros</a></li>
                            </ul>
                        </li>
                        <li class="item-139  deeper parent"><a
                                href="/index.php?option=com_content&amp;view=article&amp;id=8632&amp;Itemid=139">
                                Tecnificación</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-139"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-139">
                                <li class="item-270"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=12983&amp;Itemid=270">
                                        Tecnificación 2025</a></li>
                                <li class="item-261"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=594&amp;Itemid=261">
                                        PROTAMA</a></li>
                                <li class="item-262"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=8631&amp;Itemid=262">
                                        PROSEMA</a></li>
                            </ul>
                        </li>
                        <li class="item-111  current active deeper parent"><a
                                href="/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111">
                                Calendario</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-111"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-111">
                                <li class="item-241"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Pista%20Aire%20Libre">
                                        Calendario: Aire Libre</a></li>
                                <li class="item-242"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Pista%20Cubierta">
                                        Calendario: Pista Cubierta</a></li>
                                <li class="item-243"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Ruta">
                                        Calendario: Ruta</a></li>
                                <li class="item-244"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Marcha">
                                        Calendario: Marcha</a></li>
                                <li class="item-245"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Campo%20a%20traves">
                                        Calendario: Campo a Través</a></li>
                                <li class="item-246"> <a
                                        href="https://www.atletismomadrid.com/index.php?option=com_content&amp;view=article&amp;id=3292&amp;Itemid=111&amp;tipo=Trail%20-%20Montaña">
                                        Calendario: Trail - Montaña</a></li>
                                <li class="item-185"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=4755&amp;Itemid=185">
                                        Carreras Populares</a></li>
                                <li class="item-257"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=10180&amp;Itemid=257">
                                        Circuito Universitario Cross</a></li>
                            </ul>
                        </li>
                        <li class="item-127  deeper parent"><a
                                href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=38&amp;Itemid=127">
                                Noticias</a><span class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-127"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-127">
                                <li class="item-128"><a
                                        href="/index.php?option=com_content&amp;view=category&amp;layout=blog&amp;id=39&amp;Itemid=128">
                                        Entrevistas</a></li>
                                <li class="item-167"> <a
                                        href="https://www.youtube.com/channel/UCq2TNbY1dpYLx4ov8y7hfMA/videos"
                                        rel="noopener noreferrer" target="_blank"> Videos</a></li>
                                <li class="item-168"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=10679&amp;Itemid=168">
                                        Fotos</a></li>
                                <li class="item-171"> <a href="https://twitter.com/atletismomadrid"
                                        rel="noopener noreferrer" target="_blank"> Twitter</a></li>
                                <li class="item-172"> <a
                                        href="https://www.facebook.com/pages/Federacion-de-Atletismo-de-Madrid/511260275563407"
                                        rel="noopener noreferrer" target="_blank"> Facebook</a></li>
                                <li class="item-267"> <a
                                        href="https://www.instagram.com/federacion_atletismo_madrid/?hl=es"
                                        rel="noopener noreferrer" target="_blank"> Instragram</a></li>
                                <li class="item-269"> <a href="https://www.flickr.com/photos/atletismo_madrid/"
                                        rel="noopener noreferrer" target="_blank"> Flickr</a></li>
                            </ul>
                        </li>
                        <li class="item-131  deeper parent"> <a
                                href="https://atletismorfea.es/federaciones/ranking/mad"> Estadistica</a><span
                                class="offcanvas-menu-toggler collapsed" data-toggle="collapse"
                                data-target="#collapse-menu-131"><i class="open-icon fa fa-angle-down"></i><i
                                    class="close-icon fa fa-angle-up"></i></span>
                            <ul class="collapse" id="collapse-menu-131">
                                <li class="item-132"> <a href="https://atletismorfea.es/federaciones/ranking/mad">
                                        Ranking On-line</a></li>
                                <li class="item-133"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=3265&amp;Itemid=133">
                                        Ranking antiguos</a></li>
                                <li class="item-247"><a
                                        href="/index.php?option=com_content&amp;view=article&amp;id=9362&amp;Itemid=247">
                                        Records</a></li>
                                <li class="item-256"><a
                                        href="/index.php?option=com_content&amp;view=category&amp;id=54&amp;Itemid=256">
                                        Historia</a></li>
                                <li class="item-271"> <a
                                        href="https://drive.google.com/drive/folders/1Wr99MmSj_7Ar1xW8TUGoH1VVqouy-zSJ?usp=drive_link"
                                        rel="noopener noreferrer" target="_blank"> Ranking FAM (excel)</a></li>
                            </ul>
                        </li>
                        <li class="item-144"><a
                                href="/index.php?option=com_content&amp;view=article&amp;id=4131&amp;Itemid=144">
                                Clubes</a></li>
                        <li class="item-140"><a
                                href="/index.php?option=com_content&amp;view=article&amp;id=12&amp;Itemid=140">
                                Seguro</a></li>
                        <li class="item-170"><a href="/index.php?option=com_search&amp;view=search&amp;Itemid=170"> <i
                                    class="fa fa-search"></i> Buscar</a></li>
                    </ul>
                </div>
            </div>
        </div> <!-- /.offcanvas-inner -->
    </div> <!-- /.offcanvas-menu -->




    <!-- Preloader -->

    <!-- Go to top -->
    <a href="javascript:void(0)" class="scrollup" aria-label="Go To Top">&nbsp;</a>
</body>

</html>
    """


@pytest.fixture
def sample_events_table() -> list[list[str]]:
    """Tabla de pruebas de ejemplo."""
    return [
        ["Prueba", "Sexo", "Hora", "Categoría"],
        ["60m", "M", "10:00", "Senior"],
        ["60m", "F", "10:15", "Senior"],
        ["200m", "M", "10:30", "Senior"],
        ["Altura", "F", "11:00", "Sub23"],
        ["Pértiga", "M", "11:30", "Absoluto"],
        ["Peso", "F", "12:00", "Senior"],
    ]


@pytest.fixture
def sample_pdf_text() -> str:
    """Texto de ejemplo extraído de un PDF."""
    return """
    FEDERACIÓN DE ATLETISMO DE MADRID

    CONTROL DE PISTA CUBIERTA

    Fecha: 11 de enero de 2026
    Lugar: Polideportivo Gallur

    PROGRAMA DE PRUEBAS

    CARRERAS

    10:00 - 60m masculino
    10:15 - 60m femenino
    10:30 - 200m masculino
    10:45 - 200m femenino
    11:00 - 400m masculino
    11:15 - 400m femenino

    CONCURSOS

    10:00 - Altura femenino
    10:30 - Pértiga masculino
    11:00 - Longitud masculino
    11:30 - Peso femenino
    """
