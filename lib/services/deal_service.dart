import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../models/deal_item.dart';

class DealService {
  static final DealService _instance = DealService._internal();
  factory DealService() => _instance;
  DealService._internal();

  /// Uzak sunucu adresleri - Doğrudan GitHub Canlı Depo API + Raw + Yedek Sunucu
  static const String githubApiRawUrl =
      'https://api.github.com/repos/exonotzor/kaydirak-app/contents/assets/data/live_deals.json';
  static const String githubRawUrl =
      'https://raw.githubusercontent.com/exonotzor/kaydirak-app/main/assets/data/live_deals.json';
  static const String primaryRemoteUrl =
      'https://extendsclass.com/api/json-storage/bin/ccbacbe';

  List<DealItem> _cachedDeals = [];

  File get _cacheFile =>
      File('${Directory.systemTemp.path}/live_deals_cache_v3.json');

  /// İndirimleri yükler:
  /// 1. Hafızada varsa döndürür (forceRefresh değilse).
  /// 2. Uzak sunucudan canlı çeker (Her zaman en taze veriyi almak için zaman damgası ekler).
  /// 3. Bağlantı yoksa önceki oturumdan kalan disk önbelleğini kullanır.
  Future<List<DealItem>> loadDeals({bool forceRefresh = false}) async {
    if (!forceRefresh && _cachedDeals.isNotEmpty) {
      return _cachedDeals;
    }

    // 1. Öncelikle uzak sunucudan canlı verileri indir (Sıfır Önbellek / Zero CDN Cache)
    final remoteDeals = await _fetchFromRemote();
    if (remoteDeals.isNotEmpty) {
      _cachedDeals = remoteDeals;
      return _cachedDeals;
    }

    // 2. İnternet kesintisi durumunda disk önbelleğine bak
    if (await _cacheFile.exists()) {
      try {
        final cachedJson = await _cacheFile.readAsString();
        final List<dynamic> jsonList =
            json.decode(cachedJson) as List<dynamic>;
        final deals = _parseAndFilter(jsonList);
        if (deals.isNotEmpty) {
          _cachedDeals = deals;
          return _cachedDeals;
        }
      } catch (e) {
        debugPrint('Disk cache okuma hatası: $e');
      }
    }

    // 3. Bundled asset (çevrimdışı ilk açılış emniyet kopyası)
    try {
      final jsonString =
          await rootBundle.loadString('assets/data/live_deals.json');
      final List<dynamic> jsonList = json.decode(jsonString) as List<dynamic>;
      _cachedDeals = _parseAndFilter(jsonList);
    } catch (e) {
      debugPrint('Asset veri okuma hatası: $e');
      _cachedDeals = [];
    }

    return _cachedDeals;
  }

  /// Story ekranında aşağı çekince sunucudan yeni verileri çeker
  Future<List<DealItem>> refreshDeals() async {
    return loadDeals(forceRefresh: true);
  }

  /// Uzak sunucudan HTTP GET ile canlı indirimleri indirir (CDN önbelleğini atlatarak)
  Future<List<DealItem>> _fetchFromRemote() async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    for (final baseUrl in [githubApiRawUrl, githubRawUrl, primaryRemoteUrl]) {
      try {
        final cacheBustedUrl = '$baseUrl?t=$timestamp';
        final client = HttpClient()
          ..connectionTimeout = const Duration(seconds: 8)
          ..badCertificateCallback = (cert, host, port) => true;

        final request = await client.getUrl(Uri.parse(cacheBustedUrl));
        if (baseUrl == githubApiRawUrl) {
          request.headers.set('Accept', 'application/vnd.github.v3.raw');
        }
        request.headers
            .set('Cache-Control', 'no-cache, no-store, must-revalidate');
        request.headers.set('Pragma', 'no-cache');
        request.headers.set('Expires', '0');
        request.headers.set('User-Agent', 'KaydirakApp/3.0 (Android)');

        final response =
            await request.close().timeout(const Duration(seconds: 10));

        if (response.statusCode == 200) {
          final responseBody = await response.transform(utf8.decoder).join();
          final dynamic decoded = json.decode(responseBody);
          if (decoded is! List) {
            debugPrint('Beklenmeyen yanıt biçimi (List değil): $baseUrl');
            continue;
          }
          final deals = _parseAndFilter(decoded);

          if (deals.isNotEmpty) {
            // Başarılı indirildiyse diske taze önbellek olarak kaydet
            try {
              await _cacheFile.writeAsString(responseBody);
            } catch (e) {
              debugPrint('Disk cache yazma hatası: $e');
            }
            return deals;
          }
        }
      } catch (e) {
        debugPrint('Uzak sunucudan canlı veri çekilemedi ($baseUrl): $e');
      }
    }
    return [];
  }

  List<DealItem> _parseAndFilter(List<dynamic> jsonList) {
    final deals = jsonList
        .map((item) => DealItem.fromJson(item as Map<String, dynamic>))
        .where((item) =>
            item.originalPrice > 0 &&
            item.discountedPrice > 0 &&
            item.discountedPrice < item.originalPrice)
        .toList();

    return deals;
  }

  List<String> getCategories(List<DealItem> deals) {
    final categories = {'Tümü'};
    for (final deal in deals) {
      if (deal.category.isNotEmpty) {
        categories.add(deal.category);
      }
    }
    return categories.toList();
  }
}
