import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/auth_provider.dart';

final casesProvider = StateNotifierProvider<CasesNotifier, AsyncValue<List<CaseModel>>>((ref) {
  return CasesNotifier(ref.watch(apiClientProvider));
});

class CaseModel {
  final String id;
  final String title;
  final String description;
  final String status;
  final String priority;
  final List<String> tags;
  CaseModel({required this.id, required this.title, required this.description, required this.status, required this.priority, required this.tags});

  factory CaseModel.fromJson(Map<String, dynamic> json) => CaseModel(
        id: json['id'],
        title: json['title'],
        description: json['description'],
        status: json['status'],
        priority: json['priority'],
        tags: List<String>.from(json['tags'] ?? []),
      );
}

class CasesNotifier extends StateNotifier<AsyncValue<List<CaseModel>>> {
  final ApiClient api;
  CasesNotifier(this.api) : super(const AsyncValue.loading()) {
    fetch();
  }

  Future<void> fetch() async {
    try {
      final response = await api.dio.get('/api/v1/cases');
      final items = (response.data['items'] as List).map((e) => CaseModel.fromJson(e)).toList();
      state = AsyncValue.data(items);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> create(String title, String description, List<String> tags) async {
    try {
      await api.dio.post('/api/v1/cases', data: {
        'title': title,
        'description': description,
        'tags': tags,
      });
      await fetch();
    } catch (e) {
      // error handling
    }
  }
}
