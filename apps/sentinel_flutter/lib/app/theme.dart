import 'package:flutter/material.dart';

ThemeData buildTheme() {
  const seed = Color(0xFF00BCD4);
  final scheme = ColorScheme.fromSeed(
    seedColor: seed,
    brightness: Brightness.dark,
  ).copyWith(
    surface: const Color(0xFF14181C),
    surfaceContainerHighest: const Color(0xFF1E242A),
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: const Color(0xFF0E1114),
    cardTheme: CardThemeData(
      color: const Color(0xFF1A1F24),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0xFF2A3138)),
      ),
    ),
    inputDecorationTheme: const InputDecorationTheme(
      border: OutlineInputBorder(),
    ),
  );
}