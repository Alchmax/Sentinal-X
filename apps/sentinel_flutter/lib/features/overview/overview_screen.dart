import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/auth_provider.dart';
import '../../core/global_scan_provider.dart';
import '../../core/selected_case_provider.dart';
import '../cases/login_screen.dart';

class OverviewScreen extends ConsumerWidget {
  const OverviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    if (!auth.isAuthenticated) return LoginScreen();

    final scanState = ref.watch(globalScanProvider);
    final selectedCaseId = ref.watch(selectedCaseProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(context, selectedCaseId),
          const SizedBox(height: 32),
          _buildQuickActions(context, ref, scanState),
          const SizedBox(height: 32),
          Text('Case Summary', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 16),
          _buildMetricsGrid(context),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, String? selectedCaseId) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Sentinel X Dashboard', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, color: Colors.cyanAccent)),
        const SizedBox(height: 8),
        Text(
          selectedCaseId == null 
            ? 'Welcome back. Please run a scan to start your investigation.' 
            : 'Currently analyzing Case: $selectedCaseId', 
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }

  Widget _buildQuickActions(BuildContext context, WidgetRef ref, AsyncValue<String> scanState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Quick Actions', style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            _ActionButton(
              label: scanState.isLoading ? 'Scanning...' : 'Global Device Scan', 
              icon: scanState.isLoading ? Icons.sync : Icons.security, 
              color: Colors.cyanAccent, 
              onTap: () {
                ref.read(globalScanProvider.notifier).runFullDeviceScan();
              }
            ),
            _ActionButton(
              label: 'New Case', 
              icon: Icons.add_circle_outline, 
              color: Colors.blueAccent, 
              onTap: () => context.go('/cases')
            ),
            _ActionButton(
              label: 'Upload Evidence', 
              icon: Icons.upload_file, 
              color: Colors.orangeAccent, 
              onTap: () => context.go('/file-forensics')
            ),
            _ActionButton(
              label: 'Run Analysis', 
              icon: Icons.analytics_outlined, 
              color: Colors.greenAccent, 
              onTap: () => context.go('/log-investigation')
            ),
            _ActionButton(
              label: 'View Reports', 
              icon: Icons.description, 
              color: Colors.purpleAccent, 
              onTap: () => context.go('/reports')
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricsGrid(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: MediaQuery.of(context).size.width < 600 ? 1 : 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 2.5,
      children: const [
        _MetricCard(label: 'Active Cases', value: '0', icon: Icons.folder),
        _MetricCard(label: 'Evidence Items', value: '0', icon: Icons.library_books),
        _MetricCard(label: 'Security Alerts', value: '0', icon: Icons.warning_amber),
        _MetricCard(label: 'Completed Reports', value: '0', icon: Icons.check_circle),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _ActionButton({required this.label, required this.icon, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.5)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(width: 8),
            Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  const _MetricCard({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(color: Colors.cyan.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
              child: Icon(icon, color: Colors.cyanAccent),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(label, style: Theme.of(context).textTheme.labelMedium),
                Text(value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}