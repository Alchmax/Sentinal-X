import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../shared/navigation.dart';
import '../features/overview/overview_screen.dart';
import '../features/cases/cases_screen.dart';
import '../features/cases/case_detail_screen.dart';
import '../features/cases/login_screen.dart';
import '../features/cases/register_screen.dart';
import '../features/file_forensics/file_forensics_screen.dart';
import '../features/log_investigation/log_screen.dart';
import '../features/integrity/integrity_screen.dart';
import '../features/timeline/timeline_screen.dart';
import '../features/reports/reports_screen.dart';
import '../features/ai/ai_screen.dart';
import '../features/advanced/advanced_screen.dart';
import '../features/settings/settings_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/login', builder: (_, _) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, _) => const RegisterScreen()),
      ShellRoute(
        builder: (context, state, child) => AppNavigation(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, _) => const OverviewScreen()),
          GoRoute(path: '/cases', builder: (_, _) => const CasesScreen()),
          GoRoute(path: '/cases/:id', builder: (_, state) => CaseDetailScreen(caseId: state.pathParameters['id']!)),
          GoRoute(path: '/file-forensics', builder: (_, _) => const FileForensicsScreen()),
          GoRoute(path: '/log-investigation', builder: (_, _) => const LogScreen()),
          GoRoute(path: '/integrity', builder: (_, _) => const IntegrityScreen()),
          GoRoute(path: '/timeline', builder: (_, _) => const TimelineScreen()),
          GoRoute(path: '/reports', builder: (_, _) => const ReportsScreen()),
          GoRoute(path: '/ai', builder: (_, _) => const AiScreen()),
          GoRoute(path: '/advanced', builder: (_, _) => const AdvancedScreen()),
          GoRoute(path: '/settings', builder: (_, _) => const SettingsScreen()),
        ],
      ),
    ],
  );
});
