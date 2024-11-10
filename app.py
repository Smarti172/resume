from flask import Flask, render_template, request, jsonify
import pdfminer.high_level as pdfminer
import boto3
import re
import smtplib
from email.mime.text import MIMEText
import io

app = Flask(__name__)

S3_BUCKET = 'resumestorage172'
S3_REGION = 'eu-north-1'  
ACCESS_KEY = 'AKIAYXWBNTBVTSZIUKFY'
SECRET_KEY = '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'

s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=S3_REGION
)

def extract_text_from_pdf(pdf_file):
    return pdfminer.extract_text(pdf_file)

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def send_email(to_email):
    sender_email = "agtalgatov2007@gmail.com"
    sender_password = "nzke uxgn mtwg wbpi"

    msg = MIMEText("Поздравляем! Вы прошли предварительный отбор на вакансию. Просим вас связаться для следующего этапа отбора")
    msg["Subject"] = "Предварительный отбор"
    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

def generate_candidate_assessment(candidate_pdf, vacancy_requirements, file_key):
    candidate_text = extract_text_from_pdf(candidate_pdf)

    email = extract_email(candidate_text)

    requirements = vacancy_requirements.split()
    if all(requirement.lower() in candidate_text.lower() for requirement in requirements):
        assessment = "Кандидат подходит"
        resume_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_key}"
        if email:
            send_email(email) 
        return {"resume": file_key, "assessment": assessment, "resume_url": resume_url}
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    vacancy_requirements = request.form['vacancy_requirements']
    s3_files = s3_client.list_objects_v2(Bucket=S3_BUCKET).get('Contents', [])
    results = []

    for file in s3_files:
        pdf_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file['Key'])
        pdf_file = io.BytesIO(pdf_obj['Body'].read())
        result = generate_candidate_assessment(pdf_file, vacancy_requirements, file['Key'])
        if result:
            results.append(result)

    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True, host='192.168.8.24', port=5000)
