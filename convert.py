import urllib.request
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Ссылка на ваш YML в Тильде
SOURCE_YML_URL = "http://ove.moscow/tstore/yml/046650b78c58ce90db5a20fe923eb24b.yml"
OUTPUT_XML_FILE = "pinterest_feed.xml"

category_mapping = {
    "480020645053": "Apparel & Accessories > Clothing > Shirts & Tops",
    "752268862133": "Apparel & Accessories > Clothing > Outerwear",
    "141690824832": "Apparel & Accessories > Clothing > Pants",
    "541377829252": "Apparel & Accessories > Clothing > Shirts & Tops",
    "583799011412": "Apparel & Accessories > Clothing > Shirts & Tops",
    "436732181942": "Apparel & Accessories > Clothing > Shorts",
    "538696474182": "Apparel & Accessories > Clothing Accessories > Hats",
    "661841959253": "Apparel & Accessories > Clothing > Dresses",
    "628697075733": "Apparel & Accessories > Clothing > Skirts",
    "970069655343": "Apparel & Accessories > Clothing > Shirts & Tops",
}

def convert():
    print(f"Скачиваю файл: {SOURCE_YML_URL}...")
    req = urllib.request.Request(SOURCE_YML_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        yml_content = response.read()

    root = ET.fromstring(yml_content)

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:g": "http://base.google.com/ns/1.0"
    })
    channel = ET.SubElement(rss, "channel")

    shop_name = root.findtext(".//shop/name", default="OVE")
    shop_url = root.findtext(".//shop/url", default="http://ove.moscow")
    ET.SubElement(channel, "title").text = shop_name
    ET.SubElement(channel, "link").text = shop_url
    ET.SubElement(channel, "description").text = f"Каталог товаров {shop_name}"

    offers = root.findall(".//offer")
    print(f"Найдено товаров: {len(offers)}")

    for offer in offers:
        offer_id = offer.get("id")
        group_id = offer.get("group_id")
        name = offer.findtext("name", default="").strip()
        description = offer.findtext("description", default="").strip()
        url = offer.findtext("url", default="").strip()
        picture = offer.findtext("picture", default="").strip()
        price = offer.findtext("price", default="0").strip()
        
        count_text = offer.findtext("count", default="0").strip()
        try:
            count = int(count_text)
        except ValueError:
            count = 0
        availability = "in stock" if count > 0 else "out of stock"

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "g:id").text = str(offer_id)
        ET.SubElement(item, "title").text = name
        ET.SubElement(item, "description").text = description
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "g:image_link").text = picture
        ET.SubElement(item, "g:price").text = f"{price} RUB"
        ET.SubElement(item, "g:availability").text = availability
        ET.SubElement(item, "g:condition").text = "new"

        if group_id:
            ET.SubElement(item, "g:item_group_id").text = str(group_id)

        for param in offer.findall("param"):
            if param.get("name") == "Размер":
                ET.SubElement(item, "g:size").text = param.text
                break
        
        category_id = offer.findtext("categoryId")
        if category_id in category_mapping:
            ET.SubElement(item, "g:google_product_category").text = category_mapping[category_id]
        else:
            ET.SubElement(item, "g:google_product_category").text = "Apparel & Accessories > Clothing"

    rough_string = ET.tostring(rss, encoding='utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

    with open(OUTPUT_XML_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"ГОТОВО! Файл {OUTPUT_XML_FILE} создан.")

if __name__ == "__main__":
    convert()
