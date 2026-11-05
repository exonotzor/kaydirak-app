import 'package:flutter/material.dart';

class StoryProgressBar extends StatelessWidget {
  final int totalCount;
  final int currentIndex;
  final double currentProgress; // 0.0 to 1.0

  const StoryProgressBar({
    super.key,
    required this.totalCount,
    required this.currentIndex,
    required this.currentProgress,
  });

  @override
  Widget build(BuildContext context) {
    if (totalCount <= 0) return const SizedBox.shrink();

    return Row(
      children: List.generate(totalCount, (index) {
        double progress = 0.0;
        if (index < currentIndex) {
          progress = 1.0;
        } else if (index == currentIndex) {
          progress = currentProgress.clamp(0.0, 1.0);
        }

        return Expanded(
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 2.0),
            height: 3.5,
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(2.0),
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: progress,
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFFFF4757), // Modern vivid coral/red
                  borderRadius: BorderRadius.circular(2.0),
                ),
              ),
            ),
          ),
        );
      }),
    );
  }
}
