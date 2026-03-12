const { createClient } = require('@supabase/supabase-js');
const path = require('path');
const config = require('./config');
const storage = require('./storage');

require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const MAX_CHATS = 5;

function getSupabaseForChats() {
  const url = process.env.SUPABASE_URL || config.getEnv('SUPABASE_URL');
  const anonKey = process.env.SUPABASE_KEY || config.getEnv('SUPABASE_KEY');
  if (!url || !anonKey) return null;
  const client = createClient(url, anonKey, { auth: { persistSession: false } });
  const accessToken = storage.getAccessToken();
  const refreshToken = storage.getRefreshToken();
  if (!accessToken) return null;
  try {
    client.auth.setSession({ access_token: accessToken, refresh_token: refreshToken || '' });
  } catch (_) {
    return null;
  }
  return client;
}

async function loadChatsFromDb() {
  const supabase = getSupabaseForChats();
  if (!supabase) return null;
  try {
    const { data: chats, error: chatsError } = await supabase
      .from('omni_chats')
      .select('id, title, created_at')
      .order('created_at', { ascending: true });
    if (chatsError || !chats || chats.length === 0) {
      return chatsError ? null : [];
    }
    const result = [];
    for (const chat of chats) {
      const { data: rows } = await supabase
        .from('omni_messages')
        .select('role, content')
        .eq('chat_id', chat.id)
        .order('created_at', { ascending: true });
      const messages = (rows || []).map((m) => ({ role: m.role, content: m.content }));
      result.push({ id: chat.id, title: chat.title || 'New Session', messages });
    }
    return result;
  } catch (e) {
    console.error('loadChatsFromDb error', e);
    return null;
  }
}

async function saveChatsToDb(chats) {
  const supabase = getSupabaseForChats();
  if (!supabase) return { ok: false, error: 'No session' };
  const list = Array.isArray(chats) ? chats.slice(0, MAX_CHATS) : [];
  const updatedChats = [];
  try {
    const existingIds = new Set();
    for (const chat of list) {
      const id = chat.id;
      const isUuid = typeof id === 'string' && id.length === 36 && id.includes('-');
      const title = (chat.title || 'New Session').slice(0, 500);
      const messages = Array.isArray(chat.messages) ? chat.messages : [];
      if (isUuid && id) {
        await supabase.from('omni_chats').update({ title, updated_at: new Date().toISOString() }).eq('id', id);
        const { data: existing } = await supabase.from('omni_messages').select('id').eq('chat_id', id);
        if (existing && existing.length > 0) {
          await supabase.from('omni_messages').delete().eq('chat_id', id);
        }
        for (const m of messages) {
          if (m && (m.role === 'user' || m.role === 'assistant') && m.content != null) {
            await supabase.from('omni_messages').insert({
              chat_id: id,
              role: m.role,
              content: String(m.content).slice(0, 500000)
            });
          }
        }
        existingIds.add(id);
        updatedChats.push({ id, title: chat.title || 'New Session', messages: chat.messages || [] });
      } else {
        const { data: inserted, error: insertErr } = await supabase
          .from('omni_chats')
          .insert({ title })
          .select('id')
          .single();
        if (insertErr || !inserted) continue;
        const chatId = inserted.id;
        for (const m of messages) {
          if (m && (m.role === 'user' || m.role === 'assistant') && m.content != null) {
            await supabase.from('omni_messages').insert({
              chat_id: chatId,
              role: m.role,
              content: String(m.content).slice(0, 500000)
            });
          }
        }
        existingIds.add(chatId);
        updatedChats.push({ id: chatId, title: chat.title || 'New Session', messages: chat.messages || [] });
      }
    }
    const { data: allChats } = await supabase.from('omni_chats').select('id').order('created_at', { ascending: true });
    const toDelete = (allChats || []).filter((c) => !existingIds.has(c.id));
    for (const c of toDelete) {
      await supabase.from('omni_chats').delete().eq('id', c.id);
    }
    return { ok: true, chats: updatedChats };
  } catch (e) {
    console.error('saveChatsToDb error', e);
    return { ok: false, error: e.message };
  }
}

module.exports = {
  loadChatsFromDb,
  saveChatsToDb,
  MAX_CHATS
};
