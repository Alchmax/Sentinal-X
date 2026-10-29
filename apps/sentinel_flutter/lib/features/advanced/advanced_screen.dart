import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';
import '../../core/selected_case_provider.dart';
import '../../features/cases/login_screen.dart';

final advancedProvider = StateNotifierProvider<AdvancedNotifier, AsyncValue<Map<String, dynamic>>>((ref) {
  return AdvancedNotifier(ref.watch(apiClientProvider));
});

class AdvancedNotifier extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  final ApiClient api;
  AdvancedNotifier(this.api) : super(const AsyncValue.data({}));

  Future<void> checkHash(String hash) async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.post('/api/v1/advanced/threat-intel/check-hash', queryParameters: {'hash_value': hash});
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> listProcesses() async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.get('/api/v1/advanced/processes');
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> deployCanaries() async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.post('/api/v1/advanced/canary/deploy');
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> checkCanaries() async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.get('/api/v1/advanced/canary/status');
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> listConnections() async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.get('/api/v1/advanced/network/connections');
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> verifyChain(String caseId) async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.post('/api/v1/advanced/evidence/verify-chain', queryParameters: {'case_id': caseId});
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> getMitreMappings() async {
    state = const AsyncValue.loading();
    try {
      final res = await api.dio.get('/api/v1/advanced/mitre/mappings');
      state = AsyncValue.data(Map<String, dynamic>.from(res.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

class AdvancedScreen extends ConsumerStatefulWidget {
  const AdvancedScreen({super.key});
  @override
  ConsumerState<AdvancedScreen> createState() => _AdvancedScreenState();
}

class _AdvancedScreenState extends ConsumerState<AdvancedScreen> {
  final _hashCtrl = TextEditingController();
  int _selectedTab = 0;

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final selectedCaseId = ref.watch(selectedCaseProvider);
    final advancedState = ref.watch(advancedProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Advanced Security Lab', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          const Text('Threat intelligence, memory forensics, ransomware protection, and more.'),
          const SizedBox(height: 16),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _TabButton('Threat Intel', 0, _selectedTab, (i) => setState(() => _selectedTab = i)),
                _TabButton('Processes', 1, _selectedTab, (i) => setState(() => _selectedTab = i)),
                _TabButton('Canary Files', 2, _selectedTab, (i) => setState(() => _selectedTab = i)),
                _TabButton('Network', 3, _selectedTab, (i) => setState(() => _selectedTab = i)),
                _TabButton('MITRE ATT&CK', 4, _selectedTab, (i) => setState(() => _selectedTab = i)),
                _TabButton('Chain of Custody', 5, _selectedTab, (i) => setState(() => _selectedTab = i)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: advancedState.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
              data: (data) => _buildTabContent(context, ref, _selectedTab, data, selectedCaseId),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabContent(BuildContext context, WidgetRef ref, int tab, Map<String, dynamic> data, String? caseId) {
    switch (tab) {
      case 0: return _buildThreatIntel(context, ref, data);
      case 1: return _buildProcesses(context, ref, data);
      case 2: return _buildCanary(context, ref, data);
      case 3: return _buildNetwork(context, ref, data);
      case 4: return _buildMitre(context, ref, data);
      case 5: return _buildChainOfCustody(context, ref, data, caseId);
      default: return const SizedBox();
    }
  }

  Widget _buildThreatIntel(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(child: TextField(controller: _hashCtrl, decoration: const InputDecoration(labelText: 'File Hash (MD5/SHA-1/SHA-256)'))),
            const SizedBox(width: 12),
            FilledButton(onPressed: () => ref.read(advancedProvider.notifier).checkHash(_hashCtrl.text), child: const Text('Check Hash')),
          ],
        ),
        const SizedBox(height: 16),
        if (data.isNotEmpty) ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Result', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text('Hash: ${data['hash'] ?? 'N/A'}'),
                  Text('Type: ${data['hash_type'] ?? 'N/A'}'),
                  Text('Malicious: ${data['is_malicious'] ?? 'N/A'}'),
                  Text('Threat: ${data['threat_name'] ?? 'N/A'}'),
                  Text('Confidence: ${data['confidence'] ?? 'N/A'}'),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildProcesses(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    return Column(
      children: [
        FilledButton.icon(onPressed: () => ref.read(advancedProvider.notifier).listProcesses(), icon: const Icon(Icons.memory), label: const Text('Scan Processes')),
        const SizedBox(height: 16),
        if (data.isNotEmpty) ...[
          Text('Total: ${data['total'] ?? 0} | Suspicious: ${data['suspicious'] ?? 0}'),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.builder(
              itemCount: (data['processes'] as List?)?.length ?? 0,
              itemBuilder: (_, i) {
                final p = (data['processes'] as List)[i];
                return Card(
                  color: p['suspicious'] == true ? Colors.red.withValues(alpha: 0.1) : null,
                  child: ListTile(
                    leading: Icon(p['suspicious'] == true ? Icons.warning : Icons.check_circle, color: p['suspicious'] == true ? Colors.red : Colors.green),
                    title: Text('${p['name']} (PID: ${p['pid']})'),
                    subtitle: Text('Memory: ${p['memory']}'),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildCanary(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    return Column(
      children: [
        Row(
          children: [
            FilledButton.icon(onPressed: () => ref.read(advancedProvider.notifier).deployCanaries(), icon: const Icon(Icons.security), label: const Text('Deploy Canaries')),
            const SizedBox(width: 12),
            FilledButton.icon(onPressed: () => ref.read(advancedProvider.notifier).checkCanaries(), icon: const Icon(Icons.check), label: const Text('Check Status')),
          ],
        ),
        const SizedBox(height: 16),
        if (data.isNotEmpty) ...[
          Text('Status: ${data['status'] ?? 'N/A'}'),
          if (data['directory'] != null) Text('Directory: ${data['directory']}'),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.builder(
              itemCount: (data['files'] as List?)?.length ?? 0,
              itemBuilder: (_, i) {
                final f = (data['files'] as List)[i];
                return Card(
                  color: f['triggered'] == true ? Colors.red.withValues(alpha: 0.1) : null,
                  child: ListTile(
                    leading: Icon(f['triggered'] == true ? Icons.warning : Icons.check_circle, color: f['triggered'] == true ? Colors.red : Colors.green),
                    title: Text(f['name'] ?? ''),
                    subtitle: Text(f['path'] ?? ''),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildNetwork(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    return Column(
      children: [
        FilledButton.icon(onPressed: () => ref.read(advancedProvider.notifier).listConnections(), icon: const Icon(Icons.wifi), label: const Text('Scan Network Connections')),
        const SizedBox(height: 16),
        if (data.isNotEmpty) ...[
          Text('Total: ${data['total'] ?? 0} | Suspicious: ${data['suspicious'] ?? 0}'),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.builder(
              itemCount: (data['connections'] as List?)?.length ?? 0,
              itemBuilder: (_, i) {
                final c = (data['connections'] as List)[i];
                return Card(
                  color: c['suspicious'] == true ? Colors.red.withValues(alpha: 0.1) : null,
                  child: ListTile(
                    leading: Icon(c['suspicious'] == true ? Icons.warning : Icons.check_circle, color: c['suspicious'] == true ? Colors.red : Colors.green),
                    title: Text('${c['protocol']} ${c['local']} → ${c['remote']}'),
                    subtitle: Text('State: ${c['state']} | PID: ${c['pid']}'),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildMitre(BuildContext context, WidgetRef ref, Map<String, dynamic> data) {
    return Column(
      children: [
        FilledButton.icon(onPressed: () => ref.read(advancedProvider.notifier).getMitreMappings(), icon: const Icon(Icons.map), label: const Text('Load MITRE Mappings')),
        const SizedBox(height: 16),
        if (data.isNotEmpty)
          Expanded(
            child: ListView.builder(
              itemCount: data.length,
              itemBuilder: (_, i) {
                final key = data.keys.elementAt(i);
                final val = data[key];
                return Card(
                  child: ListTile(
                    leading: const Icon(Icons.security),
                    title: Text('${val['id']} - ${val['name']}'),
                    subtitle: Text('Tactic: ${val['tactic']}'),
                    trailing: const Icon(Icons.open_in_new),
                  ),
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _buildChainOfCustody(BuildContext context, WidgetRef ref, Map<String, dynamic> data, String? caseId) {
    if (caseId == null) {
      return const Center(child: Text('Please run a Global Device Scan first.'));
    }
    return Column(
      children: [
        FilledButton.icon(
          onPressed: () => ref.read(advancedProvider.notifier).verifyChain(caseId),
          icon: const Icon(Icons.verified),
          label: const Text('Verify Evidence Chain'),
        ),
        const SizedBox(height: 16),
        if (data.isNotEmpty) ...[
          Text('Total: ${data['total_evidence'] ?? 0} | Verified: ${data['verified'] ?? 0} | Chain Intact: ${data['chain_intact'] ?? false}'),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.builder(
              itemCount: (data['details'] as List?)?.length ?? 0,
              itemBuilder: (_, i) {
                final d = (data['details'] as List)[i];
                return Card(
                  color: d['verified'] == true ? Colors.green.withValues(alpha: 0.1) : Colors.red.withValues(alpha: 0.1),
                  child: ListTile(
                    leading: Icon(d['verified'] == true ? Icons.check_circle : Icons.error, color: d['verified'] == true ? Colors.green : Colors.red),
                    title: Text(d['filename'] ?? ''),
                    subtitle: Text('SHA-256: ${d['sha256'] ?? 'N/A'}'),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }
}

class _TabButton extends StatelessWidget {
  final String label;
  final int index;
  final int selected;
  final ValueChanged<int> onTap;
  const _TabButton(this.label, this.index, this.selected, this.onTap);
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilledButton(
        onPressed: () => onTap(index),
        style: FilledButton.styleFrom(
          backgroundColor: selected == index ? Colors.cyanAccent : Colors.grey[800],
          foregroundColor: selected == index ? Colors.black : Colors.white,
        ),
        child: Text(label),
      ),
    );
  }
}