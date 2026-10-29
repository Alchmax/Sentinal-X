import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import '../../core/auth_provider.dart';

final fileAnalysisProvider = StateProvider<Map<String, dynamic>?>((ref) => null);

class FileForensicsScreen extends ConsumerStatefulWidget {
  const FileForensicsScreen({super.key});
  @override
  ConsumerState<FileForensicsScreen> createState() => _FileForensicsScreenState();
}

class _FileForensicsScreenState extends ConsumerState<FileForensicsScreen> {
  bool _isAnalyzing = false;
  String _status = 'No file selected.';

  Future<void> _pickAndAnalyze() async {
    final res = await FilePicker.platform.pickFiles(withData: true);
    if (res == null || res.files.isEmpty) {
      setState(() => _status = 'File selection cancelled.');
      return;
    }

    final file = res.files.first;
    setState(() {
      _isAnalyzing = true;
      _status = 'Analyzing ${file.name}...';
    });

    try {
      final api = ref.read(apiClientProvider);
      
      FormData formData = FormData.fromMap({
        "file": MultipartFile.fromBytes(
          file.bytes!, 
          filename: file.name,
        ),
      });

      final response = await api.dio.post('/api/v1/evidence/analyze', data: formData);
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        setState(() {
          _status = 'Analysis Complete: ${data['sha256']}';
        });
        ref.read(fileAnalysisProvider.notifier).state = data;
      }
    } catch (e) {
      setState(() => _status = 'Analysis failed: $e');
    } finally {
      setState(() => _isAnalyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final analysis = ref.watch(fileAnalysisProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('File Forensics Lab', style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: _isAnalyzing ? null : _pickAndAnalyze, 
            icon: _isAnalyzing 
              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) 
              : const Icon(Icons.upload_file), 
            label: Text(_isAnalyzing ? 'Analyzing...' : 'Select File'),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.cyan.withValues(alpha: 0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(_status, style: const TextStyle(fontFamily: 'Courier', fontSize: 13)),
                if (analysis != null) ...[
                  const Divider(height: 24),
                  Text('Detailed Results:', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                  _ResultRow('Size', '${analysis['size_bytes']} bytes'),
                  _ResultRow('Extension', analysis['extension']),
                  _ResultRow('MIME', analysis['mime_guess']),
                  _ResultRow('Hash', analysis['sha256']),
                  if (analysis['mismatch'] == true) 
                    Text('⚠️ ${analysis['mismatch_reason']}', style: const TextStyle(color: Colors.redAccent)),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ResultRow extends StatelessWidget {
  final String label;
  final String value;
  const _ResultRow(this.label, this.value);
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
          Expanded(child: Text(value, overflow: TextOverflow.ellipsis)),
        ],
      ),
    );
  }
}