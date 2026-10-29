import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';

final logAnalysisProvider = StateNotifierProvider<LogAnalysisNotifier, AsyncValue<LogAnalysisState>>((ref) {
  return LogAnalysisNotifier(ref.watch(apiClientProvider));
});

class LogAnalysisState {
  final List<LogEventModel> events;
  final List<DetectionModel> detections;
  LogAnalysisState({required this.events, required this.detections});
}

class LogEventModel {
  final String id, timestamp, source, eventType, severity, actor, target, message;
  LogEventModel({required this.id, required this.timestamp, required this.source, required this.eventType, required this.severity, required this.actor, required this.target, required this.message});
  factory LogEventModel.fromJson(Map<String, dynamic> json) => LogEventModel(
    id: json['id'] ?? '', timestamp: json['timestamp'] ?? '', source: json['source'] ?? '', eventType: json['event_type'] ?? '', severity: json['severity'] ?? '', actor: json['actor'] ?? '', target: json['target'] ?? '', message: json['message'] ?? '');
}

class DetectionModel {
  final String ruleId, title, description, severity;
  final List<String> eventIds;
  DetectionModel({required this.ruleId, required this.title, required this.description, required this.severity, required this.eventIds});
  factory DetectionModel.fromJson(Map<String, dynamic> json) => DetectionModel(
    ruleId: json['rule_id'] ?? '', title: json['title'] ?? '', description: json['description'] ?? '', severity: json['severity'] ?? '', eventIds: List<String>.from(json['event_ids'] ?? []));
}

class LogAnalysisNotifier extends StateNotifier<AsyncValue<LogAnalysisState>> {
  final ApiClient api;
  LogAnalysisNotifier(this.api) : super(AsyncValue.data(LogAnalysisState(events: [], detections: [])));

  Future<void> importLog(String caseId, FormData formData) async {
    state = const AsyncValue.loading();
    try {
      await api.dio.post('/api/v1/log-analysis/import', data: formData, queryParameters: {'case_id': caseId});
      await fetchEvents(caseId);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> fetchEvents(String caseId) async {
    try {
      final res = await api.dio.get('/api/v1/log-analysis/events/$caseId');
      final events = (res.data as List).map((e) => LogEventModel.fromJson(e)).toList();
      state = AsyncValue.data(LogAnalysisState(events: events, detections: []));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> runDetections(String caseId) async {
    try {
      final res = await api.dio.post('/api/v1/log-analysis/detect/$caseId');
      final dets = (res.data as List).map((e) => DetectionModel.fromJson(e)).toList();
      state = AsyncValue.data(LogAnalysisState(events: state.value?.events ?? [], detections: dets));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class LogScreen extends ConsumerStatefulWidget {
  const LogScreen({super.key});
  @override
  ConsumerState<LogScreen> createState() => _LogScreenState();
}

class _LogScreenState extends ConsumerState<LogScreen> {
  void _importLog(String caseId) async {
    final res = await FilePicker.platform.pickFiles(withData: true);
    if (res == null) return;
    
    final file = res.files.first;
    final formData = FormData.fromMap({
      "file": MultipartFile.fromBytes(file.bytes!, filename: file.name),
    });

    await ref.read(logAnalysisProvider.notifier).importLog(caseId, formData);
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return const LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final logState = ref.watch(logAnalysisProvider);

    if (selectedCaseId == null) {
      return const Center(child: Text('Please select a case from the Cases screen first.'));
    }

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Log Investigation', style: Theme.of(context).textTheme.headlineMedium),
              Chip(label: Text('Active Case: $selectedCaseId'), backgroundColor: Colors.blue.withValues(alpha: 0.1)),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              FilledButton.icon(onPressed: () => _importLog(selectedCaseId), icon: const Icon(Icons.upload_file), label: const Text('Import Log')),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: () => ref.read(logAnalysisProvider.notifier).runDetections(selectedCaseId),
                icon: const Icon(Icons.analytics),
                label: const Text('Run Detections'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: logState.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
              data: (data) {
                return Column(
                  children: [
                    if (data.detections.isNotEmpty) ...[
                      Text('Detections', style: Theme.of(context).textTheme.titleLarge),
                      ListView(
                        shrinkWrap: true,
                        children: data.detections.map((d) => Card(
                          color: Colors.red.withValues(alpha: 0.1),
                          child: ListTile(
                            leading: const Icon(Icons.warning, color: Colors.red),
                            title: Text(d.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text(d.description),
                          ),
                        )).toList(),
                      ),
                      const SizedBox(height: 24),
                    ],
                    Text('Event Timeline', style: Theme.of(context).textTheme.titleLarge),
                    Expanded(
                      child: ListView.builder(
                        itemCount: data.events.length,
                        itemBuilder: (BuildContext context, int i) {
                          final e = data.events[i];
                          return Card(
                            child: ListTile(
                              leading: Text(e.timestamp.split('T')[0]),
                              title: Text('${e.eventType} - ${e.actor}'),
                              subtitle: Text(e.message),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
