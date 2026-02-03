"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Settings, User, Mail, Lock, Save, AlertCircle, CheckCircle, ArrowLeft, Camera, Trash2 } from 'lucide-react';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  role: string;
  created_at: string;
}

export default function SettingsPage() {
  const { user, token, refreshUser } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Profile form state
  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    full_name: '',
  });
  
  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Profile picture upload state
  const [uploadingPicture, setUploadingPicture] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    
    console.log('🔍 Settings page - Current user data:', user);
    console.log('🔍 Settings page - Profile picture:', user.profile_picture);
    
    // Initialize profile data
    setProfileData({
      username: user.username || '',
      email: user.email || '',
      full_name: user.full_name || '',
    });
  }, [user, router]);

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:8001/api/auth/update-profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update profile');
      }

      setSuccessMessage('Profile updated successfully!');
      // Refresh user data in context
      if (refreshUser) {
        refreshUser().catch(err => console.error('Failed to refresh user:', err));
      }
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to update profile');
      setTimeout(() => setErrorMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    // Validate passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      setErrorMessage('New passwords do not match');
      setLoading(false);
      setTimeout(() => setErrorMessage(''), 5000);
      return;
    }

    // Validate password length
    if (passwordData.new_password.length < 8) {
      setErrorMessage('New password must be at least 8 characters');
      setLoading(false);
      setTimeout(() => setErrorMessage(''), 5000);
      return;
    }

    try {
      const response = await fetch('http://localhost:8001/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to change password');
      }

      setSuccessMessage('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to change password');
      setTimeout(() => setErrorMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleProfilePictureUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setErrorMessage('Please select an image file');
      setTimeout(() => setErrorMessage(''), 5000);
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage('Image size should be less than 5MB');
      setTimeout(() => setErrorMessage(''), 5000);
      return;
    }

    setUploadingPicture(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8001/api/auth/upload-profile-picture', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to upload profile picture');
      }

      setSuccessMessage('Profile picture updated successfully!');
      // Refresh user data to show new picture
      if (refreshUser) {
        refreshUser().catch(err => console.error('Failed to refresh user:', err));
      }
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to upload profile picture');
      setTimeout(() => setErrorMessage(''), 5000);
    } finally {
      setUploadingPicture(false);
    }
  };

  const handleDeleteProfilePicture = async () => {
    if (!confirm('Are you sure you want to delete your profile picture?')) {
      return;
    }

    setUploadingPicture(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:8001/api/auth/delete-profile-picture', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to delete profile picture');
      }

      setSuccessMessage('Profile picture deleted successfully!');
      // Refresh user data to remove picture
      if (refreshUser) {
        refreshUser().catch(err => console.error('Failed to refresh user:', err));
      }
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to delete profile picture');
      setTimeout(() => setErrorMessage(''), 5000);
    } finally {
      setUploadingPicture(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a] text-white overflow-hidden">
      {/* Header */}
      <div className="bg-[#181818]">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-[#ec6438]" />
              <h1 className="text-2xl font-semibold">Settings</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
          {/* Success/Error Messages */}
          {successMessage && (
            <div className="mb-6 bg-green-500/10 rounded-lg p-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <p className="text-green-500">{successMessage}</p>
          </div>
        )}
        
          {errorMessage && (
            <div className="mb-6 bg-red-500/10 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="text-red-500">{errorMessage}</p>
          </div>
        )}

          <div className="grid gap-6">
            {/* Profile Picture */}
            <div className="bg-[#181818] rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Camera className="w-5 h-5 text-[#ec6438]" />
              <h2 className="text-xl font-semibold">Profile Picture</h2>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="relative">
                {user.profile_picture ? (
                  <img
                    src={user.profile_picture.startsWith('http') 
                      ? user.profile_picture 
                      : `http://localhost:8001/${user.profile_picture}`}
                    alt="Profile"
                    className="w-24 h-24 rounded-full object-cover border-2 border-gray-700"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      if (e.currentTarget.nextElementSibling) {
                        (e.currentTarget.nextElementSibling as HTMLElement).style.display = 'flex';
                      }
                    }}
                  />
                ) : null}
                <div 
                  className="w-24 h-24 rounded-full bg-[#ec6438] flex items-center justify-center text-white font-semibold text-3xl border-2 border-gray-700"
                  style={{ display: user.profile_picture ? 'none' : 'flex' }}
                >
                  {(user.full_name || user.username).charAt(0).toUpperCase()}
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleProfilePictureUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingPicture}
                  className="bg-[#ec6438] hover:bg-[#d5552f] text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Camera className="w-4 h-4" />
                  {uploadingPicture ? 'Uploading...' : 'Upload Picture'}
                </button>
                
                {user.profile_picture && (
                  <button
                    onClick={handleDeleteProfilePicture}
                    disabled={uploadingPicture}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Picture
                  </button>
                )}
                
                <p className="text-xs text-gray-400">
                  Recommended: Square image, max 5MB (JPG, PNG, GIF, WebP)
                </p>
              </div>
            </div>
          </div>

            {/* Profile Information */}
            <div className="bg-[#181818] rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <User className="w-5 h-5 text-[#ec6438]" />
              <h2 className="text-xl font-semibold">Profile Information</h2>
            </div>
            
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={profileData.username}
                  onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Enter username"
                  minLength={3}
                  maxLength={100}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Enter email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={profileData.full_name}
                  onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Enter full name"
                  minLength={1}
                  maxLength={255}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#ec6438] hover:bg-[#d5552f] text-white px-6 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-5 h-5" />
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          </div>

            {/* Change Password */}
            <div className="bg-[#181818] rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-5 h-5 text-[#ec6438]" />
              <h2 className="text-xl font-semibold">Change Password</h2>
            </div>
            
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Enter current password"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Enter new password (min 8 characters)"
                  minLength={8}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  className="w-full px-4 py-3 bg-[#252525] border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ec6438] text-white"
                  placeholder="Confirm new password"
                  minLength={8}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#ec6438] hover:bg-[#d5552f] text-white px-6 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Lock className="w-5 h-5" />
                {loading ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>

            {/* Account Information */}
            <div className="bg-[#181818] rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Mail className="w-5 h-5 text-[#ec6438]" />
              <h2 className="text-xl font-semibold">Account Information</h2>
            </div>
            
              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-gray-900">
                <span className="text-gray-400">Account Status</span>
                <span className={user.is_active ? 'text-green-500' : 'text-red-500'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-900">
                <span className="text-gray-400">Role</span>
                <span className="text-white capitalize">{user.role}</span>
              </div>
                <div className="flex justify-between py-2">
                <span className="text-gray-400">Member Since</span>
                <span className="text-white">
                  {user.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  }) : 'N/A'}
                </span>
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
