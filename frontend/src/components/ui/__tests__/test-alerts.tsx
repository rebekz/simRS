// Test file to verify Alert and Notification components
// This file demonstrates the usage of all created components

import React from 'react';
import { Alert } from '../Alert';
import { CriticalAlert } from '../CriticalAlert';
import { toast } from '../toast';
import { Toaster } from '../toaster';

export function AlertDemo() {
  return (
    <div className="space-y-4 p-4">
      <h2 className="text-2xl font-bold">Alert Component Demo</h2>

      {/* Info Alert */}
      <Alert
        variant="info"
        title="Information"
        message="This is an informational alert message."
        dismissible
        onDismiss={() => console.log('Info dismissed')}
      />

      {/* Success Alert */}
      <Alert
        variant="success"
        title="Success"
        message="Operation completed successfully!"
        dismissible
      />

      {/* Warning Alert */}
      <Alert
        variant="warning"
        title="Warning"
        message="Please review this warning message."
        dismissible
      />

      {/* Error Alert */}
      <Alert
        variant="error"
        title="Error"
        message="An error has occurred. Please try again."
        dismissible
      />

      {/* Alert with custom icon */}
      <Alert
        variant="info"
        title="Custom Icon"
        message="This alert has a custom icon."
        icon={<span>🔔</span>}
        dismissible
      />

      {/* Alert without title */}
      <Alert
        variant="success"
        message="Simple message without title"
      />

      <h2 className="text-2xl font-bold mt-8">CriticalAlert Demo</h2>

      {/* Emergency Alert */}
      <CriticalAlert
        emergencyType="emergency"
        title="Medical Emergency"
        message="Patient requires immediate attention"
        pulse
      />

      {/* Critical Alert */}
      <CriticalAlert
        emergencyType="critical"
        title="Critical Condition"
        message="Vital signs unstable - immediate intervention required"
        pulse
      />

      {/* Code Blue */}
      <CriticalAlert
        emergencyType="code-blue"
        title="CODE BLUE"
        message="Cardiac arrest - Room 304"
        pulse
      />

      {/* Code Red */}
      <CriticalAlert
        emergencyType="code-red"
        title="CODE RED"
        message="Fire detected in building"
        pulse
      />

      {/* Non-pulsing critical alert */}
      <CriticalAlert
        emergencyType="critical"
        title="Stable Critical"
        message="Patient condition critical but stable"
        pulse={false}
      />

      <h2 className="text-2xl font-bold mt-8">Toast Demo</h2>

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => toast.success('Success message!')}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          Success Toast
        </button>

        <button
          onClick={() => toast.error('Error occurred!')}
          className="px-4 py-2 bg-red-500 text-white rounded"
        >
          Error Toast
        </button>

        <button
          onClick={() => toast.info('Information message')}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Info Toast
        </button>

        <button
          onClick={() => toast.warning('Warning message')}
          className="px-4 py-2 bg-yellow-500 text-white rounded"
        >
          Warning Toast
        </button>

        <button
          onClick={() => toast.success('With title', { title: 'Operation Complete' })}
          className="px-4 py-2 bg-purple-500 text-white rounded"
        >
          Toast with Title
        </button>

        <button
          onClick={() => toast.info('With action', {
            action: {
              label: 'Undo',
              onClick: () => console.log('Undo clicked')
            }
          })}
          className="px-4 py-2 bg-indigo-500 text-white rounded"
        >
          Toast with Action
        </button>

        <button
          onClick={() => toast.error('Custom duration', { duration: 10000 })}
          className="px-4 py-2 bg-pink-500 text-white rounded"
        >
          Long Duration Toast
        </button>
      </div>

      {/* Toast Container */}
      <Toaster />
    </div>
  );
}

export default AlertDemo;
