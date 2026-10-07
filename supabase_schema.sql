create extension if not exists "pgcrypto";

create table if not exists public.profiles (
    id uuid primary key default gen_random_uuid(),
    email text unique not null,
    name text not null,
    password_hash text,
    age integer,
    weight integer,
    job text default 'desk_job',
    condition text default 'none',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.food_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references public.profiles(id) on delete cascade,
    user_email text not null,
    food_name text not null,
    calories integer not null default 0,
    protein integer not null default 0,
    carbs integer not null default 0,
    fat integer not null default 0,
    logged_at timestamptz not null default now()
);

create index if not exists idx_profiles_email on public.profiles(email);
create index if not exists idx_food_logs_user_email on public.food_logs(user_email);
create index if not exists idx_food_logs_user_id on public.food_logs(user_id);

alter table public.profiles enable row level security;
alter table public.food_logs enable row level security;

create policy "Profiles are viewable by authenticated users"
on public.profiles for select
using (auth.role() = 'authenticated');

create policy "Users can update their own profile"
on public.profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "Users can insert their own profile"
on public.profiles for insert
with check (auth.uid() = id);

create policy "Users can view their own food logs"
on public.food_logs for select
using (auth.uid() = user_id or auth.email() = user_email);

create policy "Users can insert their own food logs"
on public.food_logs for insert
with check (auth.uid() = user_id or auth.email() = user_email);

create policy "Users can update their own food logs"
on public.food_logs for update
using (auth.uid() = user_id or auth.email() = user_email)
with check (auth.uid() = user_id or auth.email() = user_email);
