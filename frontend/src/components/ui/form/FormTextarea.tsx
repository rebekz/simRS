import React, { forwardRef, TextareaHTMLAttributes, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import * as Label from '@radix-ui/react-label';

export interface FormTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  autoResize?: boolean;
  containerClassName?: string;
}

const FormTextarea = forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  (
    {
      label,
      hint,
      error,
      required,
      disabled,
      autoResize = true,
      className,
      containerClassName,
      id,
      value,
      ...props
    },
    ref
  ) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${textareaId}-error` : undefined;
    const hintId = hint ? `${textareaId}-hint` : undefined;
    const internalRef = useRef<HTMLTextAreaElement>(null);
    const textareaRef = (ref as React.RefObject<HTMLTextAreaElement>) || internalRef;

    useEffect(() => {
      if (autoResize && textareaRef.current) {
        const textarea = textareaRef.current;
        const adjustHeight = () => {
          textarea.style.height = 'auto';
          const newHeight = Math.max(80, textarea.scrollHeight);
          textarea.style.height = `${newHeight}px`;
        };

        adjustHeight();

        textarea.addEventListener('input', adjustHeight);
        return () => {
          textarea.removeEventListener('input', adjustHeight);
        };
      }
    }, [value, autoResize, textareaRef]);

    return (
      <div className={cn('form-group', containerClassName)}>
        {label && (
          <Label.Root
            htmlFor={textareaId}
            className="form-label"
          >
            {label}
            {required && <span className="required" aria-label="required">*</span>}
          </Label.Root>
        )}

        <textarea
          ref={textareaRef}
          id={textareaId}
          disabled={disabled}
          className={cn(
            'form-textarea',
            error && 'border-[var(--simrs-emergency)] focus:border-[var(--simrs-emergency)] focus:shadow-[0_0_0_3px_rgba(220,38,38,0.1)]',
            !autoResize && 'resize-vertical',
            className
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={cn(
            errorId,
            hintId
          )}
          aria-required={required}
          value={value}
          {...props}
        />

        {hint && !error && (
          <p id={hintId} className="form-hint">
            {hint}
          </p>
        )}

        {error && (
          <p id={errorId} className="form-error" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

FormTextarea.displayName = 'FormTextarea';

export { FormTextarea };
