from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from minio import Minio
from minio.error import S3Error
import os
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar flash messages

# Configurações do MinIO
minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Verifica se o bucket existe, caso contrário, cria-o
bucket_name = "data"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

# Função para ler o conteúdo do arquivo diretamente do MinIO
def read_csv_from_minio(bucket_name, object_name):
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read()
        return pd.read_csv(io.BytesIO(data))
    except S3Error as e:
        print(f"Erro ao ler o arquivo {object_name} do MinIO: {e}")
        return None

# Função para ler a senha diretamente do MinIO
def read_password_from_minio(bucket_name, object_name):
    try:
        response = minio_client.get_object(bucket_name, object_name)
        data = response.read().decode('utf-8').strip()
        return data
    except S3Error as e:
        print(f"Erro ao ler o arquivo {object_name} do MinIO: {e}")
        return None

# Carrega os dados do MinIO
schedule_csv = "schedule.csv"
senha_csv = "senha.csv"

# carrega Dataset
df = read_csv_from_minio(bucket_name, schedule_csv)
df['Dia'] = df['Dia'].astype(int)
df.fillna('-', inplace=True)

PASSWORD = read_password_from_minio(bucket_name, senha_csv)

# Verifique as colunas do DataFrame
if df is not None:
    print("Colunas lidas do CSV:", df.columns)
    print("Número de colunas lidas:", len(df.columns))
    expected_columns = ['Ano', 'Mês_Descrição', 'Dia', 'Dia_Semana', 'Feriado', 'Grau', 'Tipo', 'Atividade', 'Observações']
    if len(df.columns) == len(expected_columns):
        df.columns = expected_columns
        df['Dia'] = df['Dia'].astype(int)
    else:
        print(f"Erro: O número de colunas no CSV ({len(df.columns)}) não corresponde ao esperado ({len(expected_columns)}).")
        print("Primeiras linhas do DataFrame para inspeção:")
        print(df.head())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            return redirect(url_for('select_year'))
        else:
            return render_template('index.html', error="Incorrect password")
    return render_template('index.html')

@app.route('/select_year', methods=['GET', 'POST'])
def select_year():
    df = read_csv_from_minio(bucket_name, schedule_csv)
    df['Dia'] = df['Dia'].astype(int)   
    df.fillna('-', inplace=True)
    current_year = datetime.now().year
    if df is not None:
        years = df['Ano'].unique()
        if request.method == 'POST':
            year = request.form['year']
            return redirect(url_for('select_month', year=year))
        return render_template('select_year.html', years=years, current_year=current_year)
    else:
        return "Erro ao carregar os dados do MinIO."

@app.route('/select_month/<year>', methods=['GET', 'POST'])
def select_month(year):
    current_month = datetime.now().strftime('%B')
    current_month_pt = months_pt[current_month]  # Converte o mês atual para português
    if request.method == 'POST':
        month = request.form['month']
        return redirect(url_for('show_schedule', year=year, month=month))
    return render_template('select_month.html', year=year, current_month=current_month_pt)

# Dicionário de meses em português
months_pt = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

@app.route('/schedule/<year>/<month>')
def show_schedule(year, month):
    df = read_csv_from_minio(bucket_name, schedule_csv)
    df['Dia'] = df['Dia'].astype(int)
    df.fillna('-', inplace=True)
    if df is not None:
        month_data = df[(df['Ano'] == int(year)) & (df['Mês_Descrição'] == month)]
        month_data = month_data[['Dia', 'Dia_Semana', 'Feriado', 'Grau', 'Tipo', 'Atividade', 'Observações']]
        # Converte o DataFrame para HTML com formatação limpa
        table_html = month_data.to_html(classes='table table-striped table-bordered', index=False, border=0)
        return render_template('schedule.html', year=year, month=month, table_html=table_html)
    else:
        return "Erro ao carregar os dados do MinIO."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
