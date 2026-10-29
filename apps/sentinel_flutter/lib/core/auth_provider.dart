import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_client.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  // Use a configurable base URL. For dev, it's localhost:8001.
  // Use a configurable base URL. Override with --dart-define=API_BASE_URL=https://your-api.onrender.com
  return ApiClient(baseUrl: const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8081'));
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(apiClientProvider));
});

class AuthState {
  final String? token;
  final bool isAuthenticated;
  AuthState({this.token, this.isAuthenticated = false});

  factory AuthState.guest() => AuthState(token: null, isAuthenticated: false);
  factory AuthState.authenticated(String token) => AuthState(token: token, isAuthenticated: true);
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient api;
  final _storage = const FlutterSecureStorage();

  AuthNotifier(this.api) : super(AuthState.guest()) {
    _init();
  }

  Future<void> _init() async {
    final token = await _storage.read(key: 'jwt_token');
    if (token != null) {
      api.setToken(token);
      state = AuthState.authenticated(token);
    }
  }

  Future<bool> login(String email, String password) async {
    try {
      final response = await api.dio.post('/api/v1/auth/login', data: {
        'email': email,
        'password': password,
      });
      final token = response.data['access_token'] as String;
      await _storage.write(key: 'jwt_token', value: token);
      api.setToken(token);
      state = AuthState.authenticated(token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt_token');
    api.setToken(null);
    state = AuthState.guest();
  }
}