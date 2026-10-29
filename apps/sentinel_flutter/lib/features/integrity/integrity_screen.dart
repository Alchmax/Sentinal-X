import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';


final integrityProvider = StateNotifierProvider<IntegrityNotifier, AsyncValue<List<IntegrityDiff>>>((ref) {
  return IntegrityNotifier(ref.watch(apiClientProvider));
});

class IntegrityDiff {
  final List<String> added;
  final List<String> deleted;
  final List<Map<String, dynamic>> modified;
  IntegrityDiff({required this.added, required this.deleted, required this.modified});
  factory IntegrityDiff.fromJson(Map<String, dynamic> json) => IntegrityDiff(
    added: List<String>.from(json['added'] ?? []),
    deleted: List<String>.from(json['deleted'] ?? []),
    modified: List<Map<String, dynamic>>.from(json['modified'] ?? []),
  );
}

class IntegrityNotifier extends StateNotifier<AsyncValue<List<IntegrityDiff>>> {
  final ApiClient api;
  IntegrityNotifier(this.api) : super(const AsyncValue.data([]));

  Future<void> createBaseline(String rootPath, String? caseId) async {
    try {
      await api.dio.post('/api/v1/integrity/baseline', data: {"root_path": rootPath, "case_id": caseId});
      state = AsyncValue.data([]);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> rescan(String baselineId) async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.post('/api/v1/integrity/rescan', data: {"baseline_id": baselineId});
      state = AsyncValue.data([IntegrityDiff.fromJson(res.data)]);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class IntegrityScreen extends ConsumerStatefulWidget {
  const IntegrityScreen({super.key});
  @override
  ConsumerState<IntegrityScreen> createState() => _IntegrityScreenState();
}

class _IntegrityScreenState extends ConsumerState<IntegrityScreen> {
  final _pathCtrl = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final integrityAsync = ref.watch(integrityProvider);

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
              Text('File Integrity Monitor', style: Theme.of(context).textTheme.headlineMedium),
              Chip(label: Text('Active Case: $selectedCaseId'), backgroundColor: Colors.blue.withValues(alpha: 0.1)),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _pathCtrl,
                  decoration: const InputDecoration(labelText: 'Directory Path', hintText: 'C:/Windows/System32'),
                ),
              ),
              const SizedBox(width: 16),
              FilledButton(
                onPressed: () => ref.read(integrityProvider.notifier).createBaseline(_pathCtrl.text, selectedCaseId),
                child: const Text('Create Baseline'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: integrityAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
              data: (diffs) {
                if (diffs.isEmpty) return const Center(child: Text('No scan results yet. Create a baseline and rescan.'));
                final diff = diffs.first;
                return ListView(
                  children: [
                    _diffSection('Added Files', diff.added, Colors.green),
                    _diffSection('Deleted Files', diff.deleted, Colors.red),
                    _diffSection('Modified Files', diff.modified.map((m) => m['path'].toString()).toList(), Colors.orange),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _diffSection(String title, List<String> items, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Text(title, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
        ),
        ...items.map((i) => Card(child: ListTile(title: Text(i)))),
        const SizedBox(height: 16),
      ],
    );
  }
}