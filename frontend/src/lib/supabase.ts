import { createClient } from '@supabase/supabase-js';

// Використовуємо примусове приведення до рядка (as string), 
// щоб TypeScript не сварився на можливий undefined
const supabaseUrl = (process.env.NEXT_PUBLIC_SUPABASE_URL || '') as string;
const supabaseAnonKey = (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '') as string;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('⚠️ Supabase environment variables are missing. Please check your .env.local file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
