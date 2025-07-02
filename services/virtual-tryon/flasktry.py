from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
import json
from flask_cors import CORS
import numpy as np
import cv2                              # Biblioteca para processamento de imagens
from math import floor
import os
import uuid
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
import random  # Para simular dados de blockchain e recompensas
import requests  # Para baixar imagens fornecidas via URL

# Importar SkinToneClassifier
try:
    from skin_tone_classifier import SkinToneClassifier
    print("SkinToneClassifier local importado com sucesso")
    SKIN_TONE_AVAILABLE = True
except ImportError as e:
    print(f"Erro de importação: {str(e)}")
    SKIN_TONE_AVAILABLE = False
    print("SkinToneClassifier não disponível. Instale com: pip install skin-tone-classifier")

app = Flask(__name__)
# Habilitar CORS para todas as rotas e origens
CORS(app, resources={r"/*": {"origins": "*"}})

# Caminho para o diretório de build do app React
REACT_APP_BUILD_DIR = os.path.join('static', 'react-app')

# Caminho para uploads de usuários
USER_UPLOADS_DIR = os.path.join('static', 'user-uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Caminho para dados do catálogo
CATALOG_FILE = os.path.join('static', 'catalog.json')

# Criar diretório de uploads de usuários se não existir
os.makedirs(os.path.join(app.root_path, USER_UPLOADS_DIR), exist_ok=True)

# Dados simulados de blockchain e recompensas
BLOCKCHAIN_DATA = {
    'transactions': 0,
    'active_nodes': 120,
    'block_height': 1000000
}

REWARDS_DATA = {
    'tokens': 340,
    'level': 2,
    'progress': 65,
    'achievements': [
        {
            'title': 'Explorador da Moda',
            'description': 'Experimente 10 itens diferentes',
            'progress': 7,
            'total': 10,
            'reward': 50
        },
        {
            'title': 'Borboleta Social',
            'description': 'Compartilhe 5 resultados de prova',
            'progress': 3,
            'total': 5,
            'reward': 30
        }
    ]
}

# Imagens de demonstração de prova para diferentes combinações
DEMO_IMAGES = {
    '1_1': '/static/assets/bg1.jpg',  # Camiseta azul + calça branca
    '2_1': '/static/assets/bg.jpg',   # Camisa azul + calça branca
    '3_2': '/static/assets/background.jpg',  # Camiseta preta + calça azul
    '4_2': '/static/assets/bg.jpeg',  # Camiseta cinza + calça azul
    'default': '/static/assets/leftimage-removebg-preview.png'  # Imagem padrão
}

# Itens padrão do catálogo
default_catalog = {
    'shirts': [
        {'id': '1', 'name': 'Camiseta Azul',
            'image': '/static/assets/shirt1.png', 'type': 'default'},
        {'id': '2', 'name': 'Camisa Azul',
            'image': '/static/assets/shirt2.png', 'type': 'default'},
        {'id': '3', 'name': 'Camiseta Preta',
            'image': '/static/assets/shirt51.jpg', 'type': 'default'},
        {'id': '4', 'name': 'Camiseta Cinza',
            'image': '/static/assets/shirt6.png', 'type': 'default'}
    ],
    'pants': [
        {'id': '1', 'name': 'Calça Branca',
            'image': '/static/assets/pant7.jpg', 'type': 'default'},
        {'id': '2', 'name': 'Calça Azul',
            'image': '/static/assets/pant21.png', 'type': 'default'}
    ]
}

# Carregar catálogo do arquivo ou usar padrão


def load_catalog():
    try:
        if os.path.exists(os.path.join(app.root_path, CATALOG_FILE)):
            with open(os.path.join(app.root_path, CATALOG_FILE), 'r') as f:
                return json.load(f)
        return default_catalog
    except Exception as e:
        print(f"Erro ao carregar catálogo: {str(e)}")
        return default_catalog

# Salvar catálogo no arquivo


def save_catalog(catalog_data):
    try:
        with open(os.path.join(app.root_path, CATALOG_FILE), 'w') as f:
            json.dump(catalog_data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar catálogo: {str(e)}")


# Inicializar catálogo
catalog = load_catalog()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def remove_background(input_path, output_path):
    """
    Remove o fundo de uma imagem e salva com fundo transparente
    Usando técnicas melhoradas para melhores resultados com uploads personalizados
    """
    try:
        # Ler a imagem
        img = cv2.imread(input_path)
        if img is None:
            print(f"Erro: Não foi possível ler a imagem em {input_path}")
            return False

        # Converter para RGB para processamento
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Criar uma máscara com múltiplos métodos e combiná-los
        # Método 1: Limiarização simples em tons de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh1 = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

        # Método 2: Segmentação baseada em cor
        # Converter para espaço de cor HSV
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Definir faixa para cores de fundo (assumindo fundo branco/claro)
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 30, 255])

        # Criar máscara para fundo branco/claro
        thresh2 = cv2.inRange(img_hsv, lower_white, upper_white)
        thresh2 = cv2.bitwise_not(thresh2)

        # Método 3: Limiarização adaptativa para melhor manuseio de itens escuros
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Combinar máscaras
        combined_mask = cv2.bitwise_or(thresh1, thresh2)
        combined_mask = cv2.bitwise_or(combined_mask, adaptive_thresh)

        # Aplicar operações morfológicas para melhorar a máscara
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(
            combined_mask, cv2.MORPH_CLOSE, kernel)

        # Encontrar o maior contorno (assumido como sendo o item de roupa)
        contours, _ = cv2.findContours(
            combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Se contornos foram encontrados, usar o maior
        if contours:
            # Criar uma nova máscara com apenas o maior contorno
            refined_mask = np.zeros_like(combined_mask)
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(refined_mask, [largest_contour], 0, 255, -1)

            # Preencher buracos no contorno
            # Primeiro inverter a máscara para tornar os buracos brancos
            mask_inv = cv2.bitwise_not(refined_mask)
            # Encontrar todos os contornos na máscara invertida
            hole_contours, _ = cv2.findContours(
                mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # Preencher todos exceto o maior contorno (que é o limite externo)
            for contour in hole_contours:
                if cv2.contourArea(contour) < cv2.contourArea(largest_contour):
                    cv2.drawContours(refined_mask, [contour], 0, 255, -1)

            # Dilatar para garantir que não cortemos a roupa muito apertado
            refined_mask = cv2.dilate(refined_mask, kernel, iterations=2)
        else:
            refined_mask = combined_mask

        # Limpeza final
        refined_mask = cv2.GaussianBlur(refined_mask, (5, 5), 0)
        _, refined_mask = cv2.threshold(
            refined_mask, 127, 255, cv2.THRESH_BINARY)

        # Criar canal alfa da máscara
        alpha = refined_mask

        # Converter imagem para BGRA (adicionar canal alfa)
        bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

        # Definir canal alfa na imagem BGRA
        bgra[:, :, 3] = alpha

        # Salvar a imagem com transparência
        cv2.imwrite(output_path, bgra)

        # Verificação de confirmação
        result = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)
        # Verificar se o canal alfa existe
        if result is None or result.shape[2] < 4:
            print(
                f"Aviso: Falha ao criar imagem transparente. Salvando com método de fallback.")
            # Método de fallback: apenas salvar o original com remoção básica de fundo
            _, simple_mask = cv2.threshold(
                gray, 250, 255, cv2.THRESH_BINARY_INV)
            bgra[:, :, 3] = simple_mask
            cv2.imwrite(output_path, bgra)

        return True
    except Exception as e:
        print(f"Erro ao remover fundo: {str(e)}")
        return False

# Servir App React


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, 'react-app', path)):
        return send_from_directory(os.path.join(app.static_folder, 'react-app'), path)
    else:
        return send_from_directory(os.path.join(app.static_folder, 'react-app'), 'index.html')

# Adicionar rota explícita para servir assets estáticos


@app.route('/static/assets/<path:filename>')
def serve_static_assets(filename):
    response = send_from_directory(os.path.join(
        app.static_folder, 'assets'), filename)
    # Definir cabeçalho Cache-Control para prevenir problemas de cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Novo endpoint da API para sistema de recompensas


@app.route('/api/rewards/status', methods=['GET'])
def rewards_status():
    return jsonify({
        'success': True,
        'data': REWARDS_DATA
    })

# Novo endpoint da API para atualizar recompensas


@app.route('/api/rewards/update', methods=['POST'])
def update_rewards():
    try:
        data = request.get_json()
        action = data.get('action')

        if action == 'try_on':
            REWARDS_DATA['tokens'] += 5
            # Atualizar progresso da conquista
            for achievement in REWARDS_DATA['achievements']:
                if achievement['title'] == 'Explorador da Moda':
                    if achievement['progress'] < achievement['total']:
                        achievement['progress'] += 1
        elif action == 'share':
            REWARDS_DATA['tokens'] += 10
            # Atualizar progresso da conquista
            for achievement in REWARDS_DATA['achievements']:
                if achievement['title'] == 'Borboleta Social':
                    if achievement['progress'] < achievement['total']:
                        achievement['progress'] += 1

        # Atualizar progresso do nível
        REWARDS_DATA['progress'] = min(
            100, REWARDS_DATA['progress'] + random.randint(1, 5))
        if REWARDS_DATA['progress'] >= 100:
            REWARDS_DATA['level'] += 1
            REWARDS_DATA['progress'] = 0

        return jsonify({
            'success': True,
            'data': REWARDS_DATA
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# API de prova melhorada com integração de recompensas


@app.route('/api/tryon', methods=['POST'])
def tryon_api():
    try:
        data = request.get_json()
        shirt_id = data.get('shirt', '0')
        pant_id = data.get('pant', '0')

        # Sempre usar modo câmera, ignorando a flag use_camera
        # Redirecionar para a experiência de prova baseada em câmera
        return jsonify({
            'success': True,
            'redirect': True,
            'url': f'/api/predict?shirt={shirt_id}&pant={pant_id}'
        })

        # O código abaixo nunca será executado já que estamos sempre redirecionando
        # Para fins de demonstração, retornar uma imagem estática baseada na seleção
        image_key = f"{shirt_id}_{pant_id}"
        image_url = DEMO_IMAGES.get(image_key, DEMO_IMAGES['default'])

        # Atualizar recompensas para ação de prova
        update_rewards({'action': 'try_on'})

        # Simular tempo de processamento
        import time
        time.sleep(1)

        result = {
            'success': True,
            'message': f'Prova realizada com sucesso com camisa {shirt_id} e calça {pant_id}',
            'image_url': image_url,
            'rewards': {
                'tokens_earned': 5,
                'current_tokens': REWARDS_DATA['tokens']
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Endpoint da API para catálogo


@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    global catalog
    catalog = load_catalog()  # Recarregar catálogo a cada requisição para garantir frescor
    return jsonify(catalog)

# Endpoint da API para upload de novos itens de roupa


@app.route('/api/catalog/upload', methods=['POST'])
def upload_item():
    global catalog

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})

    file = request.files['file']
    item_type = request.form.get('type', 'shirt')
    name = request.form.get('name', f'{item_type.capitalize()} Personalizada')

    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})

    if file and allowed_file(file.filename):
        try:
            # Gerar nome de arquivo único
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1]
            new_filename = f"{item_type}_{unique_id}{file_ext}"

            # Criar diretórios se não existirem
            os.makedirs(os.path.join(app.root_path,
                        USER_UPLOADS_DIR), exist_ok=True)

            # Salvar arquivo original
            original_path = os.path.join(
                app.root_path, USER_UPLOADS_DIR, f"original_{new_filename}")
            file.save(original_path)

            # Processar imagem para remover fundo
            processed_filename = f"processed_{new_filename}"
            processed_path = os.path.join(
                app.root_path, USER_UPLOADS_DIR, processed_filename)

            print(f"Processando imagem: {original_path} -> {processed_path}")
            success = remove_background(original_path, processed_path)

            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Falha ao processar imagem. Por favor, certifique-se de que a imagem tenha bom contraste com o fundo.'
                })

            # Adicionar ao catálogo
            current_catalog = load_catalog()

            if item_type == 'shirt':
                collection = 'shirts'
                new_id = str(len(current_catalog[collection]) + 1)
            elif item_type == 'pant':
                collection = 'pants'
                new_id = str(len(current_catalog[collection]) + 1)
            else:
                collection = f"{item_type}s"
                new_id = unique_id

            item = {
                'id': new_id,
                'name': name,
                'image': f'/{USER_UPLOADS_DIR}/{processed_filename}',
                'type': 'user'
            }

            current_catalog[collection].append(item)
            save_catalog(current_catalog)
            catalog = current_catalog

            return jsonify({
                'success': True,
                'message': f'{item_type.capitalize()} enviada e processada com sucesso',
                'item': item
            })
        except Exception as e:
            print(f"Erro no processo de upload: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Ocorreu um erro ao processar seu upload: {str(e)}'
            })

    return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido. Por favor, envie uma imagem JPG, JPEG ou PNG.'})


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Suportar tanto dados de formulário (do HTML legado) quanto parâmetros de consulta (do novo app React)
    if request.method == 'POST':
        shirtno = request.form["shirt"]
        pantno = request.form["pant"]
    else:  # Requisição GET
        shirtno = request.args.get("shirt", "1")
        pantno = request.args.get("pant", "1")

    # Carregar o catálogo para acessar todas as imagens de camisas e calças
    current_catalog = load_catalog()

    # Encontrar a camisa e calça selecionadas do catálogo
    selected_shirt = None
    for shirt in current_catalog['shirts']:
        if shirt['id'] == shirtno:
            selected_shirt = shirt
            break

    selected_pant = None
    for pant in current_catalog['pants']:
        if pant['id'] == pantno:
            selected_pant = pant
            break

    # Se camisa ou calça não forem encontradas, usar padrões
    if not selected_shirt:
        selected_shirt = current_catalog['shirts'][0]
    if not selected_pant:
        selected_pant = current_catalog['pants'][0]

    # Obter caminhos e preparar para processamento
    shirt_path = os.path.join(
        app.root_path, selected_shirt['image'].lstrip('/'))
    pant_path = os.path.join(app.root_path, selected_pant['image'].lstrip('/'))

    cv2.waitKey(1)
    cap = cv2.VideoCapture(0)

    while True:
        # Ler a camisa selecionada
        imgshirt = cv2.imread(shirt_path, 1)  # imagem original em bgr
        if imgshirt is None:
            print(f"Erro: Não foi possível ler a imagem da camisa em {shirt_path}")
            # Usar uma camisa padrão como fallback
            imgshirt = cv2.imread(os.path.join(
                app.root_path, 'static/assets/shirt1.png'), 1)

        # Processar máscara da camisa
        shirtgray = cv2.cvtColor(imgshirt, cv2.COLOR_BGR2GRAY)

        # Verificar se é uma camisa personalizada enviada
        if 'user-uploads' in shirt_path:
            # Camisas personalizadas enviadas já devem ter transparência do nosso processamento
            # Verificar se a imagem tem um canal alfa
            if imgshirt.shape[2] == 4:  # formato BGRA
                # Usar canal alfa diretamente
                _, orig_masks = cv2.threshold(
                    imgshirt[:, :, 3], 127, 255, cv2.THRESH_BINARY)
                orig_masks_inv = cv2.bitwise_not(orig_masks)
            else:
                # Voltar ao processamento regular
                ret, orig_masks = cv2.threshold(
                    shirtgray, 240, 255, cv2.THRESH_BINARY_INV)
                orig_masks_inv = cv2.bitwise_not(orig_masks)
        elif 'shirt51.jpg' in shirt_path:  # Caso especial para shirt3
            ret, orig_masks_inv = cv2.threshold(
                shirtgray, 200, 255, cv2.THRESH_BINARY)
            orig_masks = cv2.bitwise_not(orig_masks_inv)
        else:
            ret, orig_masks = cv2.threshold(
                shirtgray, 0, 255, cv2.THRESH_BINARY)
            orig_masks_inv = cv2.bitwise_not(orig_masks)

        origshirtHeight, origshirtWidth = imgshirt.shape[:2]

        # Ler a calça selecionada
        imgpant = cv2.imread(pant_path, 1)
        if imgpant is None:
            print(f"Erro: Não foi possível ler a imagem da calça em {pant_path}")
            # Usar uma calça padrão como fallback
            imgpant = cv2.imread(os.path.join(
                app.root_path, 'static/assets/pant7.jpg'), 1)

        imgpant = imgpant[:, :, 0:3]
        pantgray = cv2.cvtColor(imgpant, cv2.COLOR_BGR2GRAY)

        # Processar máscara da calça - ajustar limiar baseado no tipo de calça
        if 'pant7.jpg' in pant_path:  # Calças brancas
            ret, orig_mask = cv2.threshold(
                pantgray, 100, 255, cv2.THRESH_BINARY)
        else:  # Padrão para outras calças
            ret, orig_mask = cv2.threshold(
                pantgray, 50, 255, cv2.THRESH_BINARY)

        # Criar máscara inversa
        orig_mask_inv = cv2.bitwise_not(orig_mask)
        origpantHeight, origpantWidth = imgpant.shape[:2]

        face_cascade = cv2.CascadeClassifier(
            'haarcascade_frontalface_default.xml')

        ret, img = cap.read()

        height = img.shape[0]
        width = img.shape[1]
        resizewidth = int(width*3/2)
        resizeheight = int(height*3/2)

        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("img", (int(width*3/2), int(height*3/2)))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Processamento das calças
            pantWidth = 3 * w
            pantHeight = pantWidth * origpantHeight / origpantWidth

            # Posicionamento padrão para calças
            x1 = x - w
            x2 = x1 + 3*w
            y1 = y + 5*h
            y2 = y + h*10

            # Ajustar posição para calças específicas se necessário
            if 'pant21.png' in pant_path:  # Calças azuis
                x1 = x - w/2
                x2 = x1 + 2*w
                y1 = y + 4*h
                y2 = y + h*9

            # Verificações de limites
            if x1 < 0:
                x1 = 0
            if x2 > img.shape[1]:
                x2 = img.shape[1]
            if y2 > img.shape[0]:
                y2 = img.shape[0]
            if y1 > img.shape[0]:
                y1 = img.shape[0]
            if y1 == y2:
                y1 = 0

            temp = 0
            if y1 > y2:
                temp = y1
                y1 = y2
                y2 = temp

            pantWidth = int(abs(x2 - x1))
            pantHeight = int(abs(y2 - y1))
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)

            pant = cv2.resize(imgpant, (pantWidth, pantHeight),
                              interpolation=cv2.INTER_AREA)
            mask = cv2.resize(orig_mask, (pantWidth, pantHeight),
                              interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(
                orig_mask_inv, (pantWidth, pantHeight), interpolation=cv2.INTER_AREA)

            roi = img[y1:y2, x1:x2]

            # Garantir que mask_inv tenha o tamanho e tipo corretos
            if mask_inv.shape[:2] != roi.shape[:2]:
                mask_inv = cv2.resize(
                    mask_inv, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_AREA)
            if len(mask_inv.shape) > 2:
                mask_inv = cv2.cvtColor(mask_inv, cv2.COLOR_BGR2GRAY)

            roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

            # Garantir que mask tenha o tamanho e tipo corretos
            if mask.shape[:2] != pant.shape[:2]:
                mask = cv2.resize(
                    mask, (pant.shape[1], pant.shape[0]), interpolation=cv2.INTER_AREA)
            if len(mask.shape) > 2:
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

            roi_fg = cv2.bitwise_and(pant, pant, mask=mask)

            # Inicializar roi_fgs e roi_bgs
            roi_fgs = roi_fg
            roi_bgs = roi_bg

            # Garantir que roi_fgs e roi_bgs tenham a mesma forma e canais
            if roi_fgs.shape != roi_bgs.shape:
                roi_fgs = cv2.resize(
                    roi_fgs, (roi_bgs.shape[1], roi_bgs.shape[0]), interpolation=cv2.INTER_AREA)

            # Certificar-se de que tenham o mesmo número de canais
            if len(roi_fgs.shape) != len(roi_bgs.shape):
                if len(roi_fgs.shape) > len(roi_bgs.shape):
                    roi_bgs = cv2.cvtColor(roi_bgs, cv2.COLOR_GRAY2BGR)
                else:
                    roi_fgs = cv2.cvtColor(roi_fgs, cv2.COLOR_GRAY2BGR)

            dsts = cv2.add(roi_bgs, roi_fgs)

            # Aplicar efeito de desfoque ao resto da imagem
            top = img[0:y, 0:resizewidth]
            bottom = img[y+h:resizeheight, 0:resizewidth]
            midleft = img[y:y+h, 0:x]
            midright = img[y:y+h, x+w:resizewidth]
            blurvalue = 5
            top = cv2.GaussianBlur(top, (blurvalue, blurvalue), 0)
            bottom = cv2.GaussianBlur(bottom, (blurvalue, blurvalue), 0)
            midright = cv2.GaussianBlur(midright, (blurvalue, blurvalue), 0)
            midleft = cv2.GaussianBlur(midleft, (blurvalue, blurvalue), 0)
            img[0:y, 0:resizewidth] = top
            img[y+h:resizeheight, 0:resizewidth] = bottom
            img[y:y+h, 0:x] = midleft
            img[y:y+h, x+w:resizewidth] = midright
            img[y1:y2, x1:x2] = dsts

            # Processamento da camisa
            shirtWidth = 3 * w
            shirtHeight = shirtWidth * origshirtHeight / origshirtWidth

            x1s = x - w
            x2s = x1s + 3*w
            y1s = y + h
            y2s = y1s + h*4

            # Verificações de limites
            if x1s < 0:
                x1s = 0
            if x2s > img.shape[1]:
                x2s = img.shape[1]
            if y2s > img.shape[0]:
                y2s = img.shape[0]

            temp = 0
            if y1s > y2s:
                temp = y1s
                y1s = y2s
                y2s = temp

            shirtWidth = int(abs(x2s - x1s))
            shirtHeight = int(abs(y2s - y1s))
            y1s = int(y1s)
            y2s = int(y2s)
            x1s = int(x1s)
            x2s = int(x2s)

            shirt = cv2.resize(
                imgshirt, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(
                orig_masks, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)
            masks_inv = cv2.resize(
                orig_masks_inv, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)

            rois = img[y1s:y2s, x1s:x2s]

            # Garantir que masks_inv tenha o tamanho e tipo corretos
            if masks_inv.shape[:2] != rois.shape[:2]:
                masks_inv = cv2.resize(
                    masks_inv, (rois.shape[1], rois.shape[0]), interpolation=cv2.INTER_AREA)
            if len(masks_inv.shape) > 2:
                masks_inv = cv2.cvtColor(masks_inv, cv2.COLOR_BGR2GRAY)

            roi_bgs = cv2.bitwise_and(rois, rois, mask=masks_inv)

            # Garantir que mask tenha o tamanho e tipo corretos
            if mask.shape[:2] != shirt.shape[:2]:
                mask = cv2.resize(
                    mask, (shirt.shape[1], shirt.shape[0]), interpolation=cv2.INTER_AREA)
            if len(mask.shape) > 2:
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

            roi_fgs = cv2.bitwise_and(shirt, shirt, mask=mask)

            # Garantir que roi_fgs e roi_bgs tenham a mesma forma e canais
            if roi_fgs.shape != roi_bgs.shape:
                roi_fgs = cv2.resize(
                    roi_fgs, (roi_bgs.shape[1], roi_bgs.shape[0]), interpolation=cv2.INTER_AREA)

            # Certificar-se de que tenham o mesmo número de canais
            if len(roi_fgs.shape) != len(roi_bgs.shape):
                if len(roi_fgs.shape) > len(roi_bgs.shape):
                    roi_bgs = cv2.cvtColor(roi_bgs, cv2.COLOR_GRAY2BGR)
                else:
                    roi_fgs = cv2.cvtColor(roi_fgs, cv2.COLOR_GRAY2BGR)

            dsts = cv2.add(roi_bgs, roi_fgs)
            img[y1s:y2s, x1s:x2s] = dsts

            break

        cv2.imshow("img", img)
        if cv2.waitKey(100) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Redirecionar de volta para o app React
    return redirect('/')

# Adicionar endpoint da API para compatibilidade com frontend React


@app.route('/api/predict', methods=['GET', 'POST'])
def api_predict():
    return predict()

# Endpoint da API para análise de tom de pele


@app.route('/api/skin-tone-analysis', methods=['POST'])
def skin_tone_analysis():
    """
    Analisar tom de pele usando a biblioteca SkinToneClassifier.

    Opções de entrada (mutuamente exclusivas):
    1. Corpo JSON 👉 {"url_image": "http://.../image.jpg"}
       • A API fará o download da imagem antes de processar.
    2. multipart/form-data com o campo file "image" (comportamento legado).
    """
    if not SKIN_TONE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Biblioteca SkinToneClassifier não está instalada no servidor'
        }), 500

    # --------------------------------------------------
    # 1) Manipular corpo JSON com uma URL de imagem externa
    # --------------------------------------------------
    tone_category: str = "Médio"  # Valor padrão definido cedo para evitar problemas de referência
    filepath: str | None = None
    if request.is_json:
        json_payload: dict[str, str] = request.get_json(silent=True) or {}
        url_image: str | None = json_payload.get(
            'url_image') if isinstance(json_payload, dict) else None

        if url_image:
            try:
                # Faz o download da imagem
                response = requests.get(url_image, stream=True, timeout=10)
                if response.status_code != 200:
                    return jsonify({'success': False, 'error': 'Falha ao baixar a imagem (status HTTP != 200)'}), 400

                # Determina extensão do arquivo (fallback para .jpg se não for possível)
                parsed_ext = os.path.splitext(
                    url_image.split('?')[0])[1].lower()
                if parsed_ext.replace('.', '') not in ALLOWED_EXTENSIONS:
                    content_type = response.headers.get('Content-Type', '')
                    if 'png' in content_type:
                        parsed_ext = '.png'
                    elif 'jpeg' in content_type or 'jpg' in content_type:
                        parsed_ext = '.jpg'
                    else:
                        return jsonify({'success': False, 'error': 'Extensão não suportada. Apenas JPG, JPEG ou PNG'}), 400

                filename = secure_filename(f"{uuid.uuid4()}{parsed_ext}")
                filepath = os.path.join(
                    app.root_path, USER_UPLOADS_DIR, filename)

                # Garante diretório existente e grava o arquivo
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f_out:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f_out.write(chunk)
            except requests.RequestException as req_err:
                return jsonify({'success': False, 'error': f'Erro ao baixar a imagem: {req_err}'}), 400
        else:
            # Nenhuma URL fornecida, continuaremos a verificar upload de arquivo abaixo
            pass

    # --------------------------------------------------
    # 2) Manipular upload multipart legado (se URL não foi fornecida)
    # --------------------------------------------------
    if filepath is None:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhuma imagem fornecida. Esperando JSON com "url_image" ou campo multipart "image".'
            }), 400

        file_storage = request.files['image']
        if file_storage.filename == '':
            return jsonify({'success': False, 'error': 'Nenhuma imagem selecionada'}), 400

        if not allowed_file(file_storage.filename):
            return jsonify({
                'success': False,
                'error': 'Tipo de arquivo não suportado. Por favor, envie JPG, JPEG ou PNG'
            }), 400

        filename = secure_filename(
            f"{uuid.uuid4()}{os.path.splitext(file_storage.filename)[1]}")
        filepath = os.path.join(app.root_path, USER_UPLOADS_DIR, filename)
        file_storage.save(filepath)

    try:
        print(f"Processando imagem em: {filepath}")

        # Processar a imagem com SkinToneClassifier
        try:
            result = SkinToneClassifier.analyze(
                filepath,
                tone_palette="perla",  # Usar a paleta PERLA (padrão)
                n_dominant_colors=3,   # Extrair 3 cores dominantes
                return_report_image=True  # Incluir a imagem anotada nos resultados
            )
            print("Resultado do processo SkinToneClassifier:", result)
        except Exception as process_error:
            print(f"Erro no SkinToneClassifier: {str(process_error)}")
            raise Exception(
                f"Erro de processamento do SkinToneClassifier: {str(process_error)}")

        # Se nenhum rosto foi detectado
        if 'faces' not in result:
            print("Nenhuma chave 'faces' no resultado:", result)
            return jsonify({
                'success': False,
                'error': 'Formato de imagem inválido ou erro de processamento. Por favor, tente uma imagem diferente.'
            }), 400

        if not result['faces']:
            print("Array 'faces' vazio no resultado:", result)
            return jsonify({
                'success': False,
                'error': 'Nenhum rosto detectado na imagem. Por favor, envie uma foto clara do rosto com boa iluminação.'
            }), 400

        # Obter o resultado do primeiro rosto (rosto mais proeminente)
        face = result['faces'][0]

        # Extrair cores do resultado do rosto
        # Baseado nos logs, dominant_colors é um array de objetos com propriedades 'color' e 'percent'
        dominant_colors = []
        try:
            if 'dominant_colors' in face:
                for color_obj in face['dominant_colors']:
                    if 'color' in color_obj:
                        dominant_colors.append(color_obj['color'])

            # Se não temos cores suficientes, adicionar padrões
            while len(dominant_colors) < 3:
                dominant_colors.append('#E6B76D')
        except Exception as color_error:
            print(f"Erro ao extrair cores dominantes: {str(color_error)}")
            dominant_colors = ['#E6B76D', '#D99559',
                               '#C27A46']  # Fallback padrão

        # Salvar a imagem do relatório se disponível
        report_image_url = None
        if 'report_images' in result and result['report_images']:
            try:
                report_filename = f"report_{filename}"
                report_filepath = os.path.join(
                    app.root_path, 'static', 'reports', report_filename)
                os.makedirs(os.path.dirname(report_filepath), exist_ok=True)

                print(f"Imagens de relatório encontradas: {type(result['report_images'])}")
                print(f"Conteúdo das imagens de relatório: {result['report_images']}")

                # Manipular se report_images for um dicionário (como mostrado nos logs)
                if isinstance(result['report_images'], dict):
                    report_image = next(iter(result['report_images'].values()))
                    print(
                        f"Usando primeira imagem do dicionário: {type(report_image)}")
                else:
                    report_image = result['report_images'][0]
                    print(f"Usando primeira imagem da lista: {type(report_image)}")

                cv2.imwrite(report_filepath, report_image)
                print(f"Imagem do relatório salva em: {report_filepath}")
                report_image_url = f"/static/reports/{report_filename}"
                print(f"URL da imagem do relatório: {report_image_url}")
            except Exception as report_error:
                print(f"Erro ao salvar imagem do relatório: {str(report_error)}")
                # Criar uma imagem de relatório básica como fallback
                try:
                    # Criar uma imagem de relatório simples com informações do tom de pele
                    fallback_report = np.ones(
                        (400, 600, 3), dtype=np.uint8) * 255  # Fundo branco

                    # Adicionar informações do tom de pele
                    cv2.putText(fallback_report, f"Tom de Pele: {tone_category}", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

                    # Adicionar caixas coloridas para cores dominantes
                    for i, color in enumerate(dominant_colors[:3]):
                        # Converter hex para RGB
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)

                        # Desenhar retângulo colorido
                        cv2.rectangle(fallback_report, (50 + i*100, 100),
                                      (130 + i*100, 180), (b, g, r), -1)

                    report_filename = f"fallback_report_{filename}"
                    report_filepath = os.path.join(
                        app.root_path, 'static', 'reports', report_filename)
                    cv2.imwrite(report_filepath, fallback_report)
                    report_image_url = f"/static/reports/{report_filename}"
                    print(f"Imagem de relatório fallback criada: {report_image_url}")
                except Exception as fallback_error:
                    print(
                        f"Erro ao criar relatório fallback: {str(fallback_error)}")

        # Mapear tons de pele para recomendações de cores sazonais
        seasonal_colors = {
            'Muito Claro': {
                'season': 'Verão',
                'colors': ['#7EC8E3', '#BFD3C1', '#89CFF0', '#F4C2C2', '#FAF0E6'],
                'description': 'Sua pele tem tons frios com profundidade muito clara. Cores que complementam seu tom incluem pastéis, azuis suaves e rosas claros.'
            },
            'Claro': {
                'season': 'Primavera',
                'colors': ['#FFDB58', '#98FB98', '#87CEFA', '#F08080', '#FFDAB9'],
                'description': 'Sua pele tem tons quentes com profundidade clara. Cores que complementam seu tom incluem amarelos quentes, verdes claros e tons coral.'
            },
            'Médio Claro': {
                'season': 'Primavera',
                'colors': ['#FFD700', '#90EE90', '#00BFFF', '#FF6347', '#FFDEAD'],
                'description': 'Sua pele tem tons quentes com profundidade médio clara. Cores que complementam seu tom incluem amarelos dourados, verdes vibrantes e vermelhos coral.'
            },
            'Médio': {
                'season': 'Outono',
                'colors': ['#8B5A2B', '#F4A460', '#CD853F', '#006400', '#FF7F50'],
                'description': 'Sua pele tem tons quentes com profundidade média. Cores que complementam seu tom incluem tons terrosos, verdes quentes e tons coral.'
            },
            'Médio Escuro': {
                'season': 'Outono',
                'colors': ['#B8860B', '#A0522D', '#556B2F', '#8B0000', '#D2691E'],
                'description': 'Sua pele tem tons quentes com profundidade médio escura. Cores que complementam seu tom incluem dourados ricos, verdes oliva e vermelhos tijolo.'
            },
            'Escuro': {
                'season': 'Inverno',
                'colors': ['#4B0082', '#800000', '#008000', '#000080', '#FF0000'],
                'description': 'Sua pele tem tons frios com profundidade escura. Cores que complementam seu tom incluem roxos reais, vermelhos profundos e verdes florestais.'
            },
            'Muito Escuro': {
                'season': 'Inverno',
                'colors': ['#800080', '#8B0000', '#006400', '#000080', '#FF4500'],
                'description': 'Sua pele tem tons frios com profundidade muito escura. Cores que complementam seu tom incluem roxos ousados, vermelhos ricos e azuis profundos.'
            }
        }

        # Determinar categoria de tom baseada no valor do tom de pele
        # Vamos usar uma abordagem mais simples baseada nos dados reais dos logs
        tone_category = 'Médio'  # Padrão

        try:
            # Tentar usar o valor hex do skin_tone para determinar o brilho/categoria
            if 'skin_tone' in face:
                skin_tone_hex = face['skin_tone']
                # Conversão hex para RGB para cálculo simples de brilho
                r = int(skin_tone_hex[1:3], 16)
                g = int(skin_tone_hex[3:5], 16)
                b = int(skin_tone_hex[5:7], 16)

                # Fórmula simples de brilho (0-255)
                brightness = (r + g + b) / 3

                # Mapear brilho para categorias de tom
                if brightness > 220:
                    tone_category = 'Muito Claro'
                elif brightness > 190:
                    tone_category = 'Claro'
                elif brightness > 160:
                    tone_category = 'Médio Claro'
                elif brightness > 130:
                    tone_category = 'Médio'
                elif brightness > 100:
                    tone_category = 'Médio Escuro'
                elif brightness > 70:
                    tone_category = 'Escuro'
                else:
                    tone_category = 'Muito Escuro'

                print(
                    f"Mapeado tom de pele {skin_tone_hex} com brilho {brightness} para categoria: {tone_category}")
        except Exception as mapping_error:
            print(f"Erro ao determinar categoria de tom: {str(mapping_error)}")

        # Obter as recomendações de cores sazonais
        season_data = seasonal_colors.get(
            tone_category, seasonal_colors['Médio'])

        # Retornar resultados
        return jsonify({
            'success': True,
            'tone': tone_category,
            'season': season_data['season'],
            'colors': dominant_colors[:3],  # Top 3 cores dominantes
            'description': season_data['description'],
            'recommendedColors': season_data['colors'],
            'reportImage': report_image_url
        })

    except Exception as e:
        print(f"Erro na análise do tom de pele: {str(e)}")

        # Fornecer resultados de fallback em caso de erro
        fallback_data = {
            'success': True,  # Ainda retornar sucesso para mostrar algo ao usuário
            'tone': 'Médio',
            'season': 'Outono',
            'colors': ['#E6B76D', '#D99559', '#C27A46'],
            'description': 'Análise baseada em dados de fallback. Sua pele parece ter tons quentes com profundidade média. Cores que complementam tons médios quentes incluem tons terrosos, verdes quentes e tons coral. Análise alimentada pela tecnologia de IA SkinToneClassifier.',
            'recommendedColors': ['#8B5A2B', '#F4A460', '#CD853F', '#006400', '#FF7F50'],
            # Fornecer uma imagem de relatório de fallback
            'reportImage': '/static/assets/fallback_report.jpg'
        }

        return jsonify(fallback_data)
    finally:
        # Limpar o arquivo enviado
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)