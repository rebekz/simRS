import React, { forwardRef, InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import * as Label from '@radix-ui/react-label';

export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface FormRadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
  options: RadioOption[];
  containerClassName?: string;
}

const FormRadio = forwardRef<HTMLInputElement, FormRadioProps>(
  (
    {
      label: groupLabel,
      hint,
      error,
      required,
      disabled,
      options,
      className,
      containerClassName,
      id,
      name,
      ...props
    },
    ref
  ) => {
    const radioGroupId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${radioGroupId}-error` : undefined;
    const hintId = hint ? `${radioGroupId}-hint` : undefined;
    const radioName = name || radioGroupId;

    return (
      <div className={cn('form-group', containerClassName)}>
        {groupLabel && (
          <Label.Root
            className="form-label"
          >
            {groupLabel}
            {required && <span className="required" aria-label="required">*</span>}
          </Label.Root>
        )}

        <div
          className="space-y-2"
          role="radiogroup"
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={cn(
            errorId,
            hintId
          )}
          aria-required={required}
        >
          {options.map((option, index) => {
            const optionId = `${radioGroupId}-${index}`;
            return (
              <div key={option.value} className="flex items-center gap-3">
                <input
                  ref={index === 0 ? ref : undefined}
                  id={optionId}
                  type="radio"
                  name={radioName}
                  value={option.value}
                  disabled={disabled || option.disabled}
                  className={cn(
                    'form-radio',
                    error && 'border-[var(--simrs-emergency)]',
                    className
                  )}
                  aria-invalid={error ? 'true' : 'false'}
                  {...props}
                />

                <Label.Root
                  htmlFor={optionId}
                  className={cn(
                    'text-sm font-medium text-[var(--simrs-gray-700)] cursor-pointer',
                    (disabled || option.disabled) && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  {option.label}
                </Label.Root>
              </div>
            );
          })}
        </div>

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

FormRadio.displayName = 'FormRadio';

export { FormRadio };
