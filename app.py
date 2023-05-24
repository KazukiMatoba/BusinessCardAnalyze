from flask import Flask, render_template, request, jsonify
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import logging
import re
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #日本語を利用

# Form Recognizerの設定
endpoint = "https://bvmc-test-s123.cognitiveservices.azure.com"
key = "59dc239e8ed44be081aa3cf798cea518"
credential = AzureKeyCredential(key)
client = DocumentAnalysisClient(endpoint, credential)

# ルートURLへのGETリクエストを処理するハンドラ
@app.route('/', methods=["GET"])
def index():
    #logging.debug("debug")
    #logging.info("info")
    #logging.warning("warning")
    #logging.error("error")
    #logging.critical("critical")
    return render_template("index.html")

# フォームのデータを受け取るハンドラ
@app.route("/upload", methods=["POST"])
def upload_data():
    if "file" not in request.files:
        return "ファイルがありません"

    file = request.files["file"]

    results = client.begin_analyze_document("prebuilt-businessCard", document=file.stream.read()).result()
    # 名刺モデル
    # https://learn.microsoft.com/ja-jp/azure/applied-ai-services/form-recognizer/concept-business-card?view=form-recog-3.0.0

    for idx, business_card in enumerate(results.documents):
        result_data = {}
        
        contact_names = business_card.fields.get("ContactNames")
        if contact_names:
            for idx, contact_name in enumerate(contact_names.value):
                contact_name_dic = contact_name.value
                if idx == 0:
                    first_name = contact_name_dic.get("FirstName")
                    if first_name:
                        result_data["FirstName"] = re.sub(r"\s+", "", first_name.value)
                    last_name = contact_name_dic.get("LastName")
                    if last_name:
                        result_data["LastName"] = re.sub(r"\s+", "", last_name.value)
        
        company_names = business_card.fields.get("CompanyNames")
        if company_names:
           for idx, company_name in enumerate(company_names.value):
                if idx == 0:
                    result_data["CompanyName"] = re.sub(r"\s+", "", company_name.value)
        
        departments = business_card.fields.get("Departments")
        if departments:
            for idx, department in enumerate(departments.value):
                if idx == 0:
                    result_data["Department"] = re.sub(r"\s+", "", department.value)
        
        job_titles = business_card.fields.get("JobTitles")
        if job_titles:
            for idx, job_title in enumerate(job_titles.value):
                if idx == 0:
                    result_data["JobTitle"] = re.sub(r"\s+", "", job_title.value)
        
        emails = business_card.fields.get("Emails")
        if emails:
            for idx, email in enumerate(emails.value):
                if idx == 0:
                    result_data["Email"] = re.sub(r"\s+", "", email.value)
        
        websites = business_card.fields.get("Websites")
        if websites:
            for idx, website in enumerate(websites.value):
                if idx == 0:
                    result_data["Website"] = re.sub(r"\s+", "", website.value)
        
        addresses = business_card.fields.get("Addresses")
        if addresses:
            for idx, address in enumerate(addresses.value):
                if idx == 0:
                    addressValue = address.value
                    #https://learn.microsoft.com/en-us/python/api/azure-ai-formrecognizer/azure.ai.formrecognizer.addressvalue?view=azure-python
                    if addressValue.postal_code is not None:
                        result_data["PostalCode"] = re.sub(r"\s+", "", addressValue.postal_code)
                    
                    addressStr = ""
                    if addressValue.state is not None:
                        addressStr += addressValue.state
                    if addressValue.city is not None:
                        addressStr += addressValue.city
                    if addressValue.street_address is not None:
                        addressStr += addressValue.street_address
                    result_data["Address"] = re.sub(r"\s+", "", addressStr)
        
        mobile_phones = business_card.fields.get("MobilePhones")
        if mobile_phones:
            for idx, phone in enumerate(mobile_phones.value):
                if idx == 0:
                    result_data["MobilePhone"] = str(phone.value).replace("+81", "0")
        
        faxes = business_card.fields.get("Faxes")
        if faxes:
            for idx, fax in enumerate(faxes.value):
                if idx == 0:
                    result_data["Fax"] = str(fax.value).replace("+81", "0")
        
        work_phones = business_card.fields.get("WorkPhones")
        if work_phones:
            for idx, work_phone in enumerate(work_phones.value):
                if idx == 0:
                    result_data["WorkPhone"] = str(work_phone.value).replace("+81", "0")
        
        other_phones = business_card.fields.get("OtherPhones")
        if other_phones:
            for idx, other_phone in enumerate(other_phones.value):
                if idx == 0:
                    result_data["OtherPhone"] = str(other_phone.value).replace("+81", "0")

        #logging.warning(result_data)
        #logging.warning(jsonify(result_data))
        #logging.warning(json.dumps(result_data, ensure_ascii=False))
        #return jsonify(result_data)
        return json.dumps(result_data, ensure_ascii=False)
    else:
        result_data = {'message': '名刺データが読み込めませんでした'}
        return json.dumps(result_data, ensure_ascii=False)


if __name__ == '__main__':
    app.debug = True
    app.run()
