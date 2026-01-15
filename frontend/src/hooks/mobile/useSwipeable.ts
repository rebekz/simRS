"use client";

import { useRef, useEffect, useCallback } from "react";

/**
 * WEB-S-3.7: Swipe Gesture Hook
 *
 * Key Features:
 * - Touch and mouse swipe detection
 * - Configurable swipe threshold
 * - Prevents default scroll behavior during swipe
 * - Works on mobile and desktop
 */

// ============================================================================
// TYPES
// ============================================================================

export interface SwipeHandlers {
  onSwipedLeft?: () => void;
  onSwipedRight?: () => void;
  onSwipedUp?: () => void;
  onSwipedDown?: () => void;
  onSwiping?: (delta: { deltaX: number; deltaY: number }) => void;
  onSwipeStart?: () => void;
  onSwipeEnd?: () => void;
}

export interface UseSwipeableOptions {
  swipeThreshold?: number;
  preventScrollOnSwipe?: boolean;
  trackMouse?: boolean;
}

// ============================================================================
// HOOK
// ============================================================================

export function useSwipeable(
  handlers: SwipeHandlers,
  options: UseSwipeableOptions = {}
) {
  const {
    swipeThreshold = 50,
    preventScrollOnSwipe = false,
    trackMouse = true,
  } = options;

  const startX = useRef<number>(0);
  const startY = useRef<number>(0);
  const isSwiping = useRef(false);
  const isDragging = useRef(false);

  const {
    onSwipedLeft,
    onSwipedRight,
    onSwipedUp,
    onSwipedDown,
    onSwiping,
    onSwipeStart,
    onSwipeEnd,
  } = handlers;

  /**
   * Handle touch/mouse start
   */
  const handleStart = useCallback(
    (clientX: number, clientY: number) => {
      startX.current = clientX;
      startY.current = clientY;
      isDragging.current = true;
      onSwipeStart?.();
    },
    [onSwipeStart]
  );

  /**
   * Handle touch/mouse move
   */
  const handleMove = useCallback(
    (clientX: number, clientY: number) => {
      if (!isDragging.current) return;

      const deltaX = clientX - startX.current;
      const deltaY = clientY - startY.current;

      // Check if swipe threshold reached
      if (!isSwiping.current) {
        const absDeltaX = Math.abs(deltaX);
        const absDeltaY = Math.abs(deltaY);

        if (absDeltaX > 10 || absDeltaY > 10) {
          isSwiping.current = true;
        }
      }

      if (isSwiping.current) {
        onSwiping?.({ deltaX, deltaY });

        // Prevent default scroll behavior during horizontal swipe
        if (preventScrollOnSwipe && Math.abs(deltaX) > Math.abs(deltaY)) {
          return true; // Prevent default
        }
      }

      return false;
    },
    [onSwiping, preventScrollOnSwipe]
  );

  /**
   * Handle touch/mouse end
   */
  const handleEnd = useCallback(
    (clientX: number, clientY: number) => {
      if (!isDragging.current) return;

      const deltaX = clientX - startX.current;
      const deltaY = clientY - startY.current;

      const absDeltaX = Math.abs(deltaX);
      const absDeltaY = Math.abs(deltaY);

      // Determine swipe direction based on largest delta
      if (Math.max(absDeltaX, absDeltaY) > swipeThreshold) {
        if (absDeltaX > absDeltaY) {
          // Horizontal swipe
          if (deltaX > 0) {
            onSwipedRight?.();
          } else {
            onSwipedLeft?.();
          }
        } else {
          // Vertical swipe
          if (deltaY > 0) {
            onSwipedDown?.();
          } else {
            onSwipedUp?.();
          }
        }
      }

      isDragging.current = false;
      isSwiping.current = false;
      onSwipeEnd?.();
    },
    [
      swipeThreshold,
      onSwipedLeft,
      onSwipedRight,
      onSwipedUp,
      onSwipedDown,
      onSwipeEnd,
    ]
  );

  // Touch event handlers
  const handleTouchStart = useCallback(
    (e: React.TouchEvent) => {
      const touch = e.touches[0];
      handleStart(touch.clientX, touch.clientY);
    },
    [handleStart]
  );

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      const touch = e.touches[0];
      const shouldPreventDefault = handleMove(touch.clientX, touch.clientY);
      if (shouldPreventDefault) {
        e.preventDefault();
      }
    },
    [handleMove]
  );

  const handleTouchEnd = useCallback(
    (e: React.TouchEvent) => {
      const touch = e.changedTouches[0];
      handleEnd(touch.clientX, touch.clientY);
    },
    [handleEnd]
  );

  // Mouse event handlers (for testing on desktop)
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!trackMouse) return;
      handleStart(e.clientX, e.clientY);
    },
    [handleStart, trackMouse]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!trackMouse || !isDragging.current) return;
      const shouldPreventDefault = handleMove(e.clientX, e.clientY);
      if (shouldPreventDefault) {
        e.preventDefault();
      }
    },
    [handleMove, trackMouse]
  );

  const handleMouseUp = useCallback(
    (e: React.MouseEvent) => {
      if (!trackMouse || !isDragging.current) return;
      handleEnd(e.clientX, e.clientY);
    },
    [handleEnd, trackMouse]
  );

  /**
   * Return event handlers to attach to element
   */
  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,
    onMouseDown: handleMouseDown,
    onMouseMove: handleMouseMove,
    onMouseUp: handleMouseUp,
  };
}

/**
 * Hook for swipeable form navigation
 */
export interface UseFormSwipeOptions {
  totalFields: number;
  currentField: number;
  onNext?: () => void;
  onPrevious?: () => void;
}

export function useFormSwipe({
  totalFields,
  currentField,
  onNext,
  onPrevious,
}: UseFormSwipeOptions) {
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (currentField < totalFields - 1) {
        onNext?.();
      }
    },
    onSwipedRight: () => {
      if (currentField > 0) {
        onPrevious?.();
      }
    },
  });

  return swipeHandlers;
}

/**
 * Hook for swipeable multi-step form
 */
export interface UseStepSwipeOptions {
  totalSteps: number;
  currentStep: number;
  onNext?: () => void;
  onPrevious?: () => void;
  canGoNext?: (currentStep: number) => boolean;
  canGoPrevious?: (currentStep: number) => boolean;
}

export function useStepSwipe({
  totalSteps,
  currentStep,
  onNext,
  onPrevious,
  canGoNext,
  canGoPrevious,
}: UseStepSwipeOptions) {
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (currentStep < totalSteps - 1) {
        if (!canGoNext || canGoNext(currentStep)) {
          onNext?.();
        }
      }
    },
    onSwipedRight: () => {
      if (currentStep > 0) {
        if (!canGoPrevious || canGoPrevious(currentStep)) {
          onPrevious?.();
        }
      }
    },
  });

  return swipeHandlers;
}
