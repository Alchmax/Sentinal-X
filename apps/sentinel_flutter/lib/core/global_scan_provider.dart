import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';

final globalScanProvider = StateNotifierProvider<GlobalScanNotifier, AsyncValue<String>>((ref) {
  return GlobalScanNotifier(ref.watch(apiClientProvider), ref);
});

class GlobalScanNotifier extends StateNotifier<AsyncValue<String>> {
  final ApiClient api;
  final Ref ref;

  GlobalScanNotifier(this.api, this.ref) : super(const AsyncValue.data(''));

  Future<void> runFullDeviceScan() async {
    state = const AsyncValue.loading();
    try {
      // 1. Trigger the full scan on the backend.
      final response = await api.dio.post('/api/v1/forensics/full-scan', data: {
        'scan_type': 'full_device',
        'timestamp': DateTime.now().toIso8601String(),
      });

      // 2. The backend creates a new case automatically for this scan.
      final caseId = response.data['case_id'] as String;
      final entryCount = response.data['entry_count'] as int? ?? 0;

      // 3. SET THIS AS THE GLOBAL ACTIVE CASE
      ref.read(selectedCaseProvider.notifier).state = caseId;

      state = AsyncValue.data('Scan complete! Found $entryCount files. Case: $caseId');
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}
