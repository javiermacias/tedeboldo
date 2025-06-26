import os
import re
from bs4 import BeautifulSoup

CARPETA_FANZINES = 'fanzines'

def estandarizar_citas_desde_sup():
    if not os.path.isdir(CARPETA_FANZINES):
        print(f"Error: No se encontró la carpeta '{CARPETA_FANZINES}'.")
        return

    print(f"Iniciando la estandarización en '{CARPETA_FANZINES}'...")
    archivos_modificados = 0

    for nombre_archivo in os.listdir(CARPETA_FANZINES):
        if not nombre_archivo.endswith('.html'):
            continue

        ruta = os.path.join(CARPETA_FANZINES, nombre_archivo)
        print(f"Procesando: {nombre_archivo}")

        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()

        soup = BeautifulSoup(contenido, 'lxml')
        modificado = False

        # 1. Detectar <sup><a href="#notaX">X</a></sup>
        referencias = {}
        for sup in soup.find_all('sup'):
            a = sup.find('a', href=re.compile(r'#nota\d+'))
            if a and a.string and a.string.isdigit():
                num = a.string
                a['href'] = f'#nota{num}'

                # Colocar el id="refX" directamente en el <sup>
                sup['id'] = f'ref{num}'

                referencias[num] = True
                modificado = True

        # 2. Buscar posibles notas al pie (párrafos que empiezan con <sup>X</sup>)
        notas_candidatas = {}
        for p in soup.find_all('p'):
            if p.find('sup') and p.find('sup').string and p.find('sup').string.isdigit():
                num = p.find('sup').string
                if num in referencias:
                    texto = p.get_text().strip()
                    texto = re.sub(rf'^{num}\s*', '', texto)
                    notas_candidatas[num] = texto
                    p.decompose()
                    modificado = True

        # 3. Crear bloque de notas estándar al final del body
        if notas_candidatas:
            seccion_notas = soup.new_tag('div', id='seccion-notas')

            # Agregar título de sección de notas
            titulo_notas = soup.new_tag('h2')
            titulo_notas.string = 'Notas'
            seccion_notas.append(titulo_notas)

            for num in sorted(notas_candidatas, key=lambda x: int(x)):
                div_nota = soup.new_tag('div', id=f'nota{num}', **{'class': 'nota-al-pie'})
                p_nota = soup.new_tag('p')
                sup_nota = soup.new_tag('sup')
                sup_nota.string = num
                p_nota.append(sup_nota)
                p_nota.append(f" {notas_candidatas[num]} ")
                retorno = soup.new_tag('a', href=f'#ref{num}')
                retorno.string = '↩'
                p_nota.append(retorno)
                div_nota.append(p_nota)
                seccion_notas.append(div_nota)

            soup.body.append(seccion_notas)
            modificado = True

        # 4. Guardar si hubo cambios
        if modificado:
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            archivos_modificados += 1

    print(f"\n¡Proceso terminado! Archivos modificados: {archivos_modificados}")

if __name__ == "__main__":
    estandarizar_citas_desde_sup()
