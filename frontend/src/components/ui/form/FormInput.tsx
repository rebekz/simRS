import React, { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import * as Label from '@radix-ui/react-label';

export interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  containerClassName?: string;
}

const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
  (
    {
      label,
      hint,
      error,
      required,
      disabled,
      className,
      containerClassName,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${inputId}-error` : undefined;
    const hintId = hint ? `${inputId}-hint` : undefined;

    return (
      <div className={cn('form-group', containerClassName)}>
        {label && (
          <Label.Root
            htmlFor={inputId}
            className="form-label"
          >
            {label}
            {required && <span className="required" aria-label="required">*</span>}
          </Label.Root>
        )}

        <input
          ref={ref}
          id={inputId}
          disabled={disabled}
          className={cn(
            'form-input',
            error && 'border-[var(--simrs-emergency)] focus:border-[var(--simrs-emergency)] focus:shadow-[0_0_0_3px_rgba(220,38,38,0.1)]',
            className
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={cn(
            errorId,
            hintId
          )}
          aria-required={required}
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

FormInput.displayName = 'FormInput';

export { FormInput };
