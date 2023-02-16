import re
import nltk
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns
import base64

from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from flask import Flask, request, render_template, request, redirect
from io import BytesIO

nltk.download('punkt')


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['FILE_UPLOADS'] = "c:/GC/uploads"

#===================================================
with open('c:/GC/data/new_kamusalay.csv', encoding = 'latin-1', mode='r') as infile:
    reader = csv.reader(infile)
    ids = {rows[0]:rows[1] for rows in reader}
    
#Fungsi untuk mengubah teks menjadi huruf kecil untuk memudahkan proses cleaning
def casefolding(review):
    review = str(review).lower()
    return review

#Fungsi untuk memproses pemisahan teks menjadi potongan-potongan yang disebut sebagai token untuk kemudian di analisa
def tokenize(review):
    #token = nltk.word_tokenize(str(review))
    token = nltk.tokenize.word_tokenize(review)
    return token

#Fungsi untuk menghilangkan angka, karakter aneh dan kata yang tidak diperlukan
def filtering(review):
    # Remove angka termasuk angka yang berada dalam string
    # Remove non ASCII chars
    review = re.sub(r'[^\x00-\x7f]', r'', review)
    review = re.sub(r'(\\u[0-9A-Fa-f]+)', r'', review)
    review = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", review)
    review = re.sub(r'\\u\w\w\w\w', '', review)
    # Remove link web
    review = re.sub(r'http\S+', '', review)
    # Remove URL
    review = re.sub(r'url', '', review)
    # Remove RT USER
    review = re.sub(r'rt user', '', review)
    # Remove USER
    review = re.sub(r'user', '', review)
    # Remove @username
    review = re.sub('@[^\s]+', '', review)
    # Remove #tagger
    review = re.sub(r'#([^\s]+)', '', review)
    # Remove simbol, angka dan karakter aneh
    review = re.sub(r"[.,:;+!\-_<^/=?\"'\(\)\d\*]", " ", review)
    return review

#Fungsi untuk menghilangkan karakter yang lebih dari 1 menjai cukup 1 karakter
def replaceThreeOrMore(review):
    # Pattern to look for three or more repetitions of any character, including newlines (contoh goool -> gol).
    pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
    return pattern.sub(r"\1", review)

#Fungsi untuk mengubah kata-kata sesuai dengan kamus yang diberikan
def convertToSlangword(review):
    kamus_slangword = ids
    # Search pola kata (contoh kpn -> kapan)
    pattern = re.compile(r'\b( ' + '|'.join (kamus_slangword.keys())+r')\b') 
    content = []
    # Replace slangword berdasarkan pola review yg telah ditentukan
    for kata in review:
        filteredSlang = pattern.sub(lambda x: kamus_slangword[x.group()],kata) 
        content.append(filteredSlang.lower())
    review = content
    return review

#Fungsi untuk menghilangkan kata yang hanya terdiri dari konsonan / tidak berarti
def removeNoVowelWord(review):
    vowel = ['a','e','i','o','u'] 
    review = [word for word in review if any(v in word for v in vowel)]
    return review

#Fungsi untuk mengambil kata dasar dengan menghilangkan awal, akhiran dan sisipan dalam bahasa indonesia menggunakan library Sastrawi
def stemmer(review):
    # create stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    # stemming process
    review   = stemmer.stem(str(review))
    return review

#Fungsi untuk menghilangkan kata sambung yang tidak diperlukan untuk dianalisa
def removeStopWordIndo(review):
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    review = stopword.remove(str(review))
    return review

#Fungsi untuk membuat grafik word cloud dengan menggunakan Matplotlib
def wordcloud(review,namafile):
    # Create and generate a word cloud image:
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(review)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    # Save the image in the images folder:
    namafile = namafile + '.png'
    imagePath = ''
    imagePath = os.path.join('static',namafile)
    wordcloud.to_file(imagePath)
    return imagePath

#Fungsi yang digunakan untuk menghitung kata berulang dan menyimpannya ke dalam database sqlite
def word_count(str):
    # Count the number of occurrences of each word in the string
    counts = {}
    words = str.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    # Connect to the database
    conn = sqlite3.connect('teks.db')
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teksstat'")
    table_exists = bool(cursor.fetchone())

    if not table_exists:
        # Create the table if it doesn't exist
        cursor.execute("CREATE TABLE teksstat(kata text, jumlah integer)")

    try:
        cursor.execute("DROP TABLE teksstat")
        cursor.execute("CREATE TABLE teksstat(kata text, jumlah integer)")
        # Insert records into the table
        for word, count in counts.items():
            cursor.execute("INSERT INTO teksstat (kata, jumlah) VALUES (?, ?)", (word, count))
        conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)

    # Close the database connection
    conn.close()
    return

#fungsi untuk menampilkan grafik perulangan kata dengan menggunakan seaborn
def show_barchart():
    # Connect to the database
    conn = sqlite3.connect('teks.db')

    # Read the data from the teksstat table into a pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM teksstat ORDER BY jumlah DESC LIMIT 5", conn)

    # Close the database connection
    conn.close()

    # Create a bar chart using Seaborn
    sns.set_style('whitegrid')
    plt.figure(figsize=(6, 4))
    sns.barplot(x='kata', y='jumlah', data=df)
    plt.title('5 Kata yang sering muncul dari Teks Bersih')
    plt.xlabel('Kata')
    plt.ylabel('Jumlah')

    # Convert the plot to a PNG image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the PNG image in base64 for embedding in the HTML
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url 

#===================================================

# Routing Home menampilkan dua tombol untuk memilih apakah akan mengcleaning teks atau file
@app.route('/')
def index():
    return render_template('index.html')

# Routing Cleaning text menampilkan Scrollbox untuk inputan teks
@app.route('/cleaningtext')
def text_input():
    return render_template('indextext.html')

# Routing Cleaning text untuk memproses dan menampilkan hasil cleaning teks
@app.route('/cleaningtext', methods=["POST"])
def text_clean():
    # Mulai mengambil data dari form dan melakukan cleaning teks
    teks_asli = [request.form['note']]
    teks = casefolding(teks_asli)
    teks = filtering(teks)
    teks = replaceThreeOrMore(teks)
    teks = tokenize(teks)
    teks = convertToSlangword(teks)
    teks = removeNoVowelWord(teks)
    teks = ' '.join(teks)
    teks = stemmer(teks)
    teks = removeStopWordIndo(teks)

    #Menampilkan word cloud dengan mengcreate wordcloud dari teks dan mengembalikan path gambar word cloud untuk ditampilkan
    tekswc = wordcloud(teks,'teksbersih')
    teks_asli = ' '.join(teks_asli)
    teksasliwc = wordcloud(teks_asli,'teksasli')
    #hitung kata, masukkan ke sqlite database
    word_count(teks)
    plot_url = show_barchart()
    return render_template('hasilbersih.html', note_asli=teks_asli, note_hasil=teks, wordcloudbersih=tekswc, wordcloudasli=teksasliwc, plot_url=plot_url)
    
@app.route('/cleaningfile', methods=["GET","POST"])
def get_file():
    if request.method == 'POST':
        if request.files:
            uploaded_file = request.files['filename'] # This line uses the same variable and worked fine
            filepath = os.path.join(app.config['FILE_UPLOADS'], uploaded_file.filename)
            uploaded_file.save(filepath)
            df = pd.read_csv(filepath,encoding='latin1')
            jumlahrecord = request.form['jmlrecord']
            namakolom = request.form['namakolom']
            datasets = [df.head(int(jumlahrecord))]
            # Tampilkan Data Frame dalam bentuk tabel
            # return render_template('hasilfiletablebersih.html', tables=[df.head().to_html(classes='data')], titles=df.head().columns.values)
            # Keeping only the neccessary columns
            for teks in datasets:
                teks_asli = teks[namakolom].astype("string") 
                teks = teks[namakolom]
                teks = teks.apply(casefolding)
                teks = teks.apply(filtering)
                teks = teks.apply(replaceThreeOrMore)
                teks = teks.apply(tokenize)
                teks = teks.apply(convertToSlangword)
                teks = teks.apply(removeNoVowelWord)
                teks = teks.apply(" ".join)
                teks = teks.apply(stemmer)
                teks = teks.apply(removeStopWordIndo)
            teks = ' '.join(teks)
            teks_asli = ' '.join(teks_asli)
            # Menampilkan word cloud dengan mengcreate wordcloud dari teks dan mengembalikan path gambar word cloud untuk ditampilkan
            tekswc = wordcloud(teks,'teksbersih')
            teksasliwc = wordcloud(teks,'teksasli')
            #hitung kata, masukkan ke sqlite database
            word_count(teks)
            plot_url = show_barchart()
            return render_template('hasilfilebersih.html',note_asli=teks_asli, note_hasil=teks, wordcloudbersih=tekswc, wordcloudasli=teksasliwc, plot_url=plot_url)

    return render_template('indexfile.html')

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(debug=True)
