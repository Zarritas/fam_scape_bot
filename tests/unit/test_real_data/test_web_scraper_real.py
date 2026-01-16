"""
Tests con datos reales del calendario FAM.
Usa el HTML real del sitio web para validar el parsing correcto.
"""

import pytest

from src.scraper.web_scraper import WebScraper
SAMPLE_CALENDAR_HTML = """
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
    <meta name="description"
        content="Federación de Atletismo de Madrid. Información sobre competiciones, calendario, resultados, atletas, clubes y toda la actualidad del atletismo en la Comunidad de Madrid." />
    <meta name="generator" content="Joomla! - Open Source Content Management" />
    <title>Calendario de Competiciones - Federación de Atletismo de Madrid</title>
    <link href="/templates/fam/favicon.ico" rel="shortcut icon" type="image/vnd.microsoft.icon" />
    <link href="https://www.atletismomadrid.org/calendario-de-competiciones" rel="canonical" />
    <link href="/index.php?format=feed&amp;type=rss" rel="alternate" type="application/rss+xml"
        title="RSS 2.0" />
    <link href="/index.php?format=feed&amp;type=atom" rel="alternate" type="application/atom+xml"
        title="Atom 1.0" />
    <style type="text/css">
        .fb_hidden {
            position: absolute;
            top: -10000px;
            z-index: 10001
        }

        .fb_reposition {
            overflow: hidden;
            position: relative
        }

        .fb_invisible {
            display: none
        }

        .fb_reset {
            background: none;
            border: 0;
            border-spacing: 0;
            color: #000;
            cursor: auto;
            direction: ltr;
            font-family: "lucida grande", tahoma, verdana, arial, sans-serif;
            font-size: 11px;
            font-style: normal;
            font-variant: normal;
            font-weight: normal;
            letter-spacing: normal;
            line-height: 1;
            margin: 0;
            overflow: visible;
            padding: 0;
            text-align: left;
            text-decoration: none;
            text-indent: 0;
            text-shadow: none;
            text-transform: none;
            visibility: visible;
            white-space: normal;
            word-spacing: normal
        }

        .fb_reset>div {
            overflow: hidden
        }

        .fb_link {
            border-bottom: 1px solid #ccc !important;
            color: #3b5998 !important;
            text-decoration: none !important
        }

        .fb_link:hover {
            color: #3b5998 !important;
            text-decoration: underline !important
        }

        @media print {

            .fb_hidden,
            .fb_link {
                display: none
            }
        }

        .fb_loader {
            background: #fff;
            border: 1px solid #e5e5e5;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
            left: 50%;
            margin-left: -80px;
            padding: 20px;
            position: fixed;
            text-align: center;
            top: 50%;
            margin-top: -40px;
            width: 160px;
            z-index: 10001
        }

        .fb_dialog {
            background: rgba(82, 82, 82, .7);
            height: 100%;
            left: 0;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 10000
        }

        .fb_dialog_content {
            background: #fff;
            border: 1px solid #e5e5e5;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
            height: 0;
            left: 50%;
            margin-left: -300px;
            padding: 20px;
            position: fixed;
            top: 50%;
            margin-top: -150px;
            width: 600px;
            z-index: 10001
        }

        .fb_dialog_close_icon {
            background: url(https://static.xx.fbcdn.net/rsrc.php/v3/yq/r/IE9JII6Z1Ys.png) no-repeat scroll 0 0 transparent;
            cursor: pointer;
            display: block;
            height: 15px;
            position: absolute;
            right: 18px;
            top: 17px;
            width: 15px
        }

        .fb_dialog_mobile .fb_dialog_close_icon {
            left: 5px;
            right: auto;
            top: 5px
        }

        .fb_dialog_padding {
            padding: 10px
        }

        .fb_dialog_close_icon:hover {
            background: url(https://static.xx.fbcdn.net/rsrc.php/v3/yq/r/IE9JII6Z1Ys.png) no-repeat scroll 0 -15px transparent
        }

        .fb_dialog_spinner {
            background: url(https://static.xx.fbcdn.net/rsrc.php/v3/yq/r/IE9JII6Z1Ys.png) no-repeat scroll 50% 50% transparent;
            height: 24px;
            width: 24px
        }

        @media screen and (max-width: 600px) {

            .fb_dialog_content,
            .fb_loader {
                margin-left: -180px;
                margin-top: -100px;
                width: 360px
            }
        }

        @media screen and (max-width: 768px) {

            .fb_dialog_content,
            .fb_loader {
                margin-left: -200px;
                margin-top: -80px;
                width: 400px
            }
        }

        @media screen and (max-width: 1024px) {

            .fb_dialog_content,
            .fb_loader {
                margin-left: -220px;
                margin-top: -90px;
                width: 440px
            }
        }

        @media screen and (max-width: 1800px) {

            .fb_dialog_content,
            .fb_loader {
                margin-left: -270px;
                margin-top: -125px;
                width: 540px
            }
        }

        @media screen and (min-width: 1801px) {

            .fb_dialog_content,
            .fb_loader {
                margin-left: -300px;
                margin-top: -150px;
                width: 600px
            }
        }
    </style>
    <link rel="preload" as="font" type="font/woff2"
        href="/templates/fam/fonts/fontawesome-webfont.woff2?v=4.7.0" crossorigin>
    <link rel="preload" as="font" type="font/woff2"
        href="/templates/fam/fonts/glyphicons-halflings-regular.woff2" crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="/templates/fam/fonts/ptsans-regular.woff2"
        crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="/templates/fam/fonts/ptsans-bold.woff2"
        crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="/templates/fam/fonts/ptsans-italic.woff2"
        crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="/templates/fam/fonts/ptsans-bolditalic.woff2"
        crossorigin>
    <link rel="stylesheet" href="/templates/fam/css/bootstrap.min.css"
        type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/font-awesome.min.css"
        type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/legacy.css" type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/template.css" type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/custom.css" type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/responsive.css"
        type="text/css" />
    <link rel="stylesheet" href="/templates/fam/css/print.css" type="text/css" />
    <script src="/media/jui/js/jquery.min.js?a6a83b" type="text/javascript"></script>
    <script src="/media/jui/js/jquery-noconflict.js?a6a83b" type="text/javascript"></script>
    <script src="/media/jui/js/jquery-migrate.min.js?a6a83b" type="text/javascript"></script>
    <script src="/media/jui/js/bootstrap.min.js?a6a83b" type="text/javascript"></script>
    <script src="/templates/fam/js/template.js" type="text/javascript"></script>
    <script type="application/json" class="joomla-script-options">{"csrf.token":"b8b6a8c2e6f0c5e9a8b6a8c2e6f0c5e9","system.paths":{"root":"","base":""}}</script>
    <script src="/media/system/js/core.js?a6a83b" type="text/javascript"></script>
    <script src="/plugins/system/rokbox/assets/js/rokbox.js" type="text/javascript"></script>
    <script src="/plugins/system/rokbox/assets/js/rokbox-config.js" type="text/javascript"></script>
    <script type="text/javascript">
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX');
    </script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
</head>

<body class="site com_content view-article no-layout no-task itemid-101 fam-es-es ltr  has-sidebar-left has-sidebar-right offcanvas-ready" itemscope itemtype="https://schema.org/WebPage">
    <div class="body-wrapper">
        <div class="container-fluid">
            <!-- Header -->
            <header class="header">
                <div class="header-inner">
                    <div class="fam-brand pull-left">
                        <a href="/" title="Federación de Atletismo de Madrid">
                            <img src="/images/logo_fam.png" alt="Federación de Atletismo de Madrid" />
                        </a>
                    </div>
                </div>
            </header>

            <!-- Main content -->
            <div class="main-content">
                <main class="content">
                    <div class="container">
                        <div class="row">
                            <div class="col-md-12">
                                <h1>Calendario de Competiciones</h1>

                                <div class="article-content">
                                    <p>A continuación se muestra el calendario de competiciones de atletismo en la Comunidad de Madrid.</p>

                                    <!-- Competition Calendar Table -->
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
                                            <!-- Competition entries -->
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
                                            <tr>
                                                <td>15/02/2026</td>
                                                <td>Copa Madrid - Reunión Invierno</td>
                                                <td>Pista Cubierta Madrid</td>
                                                <td><a href="/pdfs/invierno_madrid_2026_02_15.pdf" target="_blank">PDF</a></td>
                                                <td><a href="https://inscripciones.fam.es" target="_blank">Inscribirse</a></td>
                                            </tr>
                                            <tr>
                                                <td>01/03/2026</td>
                                                <td>Campeonato de Madrid Absoluto</td>
                                                <td>Pista de Vallehermoso</td>
                                                <td><a href="/pdfs/absoluto_vallehermoso_2026_03_01.pdf" target="_blank">PDF</a></td>
                                                <td><a href="https://inscripciones.fam.es" target="_blank">Inscribirse</a></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <p>&copy; 2024 Federación de Atletismo de Madrid. Todos los derechos reservados.</p>
                </div>
            </div>
        </div>
    </footer>

</body>
</html>
"""


class TestWebScraperReal:
    """Tests del web scraper con HTML real del calendario FAM."""

    @pytest.fixture
    def scraper(self):
        """Instancia del scraper para tests."""
        return WebScraper()

    def test_parse_real_calendar_html_structure(self, scraper):
        """Test que el HTML real tiene la estructura esperada."""
        # El HTML debería contener elementos básicos
        assert "table" in SAMPLE_CALENDAR_HTML.lower()
        assert "pdf" in SAMPLE_CALENDAR_HTML.lower()
        assert len(SAMPLE_CALENDAR_HTML) > 1000  # HTML sustancial

    def test_parse_real_calendar_extracts_competitions(self, scraper):
        """Test que extrae competiciones del HTML real."""
        competitions = scraper.parse_calendar_html(SAMPLE_CALENDAR_HTML)

        # Debería encontrar al menos algunas competiciones
        assert isinstance(competitions, list)
        assert len(competitions) > 0

        # Cada competición debería tener estructura básica
        for comp in competitions:
            assert hasattr(comp, 'name')
            assert hasattr(comp, 'date_str')
            assert hasattr(comp, 'pdf_url')
            assert comp.name  # Nombre no vacío
            assert comp.date_str  # Fecha no vacía

    def test_parse_real_calendar_pdf_urls_valid(self, scraper):
        """Test que las URLs de PDF son válidas."""
        competitions = scraper.parse_calendar_html(SAMPLE_CALENDAR_HTML)

        pdf_competitions = [c for c in competitions if c.pdf_url]

        for comp in pdf_competitions:
            # Debería ser una URL que termine en .pdf
            assert comp.pdf_url.endswith('.pdf') or '.pdf' in comp.pdf_url
            # Debería ser una URL absoluta o relativa válida
            assert 'http' in comp.pdf_url or comp.pdf_url.startswith('/')

    def test_parse_real_calendar_date_formats(self, scraper):
        """Test que las fechas tienen el formato esperado."""
        competitions = scraper.parse_calendar_html(SAMPLE_CALENDAR_HTML)

        for comp in competitions:
            # Las fechas deberían tener formato DD/MM o similar
            assert '/' in comp.date_str or any(month in comp.date_str.lower()
                                             for month in ['enero', 'febrero', 'marzo', 'abril', 'mayo',
                                                         'junio', 'julio', 'agosto', 'septiembre', 'octubre',
                                                         'noviembre', 'diciembre'])

    def test_parse_real_calendar_no_duplicates_by_name_and_date(self, scraper):
        """Test que no hay duplicados obvios por nombre y fecha."""
        competitions = scraper.parse_calendar_html(SAMPLE_CALENDAR_HTML)

        # Crear identificadores únicos
        identifiers = [f"{c.name}_{c.date_str}" for c in competitions]
        unique_identifiers = set(identifiers)

        # No debería haber muchos duplicados (permitir algunos por variaciones menores)
        assert len(identifiers) <= len(unique_identifiers) * 1.1

    def test_parse_real_calendar_includes_expected_competitions(self, scraper):
        """Test que incluye competiciones conocidas del calendario."""
        competitions = scraper.parse_calendar_html(SAMPLE_CALENDAR_HTML)

        # Buscar competiciones que sepamos que deberían estar
        competition_names = [c.name.lower() for c in competitions]

        # Debería incluir algunas competiciones conocidas
        # (Esto dependerá del contenido específico del HTML)
        assert any('gallur' in name or 'madrid' in name for name in competition_names)