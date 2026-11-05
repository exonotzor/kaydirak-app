import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:discount_app/models/deal_item.dart';

void main() {
  test('Verify category purity from live REST API', () async {
    final client = HttpClient()
      ..connectionTimeout = const Duration(seconds: 10)
      ..badCertificateCallback = (cert, host, port) => true;

    final request = await client.getUrl(Uri.parse('https://extendsclass.com/api/json-storage/bin/ccbacbe?t=${DateTime.now().millisecondsSinceEpoch}'));
    final response = await request.close().timeout(const Duration(seconds: 15));
    expect(response.statusCode, 200);

    final responseBody = await response.transform(utf8.decoder).join();
    final dynamic decoded = json.decode(responseBody);
    List<dynamic> jsonList;
    if (decoded is List) {
      jsonList = decoded;
    } else {
      // If rate-limited on primary, fetch from mirror
      final mirrorReq = await client.getUrl(Uri.parse('https://files.catbox.moe/26w1tx.json'));
      final mirrorResp = await mirrorReq.close();
      final mirrorBody = await mirrorResp.transform(utf8.decoder).join();
      jsonList = json.decode(mirrorBody) as List<dynamic>;
    }
    final deals = jsonList.map((item) => DealItem.fromJson(item as Map<String, dynamic>)).toList();

    final catCounts = <String, int>{};
    for (final d in deals) {
      catCounts[d.category] = (catCounts[d.category] ?? 0) + 1;
    }
    print('Dart category counts: $catCounts');

    expect(deals.length, 120);

    final techDeals = deals.where((d) => d.category == 'Teknoloji').toList();
    final modaDeals = deals.where((d) => d.category == 'Moda').toList();
    final homeDeals = deals.where((d) => d.category == 'Ev & Yaşam').toList();
    final cosmDeals = deals.where((d) => d.category == 'Kozmetik').toList();

    expect(techDeals.length, 30);
    expect(modaDeals.length, 30);
    expect(homeDeals.length, 30);
    expect(cosmDeals.length, 30);

    // Verify Teknoloji has NO cosmetics or clothes
    for (final t in techDeals) {
      final title = t.title.toLowerCase();
      expect(title.contains('krem'), isFalse, reason: 'Teknoloji should not contain krem: ${t.title}');
      expect(title.contains('serum'), isFalse, reason: 'Teknoloji should not contain serum: ${t.title}');
      expect(title.contains('yelek'), isFalse, reason: 'Teknoloji should not contain yelek: ${t.title}');
      expect(title.contains('kapri'), isFalse, reason: 'Teknoloji should not contain kapri: ${t.title}');
      expect(title.contains('şort'), isFalse, reason: 'Teknoloji should not contain şort: ${t.title}');
      expect(title.contains('sabun'), isFalse, reason: 'Teknoloji should not contain sabun: ${t.title}');
      expect(title.contains('buzluk'), isFalse, reason: 'Teknoloji should not contain buzluk: ${t.title}');
    }

    // Verify cosmetic brands are NEVER in Teknoloji
    final niveaInTech = techDeals.where((d) => d.title.toLowerCase().contains('nivea')).toList();
    final neutroInTech = techDeals.where((d) => d.title.toLowerCase().contains('neutrogena')).toList();
    expect(niveaInTech.isEmpty, isTrue);
    expect(neutroInTech.isEmpty, isTrue);
  });
}
