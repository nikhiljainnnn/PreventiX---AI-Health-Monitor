import React, { useState, useEffect, useRef } from 'react';
import { useSettings } from './SettingsContext';
import { Heart, Activity, Droplet, Moon, Apple, Brain, Shield } from 'lucide-react';

const HealthTips = () => {
  const { settings, shouldShowNotification } = useSettings();
  const [currentTip, setCurrentTip] = useState(null);
  const [tipIndex, setTipIndex] = useState(0);
  const intervalRef = useRef(null);

  const healthTips = [
    {
      icon: <Droplet className="w-6 h-6 text-blue-500" />,
      title: "Stay Hydrated",
      description: "Drink at least 8 glasses of water daily to maintain proper hydration and support your body's functions.",
      category: "hydration"
    },
    {
      icon: <Activity className="w-6 h-6 text-green-500" />,
      title: "Daily Movement",
      description: "Aim for 30 minutes of moderate exercise daily. Even a 10-minute walk can boost your health.",
      category: "exercise"
    },
    {
      icon: <Moon className="w-6 h-6 text-purple-500" />,
      title: "Quality Sleep",
      description: "Get 7-9 hours of quality sleep each night to support your immune system and mental health.",
      category: "sleep"
    },
    {
      icon: <Apple className="w-6 h-6 text-red-500" />,
      title: "Balanced Nutrition",
      description: "Include colorful fruits and vegetables in every meal for essential vitamins and minerals.",
      category: "nutrition"
    },
    {
      icon: <Brain className="w-6 h-6 text-indigo-500" />,
      title: "Mental Wellness",
      description: "Practice mindfulness or meditation for 5-10 minutes daily to reduce stress and improve focus.",
      category: "mental"
    },
    {
      icon: <Shield className="w-6 h-6 text-orange-500" />,
      title: "Preventive Care",
      description: "Schedule regular health checkups and screenings to catch potential issues early.",
      category: "prevention"
    }
  ];

  // Initialize tip display
  useEffect(() => {
    if (shouldShowNotification('healthTips') && healthTips.length > 0) {
      setCurrentTip(healthTips[0]);
    }
  }, [shouldShowNotification]);

  // Handle tip rotation
  useEffect(() => {
    if (!shouldShowNotification('healthTips')) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const getIntervalTime = () => {
      const frequencies = {
        daily: 24 * 60 * 60 * 1000, // 24 hours
        weekly: 7 * 24 * 60 * 60 * 1000, // 7 days
        monthly: 30 * 24 * 60 * 60 * 1000 // 30 days
      };
      return frequencies[settings.health.reminderFrequency] || frequencies.weekly;
    };

    const showNextTip = () => {
      setTipIndex((prev) => {
        const nextIndex = (prev + 1) % healthTips.length;
        setCurrentTip(healthTips[nextIndex]);
        return nextIndex;
      });
    };

    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Set up new interval
    intervalRef.current = setInterval(showNextTip, getIntervalTime());

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [settings.health.reminderFrequency, shouldShowNotification]);

  if (!shouldShowNotification('healthTips') || !currentTip) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 max-w-sm bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 z-40">
      <div className="flex items-start gap-3">
        {currentTip.icon}
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
            {currentTip.title}
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {currentTip.description}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs text-gray-500 dark:text-gray-500 capitalize">
              {currentTip.category}
            </span>
            <div className="flex-1 h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div 
                className="h-1 bg-blue-500 rounded-full transition-all duration-1000"
                style={{ width: `${((tipIndex + 1) / healthTips.length) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthTips;
