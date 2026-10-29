import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/auth_provider.dart';

final authTweakProvider = Provider<void>((ref) {});

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final emailCtrl = TextEditingController();
    final passCtrl = TextEditingController();
    
    return Scaffold(
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('SENTINEL X', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 32),
              TextField(
                controller: emailCtrl, 
                decoration: const InputDecoration(
                  labelText: 'Email',
                  hintText: 'admin@sentinel.x'
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: passCtrl, 
                decoration: const InputDecoration(labelText: 'Password'), 
                obscureText: true
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () async {
                    try {
                      final success = await ref.read(authProvider.notifier).login(
                        emailCtrl.text.trim(), 
                        passCtrl.text.trim()
                      );
                      if (success) {
                        await Future.delayed(const Duration(milliseconds: 100));
                        if (context.mounted) {
                          context.go('/');
                        }
                      } else {
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Invalid email or password')),
                          );
                        }
                      }
                    } catch (e) {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Server Error: $e')),
                        );
                      }
                    }
                  },
                  child: const Text('Login'),
                ),
              ),
              const SizedBox(height: 16),
              TextButton(
                onPressed: () => context.go('/register'),
                child: const Text("Don't have an account? Sign Up"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
