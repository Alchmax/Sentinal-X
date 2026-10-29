import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';

final reportsProvider = StateNotifierProvider<ReportsNotifier, AsyncValue<List<ReportModel>>>((ref) {
  return ReportsNotifier(ref.watch(apiClientProvider));
});

class ReportModel {
  final String id, title, format;
  ReportModel({required this.id, required this.title, required this.format});
  factory ReportModel.fromJson(Map<String, dynamic> json) => ReportModel(
    id: json['id'], title: json['title'], format: json['format']);
}

class ReportsNotifier extends StateNotifier<AsyncValue<List<ReportModel>>> {
  final ApiClient api;
  ReportsNotifier(this.api) : super(const AsyncValue.data([]));

  Future<void> fetchReports(String caseId) async {
    try {
      final res = await api.dio.get('/api/v1/reports/case/$caseId');
      state = AsyncValue.data((res.data as List).map((e) => ReportModel.fromJson(e)).toList());
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> generateReport(String caseId) async {
    try {
      await api.dio.post('/api/v1/reports/generate/$caseId');
      await fetchReports(caseId);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class ReportsScreen extends ConsumerStatefulWidget {
  const ReportsScreen({super.key});
  @override
  ConsumerState<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends ConsumerState<ReportsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final caseId = ref.read(selectedCaseProvider);
      if (caseId != null) {
        ref.read(reportsProvider.notifier).fetchReports(caseId);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final reportsAsync = ref.watch(reportsProvider);

    if (selectedCaseId == null) {
      return const Center(child: Text('Please run a Global Device Scan first to create a case.'));
    }

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Investigation Reports', style: Theme.of(context).textTheme.headlineMedium),
              Chip(label: Text('Active Case: $selectedCaseId'), backgroundColor: Colors.blue.withValues(alpha: 0.1)),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              FilledButton.icon(
                onPressed: () => ref.read(reportsProvider.notifier).generateReport(selectedCaseId),
                icon: const Icon(Icons.picture_as_pdf),
                label: const Text('Generate Report'),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: () => ref.read(reportsProvider.notifier).fetchReports(selectedCaseId),
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: reportsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
              data: (reports) {
                if (reports.isEmpty) return const Center(child: Text('No reports found for this case. Generate one first.'));
                return ListView.builder(
                  itemCount: reports.length,
                  itemBuilder: (_, i) {
                    final r = reports[i];
                    return Card(
                      child: ListTile(
                        leading: const Icon(Icons.description),
                        title: Text(r.title),
                        subtitle: Text('Format: ${r.format}'),
                        trailing: const Icon(Icons.download),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}