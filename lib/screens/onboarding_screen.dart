import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import '../services/analytics_service.dart';
import 'story_feed_screen.dart';

class OnboardingSlide {
  final int id;
  final String imageUrl;
  final String assetFallback;

  const OnboardingSlide({
    required this.id,
    required this.imageUrl,
    required this.assetFallback,
  });

  factory OnboardingSlide.fromJson(Map<String, dynamic> json, int index) {
    final id = (json['id'] as num?)?.toInt() ?? (index + 1);
    return OnboardingSlide(
      id: id,
      imageUrl: json['imageUrl'] as String? ??
          'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide${id}_v25.png',
      assetFallback: 'assets/onboarding/slide${id.clamp(1, 5)}.png',
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
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide1_v25.png',
        assetFallback: 'assets/onboarding/slide1.png',
      ),
      OnboardingSlide(
        id: 2,
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide2_v25.png',
        assetFallback: 'assets/onboarding/slide2.png',
      ),
      OnboardingSlide(
        id: 3,
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide3_v25.png',
        assetFallback: 'assets/onboarding/slide3.png',
      ),
      OnboardingSlide(
        id: 4,
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide4_v25.png',
        assetFallback: 'assets/onboarding/slide4.png',
      ),
      OnboardingSlide(
        id: 5,
        imageUrl:
            'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/onboarding/slide5_v25.png',
        assetFallback: 'assets/onboarding/slide5.png',
      ),
    ];
  }

  /// Sunucudan (GitHub) güncel slayt görsel URL'lerini çeker
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
        req.headers.set('User-Agent', 'KaydirakApp/2.3 (Android)');

        final resp = await req.close().timeout(const Duration(seconds: 6));
        if (resp.statusCode == 200) {
          final body = await resp.transform(utf8.decoder).join();
          final decoded = json.decode(body);
          if (decoded is List && decoded.isNotEmpty) {
            final loaded = <OnboardingSlide>[];
            for (var i = 0; i < decoded.length; i++) {
              loaded.add(
                OnboardingSlide.fromJson(
                    decoded[i] as Map<String, dynamic>, i),
              );
            }
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
      backgroundColor: const Color(0xFF0F141C),
      body: SizedBox.expand(
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 1. Tam Ekran (Full-Page) Görseller — Yazılar Doğrudan Görselin İçindedir
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

                  return SizedBox.expand(
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
                        return Image.asset(
                          slide.assetFallback,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                        );
                      },
                      errorBuilder: (context, error, stackTrace) {
                        return Image.asset(
                          slide.assetFallback,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                        );
                      },
                    ),
                  );
                },
              ),
            ),

            // 2. Üst Bar: Yalnızca Logo (Geç/Atla butonu kaldırıldı)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: SafeArea(
                bottom: false,
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.45),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
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
                    ],
                  ),
                ),
              ),
            ),

            // 3. Alt Bar: Sayfa Noktaları ve İleri / Başla Butonu
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
      ),
    );
  }
}
