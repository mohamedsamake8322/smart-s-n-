
from googletrans import Translator
from tqdm import tqdm
import json
import time
import os

translator = Translator()

# Ta liste brute de noms en chinois (à compléter si besoin)
classes_chinoises = [
    "健康苹果", "苹果Alternaria_叶斑病", "苹果灰斑病", "苹果白粉病", "苹果花叶病", "苹果蛙眼叶斑病",
    "苹果褐斑病", "苹果赤霉病", "苹果锈病", "ip102_v1.1(c)", "ip102_v1.1", "images",
    "健康小麦(c)", "健康大豆", "健康柑橘", "健康树莓", "健康桃子", "健康樱桃", "健康玉米",
    "健康甜椒", "健康番茄", "健康草莓", "健康葡萄", "健康马铃薯", "南瓜白粉病", "柑橘黄龙病",
    "桃树细菌性穿孔病", "樱桃白粉病", "玉米叶斑病", "玉米大斑病", "玉米锈病", "甜椒细菌性斑点病",
    "番茄二斑叶螨", "番茄叶霉病", "番茄壳针孢叶斑病", "番茄早疫病", "番茄晚疫病", "番茄细菌性斑点病",
    "番茄花叶病毒病", "番茄靶斑病", "番茄黄化曲叶病毒病", "苹果桧柏锈病", "苹果黑星病", "苹果黑腐病",
    "草莓叶焦病", "葡萄叶枯病", "葡萄黑腐病", "葡萄黑麻疹病", "马铃薯早疫病", "马铃薯晚疫病",
    "大豆根腐病", "大豆细菌性斑疹病", "大豆花叶病毒病", "健康小麦", "小麦叶枯病", "小麦条锈病",
    "小麦叶锈病", "小麦松散黑穗病", "根冠腐病", "小麦白粉病", "小麦赤霉病", "叶锈病", "茎锈病",
    "东格鲁病", "稻瘟病", "细菌性枯萎病", "褐斑病", "水稻白叶枯病", "水稻纹枯病", "水稻细菌性条斑病",
    "水稻胡麻斑病", "稻曲病", "水稻大螟", "稻棘缘蝽", "稻纵卷叶螟", "稻蝗", "稻飞虱",
    "玉米南方锈病", "玉米小斑病", "甜菜夜蛾", "红缘灯蛾", "葡萄花叶病毒病", "葡萄霜霉病", "葡萄黑霉病",
    "西瓜炭疽病", "西瓜病毒病", "豇豆褐斑病", "豇豆锈病", "黄瓜炭疽病", "黄瓜白粉病", "黄瓜霜霉病",
    "黄瓜靶斑病"
]

output_file = "classes_traduites.json"

# Charger les traductions précédentes s’il y en a
if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        traductions = json.load(f)
else:
    traductions = []

# Traduire uniquement les nouveaux éléments
for nom in tqdm(classes_chinoises, desc="Traduction des classes"):
    if nom in traductions:
        continue

    try:
        traduction = translator.translate(nom, src='zh-cn', dest='fr')
        traductions.append(traduction.text.strip())
    except Exception as e:
        print(f"❌ Erreur pour {nom} : {e}")
        time.sleep(5)

    # Sauvegarde intermédiaire
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(traductions, f, ensure_ascii=False, indent=4)

print("🎉 Traductions terminées : {} classes traduites.".format(len(traductions)))
