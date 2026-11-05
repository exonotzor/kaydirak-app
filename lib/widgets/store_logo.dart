import 'package:flutter/material.dart';

class StoreLogo extends StatelessWidget {
  final String store;

  const StoreLogo({super.key, required this.store});

  @override
  Widget build(BuildContext context) {
    final s = store.toLowerCase();

    if (s.contains('amazon')) {
      return _buildAmazonLogo();
    } else if (s.contains('hepsiburada')) {
      return _buildHepsiburadaLogo();
    } else if (s.contains('idefix')) {
      return _buildIdefixLogo();
    }

    return Text(
      store,
      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
    );
  }

  Widget _buildAmazonLogo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFF131921), // Amazon dark background
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          RichText(
            text: const TextSpan(
              style: TextStyle(
                fontFamily: 'sans-serif',
                fontWeight: FontWeight.w900,
                fontSize: 15,
                color: Colors.white,
                letterSpacing: -0.5,
              ),
              children: [
                TextSpan(text: 'amazon'),
                TextSpan(
                  text: '.com.tr',
                  style: TextStyle(
                    color: Color(0xFFFF9900), // Amazon smile orange
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 4),
          const Icon(
            Icons.arrow_forward_rounded,
            color: Color(0xFFFF9900),
            size: 13,
          ),
        ],
      ),
    );
  }

  Widget _buildHepsiburadaLogo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFFF6000), // Hepsiburada vibrant orange
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFFF6000).withValues(alpha: 0.3),
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 17,
            height: 17,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: const Text(
              'H',
              style: TextStyle(
                color: Color(0xFFFF6000),
                fontWeight: FontWeight.w900,
                fontSize: 12,
                height: 1.1,
              ),
            ),
          ),
          const SizedBox(width: 6),
          const Text(
            'hepsiburada',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
              fontSize: 14,
              letterSpacing: -0.3,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIdefixLogo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFF004F9E), // Idefix iconic blue
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF004F9E).withValues(alpha: 0.3),
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'idefix',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
              fontSize: 15,
              letterSpacing: -0.5,
            ),
          ),
          SizedBox(width: 3),
          Icon(Icons.bolt_rounded, color: Color(0xFFFFD32A), size: 15),
        ],
      ),
    );
  }
}
