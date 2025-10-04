import React, { useEffect } from 'react';
import { useSettings } from './SettingsContext';

const SettingsApplier = () => {
  const { settings, isLoaded } = useSettings();

  useEffect(() => {
    if (!isLoaded) return;

    // Apply font size
    const fontSizeMap = {
      small: '14px',
      medium: '16px',
      large: '18px'
    };
    document.documentElement.style.fontSize = fontSizeMap[settings.display.fontSize] || '16px';

    // Apply animations
    if (!settings.display.animations) {
      document.documentElement.classList.add('no-animations');
    } else {
      document.documentElement.classList.remove('no-animations');
    }

    // Apply compact mode
    if (settings.display.compactMode) {
      document.documentElement.classList.add('compact-mode');
    } else {
      document.documentElement.classList.remove('compact-mode');
    }

    // Apply color scheme
    if (settings.display.colorScheme === 'light') {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    } else if (settings.display.colorScheme === 'dark') {
      document.documentElement.classList.add('dark-theme');
      document.documentElement.classList.remove('light-theme');
    } else {
      // Auto mode - use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        document.documentElement.classList.add('dark-theme');
        document.documentElement.classList.remove('light-theme');
      } else {
        document.documentElement.classList.add('light-theme');
        document.documentElement.classList.remove('dark-theme');
      }
    }

    // Apply analytics settings
    if (settings.privacy.analytics) {
      document.documentElement.classList.add('analytics-enabled');
    } else {
      document.documentElement.classList.add('analytics-disabled');
    }

    // Apply data sharing settings
    if (settings.privacy.dataSharing) {
      document.documentElement.classList.add('data-sharing-enabled');
    } else {
      document.documentElement.classList.add('data-sharing-disabled');
    }

    // Apply health tracking settings
    if (settings.health.goalTracking && settings.health.progressTracking) {
      document.documentElement.classList.add('health-tracking-enabled');
    } else {
      document.documentElement.classList.add('health-tracking-disabled');
    }

    // Apply account security settings
    const securityLevel = settings.account.twoFactorAuth ? 'high' : 
                         settings.account.autoBackup ? 'medium' : 'low';
    document.documentElement.classList.add(`security-${securityLevel}`);

  }, [settings, isLoaded]);

  return null; // This component doesn't render anything
};

export default SettingsApplier;

