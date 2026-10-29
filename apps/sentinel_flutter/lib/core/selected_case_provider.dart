import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Provider to keep track of the currently active case across the entire application.
/// When a user selects a case in the 'Cases' screen, this value is updated,
/// and all other screens (Logs, AI, Reports, etc.) will automatically react.
final selectedCaseProvider = StateProvider<String?>((ref) => null);
