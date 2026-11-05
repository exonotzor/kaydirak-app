import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../models/deal_item.dart';

class DealService {
  static final DealService _instance = DealService._internal();
  factory DealService() => _instance;
  DealService._internal();

  /// Uzak sunucu adresleri - Kalici REST API ve yedek ayna uclari
  static const String primaryRemoteUrl = 'https://extendsclass.com/api/json-storage/bin/ccbacbe';
  static const String mirrorRemoteUrl = 'https://files.catbox.moe/dmmlht.json';

  List<DealItem> _cachedDeals = [];

  File get _cacheFile => File('${Directory.systemTemp.path}/live_deals_cache.json');

  /// Indirimleri yukler:
  /// 1. Hafizada varsa dondurur (forceRefresh degilse).
  /// 2. Uzak sunucudan canli ceker (Her zaman en taze veriyi almak icin zaman damgasi ekler).
  /// 3. Baglanti yoksa onceki oturumdan kalan disk onbellegini kullanir.
  Future<List<DealItem>> loadDeals({bool forceRefresh = false}) async {
    if (!forceRefresh && _cachedDeals.isNotEmpty) {
      return _cachedDeals;
    }

    // 1. Oncelikle uzak sunucudan canli verileri indir (Sifir Onbellek / Zero CDN Cache)
    final remoteDeals = await _fetchFromRemote();
    if (remoteDeals.isNotEmpty) {
      _cachedDeals = remoteDeals;
      return _cachedDeals;
    }

    // 2. Internet kesintisi durumunda disk onbellegine bak
    if (await _cacheFile.exists()) {
      try {
        final cachedJson = await _cacheFile.readAsString();
        final List<dynamic> jsonList = json.decode(cachedJson) as List<dynamic>;
        final deals = _parseAndFilter(jsonList);
        if (deals.isNotEmpty) {
          _cachedDeals = deals;
          return _cachedDeals;
        }
      } catch (e) {
        debugPrint('Disk cache okuma hatasi: $e');
      }
    }

    // 3. Bundled asset (cevrimdisi ilk acilis emniyet kopyasi)
    try {
      final jsonString = await rootBundle.loadString('assets/data/live_deals.json');
      final List<dynamic> jsonList = json.decode(jsonString) as List<dynamic>;
      _cachedDeals = _parseAndFilter(jsonList);
    } catch (e) {
      debugPrint('Asset veri okuma hatasi: $e');
      _cachedDeals = [];
    }

    return _cachedDeals;
  }

  /// Story ekraninda asagi cekince sunucudan yeni verileri ceker
  Future<List<DealItem>> refreshDeals() async {
    return loadDeals(forceRefresh: true);
  }

  /// Uzak sunucudan HTTP GET ile canli indirimleri indirir (CDN onbellegini atlatarak)
  Future<List<DealItem>> _fetchFromRemote() async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    for (final baseUrl in [primaryRemoteUrl, mirrorRemoteUrl]) {
      try {
        final cacheBustedUrl = '$baseUrl?t=$timestamp';
        final client = HttpClient()
          ..connectionTimeout = const Duration(seconds: 8)
          ..badCertificateCallback = (cert, host, port) => true;

        final request = await client.getUrl(Uri.parse(cacheBustedUrl));
        request.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
        request.headers.set('Pragma', 'no-cache');
        request.headers.set('Expires', '0');
        request.headers.set('User-Agent', 'KaydirakApp/1.0 (Android)');

        final response = await request.close().timeout(const Duration(seconds: 10));

        if (response.statusCode == 200) {
          final responseBody = await response.transform(utf8.decoder).join();
          final dynamic decoded = json.decode(responseBody);
          if (decoded is! List) {
            debugPrint('Beklenmeyen yanit bicimi (List degil): $baseUrl');
            continue;
          }
          final deals = _parseAndFilter(decoded);

          if (deals.isNotEmpty) {
            // Basarili indirildiyse diske taze onbellek olarak kaydet
            try {
              await _cacheFile.writeAsString(responseBody);
            } catch (e) {
              debugPrint('Disk cache yazma hatasi: $e');
            }
            return deals;
          }
        }
      } catch (e) {
        debugPrint('Uzak sunucudan canli veri cekilemedi ($baseUrl): $e');
      }
    }
    return [];
  }

  List<DealItem> _parseAndFilter(List<dynamic> jsonList) {
    // Gelen JSON zaten sunucu tarafindan magaza ve kategoriye gore
    // akilli round-robin siralamasiyla hazirlanmistir (pes pese ayni magaza veya urun cikmaz).
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
