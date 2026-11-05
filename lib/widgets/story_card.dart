import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:share_plus/share_plus.dart';
import '../models/deal_item.dart';
import 'store_logo.dart';

class StoryCard extends StatelessWidget {
  final DealItem deal;
  final VoidCallback? onToggleFavorite;
  final VoidCallback onOpenLink;

  const StoryCard({
    super.key,
    required this.deal,
    this.onToggleFavorite,
    required this.onOpenLink,
  });

  void _shareDeal(BuildContext context) {
    Share.share(
      '🔥 %${deal.discountRate} İNDİRİM YAKALANDI!\n\n'
      '${deal.title}\n'
      'Eski Fiyat: ${deal.formattedOriginalPrice}\n'
      'İndirimli Fiyat: ${deal.formattedDiscountedPrice}\n\n'
      'Fırsatı Yakala: ${deal.productUrl}',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFFF1F2F6),
      child: Column(
        children: [
          // 1. Üst Boşluk (İlerleme çubuğu ve kategori hapları için güvenli alan)
          const SizedBox(height: 52),

          // 2. Ürün Görseli (Ekran Sınırları İçinde - Daha Geniş Alan)
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              child: Material(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                elevation: 2,
                shadowColor: Colors.black.withValues(alpha: 0.08),
                child: InkWell(
                  onTap: onOpenLink,
                  borderRadius: BorderRadius.circular(20),
                  splashColor: const Color(0xFFFF4757).withValues(alpha: 0.1),
                  highlightColor:
                      const Color(0xFFFF4757).withValues(alpha: 0.05),
                  child: Stack(
                    children: [
                      // Ürün Görseli
                      Positioned.fill(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(16),
                            child: CachedNetworkImage(
                              imageUrl: deal.imageUrl,
                              fit: BoxFit.contain,
                              alignment: Alignment.center,
                              placeholder: (context, url) => const Center(
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Color(0xFFFF4757),
                                ),
                              ),
                              errorWidget: (context, url, error) => Container(
                                color: Colors.grey[100],
                                child: const Center(
                                  child: Icon(
                                    Icons.broken_image_rounded,
                                    size: 64,
                                    color: Colors.grey,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      // Sağ Üst: Mağazada Gör Rozeti
                      Positioned(
                        top: 10,
                        right: 10,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.06),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                'Mağazada Gör',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF747D8C),
                                ),
                              ),
                              SizedBox(width: 3),
                              Icon(
                                Icons.open_in_new_rounded,
                                size: 11,
                                color: Color(0xFF747D8C),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // 3. Alt Detaylar Kartı (İndirim Rozeti, Başlık, Fiyat + Paylaş & Mağaza Butonu)
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(left: 14, right: 14, bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.08),
                  blurRadius: 12,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                // İndirim Oranı Rozeti & Mağaza Logosu
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFF3838), Color(0xFFFF4757)],
                        ),
                        borderRadius: BorderRadius.circular(8),
                        boxShadow: [
                          BoxShadow(
                            color:
                                const Color(0xFFFF3838).withValues(alpha: 0.35),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text('🔥 ', style: TextStyle(fontSize: 13)),
                          Text(
                            '%${deal.discountRate} İNDİRİM',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w900,
                              fontSize: 14,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    StoreLogo(store: deal.store),
                  ],
                ),
                const SizedBox(height: 8),

                // Ürün Başlığı (Okunaklı & 2 Satır)
                Text(
                  deal.title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Color(0xFF1E272E),
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 10),

                // Fiyat Alanı + Sağda Kompakt Paylaş Butonu (Seçenek B)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      child: FittedBox(
                        fit: BoxFit.scaleDown,
                        alignment: Alignment.centerLeft,
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.baseline,
                          textBaseline: TextBaseline.alphabetic,
                          children: [
                            // İndirimli Tutar
                            Text(
                              deal.formattedDiscountedPrice,
                              style: const TextStyle(
                                color: Color(0xFF00823B),
                                fontSize: 28,
                                fontWeight: FontWeight.w900,
                                letterSpacing: -0.5,
                              ),
                            ),
                            const SizedBox(width: 10),
                            // Eski Fiyat (Üstü Çizili)
                            Text(
                              deal.formattedOriginalPrice,
                              style: const TextStyle(
                                color: Color(0xFF747D8C),
                                fontSize: 15,
                                decoration: TextDecoration.lineThrough,
                                decorationColor: Color(0xFFFF4757),
                                decorationThickness: 2.2,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),

                    // Paylaş Butonu (Fiyat Satırının Sağında - Seçenek B)
                    InkWell(
                      onTap: () => _shareDeal(context),
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F2F6),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color:
                                const Color(0xFF2D3436).withValues(alpha: 0.1),
                          ),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.share_outlined,
                              color: Color(0xFF2D3436),
                              size: 17,
                            ),
                            SizedBox(width: 5),
                            Text(
                              'Paylaş',
                              style: TextStyle(
                                color: Color(0xFF2D3436),
                                fontWeight: FontWeight.w800,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // 4. FIRSATI YAKALA • MAĞAZADA AÇ
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: onOpenLink,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1E272E),
                      foregroundColor: Colors.white,
                      elevation: 3,
                      shadowColor: Colors.black.withValues(alpha: 0.3),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                    ),
                    child: FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.keyboard_double_arrow_up_rounded,
                            color: Color(0xFFFFD32A),
                            size: 22,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'FIRSATI YAKALA  •  ${deal.store.toUpperCase()}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.4,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                const Center(
                  child: Text(
                    'Fiyatlar periyodik çekilir, mağaza sepet fiyatı geçerlidir.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xFFA4B0BE),
                      fontSize: 10.5,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
