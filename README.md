# Brawl Stars Pick Bot

Brawl Stars **Ranked** modu için harita bazlı pick önerisi, ban adayı ve rakip takıma karşı counter önerisi sunan bir Python aracı. Veriler, resmi Brawl Stars API'sinden toplanan gerçek ranked maçlarından hesaplanır.

> Bu proje bir hayran/öğrenci projesidir. Supercell ile bağlantısı yoktur, Supercell tarafından onaylanmamıştır.

## Ne yapar?

- Seçtiğin haritada hangi brawler'ların daha iyi kazandığını gösterir (ban adayları).
- Rakip takımın seçtiği brawler'lara karşı hangi brawler'ların avantajlı olduğunu hesaplar.
- Her öneride puanın kaç maçtan geldiğini gösterir, böylece az veriye dayanan öneriler fark edilir.
- Önerilerin gerçekten işe yarayıp yaramadığını `backtest.py` ile ölçer.

## Nasıl çalışır?

1. **Veri toplama (`collector.py`):** Resmi API'den oyuncuların son maçları (battle log) çekilir. Sadece `soloRanked` maçları alınır, aynı maç tekrar sayılmaz. Her maçtan çıkan yeni oyuncu tag'leri sıraya eklenir, böylece veri havuzu kendiliğinden büyür. Maçlar yerel bir SQLite veritabanına (`matches.db`) kaydedilir.
2. **İstatistik (`build_data.py`):** Veritabanından her harita için brawler kazanma oranlarını ve her brawler çiftinin birbirine karşı kazanma oranını hesaplar. Az maçlı sonuçların aşırı güçlü görünmemesi için yumuşatılmış kazanma oranı kullanılır. Puan, yumuşatılmış kazanma oranının %50'den farkıdır (örneğin `+8` kabaca %58 demektir). Sonuç `data.json` dosyasına yazılır.
3. **Öneri (`main.py`):** Harita, ban'lar, kendi takımın ve rakip brawler'lar girilince her aday için `harita puanı + rakiplere karşı toplam counter puanı` hesaplanır ve en iyi pick'ler sıralanır.
4. **Geri-test (`backtest.py`):** Maçlar zamana göre ikiye bölünür. Eski kısımdan tablolar hesaplanır, yeni kısımda "puanı yüksek çıkan takım gerçekten kazandı mı?" diye bakılır.

## Kurulum

Gereksinimler: Python 3.9+ ve `requests` kütüphanesi.

```bash
git clone https://github.com/KULLANICI_ADIN/brawl-stars-pick-bot.git
cd brawl-stars-pick-bot
pip install requests
```

### API anahtarı

1. [developer.brawlstars.com](https://developer.brawlstars.com) adresinde Supercell ID ile giriş yap.
2. Yeni bir anahtar oluştur. IP adresi olarak **genel (public) IPv4** adresini gir. Anahtar sadece bu IP'den çalışır, IP'n değişirse yeni anahtar gerekir.
3. Anahtarı kod dosyalarına yazma, ortam değişkeni olarak tanıt:

```powershell
# Windows PowerShell
$env:BS_TOKEN="anahtarın"
```

```bash
# Mac / Linux
export BS_TOKEN="anahtarın"
```

## Kullanım

```bash
# 1. Maç verisi topla (başlangıç tag'i boş bırakılırsa kayıtlı oyuncularla devam eder)
python collector.py

# 2. İstatistikleri hesapla ve data.json'u üret
python build_data.py

# 3. Öneri al
python main.py

# 4. Önerilerin isabetini ölç
python backtest.py
```

İlk çalıştırmada `collector.py` senden birkaç başlangıç oyuncu tag'i (örneğin `#ABC123`) ve taranacak oyuncu sayısını ister. Veri ne kadar çoksa öneriler o kadar güvenilir olur; başlangıç için birkaç yüz oyuncu ve birkaç bin maç iyi bir hedeftir.

## Dosya yapısı

| Dosya | Görevi |
|---|---|
| `fetch_log.py` | Tek bir oyuncunun battle log'unu API'den çeker ve ekrana yazar. |
| `ham_log.py` | Ham API cevabını incelemek için yardımcı betik. |
| `collector.py` | Birçok oyuncunun maçlarını toplayıp SQLite'a kaydeder. |
| `build_data.py` | Veritabanından harita ve counter istatistiklerini hesaplar. |
| `main.py` | Komut satırından pick ve ban önerisi verir. |
| `backtest.py` | Öneri mantığını zamana göre ayrılmış maçlarda test eder. |
| `data.json` | Hesaplanan istatistikler (`build_data.py` üretir). |

## Sınırlamalar

- API, oyuncu başına sadece son birkaç maçı verir. Veri ancak düzenli toplama ile birikir.
- Battle log'da ban bilgisi görünmüyor. Ban önerisi bu yüzden haritadaki brawler gücüne dayanır.
- Maç sonuçları takım koordinasyonu ve oyuncu becerisinden çok etkilenir. Araç bir yardımcıdır, kesin sonuç vermez.
- Oyun güncellemeleri dengeyi değiştirir, eski maçlar yanıltıcı olabilir.
- Az maça dayanan counter değerleri güvenilmezdir, bu yüzden öneriler maç sayısıyla birlikte gösterilir.

## Yol haritası

- [ ] Verinin düzenli ve otomatik toplanması
- [ ] Sadece son haftaların maçlarıyla hesaplama
- [ ] Takım arkadaşı uyumu (sinerji) puanı
- [ ] Oyuncunun sahip olduğu brawler'lara göre kişisel öneri
- [ ] Discord botu veya web arayüzü
- [ ] Sınıflara bölünmüş kod yapısı ve birim testleri

## Güvenlik notu

API anahtarını asla repoya yükleme. Bu projede anahtar yalnızca `BS_TOKEN` ortam değişkeninden okunur. `matches.db` dosyası `.gitignore` ile repo dışında tutulur.****
