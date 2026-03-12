const { createClient } = require('@supabase/supabase-js');
const path = require('path');
const config = require('./config');
const storage = require('./storage');

// Load .env from project root
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

let supabase = null;

function getSupabase() {
  if (supabase) return supabase;
  const url = process.env.SUPABASE_URL || config.getEnv('SUPABASE_URL');
  const key = process.env.SUPABASE_KEY || config.getEnv('SUPABASE_KEY');
  if (url && key) supabase = createClient(url, key);
  return supabase;
}

async function login(email, password) {
  const client = getSupabase();
  if (!client) return { ok: false, error: 'Supabase not configured' };
  try {
    const { data, error } = await client.auth.signInWithPassword({ email, password });
    if (error) return { ok: false, error: error.message };
    if (!data.user) return { ok: false, error: 'Invalid credentials' };

    let profile = await getProfileById(data.user.id);
    if (!profile) {
      const newProfile = {
        id: data.user.id,
        email,
        first_name: email.split('@')[0],
        last_name: 'User',
        plan: 'free'
      };
      const { data: insertData, error: insertErr } = await client.from('profiles').insert(newProfile).select().single();
      if (insertErr || !insertData) return { ok: false, error: 'Failed to initialize profile' };
      profile = insertData;
    }

    storage.setAuthToken(data.user.id);
    return { ok: true, profile };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

function logout() {
  storage.removeAuthToken();
  return { ok: true };
}

async function getProfileById(id) {
  const client = getSupabase();
  if (!client) return null;
  const { data } = await client.from('profiles').select('*').eq('id', id).single();
  return data && data[0] ? data[0] : (Array.isArray(data) ? data[0] : data);
}

async function getProfile() {
  const token = storage.getAuthToken();
  if (!token) return { ok: false, error: 'No session' };
  const client = getSupabase();
  if (!client) return { ok: false, error: 'Supabase not configured' };

  const isEmail = token.includes('@');
  const { data, error } = isEmail
    ? await client.from('profiles').select('*').eq('email', token).maybeSingle()
    : await client.from('profiles').select('*').eq('id', token).maybeSingle();

  const profile = data;
  if (error || !profile) return { ok: false, error: error?.message || 'Profile not found' };
  if (isEmail) storage.setAuthToken(profile.id);
  return { ok: true, profile };
}

async function validateAccess() {
  const token = storage.getAuthToken();
  if (!token) return { ok: false, needLogin: true };
  const result = await getProfile();
  if (!result.ok) return { ok: false, needLogin: true, error: result.error };

  const { profile } = result;
  const isOwner = profile.plan === 'architect';
  if (!isOwner) {
    if (!profile.purchase_id && profile.plan === 'free') {
      return { ok: false, needActivation: true, error: 'Active license required' };
    }
    const expiry = profile.plan_expires_at;
    if (expiry) {
      const expiryDate = new Date(expiry.replace('Z', '+00:00'));
      if (new Date() > expiryDate) {
        return { ok: false, error: 'Subscription expired' };
      }
    }
  }
  return { ok: true, profile };
}

async function activateKey(key) {
  const client = getSupabase();
  if (!client) return { ok: false, error: 'Supabase not configured' };
  const token = storage.getAuthToken();
  if (!token) return { ok: false, error: 'Login first' };

  try {
    const res = await getProfile();
    if (!res.ok || !res.profile) return { ok: false, error: 'Session invalid' };
    // Placeholder: validate key (e.g. call Stripe or your backend) and update profile
    // await client.from('profiles').update({ purchase_id: key, plan: 'pro' }).eq('id', res.profile.id);
    return { ok: false, error: 'Activation backend not configured. Implement your key validation.' };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

module.exports = {
  login,
  logout,
  getProfile,
  validateAccess,
  activateKey
};
