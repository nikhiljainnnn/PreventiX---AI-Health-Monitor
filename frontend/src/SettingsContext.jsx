import React, { createContext, useContext, useState, useEffect } from 'react';

const SettingsContext = createContext();

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState({
    notifications: {
      emailReminders: true,
      assessmentReminders: true,
      healthTips: true,
      riskAlerts: true,
      weeklyReports: false
    },
    privacy: {
      dataSharing: false,
      analytics: true,
      personalizedAds: false,
      healthDataExport: true
    },
    display: {
      fontSize: 'medium',
      colorScheme: 'auto',
      animations: true,
      compactMode: false
    },
    health: {
      reminderFrequency: 'weekly',
      riskThreshold: 'medium',
      goalTracking: true,
      progressTracking: true
    },
    account: {
      profileVisibility: 'private',
      dataRetention: '1year',
      autoBackup: true,
      twoFactorAuth: false
    }
  });

  const [isLoaded, setIsLoaded] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('preventix-settings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(parsedSettings);
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    }
    setIsLoaded(true);
  }, []);

  // Apply settings to the document
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
      document.documentElement.style.setProperty('--animation-duration', '0s');
      document.documentElement.style.setProperty('--transition-duration', '0s');
    } else {
      document.documentElement.style.removeProperty('--animation-duration');
      document.documentElement.style.removeProperty('--transition-duration');
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
  }, [settings.display.fontSize, settings.display.animations, settings.display.compactMode, settings.display.colorScheme, isLoaded]);

  // Update settings
  const updateSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('preventix-settings', JSON.stringify(newSettings));
  };

  // Update specific setting
  const updateSetting = (category, key, value) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    };
    updateSettings(newSettings);
  };

  // Reset to defaults
  const resetSettings = () => {
    const defaultSettings = {
      notifications: {
        emailReminders: true,
        assessmentReminders: true,
        healthTips: true,
        riskAlerts: true,
        weeklyReports: false
      },
      privacy: {
        dataSharing: false,
        analytics: true,
        personalizedAds: false,
        healthDataExport: true
      },
      display: {
        fontSize: 'medium',
        colorScheme: 'auto',
        animations: true,
        compactMode: false
      },
      health: {
        reminderFrequency: 'weekly',
        riskThreshold: 'medium',
        goalTracking: true,
        progressTracking: true
      },
      account: {
        profileVisibility: 'private',
        dataRetention: '1year',
        autoBackup: true,
        twoFactorAuth: false
      }
    };
    updateSettings(defaultSettings);
  };

  // Export settings
  const exportSettings = () => {
    const data = {
      settings: settings,
      exportDate: new Date().toISOString(),
      version: '1.0.0'
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `preventix-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Check if notifications are enabled
  const shouldShowNotification = (type) => {
    return settings.notifications[type] || false;
  };

  // Get risk threshold value
  const getRiskThreshold = () => {
    const thresholds = {
      low: 0.3,
      medium: 0.5,
      high: 0.7
    };
    return thresholds[settings.health.riskThreshold] || 0.5;
  };

  // Check if analytics are enabled
  const isAnalyticsEnabled = () => {
    return settings.privacy.analytics;
  };

  // Check if data sharing is enabled
  const isDataSharingEnabled = () => {
    return settings.privacy.dataSharing;
  };

  // Get reminder frequency in milliseconds
  const getReminderFrequency = () => {
    const frequencies = {
      daily: 24 * 60 * 60 * 1000, // 24 hours
      weekly: 7 * 24 * 60 * 60 * 1000, // 7 days
      monthly: 30 * 24 * 60 * 60 * 1000 // 30 days
    };
    return frequencies[settings.health.reminderFrequency] || frequencies.weekly;
  };

  const value = {
    settings,
    updateSettings,
    updateSetting,
    resetSettings,
    exportSettings,
    shouldShowNotification,
    getRiskThreshold,
    isAnalyticsEnabled,
    isDataSharingEnabled,
    getReminderFrequency,
    isLoaded
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};
