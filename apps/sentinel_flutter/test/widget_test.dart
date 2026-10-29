import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sentinel_flutter/main.dart';

void main() {
  testWidgets('App builds', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: SentinelApp()));
    await tester.pumpAndSettle();
    expect(find.text('Overview'), findsWidgets);
  });
}