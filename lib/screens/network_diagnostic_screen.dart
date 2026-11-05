import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'story_feed_screen.dart';

class NetworkDiagnosticScreen extends StatefulWidget {
  const NetworkDiagnosticScreen({super.key});

  @override
  State<NetworkDiagnosticScreen> createState() => _NetworkDiagnosticScreenState();
}

class TestResult {
  final String title;
  final String url;
  bool isTesting;
  bool? isSuccess;
  int? statusCode;
  int? latencyMs;
  int? itemCount;
  String? rawType;
  String? firstItemSummary;
  String? errorMessage;
  Map<String, int>? categoryCounts;

  TestResult({
    required this.title,
    required this.url,
    this.isTesting = false,
    this.isSuccess,
    this.statusCode,
    this.latencyMs,
    this.itemCount,
    this.rawType,
    this.firstItemSummary,
    this.errorMessage,
    this.categoryCounts,
  });
}

class _NetworkDiagnosticScreenState extends State<NetworkDiagnosticScreen> {
  bool _isRunningAll = false;
  String? _cacheStatus;
  int? _cacheItemCount;

  final List<TestResult> _tests = [
    TestResult(
      title: '1. Genel İnternet & SSL Bağlantısı',
      url: 'https://www.google.com',
    ),
    TestResult(
      title: '2. Birincil REST API Sunucusu (ExtendsClass)',
      url: 'https://extendsclass.com/api/json-storage/bin/ccbacbe',
    ),
    TestResult(
      title: '3. Yedek Ayna Sunucusu (Catbox CDN)',
      url: 'https://files.catbox.moe/tg85cp.json',
    ),
    TestResult(
      title: '4. Global API Bağlantı Testi (httpbin)',
      url: 'https://httpbin.org/get',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _checkCacheStatus();
    _runAllTests();
  }

  File get _cacheFile => File('${Directory.systemTemp.path}/live_deals_cache.json');

  Future<void> _checkCacheStatus() async {
    try {
      if (await _cacheFile.exists()) {
        final content = await _cacheFile.readAsString();
        final len = await _cacheFile.length();
        final dynamic decoded = json.decode(content);
        if (decoded is List) {
          setState(() {
            _cacheItemCount = decoded.length;
            _cacheStatus = 'Mevcut (${(len / 1024).toStringAsFixed(1)} KB, ${decoded.length} ürün)';
          });
        } else {
          setState(() {
            _cacheStatus = 'Mevcut ama hatalı format (${(len / 1024).toStringAsFixed(1)} KB)';
          });
        }
      } else {
        setState(() {
          _cacheStatus = 'Boş / Dosya Yok';
          _cacheItemCount = 0;
        });
      }
    } catch (e) {
      setState(() {
        _cacheStatus = 'Hata: $e';
      });
    }
  }

  Future<void> _clearCache() async {
    try {
      if (await _cacheFile.exists()) {
        await _cacheFile.delete();
      }
      await _checkCacheStatus();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Cihazdaki dahili önbellek tamamen temizlendi!'),
          backgroundColor: Color(0xFF00823B),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _runSingleTest(int index) async {
    final test = _tests[index];
    setState(() {
      test.isTesting = true;
      test.isSuccess = null;
      test.errorMessage = null;
      test.statusCode = null;
      test.latencyMs = null;
      test.itemCount = null;
      test.firstItemSummary = null;
      test.categoryCounts = null;
    });

    final stopwatch = Stopwatch()..start();
    try {
      final client = HttpClient()
        ..connectionTimeout = const Duration(seconds: 10)
        ..badCertificateCallback = (cert, host, port) => true;

      final request = await client.getUrl(Uri.parse(test.url));
      request.headers.set('User-Agent', 'YariFiyatina-Diagnostic/1.0 (Android)');
      request.headers.set('Cache-Control', 'no-cache');

      final response = await request.close().timeout(const Duration(seconds: 12));
      stopwatch.stop();

      final body = await response.transform(utf8.decoder).join();

      setState(() {
        test.latencyMs = stopwatch.elapsedMilliseconds;
        test.statusCode = response.statusCode;
        test.isTesting = false;

        if (response.statusCode == 200) {
          test.isSuccess = true;
          // Check if JSON
          try {
            final dynamic decoded = json.decode(body);
            if (decoded is List) {
              test.rawType = 'List (Dizi)';
              test.itemCount = decoded.length;
              if (decoded.isNotEmpty) {
                final first = decoded[0] as Map<String, dynamic>;
                test.firstItemSummary = '[${first['category']}] ${first['store']} - ${first['title']}';

                final counts = <String, int>{};
                for (final it in decoded) {
                  final cat = (it['category'] ?? 'Bilinmeyen').toString();
                  counts[cat] = (counts[cat] ?? 0) + 1;
                }
                test.categoryCounts = counts;
              }
            } else if (decoded is Map) {
              test.rawType = 'Map (Obje)';
              test.errorMessage = 'Sunucu dizi yerine obje döndürdü: ${body.length > 100 ? body.substring(0, 100) : body}';
              if (test.url.contains('extendsclass')) {
                test.isSuccess = false;
              }
            }
          } catch (_) {
            test.rawType = 'HTML / Düz Metin';
          }
        } else {
          test.isSuccess = false;
          test.errorMessage = 'HTTP ${response.statusCode}: ${response.reasonPhrase}\nGövde: ${body.length > 150 ? body.substring(0, 150) : body}';
        }
      });
    } catch (e) {
      stopwatch.stop();
      setState(() {
        test.isTesting = false;
        test.isSuccess = false;
        test.latencyMs = stopwatch.elapsedMilliseconds;
        test.errorMessage = '$e';
      });
    }
  }

  Future<void> _runAllTests() async {
    setState(() {
      _isRunningAll = true;
    });
    for (int i = 0; i < _tests.length; i++) {
      await _runSingleTest(i);
    }
    await _checkCacheStatus();
    setState(() {
      _isRunningAll = false;
    });
  }

  void _copyResultsToClipboard() {
    final buffer = StringBuffer();
    buffer.writeln('=== YARI FİYATINA - BAĞLANTI TEST RAPORU ===');
    buffer.writeln('Test Zamanı: ${DateTime.now().toIso8601String()}');
    buffer.writeln('Dahili Önbellek: $_cacheStatus');
    buffer.writeln('--------------------------------------------');
    for (final t in _tests) {
      buffer.writeln('Test: ${t.title}');
      buffer.writeln('URL: ${t.url}');
      buffer.writeln('Sonuç: ${t.isSuccess == true ? "BAŞARILI" : "BAŞARISIZ"} (${t.statusCode ?? "Yanıt Yok"})');
      buffer.writeln('Süre: ${t.latencyMs ?? 0} ms');
      if (t.itemCount != null) buffer.writeln('Ürün Sayısı: ${t.itemCount}');
      if (t.categoryCounts != null) buffer.writeln('Kategoriler: ${t.categoryCounts}');
      if (t.firstItemSummary != null) buffer.writeln('İlk Ürün: ${t.firstItemSummary}');
      if (t.errorMessage != null) buffer.writeln('Hata: ${t.errorMessage}');
      buffer.writeln('--------------------------------------------');
    }

    Clipboard.setData(ClipboardData(text: buffer.toString()));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('📋 Tüm test sonuçları panoya kopyalandı!'),
        backgroundColor: Color(0xFF1E272E),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        title: const Text(
          '🔍 Mobil Ağ ve Bağlantı Testi',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.white),
        ),
        actions: [
          IconButton(
            tooltip: 'Sonuçları Kopyala',
            icon: const Icon(Icons.copy_rounded, color: Colors.white),
            onPressed: _copyResultsToClipboard,
          ),
          IconButton(
            tooltip: 'Yeniden Test Et',
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFFFFD32A)),
            onPressed: _isRunningAll ? null : _runAllTests,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Banner Bilgilendirme
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF334155)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.info_outline_rounded, color: Color(0xFFFFD32A), size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Bağlantı & Canlı Veri Teşhisi',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  'Bu ekran telefonunuzun interneti ve mobil şebekesi (4.5G/Wi-Fi) üzerinden indirim sunucularına doğrudan erişip erişemediğini test eder.',
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                ),
                const Divider(color: Color(0xFF334155), height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        'Dahili Disk Önbelleği: ${_cacheStatus ?? "Kontrol ediliyor..."}',
                        style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 12),
                      ),
                    ),
                    TextButton.icon(
                      style: TextButton.styleFrom(
                        foregroundColor: const Color(0xFFFF4757),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      ),
                      onPressed: _clearCache,
                      icon: const Icon(Icons.delete_outline_rounded, size: 16),
                      label: const Text('Önbelleği Sil', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Test Kartları
          ..._tests.asMap().entries.map((entry) {
            final idx = entry.key;
            final test = entry.value;
            return _buildTestCard(idx, test);
          }),

          const SizedBox(height: 20),

          // Butonlar
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            onPressed: _isRunningAll ? null : _runAllTests,
            icon: _isRunningAll
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                  )
                : const Icon(Icons.play_arrow_rounded),
            label: Text(
              _isRunningAll ? 'Testler Çalışıyor...' : 'Tüm Testleri Yeniden Başlat',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
          const SizedBox(height: 10),

          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF38BDF8),
              side: const BorderSide(color: Color(0xFF0284C7)),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const StoryFeedScreen()),
              );
            },
            icon: const Icon(Icons.arrow_forward_rounded),
            label: const Text(
              'Ana Uygulamayı Aç (Story Ekranı)',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildTestCard(int index, TestResult test) {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    if (test.isTesting) {
      statusColor = const Color(0xFFFFD32A);
      statusIcon = Icons.hourglass_top_rounded;
      statusText = 'Test Ediliyor...';
    } else if (test.isSuccess == true) {
      statusColor = const Color(0xFF10B981);
      statusIcon = Icons.check_circle_rounded;
      statusText = 'BAŞARILI (${test.statusCode ?? 200})';
    } else if (test.isSuccess == false) {
      statusColor = const Color(0xFFEF4444);
      statusIcon = Icons.cancel_rounded;
      statusText = 'BAŞARISIZ (${test.statusCode ?? "Hata"})';
    } else {
      statusColor = const Color(0xFF64748B);
      statusIcon = Icons.help_outline_rounded;
      statusText = 'Beklemede';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: test.isSuccess == true
              ? const Color(0xFF10B981).withOpacity(0.4)
              : (test.isSuccess == false
                  ? const Color(0xFFEF4444).withOpacity(0.4)
                  : const Color(0xFF334155)),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(statusIcon, color: statusColor, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    test.title,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    statusText,
                    style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              test.url,
              style: const TextStyle(color: Color(0xFF64748B), fontSize: 11, fontFamily: 'monospace'),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),

            // Metrikler
            if (test.latencyMs != null || test.itemCount != null) ...[
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  if (test.latencyMs != null)
                    _badge('Süre: ${test.latencyMs} ms', const Color(0xFF38BDF8)),
                  if (test.rawType != null)
                    _badge('Tip: ${test.rawType}', const Color(0xFFA78BFA)),
                  if (test.itemCount != null)
                    _badge('Ürün: ${test.itemCount} adet', const Color(0xFF34D399)),
                ],
              ),
              const SizedBox(height: 8),
            ],

            // Kategori dağılımı
            if (test.categoryCounts != null && test.categoryCounts!.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Kategoriler: ${test.categoryCounts!.entries.map((e) => "${e.key}: ${e.value}").join(" | ")}',
                  style: const TextStyle(color: Color(0xFFCBD5E1), fontSize: 11, fontWeight: FontWeight.w600),
                ),
              ),
              const SizedBox(height: 6),
            ],

            // İlk ürün özeti
            if (test.firstItemSummary != null) ...[
              Text(
                'İlk Ürün: ${test.firstItemSummary}',
                style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],

            // Hata mesajı
            if (test.errorMessage != null) ...[
              const SizedBox(height: 6),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF450A0A),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF991B1B)),
                ),
                child: SelectableText(
                  'HATA DETAYI:\n${test.errorMessage}',
                  style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 11, fontFamily: 'monospace'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _badge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
      ),
    );
  }
}
