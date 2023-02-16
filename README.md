# gold_challange_andrie
Gold Challange - API Cleansing Teks Menggunakan Python, Flask, SQLite, Sastrawi, MatPlotLib, Seaborn
Metode cleansing teks dan visualisasi hasil yang digunakan dalam Gold Challange ini adalah :

Cleansing Teks
1. Mengubah huruf teks agar semua menjadi huruf kecil dengan function casefolding
2. Melakukan filtering untuk menghilangkan karakter angka, simbol dan kata yang tidak dibutuhkan dengan function filtering
3. Melakukan tokenisasi(pemisahan kata) dengan fungsi tokenize
4. Mengubah kata-kata yang tidak sesuai/kata kotor dan juga typo dari referensi kamusalay.csv dengan fungsi convertToSlangword
5. Menghapus kata yang tidak memiliki huruf vokal(tidak punya arti) dengan fungsi removeNoVowelWord
6. Mengambil kata dasar dengan melakukan stemming menggunakan library Sastrawi dengan fungsi stemmer
7. Menghilangkan kata stopword dalam bahasa indonesia yang tidak dimasukkan dalam analisa menggunakan library Sastrawi dengan fungsi removeStopWordIndo

Visualisasi Hasil
1. Menampilkan hasil berupa teks yang sudah dilakukan cleansing
2. Menampilkan word cloud teks asli dan teks yang sudah di cleansing dengan library MatPlotLib
3. Menampilkan grafik 5 kata terbanyak dari teks yang sudah dicleansing dengan library Seaborn
