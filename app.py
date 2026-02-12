import streamlit as st
import os
import asyncio
import time
from datetime import datetime, timedelta
from crawler import get_all_links
from screenshot import take_screenshot
from compare import compare_images
import requests
from urllib.parse import urlparse

st.sidebar.title("Navegación")
option = st.sidebar.radio("Selecciona la herramienta:", ["WP Mirror QA", "WP Mirror Links QA"])

# Pantalla WP Mirror QA
if option == "WP Mirror QA":
    st.set_page_config(page_title="WP Mirror QA", layout="wide")

    # Logos y título centrado
    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        st.image("assets/logo_left.png", width=120)
    with col2:
        st.markdown("<h1 style='text-align: center;'>WP Mirror QA</h1>", unsafe_allow_html=True)
    with col3:
        st.image("assets/logo_right.png", width=120)

    # Hora actual dinámica
    placeholder_time = st.empty()
    def update_time():
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            placeholder_time.markdown(
                f"<div style='text-align:right; color:black;'>Hora actual: {current_time}</div>",
                unsafe_allow_html=True
            )
            time.sleep(1)

    import threading
    threading.Thread(target=update_time, daemon=True).start()

    # Inputs
    prod_url = st.text_input("URL Producción", placeholder="https://ejemplo.com/")
    staging_url = st.text_input("URL Staging", placeholder="https://staging.ejemplo.com/")

    def colorize_percent(percent):
        if percent <= 1.0:
            return f"<span style='color:green;font-weight:bold'>{percent:.2f}%</span>"
        elif percent <= 5.0:
            return f"<span style='color:orange;font-weight:bold'>{percent:.2f}%</span>"
        else:
            return f"<span style='color:red;font-weight:bold'>{percent:.2f}%</span>"

    if st.button("Generar Reporte"):
        if not prod_url or not staging_url:
            st.error("Por favor ingresa ambas URLs.")
        else:
            with st.spinner("Generando reporte..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    links = loop.run_until_complete(get_all_links(prod_url))
                except Exception as e:
                    st.error(f"Error al obtener enlaces: {e}")
                    links = []

                if not links:
                    st.warning("No se encontraron enlaces en el sitio de producción.")
                else:
                    st.success(f"Se encontraron {len(links)} páginas para comparar.")

                report = []
                os.makedirs("report", exist_ok=True)

                avg_time_per_page = 11
                expected_seconds = len(links) * avg_time_per_page
                expected_finish = datetime.now() + timedelta(seconds=expected_seconds)
                expected_minutes = expected_seconds // 60

                progress_bar = st.progress(0)
                progress_text = st.empty()
                st.markdown(f"**Tiempo esperado:** ~{expected_minutes} minutos")
                st.markdown(f"**Hora esperada de finalización:** {expected_finish.strftime('%H:%M:%S')}")

                for i, link in enumerate(links):
                    st.write(f"Procesando página {i+1}/{len(links)}: {link}")

                    prod_file = f"report/prod_{i}.png"
                    staging_file = f"report/staging_{i}.png"
                    diff_file = f"report/diff_{i}.png"

                    try:
                        loop.run_until_complete(take_screenshot(link, prod_file))
                        staging_link = link.replace(prod_url.rstrip("/"), staging_url.rstrip("/"))
                        loop.run_until_complete(take_screenshot(staging_link, staging_file))

                        percent, status = compare_images(prod_file, staging_file, diff_file)
                        report.append((link, percent, status, prod_file, staging_file, diff_file))

                    except Exception as e:
                        st.error(f"Error en {link}: {e}")
                        report.append((link, 0, "ERROR", None, None, None))

                    progress = (i+1)/len(links)
                    progress_bar.progress(progress)
                    progress_text.markdown(f"**Avance:** {progress*100:.1f}%")

            # Generar reporte HTML adicional
            html_report = """
            <html>
            <head>
            <style>
            body { font-family: Arial; background-color: #000000; color: #ffffff; }
            table { border-collapse: collapse; width: 100%; color: #ffffff; }
            th, td { border: 1px solid #444; padding: 8px; }
            th { background-color: #222222; }
            .details { display: none; }
            .btn { cursor: pointer; color: #00aaff; text-decoration: underline; }
            </style>
            <script>
            function toggleDetails(id) {
                var x = document.getElementById(id);
                if (x.style.display === "none") {
                    x.style.display = "block";
                } else {
                    x.style.display = "none";
                }
            }
            </script>
            </head>
            <body>
            <h1>WP Mirror QA</h1>
            <table>
            <tr><th>Página</th><th>Diferencia</th><th>Estado</th><th>Acción</th></tr>
            """

            for i, (link, percent, status, prod, staging, diff) in enumerate(report):
                color_html = colorize_percent(percent)
                html_report += f"""
                <tr>
                    <td>{link}</td>
                    <td>{color_html}</td>
                    <td>{status}</td>
                    <td><span class="btn" onclick="toggleDetails('details{i}')">Ver detalles</span></td>
                </tr>
                <tr id="details{i}" class="details">
                    <td colspan="4">
                        <img src="prod_{i}.png" width="300"> 
                        <img src="staging_{i}.png" width="300"> 
                        <img src="diff_{i}.png" width="300">
                    </td>
                </tr>
                """

            html_report += "</table><br><p>Elaborado por: Minor Cascante, QA Lead</p></body></html>"

            with open("report/report.html", "w", encoding="utf-8") as f:
                f.write(html_report)

            if st.button("Abrir Reporte HTML"):
                st.markdown('<a href="report/report.html" target="_blank">Abrir Reporte HTML</a>', unsafe_allow_html=True)

# Pantalla WP Mirror Links QA
elif option == "WP Mirror Links QA":
    # Logos y título centrado
    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        st.image("assets/logo_left.png", width=120)
    with col2:
        st.markdown("<h1 style='text-align: center;'>WP Mirror link QA</h1>", unsafe_allow_html=True)
    with col3:
        st.image("assets/logo_right.png", width=120)

    prod_url = st.text_input("URL Producción", placeholder="https://ejemplo.com/", key="prod_url_links")
    staging_url = st.text_input("URL Staging", placeholder="https://staging.ejemplo.com/", key="staging_url_links")

    def normalize_url(url):
        try:
            parsed = urlparse(url)
            normalized = parsed.path
            if parsed.query:
                normalized += "?" + parsed.query
            return normalized
        except Exception:
            return url

    def get_redirect_chain(url):
        try:
            resp = requests.get(url, allow_redirects=True, timeout=10)
            chain = [normalize_url(r.url) for r in resp.history] + [normalize_url(resp.url)]
            return chain
        except Exception as e:
            return [f"ERROR: {e}"]

    if st.button("Generar Reporte de Redirecciones", key="generate_redirect_report"):
        if not prod_url or not staging_url:
            st.error("Por favor ingresa ambas URLs.")
        else:
            with st.spinner("Analizando redirecciones..."):
                links = asyncio.run(get_all_links(prod_url))
                total = len(links)
                progress_bar = st.progress(0)
                status_text = st.empty()
                report = []

                for i, link in enumerate(links, start=1):
                    staging_link = link.replace(prod_url.rstrip("/"), staging_url.rstrip("/"))
                    prod_chain = get_redirect_chain(link)
                    staging_chain = get_redirect_chain(staging_link)

                    status = "IDENTICAL" if prod_chain == staging_chain else "DIFFERENT"
                    report.append((link, prod_chain, staging_chain, status))

                    progress = int(i / total * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Procesando {i}/{total} URLs ({progress}%)")

                st.subheader("Reporte de Redirecciones")
                for link, prod_chain, staging_chain, status in report:
                    color = "green" if status == "IDENTICAL" else "red"
                    st.markdown(f"**URL:** {link} - **Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                    with st.expander("Ver cadena de redirecciones"):
                        st.markdown(f"**Producción:** {' -> '.join(prod_chain)}")
                        st.markdown(f"**Staging:** {' -> '.join(staging_chain)}")