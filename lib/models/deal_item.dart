class DealItem {
  final String id;
  final String title;
  final double originalPrice;
  final double discountedPrice;
  final int discountRate; // e.g. 55 for %55
  final String imageUrl;
  final String productUrl;
  final String store; // 'Amazon TR', 'Hepsiburada', 'Idefix'
  final String category; // 'Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik', 'Kitap & Hobi'
  final DateTime createdAt;
  bool isFavorite;

  DealItem({
    required this.id,
    required this.title,
    required this.originalPrice,
    required this.discountedPrice,
    required this.discountRate,
    required this.imageUrl,
    required this.productUrl,
    required this.store,
    required this.category,
    required this.createdAt,
    this.isFavorite = false,
  });

  static String sanitizeCategory(String rawCategory, String title) {
    final lower = title.toLowerCase();

    // SADECE ve KESİNLİKLE Teknoloji kategorisini saflaştırma kuralı:
    // Eğer bir ürün "Teknoloji" olarak etiketlenmişse ama aslında kozmetik, giyim veya züccaciye ise
    // ASLA Teknoloji listesinde gösterilmez!
    if (rawCategory == 'Teknoloji') {
      const nonTechKeywords = [
        'krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea',
        'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan',
        'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik',
        'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya',
        'yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt',
        'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı',
        'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik',
        'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'buzluk', 'cooler'
      ];

      for (final kw in nonTechKeywords) {
        if (lower.contains(kw)) {
          // Kozmetik anahtar kelimeleri
          if (['krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena', 'parfüm', 'parfum', 'şampuan', 'cilt'].any(lower.contains)) {
            return 'Kozmetik';
          }
          // Giyim anahtar kelimeleri
          if (['yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 'tişört', 'kazak', 'ayakkabı', 'bot', 'çorap', 'ceket'].any(lower.contains)) {
            return 'Moda';
          }
          return 'Ev & Yaşam';
        }
      }
    }

    return rawCategory.isNotEmpty ? rawCategory : 'Genel';
  }

  factory DealItem.fromJson(Map<String, dynamic> json) {
    final rawTitle = json['title'] as String? ?? '';
    final rawCategory = json['category'] as String? ?? 'Genel';

    return DealItem(
      id: json['id'] as String? ?? '',
      title: rawTitle,
      originalPrice: (json['originalPrice'] as num?)?.toDouble() ?? 0.0,
      discountedPrice: (json['discountedPrice'] as num?)?.toDouble() ?? 0.0,
      discountRate: (json['discountRate'] as num?)?.toInt() ?? 50,
      imageUrl: json['imageUrl'] as String? ?? '',
      productUrl: json['productUrl'] as String? ?? '',
      store: json['store'] as String? ?? 'Mağaza',
      category: sanitizeCategory(rawCategory, rawTitle),
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now()
          : DateTime.now(),
      isFavorite: json['isFavorite'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'originalPrice': originalPrice,
      'discountedPrice': discountedPrice,
      'discountRate': discountRate,
      'imageUrl': imageUrl,
      'productUrl': productUrl,
      'store': store,
      'category': category,
      'createdAt': createdAt.toIso8601String(),
      'isFavorite': isFavorite,
    };
  }

  String get formattedOriginalPrice =>
      '${originalPrice.toStringAsFixed(originalPrice.truncateToDouble() == originalPrice ? 0 : 2).replaceAll('.', ',')} TL';

  String get formattedDiscountedPrice =>
      '${discountedPrice.toStringAsFixed(discountedPrice.truncateToDouble() == discountedPrice ? 0 : 2).replaceAll('.', ',')} TL';

  String get timeAgo {
    final diff = DateTime.now().difference(createdAt);
    if (diff.inMinutes < 60) {
      return '${diff.inMinutes < 1 ? 1 : diff.inMinutes} dk önce';
    } else if (diff.inHours < 24) {
      return '${diff.inHours} saat önce';
    } else {
      return '${diff.inDays} gün önce';
    }
  }
}
