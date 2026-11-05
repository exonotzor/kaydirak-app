import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import '../models/deal_item.dart';

class AnalyticsService {
  static final AnalyticsService _instance = AnalyticsService._internal();
  factory AnalyticsService() => _instance;
  AnalyticsService._internal();

  /// Uzaktan okunabilir Canlı Kullanıcı İstatistikleri Sunucu Kutusu
  static const String telemetryBinUrl =
      'https://extendsclass.com/api/json-storage/bin/afacbcb';

  bool _initialized = false;
  bool _onboardingCompleted = false;
  String _userId = '';
  String _deviceInfo = '';
  String _firstSeenAt = '';
  String _lastSeenAt = '';
  int _sessionCount = 0;
  int _totalTimeSeconds = 0;
  int _viewedProductsCount = 0;
  int _totalClicks = 0;
  Map<String, int> _categoryViews = {
    'Teknoloji': 0,
    'Moda': 0,
    'Ev & Yaşam': 0,
    'Kozmetik': 0,
  };
  List<Map<String, dynamic>> _clickedProducts = [];
  final Set<String> _viewedInSession = {};

  Timer? _heartbeatTimer;
  int _ticksSinceLastSync = 0;
  bool _isSyncing = false;

  bool get isOnboardingCompleted => _onboardingCompleted;
  String get userId => _userId;

  Future<File> _getStateFile() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      return File('${dir.path}/kaydirak_user_state_v1.json');
    } catch (_) {
      return File('${Directory.systemTemp.path}/kaydirak_user_state_v1.json');
    }
  }

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;

    try {
      final file = await _getStateFile();
      if (await file.exists()) {
        final content = await file.readAsString();
        final data = json.decode(content) as Map<String, dynamic>;
        _onboardingCompleted = data['onboardingCompleted'] as bool? ?? false;
        _userId = data['userId'] as String? ?? '';
        _deviceInfo = data['deviceInfo'] as String? ?? '';
        _firstSeenAt = data['firstSeenAt'] as String? ?? '';
        _sessionCount = (data['sessionCount'] as num?)?.toInt() ?? 0;
        _totalTimeSeconds = (data['totalTimeSeconds'] as num?)?.toInt() ?? 0;
        _viewedProductsCount =
            (data['viewedProductsCount'] as num?)?.toInt() ?? 0;
        _totalClicks = (data['totalClicks'] as num?)?.toInt() ?? 0;

        if (data['categoryViews'] is Map) {
          final rawMap = data['categoryViews'] as Map<String, dynamic>;
          rawMap.forEach((k, v) {
            _categoryViews[k] = (v as num?)?.toInt() ?? 0;
          });
        }
        if (data['clickedProducts'] is List) {
          _clickedProducts = List<Map<String, dynamic>>.from(
            (data['clickedProducts'] as List)
                .map((e) => Map<String, dynamic>.from(e as Map)),
          );
        }
      }
    } catch (e) {
      debugPrint('Analytics init okuma hatası: $e');
    }

    final nowIso = DateTime.now().toIso8601String();
    if (_userId.isEmpty) {
      final rnd = Random();
      final hex = List.generate(
              6, (_) => rnd.nextInt(16).toRadixString(16).toUpperCase())
          .join();
      _userId = 'user-$hex';
      _firstSeenAt = nowIso;
    }
    if (_deviceInfo.isEmpty) {
      _deviceInfo =
          '${Platform.operatingSystem.toUpperCase()} (${Platform.operatingSystemVersion.split(' ').first})';
    }

    _sessionCount += 1;
    _lastSeenAt = nowIso;

    await _saveLocalState();
    _startHeartbeat();
    // İlk giriş istatistiğini arka planda sunucuya gönder
    unawaited(syncToRemote());
  }

  void _startHeartbeat() {
    if (Platform.environment.containsKey('FLUTTER_TEST')) return;
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 10), (_) async {
      _totalTimeSeconds += 10;
      _lastSeenAt = DateTime.now().toIso8601String();
      _ticksSinceLastSync += 1;
      await _saveLocalState();
      // Her 30 saniyede bir uzak sunucuyu güncelle
      if (_ticksSinceLastSync >= 3) {
        _ticksSinceLastSync = 0;
        unawaited(syncToRemote());
      }
    });
  }

  Future<void> markOnboardingCompleted() async {
    _onboardingCompleted = true;
    await _saveLocalState();
    unawaited(syncToRemote());
  }

  Future<void> recordProductView(DealItem deal) async {
    if (deal.id.isEmpty) return;
    // Aynı oturumda aynı ürüne ileri-geri hızlı geçişte mükerrer sayımı önle,
    // ancak her yeni ürünü say:
    if (_viewedInSession.add(deal.id)) {
      _viewedProductsCount += 1;
      final cat = deal.category.isNotEmpty ? deal.category : 'Genel';
      _categoryViews[cat] = (_categoryViews[cat] ?? 0) + 1;
      _lastSeenAt = DateTime.now().toIso8601String();
      await _saveLocalState();
    }
  }

  Future<void> recordProductClick(DealItem deal) async {
    _totalClicks += 1;
    _lastSeenAt = DateTime.now().toIso8601String();
    _clickedProducts.insert(0, {
      'id': deal.id,
      'title': deal.title.length > 65
          ? '${deal.title.substring(0, 65)}...'
          : deal.title,
      'store': deal.store,
      'category': deal.category,
      'price': deal.discountedPrice,
      'productUrl': deal.productUrl,
      'clickedAt': _lastSeenAt,
    });
    // Son 40 tıklanan ürünü tut (sunucu boyutunu şişirmemek için)
    if (_clickedProducts.length > 40) {
      _clickedProducts = _clickedProducts.sublist(0, 40);
    }
    await _saveLocalState();
    unawaited(syncToRemote());
  }

  Future<void> _saveLocalState() async {
    try {
      final file = await _getStateFile();
      final payload = {
        'onboardingCompleted': _onboardingCompleted,
        'userId': _userId,
        'deviceInfo': _deviceInfo,
        'firstSeenAt': _firstSeenAt,
        'lastSeenAt': _lastSeenAt,
        'sessionCount': _sessionCount,
        'totalTimeSeconds': _totalTimeSeconds,
        'viewedProductsCount': _viewedProductsCount,
        'totalClicks': _totalClicks,
        'categoryViews': _categoryViews,
        'clickedProducts': _clickedProducts,
      };
      await file.writeAsString(json.encode(payload));
    } catch (e) {
      debugPrint('Analytics yerel kayıt hatası: $e');
    }
  }

  /// Uzak sunucudaki istatistik kutusunu okur, bu kullanıcının verisini birleştirip yazar
  Future<void> syncToRemote() async {
    if (Platform.environment.containsKey('FLUTTER_TEST')) return;
    if (_isSyncing || _userId.isEmpty) return;
    _isSyncing = true;

    try {
      final client = HttpClient()
        ..connectionTimeout = const Duration(seconds: 8)
        ..badCertificateCallback = (cert, host, port) => true;

      // 1. Mevcut sunucu verisini çek
      Map<String, dynamic> rootData = {
        'updatedAt': DateTime.now().toUtc().toIso8601String(),
        'users': <String, dynamic>{},
      };

      try {
        final ts = DateTime.now().millisecondsSinceEpoch;
        final getReq =
            await client.getUrl(Uri.parse('$telemetryBinUrl?t=$ts'));
        getReq.headers
            .set('Cache-Control', 'no-cache, no-store, must-revalidate');
        getReq.headers.set('User-Agent', 'KaydirakAnalytics/2.1');
        final getResp =
            await getReq.close().timeout(const Duration(seconds: 8));
        if (getResp.statusCode == 200) {
          final body = await getResp.transform(utf8.decoder).join();
          final decoded = json.decode(body);
          if (decoded is Map<String, dynamic>) {
            rootData = decoded;
          }
        }
      } catch (_) {}

      final usersMap = (rootData['users'] is Map)
          ? Map<String, dynamic>.from(rootData['users'] as Map)
          : <String, dynamic>{};

      final hours = (_totalTimeSeconds / 3600.0);
      final minutes = (_totalTimeSeconds / 60.0);

      usersMap[_userId] = {
        'userId': _userId,
        'deviceInfo': _deviceInfo,
        'firstSeenAt': _firstSeenAt,
        'lastSeenAt': _lastSeenAt,
        'sessionCount': _sessionCount,
        'totalTimeSeconds': _totalTimeSeconds,
        'totalTimeMinutes': double.parse(minutes.toStringAsFixed(1)),
        'totalTimeHours': double.parse(hours.toStringAsFixed(2)),
        'viewedProductsCount': _viewedProductsCount,
        'totalClicks': _totalClicks,
        'categoryViews': _categoryViews,
        'clickedProducts': _clickedProducts,
      };

      rootData['updatedAt'] = DateTime.now().toUtc().toIso8601String();
      rootData['totalUsers'] = usersMap.length;
      rootData['users'] = usersMap;

      // 2. Güncellenmiş veriyi sunucuya PUT ile kaydet
      final putReq = await client.openUrl('PUT', Uri.parse(telemetryBinUrl));
      putReq.headers.set('Content-Type', 'application/json; charset=utf-8');
      putReq.headers.set('User-Agent', 'KaydirakAnalytics/2.1');
      final encodedBytes = utf8.encode(json.encode(rootData));
      putReq.contentLength = encodedBytes.length;
      putReq.add(encodedBytes);
      await putReq.close().timeout(const Duration(seconds: 8));
    } catch (e) {
      debugPrint('Analytics uzak sunucu senkronizasyon hatası: $e');
    } finally {
      _isSyncing = false;
    }
  }
}
