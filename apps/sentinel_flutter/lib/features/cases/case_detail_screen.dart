import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';

final caseDetailProvider = StateNotifierProvider.family<CaseDetailNotifier, AsyncValue<CaseDetailState>, String>((ref, caseId) {
  return CaseDetailNotifier(ref.watch(apiClientProvider), caseId);
});

class CaseDetailState {
  final CaseModel caseData;
  final List<EvidenceModel> evidence;
  final List<FindingModel> findings;
  CaseDetailState({required this.caseData, required this.evidence, required this.findings});
}

class CaseModel {
  final String id, title, description, status, priority;
  CaseModel({required this.id, required this.title, required this.description, required this.status, required this.priority});
  factory CaseModel.fromJson(Map<String, dynamic> json) => CaseModel(
    id: json['id'], title: json['title'], description: json['description'], status: json['status'], priority: json['priority']);
}

class EvidenceModel {
  final String id, filename, sha256;
  EvidenceModel({required this.id, required this.filename, required this.sha256});
  factory EvidenceModel.fromJson(Map<String, dynamic> json) => EvidenceModel(
    id: json['id'], filename: json['filename'], sha256: json['sha256'] ?? 'N/A');
}

class FindingModel {
  final String id, title, description;
  FindingModel({required this.id, required this.title, required this.description});
  factory FindingModel.fromJson(Map<String, dynamic> json) => FindingModel(
    id: json['id'], title: json['title'], description: json['description']);
}

class CaseDetailNotifier extends StateNotifier<AsyncValue<CaseDetailState>> {
  final ApiClient api;
  final String caseId;
  CaseDetailNotifier(this.api, this.caseId) : super(const AsyncValue.loading()) {
    fetch();
  }

  Future<void> fetch() async {
    try {
      final caseRes = await api.dio.get('/api/v1/cases/$caseId');
      final evidenceRes = await api.dio.get('/api/v1/evidence/case/$caseId');
      final findingsRes = await api.dio.get('/api/v1/cases/$caseId/findings');
      
      state = AsyncValue.data(CaseDetailState(
        caseData: CaseModel.fromJson(caseRes.data),
        evidence: (evidenceRes.data as List).map((e) => EvidenceModel.fromJson(e)).toList(),
        findings: (findingsRes.data as List).map((f) => FindingModel.fromJson(f)).toList(),
      ));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class CaseDetailScreen extends ConsumerWidget {
  final String caseId;
  const CaseDetailScreen({super.key, required this.caseId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(caseDetailProvider(caseId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Case Details'),
        actions: [
          FilledButton.icon(
            onPressed: () => _generateReport(context, ref),
            icon: const Icon(Icons.picture_as_pdf),
            label: const Text('Generate Report'),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
        data: (data) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(data.caseData.title, style: Theme.of(context).textTheme.headlineMedium),
              Text('ID: ${data.caseData.id}', style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Description', style: Theme.of(context).textTheme.titleSmall),
                      const SizedBox(height: 8),
                      Text(data.caseData.description),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text('Evidence Inventory', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              ...data.evidence.map((e) => Card(
                child: ListTile(
                  leading: const Icon(Icons.insert_drive_file),
                  title: Text(e.filename),
                  subtitle: Text(e.sha256),
                ),
              )),
              const SizedBox(height: 24),
              Text('Findings', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              ...data.findings.map((f) => Card(
                child: ListTile(
                  leading: const Icon(Icons.lightbulb, color: Colors.yellow),
                  title: Text(f.title),
                  subtitle: Text(f.description),
                ),
              )),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _generateReport(BuildContext context, WidgetRef ref) async {
    try {
      final api = ref.read(apiClientProvider);
      final response = await api.dio.post('/api/v1/reports/generate/$caseId', 
        options: Options(responseType: ResponseType.json));
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Report generated! ID: ${response.data['id']}')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Report failed: $e')),
        );
      }
    }
  }
}