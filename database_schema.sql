-- FINAL CORRECTED SQL SCHEMA
-- Run this in Supabase SQL Editor

-- 1. Leads Table
create table leads (
  id uuid default gen_random_uuid() primary key,
  company_name text not null,
  website text,
  email text,
  phone text,
  instagram text,
  facebook text,
  x_profile text,
  region text,
  category text,
  google_rating numeric,
  review_count int,
  status text default 'new', 
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 2. Analysis Table
create table analysis (
  id uuid default gen_random_//uuid() primary key,
  lead_id uuid references leads(id) on delete cascade,
  lead_score int,
  pain_points text[],
  business_analysis text,
  suggested_solution text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Offers Table
create table offers (
  id uuid default gen_random_uuid() primary key,
  lead_id uuid references leads(id) on delete cascade,
  offer_text text,
  channel text,
  is_sent boolean default false,
  sent_at timestamp with time zone,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 4. Messages Table (For Dialogue Memory)
create table messages (
  id uuid default gen_random_uuid() primary key,
  lead_id uuid references leads(id) on delete cascade,
  sender text, -- 'ai' or 'client'
  text text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

alter table leads enable row level security;
alter table analysis enable row level security;
alter table offers enable row level security;
alter table messages enable row level security;

create policy "Full access for service role" on leads using (true);
create policy "Full access for service role" on analysis using (true);
create policy "Full access for service role" on offers using (true);
create policy "Full access for service role" on messages using (true);
