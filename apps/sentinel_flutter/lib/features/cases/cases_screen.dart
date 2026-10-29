import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/auth_provider.dart';
import 'cases_provider.dart';
import 'login_screen.dart';

class CasesScreen extends ConsumerStatefulWidget {
  const CasesScreen({super.key});
  @override
  ConsumerState<CasesScreen> createState() => _CasesScreenState();
}

class _CasesScreenState extends ConsumerState<CasesScreen> {
  final _titleCtrl = TextEditingController();
  bool _isScanning = false;

  void _showCreate() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Create New Investigation'),
        content: TextField(
          controller: _titleCtrl, 
          decoration: const InputDecoration(
            labelText: 'Case Title',
            hintText: 'e.g., Incident-2024-001',
          )
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (_titleCtrl.text.trim().isNotEmpty) {
                ref.read(casesProvider.notifier).create(_titleCtrl.text, "New investigation case", []);
                _titleCtrl.clear();
                Navigator.of(dialogContext).pop();
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  Future<void> _runDeviceScan() async {
    setState(() => _isScanning = true);
    try {
      final api = ref.read(apiClientProvider);
      final response = await api.dio.post('/api/v1/integrity/baseline', data: {
        "root_path": "C:/Users", 
        "case_id": null
      });
      
      if (mounted) {
        if (response.statusCode == 200) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Scan complete! Found ${response.data['entry_count']} files.')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Scan failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isScanning = false);
      }
    }
  }

  void _showDeviceScan() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Full Device Scan'),
        content: const Text('This will initiate a deep scan of the filesystem for suspicious patterns. This may take several minutes.'),
        actions: [
          TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              _runDeviceScan();
            },
            child: const Text('Start Scan'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final casesAsync = ref.watch(casesProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            alignment: WrapAlignment.start,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 12,
            runSpacing: 12,
            children: [
              Text('Cases', style: Theme.of(context).textTheme.headlineMedium),
              FilledButton.icon(
                onPressed: _isScanning ? null : _showDeviceScan, 
                icon: _isScanning 
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) 
                  : const Icon(Icons.search), 
                label: Text(_isScanning ? 'Scanning...' : 'Device Scan'),
                style: FilledButton.styleFrom(backgroundColor: Colors.orangeAccent),
              ),
              FilledButton.icon(
                onPressed: _showCreate, 
                icon: const Icon(Icons.add), 
                label: const Text('New Case'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: casesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error loading cases: $err')),
              data: (cases) {
                if (cases.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.folder_open, size: 64, color: Colors.grey[600]),
                        const SizedBox(height: 16),
                        const Text('No active cases found.'),
                        const SizedBox(height: 8),
                        TextButton(onPressed: _showCreate, child: const Text('Create your first case')),
                      ],
                    ),
                  );
                }
                return ListView.builder(
                  itemCount: cases.length,
                  itemBuilder: (_, i) {
                    final c = cases[i];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: const Icon(Icons.folder),
                        title: Text(c.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text('Status: ${c.status} • Priority: ${c.priority}'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => context.go('/cases/${c.id}'),
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