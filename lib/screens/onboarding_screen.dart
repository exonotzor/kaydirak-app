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
        req.headers.set('User-Agent', 'KaydirakApp/2.1 (Android)');

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
      backgroundColor: const Color(0xFF1E272E),
      body: SafeArea(
        child: Column(
          children: [
            // Üst Bar: Logo & Atla Butonu
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.asset(
                          'assets/icons/app_logo.png',
                          width: 34,
                          height: 34,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'Kaydırak',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          letterSpacing: -0.3,
                        ),
                      ),
                    ],
                  ),
                  if (!isLastPage)
                    TextButton(
                      onPressed: _completeOnboarding,
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.white70,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 6),
                      ),
                      child: const Text(
                        'Atla',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // Orta Alan: Sunucudan Gelen Tam Ekran Görselli Slaytlar
            Expanded(
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

                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      children: [
                        // 1. Görsel Kartı (Sunucudan Canlı Çekilir)
                        Expanded(
                          flex: 58,
                          child: Container(
                            width: double.infinity,
                            margin: const EdgeInsets.only(top: 6, bottom: 18),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(28),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFFFF4757)
                                      .withValues(alpha: 0.25),
                                  blurRadius: 24,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(28),
                              child: Image.network(
                                serverImgUrl,
                                fit: BoxFit.cover,
                                width: double.infinity,
                                height: double.infinity,
                                headers: const {
                                  'Cache-Control': 'no-cache',
                                },
                                loadingBuilder: (context, child, progress) {
                                  if (progress == null) return child;
                                  return const Center(
                                    child: CircularProgressIndicator(
                                      color: Color(0xFFFF4757),
                                      strokeWidth: 3,
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
                                          Color(0xFFFF4757),
                                          Color(0xFFFF6B81),
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
                                        size: 96,
                                        color: Colors.white,
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),
                        ),

                        // 2. Esprili Başlık ve Açıklama Alanı
                        Expanded(
                          flex: 42,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.start,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 14, vertical: 6),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFFD32A)
                                      .withValues(alpha: 0.18),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: const Color(0xFFFFD32A)
                                        .withValues(alpha: 0.5),
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
                                  fontSize: 23,
                                  fontWeight: FontWeight.w900,
                                  height: 1.22,
                                ),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                slide.subtitle,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  color: Color(0xFFD2DAE2),
                                  fontSize: 15,
                                  fontWeight: FontWeight.w500,
                                  height: 1.45,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),

            // Alt Bar: Sayfa Noktaları ve İleri / Başla Butonu
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
              child: Column(
                children: [
                  // Sayfa İndikatörleri
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
                              : Colors.white.withValues(alpha: 0.25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                      );
                    }),
                  ),
                  const SizedBox(height: 18),

                  // Ana İlerleme Butonu
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
                        elevation: 6,
                        shadowColor: (isLastPage
                                ? const Color(0xFF00C853)
                                : const Color(0xFFFF4757))
                            .withValues(alpha: 0.45),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      child: Text(
                        isLastPage
                            ? 'KAYDIRMAYA BAŞLA  🛝'
                            : 'DEVAM ET  ➔',
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
          ],
        ),
      ),
    );
  }
}
