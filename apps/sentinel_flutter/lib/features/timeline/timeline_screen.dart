import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';

final timelineProvider = StateNotifierProvider<TimelineNotifier, AsyncValue<List<TimelineEntry>>>((ref) {
  return TimelineNotifier(ref.watch(apiClientProvider));
});

class TimelineEntry {
  final String id, timestamp, title, description, type;
  TimelineEntry({required this.id, required this.timestamp, required this.title, required this.description, required this.type});
  factory TimelineEntry.fromJson(Map<String, dynamic> json) => TimelineEntry(
    id: json['id'], timestamp: json['timestamp'] ?? '', title: json['title'] ?? '', description: json['description'] ?? '', type: json['entry_type'] ?? '');
}

class TimelineNotifier extends StateNotifier<AsyncValue<List<TimelineEntry>>> {
  final ApiClient api;
  TimelineNotifier(this.api) : super(const AsyncValue.data([]));

  Future<void> buildTimeline(String caseId) async {
    try {
      await api.dio.post('/api/v1/timeline/build/$caseId');
      final res = await api.dio.get('/api/v1/timeline/$caseId');
      state = AsyncValue.data((res.data as List).map((e) => TimelineEntry.fromJson(e)).toList());
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class TimelineScreen extends ConsumerStatefulWidget {
  const TimelineScreen({super.key});
  @override
  ConsumerState<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends ConsumerState<TimelineScreen> {
  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final timelineAsync = ref.watch(timelineProvider);

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
              Text('Evidence Timeline', style: Theme.of(context).textTheme.headlineMedium),
              Chip(label: Text('Active Case: $selectedCaseId'), backgroundColor: Colors.blue.withValues(alpha: 0.1)),
            ],
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => ref.read(timelineProvider.notifier).buildTimeline(selectedCaseId),
            icon: const Icon(Icons.timeline),
            label: const Text('Build Timeline'),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: timelineAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
              data: (entries) {
                if (entries.isEmpty) return const Center(child: Text('No timeline entries. Build one for a case.'));
                return ListView.builder(
                  itemCount: entries.length,
                  itemBuilder: (_, i) {
                    final e = entries[i];
                    return ListTile(
                      leading: Icon(Icons.event, color: Colors.cyanAccent),
                      title: Text(e.title),
                      subtitle: Text('${e.timestamp} - ${e.type}'),
                      trailing: const Icon(Icons.arrow_forward),
                      onTap: () {},
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