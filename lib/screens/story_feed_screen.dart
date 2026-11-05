import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/deal_item.dart';
import '../services/analytics_service.dart';
import '../services/deal_service.dart';
import '../widgets/story_progress_bar.dart';
import '../widgets/story_card.dart';

class StoryFeedScreen extends StatefulWidget {
  const StoryFeedScreen({super.key});

  @override
  State<StoryFeedScreen> createState() => _StoryFeedScreenState();
}

class _StoryFeedScreenState extends State<StoryFeedScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  final PageController _pageController = PageController();

  List<DealItem> _allDeals = [];
  List<DealItem> _filteredDeals = [];
  int _currentIndex = 0;
  String _selectedCategory = 'Tümü';
  bool _isLoading = true;
  bool _isRefreshing = false;

  List<String> _categories = [
    'Tümü',
    'Teknoloji',
    'Moda',
    'Ev & Yaşam',
    'Kozmetik',
    'Kitap & Hobi',
  ];

  @override
  void initState() {
    super.initState();

    // 8 saniye otomatik ilerleme süresi
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 8),
    );

    _animController.addListener(() {
      setState(() {});
    });

    _animController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _goToNextStory();
      }
    });

    _loadData();
  }

  void _trackCurrentDealView() {
    if (_filteredDeals.isNotEmpty &&
        _currentIndex >= 0 &&
        _currentIndex < _filteredDeals.length) {
      AnalyticsService().recordProductView(_filteredDeals[_currentIndex]);
    }
  }

  Future<void> _loadData() async {
    final deals = await DealService().loadDeals();
    if (!mounted) return;

    setState(() {
      _allDeals = deals;
      _categories = DealService().getCategories(deals);
      _isLoading = false;
      _applyFilter('Tümü');
    });

    _animController.reset();
    _animController.forward();
  }

  void _applyFilter(String category) {
    setState(() {
      _selectedCategory = category;
      if (category == 'Tümü') {
        _filteredDeals = List.from(_allDeals);
      } else {
        _filteredDeals =
            _allDeals.where((item) => item.category == category).toList();
      }
      _currentIndex = 0;
    });

    if (_pageController.hasClients) {
      _pageController.jumpToPage(0);
    }
    _trackCurrentDealView();
    _animController.reset();
    _animController.forward();
  }

  void _goToNextStory() {
    if (_filteredDeals.isEmpty) return;

    if (_currentIndex < _filteredDeals.length - 1) {
      setState(() {
        _currentIndex++;
      });
      _pageController.animateToPage(
        _currentIndex,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeInOut,
      );
      _animController.reset();
      _animController.forward();
    } else {
      // Hikayeler bittiğinde başa dön
      setState(() {
        _currentIndex = 0;
      });
      _pageController.animateToPage(
        0,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeInOut,
      );
      _animController.reset();
      _animController.forward();
    }
  }

  void _goToPreviousStory() {
    if (_filteredDeals.isEmpty) return;

    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
      });
      _pageController.animateToPage(
        _currentIndex,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeInOut,
      );
      _animController.reset();
      _animController.forward();
    } else {
      _animController.reset();
      _animController.forward();
    }
  }

  void _pauseTimer() {
    _animController.stop();
  }

  void _resumeTimer() {
    _animController.forward();
  }

  /// Story kartlarında aşağı çekildiğinde sunucudan güncel fırsatları çeker
  Future<void> _refreshDealsFromRemote() async {
    if (_isRefreshing) return;
    _pauseTimer();
    setState(() {
      _isRefreshing = true;
    });

    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Row(
          children: [
            SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFFFFD32A),
              ),
            ),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                '🔄 Sunucudan güncel indirimler taranıyor...',
                style:
                    TextStyle(fontWeight: FontWeight.w600, color: Colors.white),
              ),
            ),
          ],
        ),
        duration: Duration(milliseconds: 2000),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Color(0xFF1E272E),
      ),
    );

    final freshDeals = await DealService().refreshDeals();
    if (!mounted) return;

    setState(() {
      _isRefreshing = false;
      if (freshDeals.isNotEmpty) {
        _allDeals = freshDeals;
        _categories = DealService().getCategories(freshDeals);
      }
      _applyFilter(_selectedCategory);
    });

    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '✨ v2.1: ${_allDeals.length} güncel ürün hazır!',
          style:
              const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        duration: const Duration(milliseconds: 2000),
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF00823B),
      ),
    );
  }

  /// Kesintisiz ve garantili Link Açıcı + İstatistik Tıklama Kaydı
  Future<void> _launchProductUrl(DealItem deal) async {
    _pauseTimer();
    final cleanUrl = deal.productUrl.trim();
    if (cleanUrl.isEmpty) {
      _resumeTimer();
      return;
    }

    // Kullanıcı tıklama istatistiğini kaydet ve sunucuya gönder
    AnalyticsService().recordProductClick(deal);

    final uri = Uri.parse(cleanUrl);

    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          '🛍️ Mağaza sayfası açılıyor...',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        duration: Duration(milliseconds: 1200),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Color(0xFF1E272E),
      ),
    );

    try {
      bool launched = false;
      try {
        launched = await launchUrl(uri, mode: LaunchMode.platformDefault);
      } catch (_) {}

      if (!launched) {
        try {
          launched = await launchUrl(uri, mode: LaunchMode.inAppBrowserView);
        } catch (_) {}
      }

      if (!launched) {
        try {
          launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
        } catch (_) {}
      }

      if (!launched) {
        if (await canLaunchUrl(uri)) {
          await launchUrl(uri);
        }
      }
    } catch (e) {
      debugPrint('Link açılamadı: $e');
    } finally {
      _resumeTimer();
    }
  }

  void _showPrivacyDialog() {
    _pauseTimer();
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Row(
          children: [
            Icon(Icons.verified_user_outlined, color: Color(0xFFFF4757)),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'Kaydırak Hakkında & Gizlilik',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        content: const SingleChildScrollView(
          child: Text(
            '• Kaydırak; Amazon TR, Hepsiburada ve İdefix\'teki popüler fırsatları 4 saatte bir yenileyerek sunar.\n\n'
            '• Fiyatlar mağazalardan periyodik olarak çekilir; satın alma esnasında ilgili mağazanın sepetindeki güncel fiyat ve stok durumu geçerlidir.\n\n'
            '• Gizlilik: Uygulamamız ad, e-posta, telefon veya konum gibi kişisel verilerinizi toplamaz. Yalnızca uygulama deneyimini geliştirmek adına anonim kullanım istatistikleri işlenir.',
            style: TextStyle(fontSize: 13.5, height: 1.45, color: Color(0xFF2D3436)),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () async {
              final uri = Uri.parse(
                  'https://github.com/exonotzor/kaydirak-app/blob/main/PRIVACY_POLICY.md');
              await launchUrl(uri, mode: LaunchMode.externalApplication);
            },
            child: const Text('Tam Gizlilik Politikası'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFFF4757),
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    ).then((_) => _resumeTimer());
  }

  @override
  void dispose() {
    _animController.dispose();
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFF4757).withValues(alpha: 0.3),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(22),
                  child: Image.asset(
                    'assets/icons/app_logo.png',
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'Kaydırak v2.2',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E272E),
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Çok Satan Fırsatlar Yükleniyor...',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF747D8C),
                ),
              ),
              const SizedBox(height: 20),
              const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: Color(0xFFFF4757),
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_filteredDeals.isEmpty) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Bu kategoride indirim bulunamadı.'),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => _applyFilter('Tümü'),
                child: const Text('Tüm İndirimleri Göster'),
              ),
            ],
          ),
        ),
      );
    }

    final currentDeal = _filteredDeals[_currentIndex];

    return Scaffold(
      backgroundColor: const Color(0xFFF1F2F6),
      body: SafeArea(
        child: Stack(
          children: [
            // 1. Dikey/Yatay Kaydırma ve Sayfa Akışı
            GestureDetector(
              onLongPressStart: (_) => _pauseTimer(),
              onLongPressEnd: (_) => _resumeTimer(),
              onVerticalDragEnd: (details) {
                if (details.primaryVelocity != null) {
                  // Ekranın herhangi bir yerinden yukarı kaydırınca -> Doğrudan ürüne git
                  if (details.primaryVelocity! < -200) {
                    _launchProductUrl(currentDeal);
                  }
                  // Aşağı çekince -> Sunucudan güncel indirimleri yenile
                  else if (details.primaryVelocity! > 200) {
                    _refreshDealsFromRemote();
                  }
                }
              },
              child: PageView.builder(
                controller: _pageController,
                physics: const ClampingScrollPhysics(),
                itemCount: _filteredDeals.length,
                onPageChanged: (index) {
                  setState(() {
                    _currentIndex = index;
                  });
                  _trackCurrentDealView();
                  _animController.reset();
                  _animController.forward();
                },
                itemBuilder: (context, index) {
                  return StoryCard(
                    deal: _filteredDeals[index],
                    onOpenLink: () => _launchProductUrl(_filteredDeals[index]),
                  );
                },
              ),
            ),

            // 2. Sol / Sağ Hızlı Dokunma Alanları
            Positioned(
              top: 110,
              bottom: 210,
              left: 0,
              right: 0,
              child: Row(
                children: [
                  Expanded(
                    flex: 28,
                    child: GestureDetector(
                      behavior: HitTestBehavior.translucent,
                      onTap: _goToPreviousStory,
                      child: const SizedBox.expand(),
                    ),
                  ),
                  const Expanded(
                    flex: 44,
                    child: IgnorePointer(
                      child: SizedBox.expand(),
                    ),
                  ),
                  Expanded(
                    flex: 28,
                    child: GestureDetector(
                      behavior: HitTestBehavior.translucent,
                      onTap: _goToNextStory,
                      child: const SizedBox.expand(),
                    ),
                  ),
                ],
              ),
            ),

            // 3. Üst Bar: İlerleme Çubukları + Kategori Hapları
            Positioned(
              top: 8,
              left: 12,
              right: 12,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  StoryProgressBar(
                    totalCount: _filteredDeals.length.clamp(1, 35),
                    currentIndex: _currentIndex.clamp(0, 34),
                    currentProgress: _animController.value,
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: SizedBox(
                          height: 32,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            itemCount: _categories.length,
                            separatorBuilder: (context, index) =>
                                const SizedBox(width: 8),
                            itemBuilder: (context, idx) {
                              final cat = _categories[idx];
                              final isSelected = cat == _selectedCategory;
                              return GestureDetector(
                                onTap: () => _applyFilter(cat),
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 200),
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 14, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? const Color(0xFFFF4757)
                                        : Colors.white.withValues(alpha: 0.95),
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: [
                                      BoxShadow(
                                        color:
                                            Colors.black.withValues(alpha: 0.08),
                                        blurRadius: 4,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: Text(
                                    cat,
                                    style: TextStyle(
                                      color: isSelected
                                          ? Colors.white
                                          : const Color(0xFF2D3436),
                                      fontWeight: isSelected
                                          ? FontWeight.bold
                                          : FontWeight.w600,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      GestureDetector(
                        onTap: _showPrivacyDialog,
                        child: Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.95),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.08),
                                blurRadius: 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.info_outline_rounded,
                            size: 17,
                            color: Color(0xFF2D3436),
                          ),
                        ),
                      ),
                    ],
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
