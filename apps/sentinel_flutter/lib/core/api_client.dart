import 'package:dio/dio.dart';

const String _defaultBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8081');

class ApiClient {
  ApiClient({String baseUrl = _defaultBaseUrl})
      : dio = Dio(BaseOptions(baseUrl: baseUrl, connectTimeout: const Duration(seconds: 15), receiveTimeout: const Duration(minutes: 5)));

  final Dio dio;

  void setToken(String? token) {
    if (token == null) {
      dio.options.headers.remove('Authorization');
    } else {
      dio.options.headers['Authorization'] = 'Bearer $token';
    }
  }
}