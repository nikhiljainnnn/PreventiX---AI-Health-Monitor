import React, { useEffect, useState } from 'react';
import { useSettings } from './SettingsContext';
import toast from 'react-hot-toast';

export const NotificationManager = () => {
  const { settings, shouldShowNotification, getReminderFrequency } = useSettings();
  const [lastReminder, setLastReminder] = useState(null);

  // Check if it's time for a reminder
  useEffect(() => {
    const checkReminders = () => {
      const now = Date.now();
      const frequency = getReminderFrequency();
      const lastReminderTime = localStorage.getItem('last-health-reminder');
      
      if (!lastReminderTime || (now - parseInt(lastReminderTime)) > frequency) {
        if (shouldShowNotification('emailReminders')) {
          showHealthReminder();
          setLastReminder(now);
          localStorage.setItem('last-health-reminder', now.toString());
        }
      }
    };

    // Check immediately
    checkReminders();

    // Set up interval to check every hour
    const interval = setInterval(checkReminders, 60 * 60 * 1000);

    return () => clearInterval(interval);
  }, [settings, shouldShowNotification, getReminderFrequency]);

  const showHealthReminder = () => {
    if (shouldShowNotification('emailReminders')) {
      toast.success(
        <div className="flex items-center gap-2">
          <span>💡 Time for your health check!</span>
        </div>,
        {
          duration: 6000,
          icon: '💡',
        }
      );
    }
  };

  const showAssessmentReminder = () => {
    if (shouldShowNotification('assessmentReminders')) {
      toast.success(
        <div className="flex items-center gap-2">
          <span>📊 Monthly assessment due!</span>
        </div>,
        {
          duration: 6000,
          icon: '📊',
        }
      );
    }
  };

  const showHealthTip = () => {
    if (shouldShowNotification('healthTips')) {
      const tips = [
        "💧 Stay hydrated! Drink 8 glasses of water daily.",
        "🚶‍♂️ Take a 10-minute walk every hour.",
        "🥗 Include more vegetables in your meals.",
        "😴 Aim for 7-9 hours of sleep each night.",
        "🧘‍♀️ Practice 5 minutes of deep breathing daily."
      ];
      
      const randomTip = tips[Math.floor(Math.random() * tips.length)];
      
      toast.success(
        <div className="flex items-center gap-2">
          <span>{randomTip}</span>
        </div>,
        {
          duration: 8000,
          icon: '💡',
        }
      );
    }
  };

  const showRiskAlert = (riskType, riskLevel) => {
    if (shouldShowNotification('riskAlerts')) {
      const alertMessages = {
        diabetes: `⚠️ High diabetes risk detected (${riskLevel}%)`,
        hypertension: `⚠️ High blood pressure risk detected (${riskLevel}%)`,
        general: `⚠️ Elevated health risk detected`
      };

      toast.error(
        <div className="flex items-center gap-2">
          <span>{alertMessages[riskType] || alertMessages.general}</span>
        </div>,
        {
          duration: 10000,
          icon: '⚠️',
        }
      );
    }
  };

  // Expose methods for other components to use
  useEffect(() => {
    window.notificationManager = {
      showHealthReminder,
      showAssessmentReminder,
      showHealthTip,
      showRiskAlert
    };
  }, [settings]);

  return null; // This component doesn't render anything
};

export default NotificationManager;

