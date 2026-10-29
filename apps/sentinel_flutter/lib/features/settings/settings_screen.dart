import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Settings & Diagnostics', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 16),
          const Text('API base URL is configured by environment. Secrets are never stored in the client.'),
        ],
      ),
    );
  }
}