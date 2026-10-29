import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

const navItems = <(String, String, IconData)>[
  ('/', 'Overview', Icons.dashboard_outlined),
  ('/cases', 'Cases', Icons.folder_outlined),
  ('/file-forensics', 'File Forensics', Icons.fingerprint),
  ('/log-investigation', 'Log Investigation', Icons.receipt_long_outlined),
  ('/integrity', 'Integrity Monitor', Icons.verified_user_outlined),
  ('/timeline', 'Evidence Timeline', Icons.timeline),
  ('/reports', 'Reports', Icons.description_outlined),
  ('/ai', 'AI Assistant', Icons.smart_toy_outlined),
  ('/advanced', 'Advanced Lab', Icons.science_outlined),
  ('/settings', 'Settings', Icons.settings_outlined),
];

class AppNavigation extends StatelessWidget {
  final Widget child;
  const AppNavigation({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    final isWide = MediaQuery.of(context).size.width >= 900;
    if (isWide) {
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              extended: true,
              selectedIndex: navItems.indexWhere((e) => e.$1 == location).clamp(0, navItems.length - 1),
              onDestinationSelected: (i) => context.go(navItems[i].$1),
              destinations: navItems
                  .map((e) => NavigationRailDestination(icon: Icon(e.$3), label: Text(e.$2)))
                  .toList(),
            ),
            const VerticalDivider(width: 1),
            Expanded(child: child),
          ],
        ),
      );
    }
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navItems.indexWhere((e) => e.$1 == location).clamp(0, navItems.length - 1),
        onDestinationSelected: (i) => context.go(navItems[i].$1),
        destinations: navItems
            .map((e) => NavigationDestination(icon: Icon(e.$3), label: e.$2))
            .toList(),
      ),
    );
  }
}