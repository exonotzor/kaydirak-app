import 'package:flutter_test/flutter_test.dart';
import 'package:discount_app/main.dart';

void main() {
  testWidgets('DiscountApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const DiscountApp());
    expect(find.byType(DiscountApp), findsOneWidget);
  });
}
