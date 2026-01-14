# Alert and Notification Components

This directory contains the Alert and Notification system for the SIMRS application.

## Components

### 1. Alert Component (`Alert.tsx`)

A versatile alert component for displaying informational messages with different severity levels.

#### Features:
- Four variants: `info`, `success`, `warning`, `error`
- Custom icons or default variant icons
- Optional title and message
- Dismissible with close button
- Accessible (ARIA attributes)
- Responsive design

#### Usage:

```tsx
import { Alert } from '@/components/ui';

// Basic alert
<Alert
  variant="info"
  title="Information"
  message="This is an informational message"
  dismissible
  onDismiss={() => console.log('Dismissed')}
/>

// Success alert
<Alert
  variant="success"
  title="Success"
  message="Operation completed successfully!"
  dismissible
/>

// Warning alert
<Alert
  variant="warning"
  title="Warning"
  message="Please review this warning"
  dismissible
/>

// Error alert
<Alert
  variant="error"
  title="Error"
  message="An error occurred"
  dismissible
/>

// Custom icon
<Alert
  variant="info"
  title="Custom Icon"
  message="With custom icon"
  icon={<CustomIcon />}
  dismissible
/>

// Without title
<Alert variant="success" message="Simple message" dismissible />
```

### 2. CriticalAlert Component (`CriticalAlert.tsx`)

A distinctive alert component designed for medical emergencies and critical situations.

#### Features:
- Four emergency types: `emergency`, `critical`, `code-blue`, `code-red`
- Cannot be dismissed (permanent until resolved)
- Distinctive 6px left border
- Emergency type badge
- Pulsing animation (optional)
- Shadow for emphasis
- ARIA live regions for screen readers

#### Usage:

```tsx
import { CriticalAlert } from '@/components/ui';

// Emergency
<CriticalAlert
  emergencyType="emergency"
  title="Medical Emergency"
  message="Patient requires immediate attention"
  pulse
/>

// Critical condition
<CriticalAlert
  emergencyType="critical"
  title="Critical Condition"
  message="Vital signs unstable"
  pulse
/>

// Code Blue
<CriticalAlert
  emergencyType="code-blue"
  title="CODE BLUE"
  message="Cardiac arrest - Room 304"
  pulse
/>

// Code Red
<CriticalAlert
  emergencyType="code-red"
  title="CODE RED"
  message="Fire detected in building"
  pulse
/>

// Without pulse
<CriticalAlert
  emergencyType="critical"
  title="Stable Critical"
  message="Condition critical but stable"
  pulse={false}
/>
```

### 3. Toast Notification System (`toast.ts`)

A flexible toast notification system with multiple variants.

#### Features:
- Four variants: `success`, `error`, `info`, `warning`
- Auto-dismiss after configurable duration
- Optional title and action buttons
- Stacked notifications
- Smooth animations
- Accessible

#### Usage:

```tsx
import { toast, Toaster } from '@/components/ui';

// Add Toaster component to your root layout
function App() {
  return (
    <>
      {children}
      <Toaster />
    </>
  );
}

// Show toast notifications
toast.success('Operation completed!');
toast.error('Something went wrong!');
toast.info('New message received');
toast.warning('Warning: Low disk space');

// With title
toast.success('Saved!', { title: 'Changes saved' });

// With action
toast.info('Item deleted', {
  action: {
    label: 'Undo',
    onClick: () => handleUndo()
  }
});

// Custom duration (default: 5000ms)
toast.error('Long process failed', { duration: 10000 });
```

## Styling

All components use the SIMRS color palette defined in `tailwind.config.ts`:

- **Info**: Blue tones for neutral information
- **Success**: Green tones for positive feedback
- **Warning**: Yellow/amber tones for cautions
- **Error**: Red tones for errors and emergencies
- **Emergency**: Bright red with pulsing animation
- **Critical**: Dark red for serious conditions
- **Code Blue**: Medical blue tones
- **Code Red**: Fire emergency red tones

## Accessibility

- All components include proper ARIA attributes
- `role="alert"` for timely information
- `aria-live="assertive"` for critical alerts
- `aria-atomic="true"` for complete message reading
- Keyboard navigation support
- Screen reader friendly

## Dependencies

- React 19
- Radix UI Toast primitives
- Lucide React icons
- TailwindCSS
- class-variance-authority
- clsx & tailwind-merge

## Files Created

1. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/Alert.tsx` - Alert component
2. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/CriticalAlert.tsx` - Critical alert component
3. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/toast.ts` - Toast notification API
4. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/toaster.tsx` - Toast renderer component
5. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/use-toast.ts` - Toast hook and state management
6. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/toast-primitive.tsx` - Radix UI toast primitives
7. `/Users/fitra/project/self/bmad/simrs/frontend/src/components/ui/__tests__/test-alerts.tsx` - Demo/test file
