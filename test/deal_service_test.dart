import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:discount_app/models/deal_item.dart';

void main() {
  test('Fetch from extendsclass endpoint', () async {
    final client = HttpClient()
      ..connectionTimeout = const Duration(seconds: 10)
      ..badCertificateCallback = (cert, host, port) => true;

    final request = await client.getUrl(Uri.parse('https://extendsclass.com/api/json-storage/bin/ccbacbe?t=${DateTime.now().millisecondsSinceEpoch}'));
    final response = await request.close().timeout(const Duration(seconds: 15));

    expect(response.statusCode, 200);

    final responseBody = await response.transform(utf8.decoder).join();
    final List<dynamic> jsonList = json.decode(responseBody) as List<dynamic>;

    expect(jsonList.length, 120);

    final deals = jsonList.map((item) => DealItem.fromJson(item as Map<String, dynamic>)).toList();
    expect(deals.length, 120);

    final stores = <String, int>{};
    for (final d in deals) {
      stores[d.store] = (stores[d.store] ?? 0) + 1;
    }

    expect(stores['Amazon TR'], 40);
    expect(stores['Hepsiburada'], 40);
    expect(stores['Idefix'], 40);
  });
}
