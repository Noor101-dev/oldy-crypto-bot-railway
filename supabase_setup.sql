-- Run this entire file in your Supabase SQL Editor

create table if not exists users (
  id bigserial primary key,
  telegram_id bigint unique not null,
  first_name text,
  email text,
  password_hash text,
  ref_code text unique,
  referred_by text,
  referral_count int default 0,
  batch text,
  batch_active boolean default false,
  joined_at timestamptz default now(),
  activated_at timestamptz
);

create table if not exists payments (
  id bigserial primary key,
  pay_id text unique not null,
  telegram_id bigint not null,
  batch text not null,
  amount numeric not null,
  status text default 'pending',
  tx_id text,
  created_at timestamptz default now()
);

create index if not exists idx_users_telegram_id on users(telegram_id);
create index if not exists idx_users_ref_code on users(ref_code);
create index if not exists idx_payments_pay_id on payments(pay_id);
create index if not exists idx_payments_status on payments(status);
