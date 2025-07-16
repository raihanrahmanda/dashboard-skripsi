# from app.utils.scraper import detikcom_scraping  
# from app.utils.pre_processing import load_and_clean_data
# from app.utils.klasifikasi_berita_relevan import predict_sentiment_from_file
# from app.utils.pemeriksaan_kesamaan_teks import update_relevant_news_and_filter
# from app.utils.prediksi_ner import prediksi_ner, extract_all_entities, process_dates, normalize_location
# from app.utils.pembentukan_tabel_visualisasi import entitas_day, entitas_time, entitas_age, entitas_cause, entitas_death, entitas_injury, entitas_loc, entitas_merk, entitas_road, entitas_vehicle
# from app.utils.pembentukan_dataset_klasifikasi import grouping_day, grouping_cause, grouping_vehicle, grouping_death, grouping_time, grouping_driver_age, grouping_road, finalisasi_dataset
# from app.utils.klasifikasi_kecelakaan_lalu_lintas import preprocessing_klasifikasi, prediksi_laka_lantas, visualisasi_surrogate_tree
# from app.utils.word_classification import BertForWordClassification

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
# from transformers import BertConfig, BertTokenizer
import traceback
from datetime import datetime
import os
import json
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

import io # Untuk menangani gambar dalam memori
import base64 # Untuk encode gambar ke base64
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg') # Penting untuk backend matplotlib tanpa GUI
import matplotlib.pyplot as plt
import requests

import gdown
from functools import lru_cache

app = Flask(
    __name__,
    template_folder='app/templates',
    static_folder='app/static'  
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scraping')
def scraping_page():
    return render_template('scraping.html')

@app.route('/data')
def data_page():
    return render_template('data.html')

@app.route('/classification')
def classification_page():
    return render_template('analisis.html')

@app.route('/download-classification-table')
def download_classification_table():
    if os.path.exists('data/dataset_klasifikasi_lengkap_terbaru.csv'):
        file_path = os.path.join('data', 'dataset_klasifikasi_lengkap_terbaru.csv')
    else:
        file_path = os.path.join('data', 'dataset_klasifikasi_lengkap.csv')

    if not os.path.exists(file_path):
        # Kembalikan status 404 supaya fetch .ok jadi false
        return "File tidak ada", 404
    
    return send_file(file_path, as_attachment=True)

@lru_cache(maxsize=32)
def load_csv_from_drive(file_id):
    """Mengunduh dan cache CSV dari Google Drive berdasarkan file ID."""
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(io.StringIO(response.text), encoding='utf-8-sig')
    else:
        raise Exception(f"Gagal mengunduh file ID {file_id}")

@app.route('/dashboard')
def dashboard_page():
    # Ambil parameter filter dari query string
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    lokasi = request.args.get('lokasi')
    periode_laka = request.args.get('periode', 'bulan')

    # ---------------------------- MENDEFINISIKAN DATAFRAME ----------------------------------------
    # VEHICLE
    file_id_df_vehicle = '14c_MceTk8eCzDTI51rKTt71zOTqpAVv4'
    df_vehicle = load_csv_from_drive(file_id_df_vehicle)
    
    # MERK
    file_id_df_merk = '1ioai7ykYF03Fygob0n33nYEMKItNUhTV'
    df_merk = load_csv_from_drive(file_id_df_merk)
    
    # DAY
    file_id_df_day = '1PRtJNgPbrp8QsRwGgVgDIIiaeMR3O8jO'
    df_day = load_csv_from_drive(file_id_df_day)
    
    # AGE
    file_id_df_age = '1hRCPZJrY-F58bgpq_WoU-Mgram4VBONK'
    df_age = load_csv_from_drive(file_id_df_age)
    
    # ROAD
    file_id_df_road = '1OhnmkIPjgVw54jnJmijOFcaGNiDMnEaN'
    df_road = load_csv_from_drive(file_id_df_road)
    
    # TIME
    file_id_df_time = '1SMJzG1kfiZRBo7lnTIitrXR6nL_GIZSY'
    df_time = load_csv_from_drive(file_id_df_time)
    
    # CAUSE
    file_id_df_cause = '1qAxMIeLcH9zL70JShSsvHY_pBOf3eQpQ'
    df_cause = load_csv_from_drive(file_id_df_cause)
    
    # LOC
    file_id_df_loc = '1lLyT7xo0THBnvfEl8MAH663Pnzu8hDZE'
    df_loc = load_csv_from_drive(file_id_df_loc)
    
    # INJURY
    file_id_df_injury = '1CPoPNFhkNQgihWhzp2CZOtpKsonKQEV7'
    df_injury = load_csv_from_drive(file_id_df_injury)
    
    # DEATH
    file_id_df_death = '1tvelEKu3mS2LV7YFOzxqv7S0-by1QB0l'
    df_death = load_csv_from_drive(file_id_df_death)
    
    # --------------------------------- PEMROSESEN ENTITAS KENDARAAN ---------------------------------
    # Entitas Jenis Kendaraan 
    # df_vehicle = pd.read_csv('data/tabel_entitas_vehicle.csv')
    # file_id_df_vehicle = '14c_MceTk8eCzDTI51rKTt71zOTqpAVv4'  # Ganti dengan file ID kamu
    # url_df_vehicle = f'https://drive.google.com/uc?export=download&id={file_id_df_vehicle}'
    # response_df_vehicle = requests.get(url_df_vehicle)
    # df_vehicle = pd.read_csv(io.StringIO(response_df_vehicle.text), encoding='utf-8-sig')
    df_vehicle['DATE_STANDARDIZED'] = pd.to_datetime(df_vehicle['DATE_STANDARDIZED'], errors='coerce')
    df_vehicle = df_vehicle[df_vehicle['VEHICLE'] != 'Tidak diketahui']

    # Standarisasi kolom lokasi
    df_vehicle['LOC'] = df_vehicle['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_vehicle_filtered = df_vehicle.copy()
    if start_date:
        df_vehicle_filtered = df_vehicle_filtered[df_vehicle_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_vehicle_filtered = df_vehicle_filtered[df_vehicle_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_vehicle_filtered = df_vehicle_filtered[df_vehicle_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_vehicle = df_vehicle_filtered.groupby('VEHICLE').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
    labels_vehicle = grouped_vehicle['VEHICLE'].tolist()
    data_vehicle = grouped_vehicle['Jumlah'].tolist()

    # --------------------------------- PEMROSESEN ENTITAS MERK KENDARAAN ---------------------------------
    # Entitas Jenis Kendaraan 
    # df_merk = pd.read_csv('data/tabel_entitas_merk.csv')
    # file_id_df_merk = '1ioai7ykYF03Fygob0n33nYEMKItNUhTV'  # Ganti dengan file ID kamu
    # url_df_merk = f'https://drive.google.com/uc?export=download&id={file_id_df_merk}'
    # response_df_merk = requests.get(url_df_merk)
    # df_merk = pd.read_csv(io.StringIO(response_df_merk.text), encoding='utf-8-sig')
    df_merk['DATE_STANDARDIZED'] = pd.to_datetime(df_merk['DATE_STANDARDIZED'], errors='coerce')
    df_merk = df_merk[df_merk['MERK'] != 'Tidak diketahui']

    # Standarisasi kolom lokasi
    df_merk['LOC'] = df_merk['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_merk_filtered = df_merk.copy()
    if start_date:
        df_merk_filtered = df_merk_filtered[df_merk_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_merk_filtered = df_merk_filtered[df_merk_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_merk_filtered = df_merk_filtered[df_merk_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_merk = (
        df_merk_filtered.groupby('MERK')
        .size()
        .reset_index(name='Jumlah')
        .sort_values(by='Jumlah', ascending=False)
        .head(5)
    )
    labels_merk = grouped_merk['MERK'].tolist()
    data_merk = grouped_merk['Jumlah'].tolist()

    # ---------------------------------- PEMROSESEN ENTITAS HARI KEJADIAN ---------------------------------
    # Entitas Hari Kejadian
    # df_day = pd.read_csv('data/tabel_entitas_day.csv')
    # file_id_df_day = '1PRtJNgPbrp8QsRwGgVgDIIiaeMR3O8jO'  # Ganti dengan file ID kamu
    # url_df_day = f'https://drive.google.com/uc?export=download&id={file_id_df_day}'
    # response_df_day = requests.get(url_df_day)
    # df_day = pd.read_csv(io.StringIO(response_df_day.text), encoding='utf-8-sig')
    df_day['DATE_STANDARDIZED'] = pd.to_datetime(df_day['DATE_STANDARDIZED'], errors='coerce')

    # Standarisasi kolom lokasi
    df_day['LOC'] = df_day['LOC'].astype(str).str.strip().str.lower()

    df_day_filtered = df_day.copy()
    if start_date:
        df_day_filtered = df_day_filtered[df_day_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_day_filtered = df_day_filtered[df_day_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_day_filtered = df_day_filtered[df_day_filtered['LOC'] == lokasi]

    # Chart: Hari Kejadian
    grouped_day = df_day_filtered.groupby('DAY').size().reset_index(name='Jumlah')
    urutan_hari = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    grouped_day['DAY'] = pd.Categorical(grouped_day['DAY'], categories=urutan_hari, ordered=True)
    grouped_day = grouped_day.sort_values('DAY')
    labels_day = grouped_day['DAY'].tolist()
    data_day = grouped_day['Jumlah'].tolist()

    # --------------------------------- PEMROSESEN ENTITAS UMUR ---------------------------------
    # Entitas Umur
    # df_age = pd.read_csv('data/tabel_entitas_age.csv')
    # file_id_df_age = '1hRCPZJrY-F58bgpq_WoU-Mgram4VBONK'  # Ganti dengan file ID kamu
    # url_df_age = f'https://drive.google.com/uc?export=download&id={file_id_df_age}'
    # response_df_age = requests.get(url_df_age)
    # df_age = pd.read_csv(io.StringIO(response_df_age.text), encoding='utf-8-sig')
    df_age['DATE_STANDARDIZED'] = pd.to_datetime(df_age['DATE_STANDARDIZED'], errors='coerce')
    df_age = df_age[df_age['AGE_CATEGORY'] != 'Tidak diketahui']

    # Standarisasi kolom lokasi
    df_age['LOC'] = df_age['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_age_filtered = df_age.copy()
    if start_date:
        df_age_filtered = df_age_filtered[df_age_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_age_filtered = df_age_filtered[df_age_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_age_filtered = df_age_filtered[df_age_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_age = df_age_filtered.groupby('AGE_CATEGORY').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
    labels_age = grouped_age['AGE_CATEGORY'].tolist()
    data_age = grouped_age['Jumlah'].tolist()

    # --------------------------------- PEMROSESEN ENTITAS ROAD ---------------------------------
    # Entitas Road
    # df_road = pd.read_csv('data/tabel_entitas_road.csv')
    # file_id_df_road = '1OhnmkIPjgVw54jnJmijOFcaGNiDMnEaN'  # Ganti dengan file ID kamu
    # url_df_road = f'https://drive.google.com/uc?export=download&id={file_id_df_road}'
    # response_df_road = requests.get(url_df_road)
    # df_road = pd.read_csv(io.StringIO(response_df_road.text), encoding='utf-8-sig')
    df_road['DATE_STANDARDIZED'] = pd.to_datetime(df_road['DATE_STANDARDIZED'], errors='coerce')
    df_road = df_road[df_road['ROAD_CATEGORY'] != 'Tidak diketahui']

    # Standarisasi kolom lokasi
    df_road['LOC'] = df_road['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_road_filtered = df_road.copy()
    if start_date:
        df_road_filtered = df_road_filtered[df_road_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_road_filtered = df_road_filtered[df_road_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_road_filtered = df_road_filtered[df_road_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_road = df_road_filtered.groupby('ROAD_CATEGORY').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
    labels_road = grouped_road['ROAD_CATEGORY'].tolist()
    data_road = grouped_road['Jumlah'].tolist()

    # --------------------------------- PEMROSESEN ENTITAS TIME ---------------------------------
    # Entitas Time
    # df_time = pd.read_csv('data/tabel_entitas_time.csv')
    # file_id_df_time = '1SMJzG1kfiZRBo7lnTIitrXR6nL_GIZSY'  # Ganti dengan file ID kamu
    # url_df_time = f'https://drive.google.com/uc?export=download&id={file_id_df_time}'
    # response_df_time = requests.get(url_df_time)
    # df_time = pd.read_csv(io.StringIO(response_df_time.text), encoding='utf-8-sig')
    df_time['DATE_STANDARDIZED'] = pd.to_datetime(df_time['DATE_STANDARDIZED'], errors='coerce')
    df_time = df_time[df_time['TIME_CATEGORY'] != 'Tidak diketahui']

    # Standarisasi kolom lokasi
    df_time['LOC'] = df_time['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_time_filtered = df_time.copy()
    if start_date:
        df_time_filtered = df_time_filtered[df_time_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_time_filtered = df_time_filtered[df_time_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_time_filtered = df_time_filtered[df_time_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_time = df_time_filtered.groupby('TIME_CATEGORY').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
    labels_time = grouped_time['TIME_CATEGORY'].tolist()
    data_time = grouped_time['Jumlah'].tolist()

    # --------------------------------- PEMROSESEN ENTITAS CAUSE ---------------------------------
    # Entitas Cause
    # df_cause = pd.read_csv('data/tabel_entitas_cause.csv')
    # file_id_df_cause = '1qAxMIeLcH9zL70JShSsvHY_pBOf3eQpQ'  # Ganti dengan file ID kamu
    # url_df_cause = f'https://drive.google.com/uc?export=download&id={file_id_df_cause}'
    # response_df_cause = requests.get(url_df_cause)
    # df_cause = pd.read_csv(io.StringIO(response_df_cause.text), encoding='utf-8-sig')
    df_cause['DATE_STANDARDIZED'] = pd.to_datetime(df_cause['DATE_STANDARDIZED'], errors='coerce')
    df_cause = df_cause[df_cause['CAUSE_CATEGORY'] != 'Lainnya']

    # Standarisasi kolom lokasi
    df_cause['LOC'] = df_cause['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_cause_filtered = df_cause.copy()
    if start_date:
        df_cause_filtered = df_cause_filtered[df_cause_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_cause_filtered = df_cause_filtered[df_cause_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_cause_filtered = df_cause_filtered[df_cause_filtered['LOC'] == lokasi]

    # Chart: Jenis kendaraan
    grouped_cause = df_cause_filtered.groupby('CAUSE_CATEGORY').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
    labels_cause = grouped_cause['CAUSE_CATEGORY'].tolist()
    data_cause = grouped_cause['Jumlah'].tolist()
    
    # ---------------------------------------- PEMROSESEN ENTITAS LOKASI KEJADIAN ---------------------------------
    def normalize_lokasi(lokasi):
        lokasi = lokasi.strip().lower()
        if lokasi.startswith('kabupaten '):
            return lokasi.replace('kabupaten ', '')
        elif lokasi.startswith('kota '):
            return lokasi  # kota tetap
        return lokasi

    # === CSV lokasi untuk peta ===
    # df_loc = pd.read_csv('data/tabel_entitas_loc.csv')
    # file_id_df_loc = '1lLyT7xo0THBnvfEl8MAH663Pnzu8hDZE'  # Ganti dengan file ID kamu
    # url_df_loc = f'https://drive.google.com/uc?export=download&id={file_id_df_loc}'
    # response_df_loc = requests.get(url_df_loc)
    # df_loc = pd.read_csv(io.StringIO(response_df_loc.text), encoding='utf-8-sig')
    df_loc['DATE_STANDARDIZED'] = pd.to_datetime(df_loc['DATE_STANDARDIZED'], errors='coerce')
    df_loc['LOC'] = df_loc['LOC'].astype(str).apply(normalize_lokasi)

    df_loc_filtered = df_loc.copy()
    if start_date:
        df_loc_filtered = df_loc_filtered[df_loc_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_loc_filtered = df_loc_filtered[df_loc_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_loc_filtered = df_loc_filtered[df_loc_filtered['LOC'] == normalize_lokasi(lokasi)]

    location_counts = df_loc_filtered.groupby('LOC').size().reset_index(name='jumlah')
    jumlah_kejadian = location_counts['jumlah'].sum()

    # === Load GeoJSON dan tambahkan data jumlah ===
    with open('data/batas_kabkota_jateng.geojson', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    # file_id_geo = '1ChrFijx7onjTqlNk-rbRXm6v8zvb8SRc'
    # output_path_geo = 'batas_kabkota_jateng.geojson'
    # url_geo = f'https://drive.google.com/uc?id={file_id_geo}'
    
    # # Download file
    # gdown.download(url_geo, output_path_geo, quiet=False)
    
    # # Buka file lokal
    # with open(output_path_geo, encoding='utf-8') as f:
    #     geojson_data = json.load(f)

    # file_id_geo = '1ChrFijx7onjTqlNk-rbRXm6v8zvb8SRc'
    # url_geo = f'https://drive.google.com/uc?export=download&id={file_id_geo}'
    
    # response = requests.get(url_geo)
    
    # try:
    #     geojson_data = response.json()
    # except Exception:
    #     try:
    #         geojson_data = json.loads(response.text)
    #     except:
    #         raise Exception("Gagal mengunduh atau memuat file GeoJSON.")

    for feature in geojson_data['features']:
        nama_asli = feature['properties']['WADMKK'].strip()
        nama_geojson = nama_asli.lower()

        # Tambahkan awalan "Kabupaten" jika tidak mengandung "kota"
        if not nama_geojson.startswith('kota'):
            feature['properties']['WADMKK'] = f'Kabupaten {nama_asli}'
            normalized_nama = nama_geojson  # tetap gunakan versi lowercase tanpa awalan "kabupaten"
        else:
            normalized_nama = nama_geojson

        match = location_counts[location_counts['LOC'] == normalized_nama]
        jumlah = int(match.iloc[0]['jumlah']) if not match.empty else 0
        feature['properties']['jumlah'] = jumlah
    
    # ---------------------------------------- PEMROSESEN ENTITAS INJURY ---------------------------------
    # df_injury = pd.read_csv('data/tabel_entitas_injury.csv')
    # file_id_df_injury = '1CPoPNFhkNQgihWhzp2CZOtpKsonKQEV7'  # Ganti dengan file ID kamu
    # url_df_injury = f'https://drive.google.com/uc?export=download&id={file_id_df_injury}'
    # response_df_injury = requests.get(url_df_injury)
    # df_injury = pd.read_csv(io.StringIO(response_df_injury.text), encoding='utf-8-sig')
    # Parsing tanggal
    df_injury['DATE_STANDARDIZED'] = pd.to_datetime(df_injury['DATE_STANDARDIZED'], errors='coerce')
    df_injury = df_injury.dropna(subset=['DATE_STANDARDIZED'])

    # Ekstrak bulan-tahun
    df_injury['month_year'] = df_injury['DATE_STANDARDIZED'].dt.to_period('M').astype(str)

    # Standarisasi kolom lokasi
    df_injury['LOC'] = df_injury['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_injury_filtered = df_injury.copy()
    if start_date:
        df_injury_filtered = df_injury_filtered[df_injury_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_injury_filtered = df_injury_filtered[df_injury_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_injury_filtered = df_injury_filtered[df_injury_filtered['LOC'] == lokasi]


    # Hitung total injury per bulan
    counts_injury = (
        df_injury_filtered.groupby('month_year')['INJURY_COUNT']
        .sum()
        .reset_index(name='jumlah')
    )

    jumlah_luka = counts_injury['jumlah'].sum() if not counts_injury.empty else 0

    # ---------------------------------------- PEMROSESEN ENTITAS DEATH ---------------------------------
    # df_death = pd.read_csv('data/tabel_entitas_death.csv')
    # file_id_df_death = '1tvelEKu3mS2LV7YFOzxqv7S0-by1QB0l'  # Ganti dengan file ID kamu
    # url_df_death = f'https://drive.google.com/uc?export=download&id={file_id_df_death}'
    # response_df_death = requests.get(url_df_death)
    # df_death = pd.read_csv(io.StringIO(response_df_death.text), encoding='utf-8-sig')

    # Parsing tanggal
    df_death['DATE_STANDARDIZED'] = pd.to_datetime(df_death['DATE_STANDARDIZED'], errors='coerce')
    df_death = df_death.dropna(subset=['DATE_STANDARDIZED'])

    # Ekstrak bulan-tahun
    df_death['month_year'] = df_death['DATE_STANDARDIZED'].dt.to_period('M').astype(str)

    # Standarisasi kolom lokasi
    df_death['LOC'] = df_death['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_death_filtered = df_death.copy()
    if start_date:
        df_death_filtered = df_death_filtered[df_death_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_death_filtered = df_death_filtered[df_death_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_death_filtered = df_death_filtered[df_death_filtered['LOC'] == lokasi]

    # Hitung total death per bulan
    counts_death = (
        df_death_filtered.groupby('month_year')['DEATH_COUNT']
        .sum()
        .reset_index(name='jumlah')
    )

    jumlah_kematian = counts_death['jumlah'].sum() if not counts_death.empty else 0

    # ------------------------------------------ FORM FILTER ------------------------------------------
    # Daftar lokasi untuk dropdown (tanpa duplikat)
    locations = pd.concat([df_vehicle['LOC'], df_day['LOC']])
    locations = locations[locations.notna()]  # buang NaN
    locations = [loc.strip() for loc in locations if isinstance(loc, str) and loc.strip().lower() != 'nan' and loc.strip() != '']
    locations = sorted(set(locations))  # buang duplikat & urutkan


    # Konversi dan normalisasi filter dari user
    if start_date:
        start_date = pd.to_datetime(start_date)
    if end_date:
        end_date = pd.to_datetime(end_date)
    if lokasi:
        lokasi = lokasi.strip().lower()

    return render_template(
        'dashboard.html',
        labels_vehicle=labels_vehicle,
        data_vehicle=data_vehicle,
        labels_merk=labels_merk,
        data_merk=data_merk,
        labels_day=labels_day,
        data_day=data_day,
        labels_age=labels_age,
        data_age=data_age,
        labels_road=labels_road,
        data_road=data_road,
        labels_time=labels_time,
        data_time=data_time,
        labels_cause=labels_cause,
        data_cause=data_cause,
        jumlah_kejadian=jumlah_kejadian,
        jumlah_kematian=jumlah_kematian,
        jumlah_luka=jumlah_luka,
        lokasi_terpilih=lokasi,
        lokasi_list=locations,
        start_date=start_date,
        end_date=end_date,
        geojson_data=json.dumps(geojson_data),
        periode_laka=periode_laka,
    )


@app.route('/get_chart_date')
def get_chart_date():
    periode = request.args.get('periode', 'bulan')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    lokasi = request.args.get('lokasi')

    # df_date = pd.read_csv('data/tabel_entitas_loc.csv')
    # file_id_df_date = '1lLyT7xo0THBnvfEl8MAH663Pnzu8hDZE'  # Ganti dengan file ID kamu
    # url_df_date = f'https://drive.google.com/uc?export=download&id={file_id_df_date}'
    # response_df_date = requests.get(url_df_date)
    # df_date = pd.read_csv(io.StringIO(response_df_date.text), encoding='utf-8-sig')
    file_id_df_loc = '1lLyT7xo0THBnvfEl8MAH663Pnzu8hDZE'
    df_loc = load_csv_from_drive(file_id_df_loc)
    
    df_loc['DATE_STANDARDIZED'] = pd.to_datetime(df_loc['DATE_STANDARDIZED'], errors='coerce')
    df_loc = df_loc.dropna(subset=['DATE_STANDARDIZED'])
    df_loc['month_year'] = df_loc['DATE_STANDARDIZED'].dt.to_period('M').astype(str)
    df_loc['year'] = df_loc['DATE_STANDARDIZED'].dt.year
    df_loc['LOC'] = df_loc['LOC'].astype(str).str.strip().str.lower()
   
    df_filtered_loc = df_loc.copy()
    if start_date:
        df_filtered_loc = df_filtered_loc[df_filtered_loc['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_filtered_loc = df_filtered_loc[df_filtered_loc['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        lokasi = lokasi.strip().lower()
        df_filtered_loc = df_filtered_loc[df_filtered_loc['LOC'] == lokasi]

    if periode == 'tahun':
        counts_loc = df_filtered_loc.groupby('year').size().reset_index(name='jumlah')
        labels_date = counts_loc['year'].astype(str).tolist()
    else:
        counts_loc = df_filtered_loc.groupby('month_year').size().reset_index(name='jumlah')
        labels_date = counts_loc['month_year'].tolist()

    data_date = counts_loc['jumlah'].tolist()

    return jsonify({'labels_date': labels_date, 'data_date': data_date})

@app.route('/get_chart_injury')
def get_chart_injury():
    periode_injury = request.args.get('periode_injury', 'bulan')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    lokasi = request.args.get('lokasi')

    # df_injury = pd.read_csv('data/tabel_entitas_injury.csv')
    # file_id_df_injury = '1CPoPNFhkNQgihWhzp2CZOtpKsonKQEV7'  # Ganti dengan file ID kamu
    # url_df_injury = f'https://drive.google.com/uc?export=download&id={file_id_df_injury}'
    # response_df_injury = requests.get(url_df_injury)
    # df_injury = pd.read_csv(io.StringIO(response_df_injury.text), encoding='utf-8-sig')
    file_id_df_injury = '1CPoPNFhkNQgihWhzp2CZOtpKsonKQEV7'
    df_injury = load_csv_from_drive(file_id_df_injury)

    # Parsing tanggal
    df_injury['DATE_STANDARDIZED'] = pd.to_datetime(df_injury['DATE_STANDARDIZED'], errors='coerce')
    df_injury = df_injury.dropna(subset=['DATE_STANDARDIZED'])

    # Ekstrak bulan-tahun
    df_injury['month_year'] = df_injury['DATE_STANDARDIZED'].dt.to_period('M').astype(str)
    df_injury['year'] = df_injury['DATE_STANDARDIZED'].dt.year

    # Standarisasi kolom lokasi
    df_injury['LOC'] = df_injury['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_injury_filtered = df_injury.copy()
    if start_date:
        df_injury_filtered = df_injury_filtered[df_injury_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_injury_filtered = df_injury_filtered[df_injury_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_injury_filtered = df_injury_filtered[df_injury_filtered['LOC'] == lokasi]

    if periode_injury == 'tahun':
        counts_injury = (
            df_injury_filtered.groupby('year')['INJURY_COUNT']
            .sum()
            .reset_index(name='jumlah')
        )
        labels_injury = counts_injury['year'].tolist()
    else:
        counts_injury = (
            df_injury_filtered.groupby('month_year')['INJURY_COUNT']
            .sum()
            .reset_index(name='jumlah')
        )
        labels_injury = counts_injury['month_year'].tolist()

    data_injury = counts_injury['jumlah'].tolist()

    return jsonify({'labels_injury': labels_injury, 'data_injury': data_injury})

@app.route('/get_chart_death')
def get_chart_death():
    periode_death = request.args.get('periode_death', 'bulan')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    lokasi = request.args.get('lokasi')

    # df_death = pd.read_csv('data/tabel_entitas_death.csv')
    # file_id_df_death = '1tvelEKu3mS2LV7YFOzxqv7S0-by1QB0l'  # Ganti dengan file ID kamu
    # url_df_death = f'https://drive.google.com/uc?export=download&id={file_id_df_death}'
    # response_df_death = requests.get(url_df_death)
    # df_death = pd.read_csv(io.StringIO(response_df_death.text), encoding='utf-8-sig')

    file_id_df_death = '1tvelEKu3mS2LV7YFOzxqv7S0-by1QB0l' 
    df_death = load_csv_from_drive(file_id_df_death)

    # Parsing tanggal
    df_death['DATE_STANDARDIZED'] = pd.to_datetime(df_death['DATE_STANDARDIZED'], errors='coerce')
    df_death = df_death.dropna(subset=['DATE_STANDARDIZED'])

    # Ekstrak bulan-tahun
    df_death['month_year'] = df_death['DATE_STANDARDIZED'].dt.to_period('M').astype(str)
    df_death['year'] = df_death['DATE_STANDARDIZED'].dt.year

    # Standarisasi kolom lokasi
    df_death['LOC'] = df_death['LOC'].astype(str).str.strip().str.lower()

    # Filter berdasarkan tanggal dan lokasi
    df_death_filtered = df_death.copy()
    if start_date:
        df_death_filtered = df_death_filtered[df_death_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_death_filtered = df_death_filtered[df_death_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_death_filtered = df_death_filtered[df_death_filtered['LOC'] == lokasi]

    if periode_death == 'tahun':
        counts_death = (
            df_death_filtered.groupby('year')['DEATH_COUNT']
            .sum()
            .reset_index(name='jumlah')
        )
        labels_death = counts_death['year'].tolist()
    else:
        counts_death = (
            df_death_filtered.groupby('month_year')['DEATH_COUNT']
            .sum()
            .reset_index(name='jumlah')
        )
        labels_death = counts_death['month_year'].tolist()

    data_death = counts_death['jumlah'].tolist()

    return jsonify({'labels_death': labels_death, 'data_death': data_death})


@app.route('/generate_wordcloud_cause')
def generate_wordcloud_cause_route(): # Ubah nama fungsi agar unik
    start_date = pd.to_datetime(request.args.get('start_date')) if request.args.get('start_date') else None
    end_date = pd.to_datetime(request.args.get('end_date')) if request.args.get('end_date') else None
    lokasi = request.args.get('lokasi').strip().lower() if request.args.get('lokasi') else None

    # df_cause = pd.read_csv('data/tabel_entitas_cause.csv')
    # file_id_df_cause = '1qAxMIeLcH9zL70JShSsvHY_pBOf3eQpQ'  # Ganti dengan file ID kamu
    # url_df_cause = f'https://drive.google.com/uc?export=download&id={file_id_df_cause}'
    # response_df_cause = requests.get(url_df_cause)
    # df_cause = pd.read_csv(io.StringIO(response_df_cause.text), encoding='utf-8-sig')
    file_id_df_cause = '1qAxMIeLcH9zL70JShSsvHY_pBOf3eQpQ'
    df_cause = load_csv_from_drive(file_id_df_cause)
    df_cause['DATE_STANDARDIZED'] = pd.to_datetime(df_cause['DATE_STANDARDIZED'], errors='coerce')
    # Jangan filter 'Lainnya' di sini jika ingin tetap ada kemungkinan muncul di wordcloud
    df_cause = df_cause[df_cause['CAUSE_CATEGORY'] != 'Lainnya'] 
    df_cause['LOC'] = df_cause['LOC'].astype(str).str.strip().str.lower()

    df_cause_filtered = df_cause.copy()
    if start_date:
        df_cause_filtered = df_cause_filtered[df_cause_filtered['DATE_STANDARDIZED'] >= start_date]
    if end_date:
        df_cause_filtered = df_cause_filtered[df_cause_filtered['DATE_STANDARDIZED'] <= end_date]
    if lokasi and lokasi != 'semua':
        df_cause_filtered = df_cause_filtered[df_cause_filtered['LOC'] == lokasi]

    # Hapus 'Tidak diketahui' atau 'Lainnya' jika tidak diinginkan dalam wordcloud
    # Anda bisa menambahkan lebih banyak kata/kategori yang ingin diabaikan
    
    # Gabungkan semua CAUSE_CATEGORY menjadi satu string besar
    # Hanya ambil kategori yang valid (bukan NaN atau kosong)
    text_series = df_cause_filtered['CAUSE'].dropna().astype(str)

    factory = StopWordRemoverFactory()
    stopwords_id = set(factory.get_stop_words())

    if text_series.empty:
        text_for_wordcloud = "Tidak ada data tersedia"
    else:
        # Gabungkan semua teks penyebab jadi satu string
        all_text = ' '.join(text_series.tolist())

        # Tokenisasi dan filter stopword
        words = all_text.lower().split()
        filtered_words = [word for word in words if word not in stopwords_id and len(word) > 2]

        # Gabungkan kembali untuk WordCloud
        cleaned_text = ' '.join(filtered_words)

        wordcloud_generator = WordCloud(
            width=800, height=400, background_color='white',
            colormap='viridis', min_font_size=10
        ).generate(cleaned_text)

        img_buffer = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_generator, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return jsonify({'wordcloud_image': img_base64})

    # Jika text_for_wordcloud di-set (karena tidak ada data)
    wordcloud_generator = WordCloud(width=400, height=200, background_color='white').generate(text_for_wordcloud)
    img_buffer = io.BytesIO()
    plt.figure(figsize=(5, 2.5)) # Ukuran lebih kecil untuk teks saja
    plt.imshow(wordcloud_generator, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close() # Tutup figure
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return jsonify({'wordcloud_image': img_base64, 'message': text_for_wordcloud if text_for_wordcloud == "Tidak ada data tersedia" else None})

# @app.route('/start-scraping', methods=['POST'])
# def start_scraping():
#     query = 'kecelakaan'
#     fromdate = '01/01/2025'
#     todate = '01/01/2025'
#     jumlah = detikcom_scraping(query, fromdate, todate)
#     return jsonify({"jumlah": jumlah})

@app.route('/load-scraping-data', methods=['GET'])
def load_scraping_data():
    try:
        # df_result = pd.read_csv('data/hasil_prediksi_scraping.csv', encoding='utf-8-sig')

        # file_id = '1zWMM271sKPLeawwJ_uM_rKIVP_Di0pZS'  # Ganti dengan file ID kamu
        # url = f'https://drive.google.com/uc?export=download&id={file_id}'

        # response = requests.get(url)
        # df_result = pd.read_csv(io.StringIO(response.text), encoding='utf-8-sig')

        file_id = '1zWMM271sKPLeawwJ_uM_rKIVP_Di0pZS'
        df_result = load_csv_from_drive(file_id)

        # Ambil tanggal terbaru
        tanggal_terbaru = df_result['news_date'].max()

        data = df_result.to_dict(orient='records')
        return jsonify({
            "data": data,
            "tanggal_terbaru": tanggal_terbaru
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
# @app.route('/filter-berita-terbaru', methods=['GET'])
# def filter_berita_terbaru():
#     try:
#         df_filtered = update_relevant_news_and_filter()
#         # 3. Simpan hasil prediksi ke file baru
#         df_filtered.to_csv('data/berita_relevan_unik.csv', index=False, encoding='utf-8-sig')

#         data = df_filtered.to_dict(orient='records')
#         return jsonify(data)
#     except Exception as e:
#         return jsonify({"error": str(e)})
    
@app.route('/load-combine-news', methods=['GET'])
def load_combine_news():
    try:
        # ==================================== df_news =======================================================
        # df_news = pd.read_csv('data/dataset_berita_lengkap.csv', encoding='utf-8-sig')
        # file_id_df_news = '1HnI-nKfqtObiVQE7L7lrKNo9UQu08R6y'  # Ganti dengan file ID kamu
        # url_df_news = f'https://drive.google.com/uc?export=download&id={file_id_df_news}'
        # response_df_news = requests.get(url_df_news)
        # df_news = pd.read_csv(io.StringIO(response_df_news.text), encoding='utf-8-sig')

        file_id_df_news = '1HnI-nKfqtObiVQE7L7lrKNo9UQu08R6y' 
        df_news = load_csv_from_drive(file_id_df_news)

        # ================================= df_news_new =========================================
        # df_news_new = pd.read_csv('data/berita_relevan_unik.csv', encoding='utf-8-sig')
        # file_id_df_news_new = '1UlfTsDrnFe5M7WLzGCOHUkP7tk-2HsYx'  # Ganti dengan file ID kamu
        # url_df_news_new = f'https://drive.google.com/uc?export=download&id={file_id_df_news_new}'
        # response_df_news_new = requests.get(url_df_news_new)
        # df_news_new = pd.read_csv(io.StringIO(response_df_news_new.text), encoding='utf-8-sig')
        
        file_id_df_news_new = '1UlfTsDrnFe5M7WLzGCOHUkP7tk-2HsYx'
        df_news_new = load_csv_from_drive(file_id_df_news_new)
        
        df_news_new = df_news_new[['title','link','news_date','content','cleaned_content','cleaned_title','news_id']]

        df_news_combined = pd.concat([df_news, df_news_new], ignore_index=True)
        df_news_combined = df_news_combined.drop_duplicates(subset=['news_id'], keep='first')
        data = df_news_combined.fillna('').to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/load-extraction-news', methods=['GET'])
def load_extraction_news():
    try:
        # if os.path.exists('data/dataset_hasil_ekstraksi_berita_terbaru.csv'):
        #     df_extraction = pd.read_csv('data/dataset_hasil_ekstraksi_berita_terbaru.csv', encoding='utf-8-sig')
        # else:
        #     df_extraction = pd.read_csv('data/dataset_hasil_ekstraksi_berita.csv', encoding='utf-8-sig')
        
        # file_id_df_extraction = '1ycl0Sy5hAALWiaNCa9XI3a9ddMdPWAyU'  # Ganti dengan file ID kamu
        # url_df_extraction = f'https://drive.google.com/uc?export=download&id={file_id_df_extraction}'
        # response_df_extraction = requests.get(url_df_extraction)
        # df_extraction = pd.read_csv(io.StringIO(response_df_extraction.text), encoding='utf-8-sig')
        
        file_id_df_extraction = '1ycl0Sy5hAALWiaNCa9XI3a9ddMdPWAyU'
        df_extraction = load_csv_from_drive( file_id_df_extraction)
        
        df_extraction = df_extraction.replace({np.nan: None})

        data = df_extraction.to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/load-classification-data', methods=['GET'])
def load_classification_data():
    try:
        # if os.path.exists('data/dataset_klasifikasi_lengkap_terbaru.csv'):
        #     df_classification = pd.read_csv('data/dataset_klasifikasi_lengkap_terbaru.csv', encoding='utf-8-sig')
        # else:
        #     df_classification = pd.read_csv('data/dataset_klasifikasi_lengkap.csv', encoding='utf-8-sig')

        # file_id_df_classification = '1GKsX4CO3EasjcYQjvRJqOBORFWx-PFZ4'  # Ganti dengan file ID kamu
        # url_df_classification = f'https://drive.google.com/uc?export=download&id={file_id_df_classification}'
        # response_df_classification = requests.get(url_df_classification)
        # df_classification = pd.read_csv(io.StringIO(response_df_classification.text), encoding='utf-8-sig')

        file_id_df_classification = '1GKsX4CO3EasjcYQjvRJqOBORFWx-PFZ4'
        df_classification = load_csv_from_drive(file_id_df_classification)
        
        df_classification = df_classification.replace({np.nan: None})

        data = df_classification.to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# @app.route('/predict-ner', methods=['GET'])
# def predict_ner():
#     try:
#         i2w = {
#             0: 'B-LOC', 1: 'I-LOC',
#             2: 'B-DAY', 3: 'I-DAY',
#             4: 'B-DATE', 5: 'I-DATE',
#             6: 'B-TIME', 7: 'I-TIME',
#             8: 'B-VEHICLE', 9: 'I-VEHICLE',
#             10: 'B-MERK', 11: 'I-MERK',
#             12: 'B-CAUSE', 13: 'I-CAUSE',
#             14: 'B-ROAD', 15: 'I-ROAD',
#             16: 'B-ORG', 17: 'I-ORG',
#             18: 'B-VICTIM_AGE', 19: 'I-VICTIM_AGE',
#             20: 'B-DRIVER_AGE', 21: 'I-DRIVER_AGE',
#             22: 'B-INJURY', 23: 'I-INJURY',
#             24: 'B-DEATH', 25: 'I-DEATH',
#             26: 'O'
#         }
#         # Load Model
#         save_path = "app/model/indobert_large"
#         tokenizer = BertTokenizer.from_pretrained(save_path)
#         model = BertForWordClassification.from_pretrained(save_path)
#         model.eval()

#         df_unik = pd.read_csv('data/berita_relevan_unik.csv', encoding='utf-8-sig')
       
#         start_counter = df_unik.get('start_counter', 21606)
#         df_ner = prediksi_ner(df_unik, start_counter=start_counter, model=model, tokenizer=tokenizer, i2w=i2w)
#         df_ner.to_csv('data/hasil_prediksi_ner.csv', index=False, encoding='utf-8-sig')

#         df_mapping = extract_all_entities(df_ner)
#         df_process_date = process_dates(df_mapping, df_unik)
#         df_normalize_location = normalize_location(df_process_date)
#         df_normalize_location.to_csv('data/hasil_ekstraksi_berita.csv', index=False, encoding='utf-8-sig')

#         # Gabung Dataframe
#         df_all_extraction = pd.read_csv('data/dataset_hasil_ekstraksi_berita.csv', encoding='utf-8-sig')
#         df_all_extraction = pd.concat([df_all_extraction, df_normalize_location], ignore_index=True)
#         df_all_extraction = df_all_extraction.drop_duplicates(subset=['news_id'], keep='first')
#         df_all_extraction.to_csv('data/dataset_hasil_ekstraksi_berita_terbaru.csv', index=False, encoding='utf-8-sig')
#         # Ubah hasil jadi list dict JSON-able
#         result = df_all_extraction.to_dict(orient='records')
#         return jsonify({'result': result})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/full-pipeline', methods=['POST'])
# def full_pipeline():
#     try:
#         # 1. Scraping
#         query = 'kecelakaan'
#         fromdate = '01/01/2025'
#         todate = '12/07/2025'
#         jumlah = detikcom_scraping(query, fromdate, todate)

#         # 2. Preprocessing dan prediksi relevansi
#         df_preprocess = load_and_clean_data('data/hasil_scraping.csv')
#         df_preprocess.to_csv('data/hasil_scraping_preprocessing.csv', index=False, encoding='utf-8-sig')

#         df_result = predict_sentiment_from_file('data/hasil_scraping_preprocessing.csv')
#         df_result.to_csv('data/hasil_prediksi_scraping.csv', index=False, encoding='utf-8-sig')

#         # 3. Filter berita terbaru
#         df_filtered = update_relevant_news_and_filter()
#         df_filtered.to_csv('data/berita_relevan_unik.csv', index=False, encoding='utf-8-sig')

#         # 4. Gabungkan dengan dataset lama
#         df_news = pd.read_csv('data/dataset_berita_lengkap.csv', encoding='utf-8-sig')
#         df_news_new = df_filtered[['title', 'link', 'news_date', 'content', 'cleaned_content', 'cleaned_title', 'news_id']]
#         df_news_combined = pd.concat([df_news, df_news_new], ignore_index=True)
#         df_news_combined = df_news_combined.drop_duplicates(subset=['news_id'], keep='first')
#         df_news_combined.to_csv('data/dataset_berita_lengkap_terbaru.csv', index=False, encoding='utf-8-sig')

#         # 5. Prediksi NER
#         i2w = {
#             0: 'B-LOC', 1: 'I-LOC', 2: 'B-DAY', 3: 'I-DAY', 4: 'B-DATE', 5: 'I-DATE',
#             6: 'B-TIME', 7: 'I-TIME', 8: 'B-VEHICLE', 9: 'I-VEHICLE', 10: 'B-MERK', 11: 'I-MERK',
#             12: 'B-CAUSE', 13: 'I-CAUSE', 14: 'B-ROAD', 15: 'I-ROAD', 16: 'B-ORG', 17: 'I-ORG',
#             18: 'B-VICTIM_AGE', 19: 'I-VICTIM_AGE', 20: 'B-DRIVER_AGE', 21: 'I-DRIVER_AGE',
#             22: 'B-INJURY', 23: 'I-INJURY', 24: 'B-DEATH', 25: 'I-DEATH', 26: 'O'
#         }

#         save_path = "app/model/indobert_large"
#         tokenizer = BertTokenizer.from_pretrained(save_path)
#         model = BertForWordClassification.from_pretrained(save_path)
#         model.eval()

#         # Load berita terbaru yang ingin diproses
#         df_unik = pd.read_csv('data/berita_relevan_unik.csv', encoding='utf-8-sig')

#         # Load base: jika file terbaru belum ada, pakai dataset awal
#         if os.path.exists('data/dataset_hasil_ekstraksi_berita_terbaru.csv'):
#             df_base = pd.read_csv('data/dataset_hasil_ekstraksi_berita_terbaru.csv', encoding='utf-8-sig')
#         else:
#             df_base = pd.read_csv('data/dataset_hasil_ekstraksi_berita.csv', encoding='utf-8-sig')

#         # Cari berita yang belum pernah diproses
#         existing_ids = set(df_base['news_id'])
#         df_unik_new = df_unik[~df_unik['news_id'].isin(existing_ids)]

#         # Prediksi jika ada berita baru
#         if not df_unik_new.empty:
#             start_counter = df_unik.get('start_counter', 21606)
#             df_ner = prediksi_ner(df_unik_new, start_counter=start_counter, model=model, tokenizer=tokenizer, i2w=i2w)
#             df_ner.to_csv('data/hasil_prediksi_ner.csv', index=False, encoding='utf-8-sig')

#             df_mapping = extract_all_entities(df_ner)
#             df_process_date = process_dates(df_mapping, df_unik_new)
#             df_new_extraction = normalize_location(df_process_date)
#             df_new_extraction.to_csv('data/hasil_ekstraksi_berita_baru.csv', index=False, encoding='utf-8-sig')

#             df_classification_new = df_new_extraction.copy()
#             df_classification_new = df_classification_new[["DATE_STANDARDIZED","DAY","TIME","VEHICLE","ROAD","CAUSE","DRIVER_AGE","DEATH"]]
#             df_classification_new = grouping_day(df_classification_new)
#             df_classification_new = df_classification_new[["DAY","TIME","VEHICLE","ROAD","CAUSE","DRIVER_AGE","DEATH"]]
#             df_classification_new = grouping_time(df_classification_new)
#             df_classification_new = grouping_vehicle(df_classification_new)
#             df_classification_new = grouping_road(df_classification_new)
#             df_classification_new = grouping_cause(df_classification_new)
#             df_classification_new = grouping_driver_age(df_classification_new)
#             df_classification_new = grouping_death(df_classification_new)
#             df_classification_new = finalisasi_dataset(df_classification_new)
#             df_classification_new.to_csv('data/data_baru_klasifikasi.csv', index=False, encoding='utf-8-sig')

#             if os.path.exists('data/dataset_klasifikasi_lengkap_terbaru.csv'):
#                 df_classification_lengkap = pd.concat([pd.read_csv('data/dataset_klasifikasi_lengkap_terbaru.csv', encoding='utf-8-sig'), df_classification_new], ignore_index=True)
#             else:
#                 df_classification_lengkap = pd.concat([pd.read_csv('data/dataset_klasifikasi_lengkap.csv', encoding='utf-8-sig'), df_classification_new], ignore_index=True)

#             df_classification_lengkap.to_csv('data/dataset_klasifikasi_lengkap_terbaru.csv', index=False, encoding='utf-8-sig')
#             # Gabungkan hasil baru dengan data base
#             df_combined = pd.concat([df_base, df_new_extraction], ignore_index=True)
#         else:
#             df_combined = df_base.copy()

#         # Bersihkan berita tahun sekarang yang tidak ada lagi di df_unik
#         current_year = datetime.now().year
#         df_combined['DATE_STANDARDIZED'] = pd.to_datetime(df_combined['DATE_STANDARDIZED'], errors='coerce')
#         df_final = df_combined[
#             ~((df_combined['DATE_STANDARDIZED'].dt.year == current_year) &
#             (~df_combined['news_id'].isin(df_unik['news_id'])))
#         ]

#         # Simpan hasil akhir (overwrite file terbaru)
#         df_final.to_csv('data/dataset_hasil_ekstraksi_berita_terbaru.csv', index=False, encoding='utf-8-sig')

#         #df_final = pd.read_csv('data/dataset_hasil_ekstraksi_berita.csv', encoding='utf-8-sig')

#         tabel_day = entitas_day(df_final)
#         tabel_day.to_csv('data/tabel_entitas_day.csv', index=False, encoding='utf-8-sig')

#         tabel_time = entitas_time(df_final)
#         tabel_time.to_csv('data/tabel_entitas_time.csv', index=False, encoding='utf-8-sig')

#         tabel_loc = entitas_loc(df_final)
#         tabel_loc.to_csv('data/tabel_entitas_loc.csv', index=False, encoding='utf-8-sig')

#         tabel_vehicle = entitas_vehicle(df_final)
#         tabel_vehicle.to_csv('data/tabel_entitas_vehicle.csv', index=False, encoding='utf-8-sig')

#         tabel_merk = entitas_merk(df_final)
#         tabel_merk.to_csv('data/tabel_entitas_merk.csv', index=False, encoding='utf-8-sig')

#         tabel_road = entitas_road(df_final)
#         tabel_road.to_csv('data/tabel_entitas_road.csv', index=False, encoding='utf-8-sig')

#         tabel_cause = entitas_cause(df_final)
#         tabel_cause.to_csv('data/tabel_entitas_cause.csv', index=False, encoding='utf-8-sig')

#         tabel_age = entitas_age(df_final)
#         tabel_age.to_csv('data/tabel_entitas_age.csv', index=False, encoding='utf-8-sig')

#         tabel_injury = entitas_injury(df_final)
#         tabel_injury.to_csv('data/tabel_entitas_injury.csv', index=False, encoding='utf-8-sig')

#         tabel_death = entitas_death(df_final)
#         tabel_death.to_csv('data/tabel_entitas_death.csv', index=False, encoding='utf-8-sig')

#         # if os.path.exists('data/dataset_klasifikasi_lengkap_terbaru.csv'):
#         #     prediksi_laka_lantas('data/dataset_klasifikasi_lengkap_terbaru.csv')  
#         # else:
#         #     prediksi_laka_lantas('data/dataset_klasifikasi_lengkap.csv')

#         return jsonify({'status': 'success', 'scraped': jumlah})
#     except Exception as e:
#         traceback.print_exc()  # ✅ Ini akan print error lengkap ke terminal
#         return jsonify({'error': str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Port default Railway
    app.run(host="0.0.0.0", port=port, debug=False)
