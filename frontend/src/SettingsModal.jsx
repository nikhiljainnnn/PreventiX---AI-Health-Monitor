import React, { useState, useEffect } from 'react';
import { X, Sun, Moon, Monitor, Bell, BellOff, Shield, User, Download, Trash2, Calendar, Clock, Heart, Activity, AlertTriangle, CheckCircle, Settings as SettingsIcon, Database, FileText, Mail, Phone, MapPin, Globe, Palette, Volume2, VolumeX } from 'lucide-react';
import { useTheme } from './ThemeContext';
import toast from 'react-hot-toast';

const SettingsModal = ({ isOpen, onClose }) => {
  const { theme, toggleTheme } = useTheme();
  
  // Settings state
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

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('preventix-settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  // Save settings to localStorage
  const updateSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('preventix-settings', JSON.stringify(newSettings));
    toast.success('Settings saved successfully!');
  };

  const handleSettingChange = (category, key, value) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    };
    updateSettings(newSettings);
  };

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
    toast.success('Settings reset to default!');
  };

  const exportData = () => {
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
    toast.success('Settings exported successfully!');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8">
          {/* Appearance Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Appearance
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Theme Selection */}
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Theme</h4>
                <div className="space-y-2">
                  <button
                    onClick={toggleTheme}
                    className={`w-full flex items-center justify-between p-3 rounded-lg border-2 transition-all ${
                      theme === 'light'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Sun className="w-4 h-4 text-yellow-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">Light</span>
                    </div>
                    {theme === 'light' && <CheckCircle className="w-4 h-4 text-blue-500" />}
                  </button>

                  <button
                    onClick={toggleTheme}
                    className={`w-full flex items-center justify-between p-3 rounded-lg border-2 transition-all ${
                      theme === 'dark'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Moon className="w-4 h-4 text-indigo-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">Dark</span>
                    </div>
                    {theme === 'dark' && <CheckCircle className="w-4 h-4 text-blue-500" />}
                  </button>
                </div>
              </div>

              {/* Font Size */}
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Font Size</h4>
                <select
                  value={settings.display.fontSize}
                  onChange={(e) => handleSettingChange('display', 'fontSize', e.target.value)}
                  className="w-full p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>

            {/* Display Options */}
            <div className="mt-4 space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Enable Animations</span>
                <input
                  type="checkbox"
                  checked={settings.display.animations}
                  onChange={(e) => handleSettingChange('display', 'animations', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Compact Mode</span>
                <input
                  type="checkbox"
                  checked={settings.display.compactMode}
                  onChange={(e) => handleSettingChange('display', 'compactMode', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
            </h3>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4 text-blue-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Email Reminders</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Weekly health check reminders</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.emailReminders}
                  onChange={(e) => handleSettingChange('notifications', 'emailReminders', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-green-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Assessment Reminders</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Monthly assessment prompts</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.assessmentReminders}
                  onChange={(e) => handleSettingChange('notifications', 'assessmentReminders', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Heart className="w-4 h-4 text-red-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Health Tips</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Daily wellness tips</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.healthTips}
                  onChange={(e) => handleSettingChange('notifications', 'healthTips', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Risk Alerts</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">High risk notifications</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.riskAlerts}
                  onChange={(e) => handleSettingChange('notifications', 'riskAlerts', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Privacy & Security Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Privacy & Security
            </h3>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Database className="w-4 h-4 text-purple-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Data Sharing</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Share anonymized data for research</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.dataSharing}
                  onChange={(e) => handleSettingChange('privacy', 'dataSharing', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <Activity className="w-4 h-4 text-blue-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Analytics</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Help improve the app</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.analytics}
                  onChange={(e) => handleSettingChange('privacy', 'analytics', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-green-500" />
                  <div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">Health Data Export</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Allow data export</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.healthDataExport}
                  onChange={(e) => handleSettingChange('privacy', 'healthDataExport', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Health Settings Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Heart className="w-5 h-5" />
              Health Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Reminder Frequency</h4>
                <select
                  value={settings.health.reminderFrequency}
                  onChange={(e) => handleSettingChange('health', 'reminderFrequency', e.target.value)}
                  className="w-full p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Risk Threshold</h4>
                <select
                  value={settings.health.riskThreshold}
                  onChange={(e) => handleSettingChange('health', 'riskThreshold', e.target.value)}
                  className="w-full p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Goal Tracking</span>
                <input
                  type="checkbox"
                  checked={settings.health.goalTracking}
                  onChange={(e) => handleSettingChange('health', 'goalTracking', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Progress Tracking</span>
                <input
                  type="checkbox"
                  checked={settings.health.progressTracking}
                  onChange={(e) => handleSettingChange('health', 'progressTracking', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Account Settings Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5" />
              Account Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Profile Visibility</h4>
                <select
                  value={settings.account.profileVisibility}
                  onChange={(e) => handleSettingChange('account', 'profileVisibility', e.target.value)}
                  className="w-full p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="private">Private</option>
                  <option value="friends">Friends Only</option>
                  <option value="public">Public</option>
                </select>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 dark:text-white">Data Retention</h4>
                <select
                  value={settings.account.dataRetention}
                  onChange={(e) => handleSettingChange('account', 'dataRetention', e.target.value)}
                  className="w-full p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="6months">6 Months</option>
                  <option value="1year">1 Year</option>
                  <option value="2years">2 Years</option>
                  <option value="forever">Forever</option>
                </select>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Auto Backup</span>
                <input
                  type="checkbox"
                  checked={settings.account.autoBackup}
                  onChange={(e) => handleSettingChange('account', 'autoBackup', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
              <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <span className="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</span>
                <input
                  type="checkbox"
                  checked={settings.account.twoFactorAuth}
                  onChange={(e) => handleSettingChange('account', 'twoFactorAuth', e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Actions Section */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <SettingsIcon className="w-5 h-5" />
              Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={exportData}
                className="flex items-center justify-center gap-2 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Download className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">Export Settings</span>
              </button>

              <button
                onClick={resetSettings}
                className="flex items-center justify-center gap-2 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Trash2 className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">Reset Settings</span>
              </button>

              <button
                onClick={onClose}
                className="flex items-center justify-center gap-2 p-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
              >
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Save & Close</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;