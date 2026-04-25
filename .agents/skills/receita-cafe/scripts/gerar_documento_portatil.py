import base64
import os

img_path = '/home/rosner/projetosgit/cafe/.agents/skills/receita-cafe/output/cafe_deploy_20260425_153810.png'
md_path = '/home/rosner/projetosgit/cafe/.agents/skills/receita-cafe/output/receita_deploy_20260425_153810.md'

if os.path.exists(img_path):
    with open(img_path, 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')

    md_content = f"""# ☕ Protocolo Portátil: Deploy Hotfix (Sul de Minas)

**Status:** ✨ Portabilidade Total Ativada (Image Embedded)
**Cenário:** Deploy de hotfix crítico no banco de dados.

## 🎬 O Cenário (Storytelling)
Você está lá, com o brilho do sol refletindo na tela, o comando de `UPDATE` sem `WHERE` já digitado e o suor escorrendo. É aquele momento clássico: ou o hotfix resolve o problema ou você vai descobrir se o backup realmente funciona.

## 🧪 Configuração Técnica de Extração
- **Café:** 21.4g (Sul de Minas)
- **Água:** 300ml
- **Temperatura:** 90°C
- **Moagem:** Média-Grossa

## 🖼️ Infográfico de Preparo (Incorporado)
![Infográfico](data:image/png;base64,{b64_data})

---
*Gerado pela Advanced Brazilian Coffee Engine v3.0. Este documento é autocontido.*
"""
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Sucesso: Documento portátil gerado em {md_path}")
else:
    print(f"Erro: Imagem não encontrada em {img_path}")
