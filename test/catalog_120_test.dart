import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:discount_app/models/deal_item.dart';

void main() {
  test('120-Item Live Deals Catalog Integration Test', () async {
    final file = File('assets/data/live_deals.json');
    expect(await file.exists(), isTrue, reason: 'live_deals.json must exist');

    final jsonString = await file.readAsString();
    final List<dynamic> jsonList = json.decode(jsonString) as List<dynamic>;

    expect(jsonList.length, 120, reason: 'Total products must be exactly 120');

    final deals = jsonList.map((item) => DealItem.fromJson(item as Map<String, dynamic>)).toList();
    expect(deals.length, 120);

    final storeCounts = <String, int>{};
    final categoryCounts = <String, int>{};

    for (var i = 0; i < deals.length; i++) {
      final deal = deals[i];
      expect(deal.id.isNotEmpty, isTrue);
      expect(deal.title.isNotEmpty, isTrue);
      expect(deal.productUrl.startsWith('http'), isTrue);
      expect(deal.imageUrl.startsWith('http'), isTrue);
      expect(deal.originalPrice > deal.discountedPrice, isTrue);
      expect(deal.discountedPrice > 0, isTrue);
      expect(deal.discountRate >= 5, isTrue);

      storeCounts[deal.store] = (storeCounts[deal.store] ?? 0) + 1;
      categoryCounts[deal.category] = (categoryCounts[deal.category] ?? 0) + 1;

      // Check consecutive collisions
      if (i < deals.length - 1) {
        final next = deals[i + 1];
        expect(deal.store != next.store, isTrue, reason: 'Consecutive stores cannot collide at index $i');
        expect(deal.category != next.category, isTrue, reason: 'Consecutive categories cannot collide at index $i');
      }
    }

    expect(storeCounts['Amazon TR'], 40);
    expect(storeCounts['Hepsiburada'], 40);
    expect(storeCounts['Idefix'], 40);

    expect(categoryCounts['Teknoloji'], greaterThanOrEqualTo(28));
    expect(categoryCounts['Moda'], greaterThanOrEqualTo(28));
    expect(categoryCounts['Ev & Yaşam'], greaterThanOrEqualTo(28));
    expect(categoryCounts['Kozmetik'], greaterThanOrEqualTo(28));
  });
}
