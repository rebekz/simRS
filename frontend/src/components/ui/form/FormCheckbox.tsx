import React, { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import * as Label from '@radix-ui/react-label';

export interface FormCheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  containerClassName?: string;
}

const FormCheckbox = forwardRef<HTMLInputElement, FormCheckboxProps>(
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
    const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${checkboxId}-error` : undefined;
    const hintId = hint ? `${checkboxId}-hint` : undefined;

    return (
      <div className={cn('form-group', containerClassName)}>
        <div className="flex items-start gap-3">
          <input
            ref={ref}
            id={checkboxId}
            type="checkbox"
            disabled={disabled}
            className={cn(
              'form-checkbox mt-[2px]',
              error && 'border-[var(--simrs-emergency)]',
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

          {label && (
            <div className="flex-1">
              <Label.Root
                htmlFor={checkboxId}
                className={cn(
                  'text-sm font-medium text-[var(--simrs-gray-700)] cursor-pointer',
                  disabled && 'opacity-50 cursor-not-allowed'
                )}
              >
                {label}
                {required && <span className="required" aria-label="required">*</span>}
              </Label.Root>

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
          )}
        </div>
      </div>
    );
  }
);

FormCheckbox.displayName = 'FormCheckbox';

export { FormCheckbox };
