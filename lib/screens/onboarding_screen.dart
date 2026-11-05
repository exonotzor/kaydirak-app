import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import '../services/analytics_service.dart';
import 'story_feed_screen.dart';

class OnboardingSlide {
  final int id;
  final String badge;
  final String title;
  final String subtitle;
  final String imageUrl;

  const OnboardingSlide({
    required this.id,
    required this.badge,
    required this.title,
    required this.subtitle,
    required this.imageUrl,
  });

  factory OnboardingSlide.fromJson(Map<String, dynamic> json) {
    return OnboardingSlide(
      id: (json['id'] as num?)?.toInt() ?? 1,
      badge: json['badge'] as String? ?? 'KAYDIRAK',
      title: json['title'] as String? ?? '',
      subtitle: json['subtitle'] as String? ?? '',
      imageUrl: json['imageUrl'] as String? ?? '',
    );
  }
}

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  static const String _remoteConfigApiUrl =
      'https://api.github.com/repos/exonotzor/kaydirak-app/contents/assets/data/onboarding_config.json';
  static const String _remoteConfigRawUrl =
      'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/data/onboarding_config.json';

  late List<OnboardingSlide> _slides;
  late final int _cacheBuster;

  @override
  void initState() {
    super.initState();
    _cacheBuster = DateTime.now().millisecondsSinceEpoch;
    _slides = _defaultSlides();
    _fetchRemoteSlides();
  }

  List<OnboardingSlide> _defaultSlides() {
    return const [
      OnboardingSlide(
        id: 1,
        badge: 'HOŞ GELDİN! 🎉',
        title: 'Paranızı Çarçur Etmenin En Eğlenceli Yolu! 💸',
        subtitle:
            'Hiç ihtiyacınız olmayan ama "Bu fiyata kesin alınır!" diyeceğiniz yüzlerce popüler ürün Kaydırak\'ta sizi bekliyor.',
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide1.png',
      ),
      OnboardingSlide(
        id: 2,
        badge: 'NASIL ÇALIŞIR? 👆',
        title: 'Instagram Gibi Kaydır, Fırsatı Yakala! 👉',
        subtitle:
            'Sağa dokun sıradaki ürüne geç. Beğendiysen yukarı kaydır (veya ürüne dokun) anında mağazaya uç! Aşağı çekersen vitrin yenilenir.',
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide2.png',
      ),
      OnboardingSlide(
        id: 3,
        badge: 'SÜREKLİ TAZE VİTRİN 🚀',
        title: 'Her 4 Saatte Bir Yepyeni 120 Ürün! 🔥',
        subtitle:
            'Amazon, Hepsiburada ve İdefix\'in en çok satanları her 4 saatte bir tamamen değişir. Cüzdanınız hazırsa başlayalım!',
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide3.png',
      ),
    ];
  }

  /// Sunucudan (GitHub) güncel slayt metinlerini ve görsel URL'lerini çeker
  Future<void> _fetchRemoteSlides() async {
    final ts = DateTime.now().millisecondsSinceEpoch;
    for (final baseUrl in [_remoteConfigRawUrl, _remoteConfigApiUrl]) {
      try {
        final client = HttpClient()
          ..connectionTimeout = const Duration(seconds: 6);

        final req = await client.getUrl(Uri.parse('$baseUrl?t=$ts'));
        if (baseUrl == _remoteConfigApiUrl) {
          req.headers.set('Accept', 'application/vnd.github.v3.raw');
        }
        req.headers.set('Cache-Control', 'no-cache');
        req.headers.set('User-Agent', 'KaydirakApp/2.2 (Android)');

        final resp = await req.close().timeout(const Duration(seconds: 6));
        if (resp.statusCode == 200) {
          final body = await resp.transform(utf8.decoder).join();
          final decoded = json.decode(body);
          if (decoded is List && decoded.isNotEmpty) {
            final loaded = decoded
                .map((e) => OnboardingSlide.fromJson(e as Map<String, dynamic>))
                .toList();
            if (mounted && loaded.isNotEmpty) {
              setState(() {
                _slides = loaded;
              });
            }
            return;
          }
        }
      } catch (_) {}
    }
  }

  Future<void> _completeOnboarding() async {
    await AnalyticsService().markOnboardingCompleted();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const StoryFeedScreen()),
    );
  }

  void _nextSlide() {
    if (_currentPage < _slides.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
      );
    } else {
      _completeOnboarding();
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLastPage = _currentPage == _slides.length - 1;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 1. Tam Sayfa Kaydırılabilir Arka Plan Görselleri ve Görsel İçi Yazılar
          Positioned.fill(
            child: PageView.builder(
              controller: _pageController,
              itemCount: _slides.length,
              onPageChanged: (idx) {
                setState(() {
                  _currentPage = idx;
                });
              },
              itemBuilder: (context, index) {
                final slide = _slides[index];
                final serverImgUrl = slide.imageUrl.contains('?')
                    ? '${slide.imageUrl}&t=$_cacheBuster'
                    : '${slide.imageUrl}?t=$_cacheBuster';

                return Stack(
                  fit: StackFit.expand,
                  children: [
                    // Tam Sayfa Resim (Sunucudan Canlı Çekilir)
                    Image.network(
                      serverImgUrl,
                      fit: BoxFit.cover,
                      width: double.infinity,
                      height: double.infinity,
                      headers: const {
                        'Cache-Control': 'no-cache',
                      },
                      loadingBuilder: (context, child, progress) {
                        if (progress == null) return child;
                        return Container(
                          color: const Color(0xFF1E272E),
                          child: const Center(
                            child: CircularProgressIndicator(
                              color: Color(0xFFFF4757),
                              strokeWidth: 3,
                            ),
                          ),
                        );
                      },
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          decoration: const BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Color(0xFF1E272E),
                                Color(0xFFFF4757),
                              ],
                            ),
                          ),
                          child: Center(
                            child: Icon(
                              index == 0
                                  ? Icons.shopping_bag_rounded
                                  : index == 1
                                      ? Icons.swipe_rounded
                                      : Icons.rocket_launch_rounded,
                              size: 110,
                              color: Colors.white54,
                            ),
                          ),
                        );
                      },
                    ),

                    // Üst ve Alt Karartma Gradyanı (Yazıların Resmin İçinde Net Okunması İçin)
                    DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          stops: const [0.0, 0.22, 0.48, 0.72, 1.0],
                          colors: [
                            Colors.black.withValues(alpha: 0.55),
                            Colors.transparent,
                            Colors.black.withValues(alpha: 0.15),
                            Colors.black.withValues(alpha: 0.78),
                            Colors.black.withValues(alpha: 0.94),
                          ],
                        ),
                      ),
                    ),

                    // Resmin İçerisinde Yer Alan Başlık ve Açıklama Metinleri
                    SafeArea(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(24, 70, 24, 130),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.end,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 6),
                              decoration: BoxDecoration(
                                color: Colors.black.withValues(alpha: 0.45),
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: const Color(0xFFFFD32A)
                                      .withValues(alpha: 0.75),
                                ),
                              ),
                              child: Text(
                                slide.badge,
                                style: const TextStyle(
                                  color: Color(0xFFFFD32A),
                                  fontSize: 12,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 0.6,
                                ),
                              ),
                            ),
                            const SizedBox(height: 14),
                            Text(
                              slide.title,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 25,
                                fontWeight: FontWeight.w900,
                                height: 1.2,
                                shadows: [
                                  Shadow(
                                    color: Colors.black87,
                                    blurRadius: 12,
                                    offset: Offset(0, 2),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              slide.subtitle,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: Color(0xFFF1F2F6),
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                                height: 1.45,
                                shadows: [
                                  Shadow(
                                    color: Colors.black87,
                                    blurRadius: 8,
                                    offset: Offset(0, 1),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),

          // 2. Üst Bar (Resmin Üzerinde): Logo & Atla Butonu
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.4),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.asset(
                            'assets/icons/app_logo.png',
                            width: 28,
                            height: 28,
                            fit: BoxFit.cover,
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Kaydırak',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            letterSpacing: -0.3,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (!isLastPage)
                    TextButton(
                      onPressed: _completeOnboarding,
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.white,
                        backgroundColor: Colors.black.withValues(alpha: 0.4),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 6),
                      ),
                      child: const Text(
                        'Atla',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // 3. Alt Bar (Resmin İçinde En Altta): Sayfa Noktaları ve İleri / Başla Butonu
          Positioned(
            left: 20,
            right: 20,
            bottom: 0,
            child: SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.only(bottom: 18),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(_slides.length, (idx) {
                        final active = idx == _currentPage;
                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 250),
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          width: active ? 28 : 9,
                          height: 9,
                          decoration: BoxDecoration(
                            color: active
                                ? const Color(0xFFFF4757)
                                : Colors.white.withValues(alpha: 0.4),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        );
                      }),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: _nextSlide,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isLastPage
                              ? const Color(0xFF00C853)
                              : const Color(0xFFFF4757),
                          foregroundColor: Colors.white,
                          elevation: 8,
                          shadowColor: Colors.black.withValues(alpha: 0.5),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child: Text(
                          isLastPage ? 'KAYDIRMAYA BAŞLA  🛝' : 'DEVAM ET  ➔',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
