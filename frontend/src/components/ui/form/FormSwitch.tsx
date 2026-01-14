import React, { forwardRef, InputHTMLAttributes, useState } from 'react';
import { cn } from '@/lib/utils';
import * as Label from '@radix-ui/react-label';

export interface FormSwitchProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  containerClassName?: string;
}

const FormSwitch = forwardRef<HTMLInputElement, FormSwitchProps>(
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
    const switchId = id || `switch-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${switchId}-error` : undefined;
    const hintId = hint ? `${switchId}-hint` : undefined;

    return (
      <div className={cn('form-group', containerClassName)}>
        <div className="flex items-start gap-3">
          <div className="form-switch">
            <input
              ref={ref}
              id={switchId}
              type="checkbox"
              role="switch"
              disabled={disabled}
              className={cn(
                error && 'border-[var(--simrs-emergency)]',
                className
              )}
              aria-invalid={error ? 'true' : 'false'}
              aria-checked={props.checked}
              aria-describedby={cn(
                errorId,
                hintId
              )}
              aria-required={required}
              {...props}
            />
          </div>

          {label && (
            <div className="flex-1">
              <Label.Root
                htmlFor={switchId}
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

FormSwitch.displayName = 'FormSwitch';

export { FormSwitch };
