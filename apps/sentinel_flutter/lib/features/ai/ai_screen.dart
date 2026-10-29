import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';

final aiAssistantProvider = StateNotifierProvider<AiAssistantNotifier, AsyncValue<String>>((ref) {
  return AiAssistantNotifier(ref.watch(apiClientProvider));
});

class AiAssistantNotifier extends StateNotifier<AsyncValue<String>> {
  final ApiClient api;
  AiAssistantNotifier(this.api) : super(const AsyncValue.data('Hello! I am your Sentinel X AI Assistant. Select a case and ask me about the evidence.'));

  Future<void> askQuestion(String caseId, String question, List<String> contextIds, bool approved) async {
    if (!approved) {
      state = AsyncValue.data('Error: You must approve the context before sending it to the cloud.');
      return;
    }
    state = const AsyncValue.loading();
    try {
      final response = await api.dio.post('/api/v1/ai/chat', data: {
        "case_id": caseId,
        "question": question,
        "context_ids": contextIds,
        "approved": approved,
      });
      state = AsyncValue.data(response.data['answer']);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class AiScreen extends ConsumerStatefulWidget {
  const AiScreen({super.key});
  @override
  ConsumerState<AiScreen> createState() => _AiScreenState();
}

class _AiScreenState extends ConsumerState<AiScreen> {
  final _qCtrl = TextEditingController();
  bool _approved = false;

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final aiState = ref.watch(aiAssistantProvider);

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
              Text('AI Investigation Assistant', style: Theme.of(context).textTheme.headlineMedium),
              Chip(label: Text('Active Case: $selectedCaseId'), backgroundColor: Colors.blue.withValues(alpha: 0.1)),
            ],
          ),
          const SizedBox(height: 8),
          const Text('AI powered analysis of your evidence. Data is sent to Ollama Cloud only after approval.'),
          const SizedBox(height: 24),
          TextField(
            controller: _qCtrl,
            decoration: const InputDecoration(labelText: 'Your Question'),
          ),
          const SizedBox(height: 16),
          CheckboxListTile(
            title: const Text('Approve transmission of evidence to Ollama Cloud'),
            value: _approved,
            onChanged: (v) => setState(() => _approved = v!),
          ),
          FilledButton(
            onPressed: () {
              ref.read(aiAssistantProvider.notifier).askQuestion(
                selectedCaseId,
                _qCtrl.text,
                [],
                _approved
              );
            },
            child: const Text('Ask Assistant'),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(12)),
              child: aiState.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (err, stack) => Text('Error: $err'),
                data: (ans) => SingleChildScrollView(child: Text(ans)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}